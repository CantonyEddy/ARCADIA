"""
Ancienne implémentation monolithique de l'interface.

Elle est gardée comme simple alias vers la nouvelle architecture
basée sur borne_interface.BorneInterface, afin de ne pas casser
éventuels imports existants.
"""

from .borne_interface import BorneInterface
        