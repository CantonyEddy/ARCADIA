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






# class XboxController:
#     def __init__(self, deadzone=0.15):
#         pygame.init()
#         pygame.joystick.init()

#         if pygame.joystick.get_count() == 0:
#             raise Exception("Aucune manette détectée")

#         self.joystick = pygame.joystick.Joystick(0)
#         self.joystick.init()
#         print("Axes disponibles :", self.joystick.get_numaxes())
#         print("Boutons disponibles :", self.joystick.get_numbuttons())


#         self.deadzone = deadzone
#         print(f"Manette détectée : {self.joystick.get_name()}")

#     def apply_deadzone(self, value):
#         return 0 if abs(value) < self.deadzone else value

#     def get_axis_safe(self, index):
#         if index < self.joystick.get_numaxes():
#             return self.joystick.get_axis(index)
#         return 0.0

#     def read(self):
#         pygame.event.pump()

#         state = {
#             "A": self.joystick.get_button(0) if self.joystick.get_numbuttons() > 0 else 0,
#             "B": self.joystick.get_button(1) if self.joystick.get_numbuttons() > 1 else 0,
#             "X": self.joystick.get_button(2) if self.joystick.get_numbuttons() > 2 else 0,
#             "Y": self.joystick.get_button(3) if self.joystick.get_numbuttons() > 3 else 0,

#             "LEFT_X": self.apply_deadzone(self.get_axis_safe(0)),
#             "LEFT_Y": self.apply_deadzone(self.get_axis_safe(1)),
#             "RIGHT_X": self.apply_deadzone(self.get_axis_safe(2)),
#             "RIGHT_Y": self.apply_deadzone(self.get_axis_safe(3)),

#             # Triggers génériques (si présents)
#             "TRIGGER_1": self.get_axis_safe(4),
#             "TRIGGER_2": self.get_axis_safe(5),
#         }

#         return state

#     def close(self):
#         pygame.quit()

# Boucle temps réel

# if __name__ == "__main__":
#     controller = XboxController()

#     try:
#         while True:
#             state = controller.read()

#             if state["A"]:
#                 print("Bouton A appuyé")
#             if state["B"]:
#                 print("Bouton B appuyé")

#             if abs(state["LEFT_X"]) > 0:
#                 print(f"Stick gauche X : {state['LEFT_X']:.2f}")
#             if abs(state["LEFT_Y"]) > 0:
#                 print(f"Stick gauche Y : {state['LEFT_Y']:.2f}")

#             time.sleep(0.05)

#     except KeyboardInterrupt:
#         controller.close()
#         print("Test arrêté")