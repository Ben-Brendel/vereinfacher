"""
Behalte den Überblick über Deine Arztrechnungen, wenn Du beihilfeberechtigt bist.

Mit Kontolupe kannst Du Deine Arztrechnungen erfassen und verwalten.
Du kannst Beihilfe- und PKV-Einreichungen erstellen und die Erstattungen
überwachen. Die App ist für die private Nutzung kostenlos.
"""

import datetime
from dateutil.relativedelta import relativedelta

import toga
from toga.app import AppStartupMethod, OnExitHandler
from toga.icons import Icon
from toga.style.pack import COLUMN, LEFT, RIGHT, ROW, TOP, BOTTOM, CENTER, Pack
from toga.paths import Paths
from decimal import Decimal
from kontolupe.buchungen import *

# set localization 
#import locale
#locale.setlocale(locale.LC_ALL, '')


class Kontolupe(toga.App):
    """Die Hauptklasse der Anwendung."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        """Initialisierung der Anwendung."""

        # Create the content boxes
        #self.create_main_box()      
        #self.create_form_box()

    def startup(self):
        """Laden der Daten und Anzeigen des Hauptfensters."""
        self.db = Datenbank()

        # lade alle Daten aus der Datenbank
        self.arztrechnungen = self.db.lade_arztrechnungen()
        self.aerzte = self.db.lade_aerzte()
        self.beihilfepakete = self.db.lade_beihilfepakete()
        self.pkvpakete = self.db.lade_pkvpakete()

        # create the main window
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.show()
        

def main():
    """Hauptschleife der Anwendung"""
    return Kontolupe()
