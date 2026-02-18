import pygame
import sys

pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("❌ Aucun joystick détecté")
    sys.exit()

joy = pygame.joystick.Joystick(0)
joy.init()

print("✅ Manette détectée :", joy.get_name())
print("➡️ Boutons :", joy.get_numbuttons())
print("➡️ Axes :", joy.get_numaxes())
print("➡️ Hats (croix) :", joy.get_numhats())
print("\n=== DIAGNOSTIC EN COURS ===\n")

DEADZONE = 0.5
clock = pygame.time.Clock()

while True:
    pygame.event.pump()

    # Boutons
    for i in range(joy.get_numbuttons()):
        if joy.get_button(i):
            print(f"🟢 BOUTON {i} appuyé")

    # Axes
    for i in range(joy.get_numaxes()):
        val = round(joy.get_axis(i), 2)
        if abs(val) > DEADZONE:
            print(f"🟡 AXE {i} = {val}")

    # Hats (si présents)
    for i in range(joy.get_numhats()):
        hat = joy.get_hat(i)
        if hat != (0, 0):
            print(f"🔵 HAT {i} = {hat}")

    clock.tick(10)
