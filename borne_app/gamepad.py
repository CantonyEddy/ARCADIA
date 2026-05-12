"""
Gestion des manettes — traduit les events joystick pygame en KEYDOWN
synthétiques afin que la navigation menu reste centralisée côté clavier.

Hot-plug : géré via JOYDEVICEADDED / JOYDEVICEREMOVED.
"""
from __future__ import annotations

import logging
from typing import Dict, Optional, Tuple

import pygame

logger = logging.getLogger(__name__)

# Bouton (Xbox-like) -> touche clavier émulée.
# Numérotation SDL2 standard : 0=A, 1=B, 2=X, 3=Y, 6=Back, 7=Start, ...
BUTTON_TO_KEY: Dict[int, int] = {
    0: pygame.K_RETURN,   # A = confirmer
    7: pygame.K_RETURN,   # Start = confirmer (alternative)
}

# Stick analogique : seuils
AXIS_DEADZONE = 0.5

# Répétition tant que la direction est maintenue
REPEAT_DELAY_MS = 380
REPEAT_INTERVAL_MS = 110


def _post_key(key: int) -> None:
    """Injecte un KEYDOWN synthétique dans la file d'events pygame."""
    pygame.event.post(
        pygame.event.Event(pygame.KEYDOWN, {"key": key, "mod": 0, "unicode": "", "scancode": 0})
    )


class GamepadManager:
    """
    Manettes connectées + traduction des events vers KEYDOWN.

    L'avantage de poster des KEYDOWN plutôt que d'appeler directement
    handle_arrow_key/handle_enter : la logique de navigation existante
    reste l'unique source de vérité.
    """

    def __init__(self) -> None:
        self.joysticks: Dict[int, pygame.joystick.Joystick] = {}
        self._held_key: Optional[int] = None
        self._held_since: int = 0
        self._last_repeat: int = 0
        # Etat directionnel par manette (instance_id -> (x, y)) pour le stick
        self._axis_dir: Dict[int, Tuple[int, int]] = {}

        # Détection initiale : pygame.joystick.init() a déjà été appelé
        # par BorneInterface, on peut énumérer.
        for i in range(pygame.joystick.get_count()):
            try:
                joy = pygame.joystick.Joystick(i)
                self._register(joy)
            except pygame.error as e:
                logger.warning("Init manette index=%d échouée : %s", i, e)

    # ============================================================
    # Lifecycle des manettes
    # ============================================================
    def _register(self, joy: pygame.joystick.Joystick) -> None:
        try:
            joy.init()
            iid = joy.get_instance_id()
            if iid in self.joysticks:
                return  # déjà connue (idempotent)
            self.joysticks[iid] = joy
            logger.info("Manette connectée : %s (instance %d)", joy.get_name(), iid)
        except pygame.error as e:
            logger.warning("Enregistrement manette échoué : %s", e)

    def _unregister(self, instance_id: int) -> None:
        joy = self.joysticks.pop(instance_id, None)
        if joy is not None:
            logger.info("Manette déconnectée : %s", joy.get_name())
        self._axis_dir.pop(instance_id, None)

    def status(self) -> str:
        """Pour l'InfoLine de SETTINGS."""
        if not self.joysticks:
            return "Non connectée"
        names = [j.get_name() for j in self.joysticks.values()]
        if len(names) == 1:
            return names[0]
        return f"{names[0]} (+{len(names) - 1})"

    def count(self) -> int:
        return len(self.joysticks)

    # ============================================================
    # Traitement des events
    # ============================================================
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Retourne True si l'event a été traité par le manager."""
        et = event.type
        if et == pygame.JOYDEVICEADDED:
            self._register(pygame.joystick.Joystick(event.device_index))
            return True
        if et == pygame.JOYDEVICEREMOVED:
            self._unregister(event.instance_id)
            return True
        if et == pygame.JOYBUTTONDOWN:
            key = BUTTON_TO_KEY.get(event.button)
            if key is not None:
                _post_key(key)
            return True
        if et == pygame.JOYHATMOTION:
            self._on_hat(event.value)
            return True
        if et == pygame.JOYAXISMOTION:
            self._on_axis(event.instance_id, event.axis, event.value)
            return True
        return False

    def tick(self) -> None:
        """À appeler une fois par frame ; gère la répétition tant qu'une
        direction est maintenue (D-pad ou stick)."""
        if self._held_key is None:
            return
        now = pygame.time.get_ticks()
        if now - self._held_since < REPEAT_DELAY_MS:
            return
        if now - self._last_repeat >= REPEAT_INTERVAL_MS:
            _post_key(self._held_key)
            self._last_repeat = now

    # ============================================================
    # Helpers directionnels
    # ============================================================
    def _on_hat(self, value: Tuple[int, int]) -> None:
        # Convention pygame hat : y=1 = haut, y=-1 = bas, x=1 = droite, x=-1 = gauche
        x, y = value
        if x == 0 and y == 0:
            self._release()
            return
        # Priorité horizontale en diagonale
        if x != 0:
            key = pygame.K_RIGHT if x > 0 else pygame.K_LEFT
        else:
            key = pygame.K_UP if y > 0 else pygame.K_DOWN
        if key != self._held_key:
            self._set_held(key)
            _post_key(key)

    def _on_axis(self, instance_id: int, axis: int, value: float) -> None:
        # Seul le stick gauche est interprété (axes 0 et 1).
        # Convention SDL : axis_y < 0 = haut, > 0 = bas.
        if axis not in (0, 1):
            return
        cur_x, cur_y = self._axis_dir.get(instance_id, (0, 0))
        if axis == 0:
            cur_x = 1 if value > AXIS_DEADZONE else (-1 if value < -AXIS_DEADZONE else 0)
        else:
            cur_y = 1 if value > AXIS_DEADZONE else (-1 if value < -AXIS_DEADZONE else 0)
        self._axis_dir[instance_id] = (cur_x, cur_y)

        if cur_x == 0 and cur_y == 0:
            # Vérifier qu'AUCUNE manette ne pousse encore avant de relâcher.
            if all(d == (0, 0) for d in self._axis_dir.values()):
                self._release()
            return
        # Priorité horizontale
        if cur_x != 0:
            key = pygame.K_RIGHT if cur_x > 0 else pygame.K_LEFT
        else:
            key = pygame.K_DOWN if cur_y > 0 else pygame.K_UP
        if key != self._held_key:
            self._set_held(key)
            _post_key(key)

    def _set_held(self, key: int) -> None:
        now = pygame.time.get_ticks()
        self._held_key = key
        self._held_since = now
        self._last_repeat = now

    def _release(self) -> None:
        self._held_key = None
