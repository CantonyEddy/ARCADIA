import pygame
import time

class XboxController:
    def __init__(self, deadzone=0.15):
        pygame.init()
        pygame.joystick.init()

        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()

        print("Axes disponibles :", self.joystick.get_numaxes())
        print("Boutons disponibles :", self.joystick.get_numbuttons())
        print("Manette détectée :", self.joystick.get_name())

        self.deadzone = deadzone

    def apply_deadzone(self, value):
        return 0 if abs(value) < self.deadzone else value


# Boucle temps réel

if __name__ == "__main__":
    controller = XboxController()

    try:
        while True:
            pygame.event.pump()

            # AXES
            axes = []
            for i in range(controller.joystick.get_numaxes()):
                value = controller.joystick.get_axis(i)
                axes.append(f"Axe {i}: {value:.2f}")

            # BOUTONS
            buttons = []
            for i in range(controller.joystick.get_numbuttons()):
                state = controller.joystick.get_button(i)
                if state:
                    buttons.append(f"Bouton {i}")

            print(
                " | ".join(axes) +
                " || Boutons appuyés : " +
                (", ".join(buttons) if buttons else "aucun")
            )

            time.sleep(0.1)

    except KeyboardInterrupt:
        pygame.quit()
        print("Test terminé")