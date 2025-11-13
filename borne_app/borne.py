# borne_app/borne.py
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty, ListProperty
from kivy.core.window import Window
from kivy.uix.button import Button

# Importe NOS modules
from . import game_scanner
from . import launcher

class GameButton(BoxLayout):
    """
    Widget Kivy custom pour notre bouton de jeu.
    (On le définira dans le .kv)
    """
    pass

class RootWidget(BoxLayout):
    # 'game_list_layout' est une référence au GridLayout dans le .kv
    game_list_layout = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)
        self.game_list = game_scanner.scan_roms()
        self.populate_game_list()

    def populate_game_list(self):
        """Remplit la liste de jeux dans l'interface."""
        for game_data in self.game_list:
            button_text = f"[{game_data['system']}] - {game_data['name']}"
            
            # On crée un bouton custom
            button = Button(
                text=button_text,
                font_size='24sp',
                size_hint_y=None,
                height=80
            )
            
            # On lie le bouton à la fonction de lancement
            button.bind(on_press=lambda btn, data=game_data: self.launch(data))
            
            self.game_list_layout.add_widget(button)

    def launch(self, game_data):
        """Fonction intermédiaire pour appeler le launcher."""
        launcher.launch_game(game_data)


class BorneApp(App):
    def build(self):
        # Kivy va automatiquement charger 'borne.kv'
        # et le définir comme le widget racine.
        Window.clearcolor = (0.1, 0.1, 0.1, 1)
        return RootWidget()