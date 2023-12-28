"""
Behalte den Überblick über Deine Arztrechnungen, wenn Du beihilfeberechtigt bist.

Mit Kontolupe kannst Du Deine Arztrechnungen erfassen und verwalten.
Du kannst Beihilfe- und PKV-Einreichungen erstellen und die Erstattungen
überwachen. Die App ist für die private Nutzung kostenlos.
"""

import datetime

import toga
from toga.app import AppStartupMethod, OnExitHandler
from toga.icons import Icon
from toga.style.pack import COLUMN, LEFT, RIGHT, ROW, TOP, BOTTOM, CENTER, Pack
from toga.paths import Paths
from kontolupe.buchungen import *

# set localization 
#import locale
#locale.setlocale(locale.LC_ALL, '')


class Kontolupe(toga.App):
    """Die Hauptklasse der Anwendung."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        """Initialisierung der Anwendung."""

        self.flag_bearbeite_arztrechnung = False
        self.arztrechnung_index = 0

    def berechne_summe_offene_buchungen(self):
        """Berechnet die Summe der offenen Buchungen."""
        summe = 0
        for arztrechnung in self.arztrechnungen:
            if arztrechnung.bezahlt == False:
                summe -= arztrechnung.betrag
        
        for beihilfepaket in self.beihilfepakete:
            if beihilfepaket.erhalten == False:
                summe += beihilfepaket.betrag

        for pkvpaket in self.pkvpakete:
            if pkvpaket.erhalten == False:
                summe += pkvpaket.betrag

        return summe


    def erzeuge_startseite(self):
        """Erzeugt die Startseite der Anwendung."""

        # Container für die Startseite
        self.box_startseite = toga.Box(style=Pack(direction=COLUMN))
        
        # Bereich, der die Summe der offenen Buchungen anzeigt
        label_start_summe_text = toga.Label('Summe offener Buchungen: ')
        self.label_start_summe_zahl = toga.Label('{:.2f} €'.format(self.berechne_summe_offene_buchungen()))
        box_startseite_summe = toga.Box(style=Pack(direction=ROW, alignment=CENTER))
        box_startseite_summe.add(label_start_summe_text)
        box_startseite_summe.add(self.label_start_summe_zahl)
        self.box_startseite.add(box_startseite_summe)

        # Bereich der Arztrechnungen
        label_start_arztrechnungen = toga.Label('Arztrechnungen')
        button_start_arztrechnungen_anzeigen = toga.Button('Anzeigen', on_press=self.zeige_seite_liste_arztrechnungen)
        button_start_arztrechnungen_neu = toga.Button('Neu', on_press=self.zeige_seite_formular_arztrechnungen_neu)
        box_startseite_arztrechnungen_buttons = toga.Box(style=Pack(direction=ROW, alignment=CENTER))
        box_startseite_arztrechnungen_buttons.add(button_start_arztrechnungen_anzeigen)
        box_startseite_arztrechnungen_buttons.add(button_start_arztrechnungen_neu)
        box_startseite_arztrechnungen = toga.Box(style=Pack(direction=COLUMN, alignment=CENTER))
        box_startseite_arztrechnungen.add(label_start_arztrechnungen)
        box_startseite_arztrechnungen.add(box_startseite_arztrechnungen_buttons)
        self.box_startseite.add(box_startseite_arztrechnungen)

        # Bereich der Beihilfe-Einreichungen
        label_start_beihilfe = toga.Label('Beihilfe-Einreichungen')
        button_start_beihilfe_anzeigen = toga.Button('Anzeigen')
        button_start_beihilfe_neu = toga.Button('Neu')
        box_startseite_beihilfe_buttons = toga.Box(style=Pack(direction=ROW, alignment=CENTER))
        box_startseite_beihilfe_buttons.add(button_start_beihilfe_anzeigen)
        box_startseite_beihilfe_buttons.add(button_start_beihilfe_neu)
        box_startseite_beihilfe = toga.Box(style=Pack(direction=COLUMN, alignment=CENTER))
        box_startseite_beihilfe.add(label_start_beihilfe)
        box_startseite_beihilfe.add(box_startseite_beihilfe_buttons)
        self.box_startseite.add(box_startseite_beihilfe)

        # Bereich der PKV-Einreichungen
        label_start_pkv = toga.Label('PKV-Einreichungen')
        button_start_pkv_anzeigen = toga.Button('Anzeigen')
        button_start_pkv_neu = toga.Button('Neu')
        box_startseite_pkv_buttons = toga.Box(style=Pack(direction=ROW, alignment=CENTER))
        box_startseite_pkv_buttons.add(button_start_pkv_anzeigen)
        box_startseite_pkv_buttons.add(button_start_pkv_neu)
        box_startseite_pkv = toga.Box(style=Pack(direction=COLUMN, alignment=CENTER))
        box_startseite_pkv.add(label_start_pkv)
        box_startseite_pkv.add(box_startseite_pkv_buttons)
        self.box_startseite.add(box_startseite_pkv)

    def zeige_startseite(self, widget):
        """Zurück zur Startseite."""
        self.label_start_summe_zahl.text = '{:.2f} €'.format(self.berechne_summe_offene_buchungen())
        self.main_window.content = self.box_startseite


    def erzeuge_seite_liste_arztrechnungen(self):
        """Erzeugt die Seite, auf der die Arztrechnungen angezeigt werden."""
        self.box_seite_liste_arztrechnungen = toga.Box(style=Pack(direction=COLUMN))
        self.box_seite_liste_arztrechnungen.add(toga.Button('Zurück', on_press=self.zeige_startseite))
        self.box_seite_liste_arztrechnungen.add(toga.Label('Arztrechnungen'))

        # Tabelle mit den Arztrechnungen
        self.tabelle_arztrechnungen = toga.Table(
            headings=['Rechnungsdatum', 'Arzt', 'Notiz', 'Betrag'], 
            data=self.arztrechnungen_liste,
            style=Pack(flex=1)
        )
        self.box_seite_liste_arztrechnungen.add(self.tabelle_arztrechnungen)

        # Buttons für die Arztrechnungen
        box_seite_liste_arztrechnungen_buttons = toga.Box(style=Pack(direction=ROW, alignment=CENTER))
        box_seite_liste_arztrechnungen_buttons.add(toga.Button('Neu', on_press=self.zeige_seite_formular_arztrechnungen_neu))
        box_seite_liste_arztrechnungen_buttons.add(toga.Button('Bearbeiten', on_press=self.zeige_seite_formular_arztrechnungen_bearbeiten))
        box_seite_liste_arztrechnungen_buttons.add(toga.Button('Löschen', on_press=self.bestaetige_arztrechnung_loeschen))
        self.box_seite_liste_arztrechnungen.add(box_seite_liste_arztrechnungen_buttons)    


    def zeige_seite_liste_arztrechnungen(self, widget):
        """Zeigt die Seite mit der Liste der Arztrechnungen."""
        self.main_window.content = self.box_seite_liste_arztrechnungen


    def erzeuge_seite_formular_arztrechnungen(self):
        """ Erzeugt das Formular zum Erstellen und Bearbeiten einer Arztrechnung."""
        self.box_seite_formular_arztrechnungen = toga.Box(style=Pack(direction=COLUMN))
        self.box_seite_formular_arztrechnungen.add(toga.Button('Zurück', on_press=self.zeige_startseite))
        self.label_formular_arztrechnungen = toga.Label('Neue Arztrechnung')
        self.box_seite_formular_arztrechnungen.add(self.label_formular_arztrechnungen)

        # Bereich zur Eingabe des Betrags
        box_formular_arztrechnungen_betrag = toga.Box(style=Pack(direction=ROW, alignment=CENTER))
        box_formular_arztrechnungen_betrag.add(toga.Label('Betrag: '))
        self.input_formular_arztrechnungen_betrag = toga.NumberInput(min=0, max=1000000, step=0.01, value=0)
        box_formular_arztrechnungen_betrag.add(self.input_formular_arztrechnungen_betrag)
        self.box_seite_formular_arztrechnungen.add(box_formular_arztrechnungen_betrag)

        # Bereich zur Eingabe des Rechnungsdatums
        box_formular_arztrechnungen_rechnungsdatum = toga.Box(style=Pack(direction=ROW, alignment=CENTER))
        box_formular_arztrechnungen_rechnungsdatum.add(toga.Label('Rechnungsdatum: '))
        self.input_formular_arztrechnungen_rechnungsdatum = toga.DateInput()
        box_formular_arztrechnungen_rechnungsdatum.add(self.input_formular_arztrechnungen_rechnungsdatum)
        self.box_seite_formular_arztrechnungen.add(box_formular_arztrechnungen_rechnungsdatum)

        # Bereich zur Auswahl des Arztes
        box_formular_arztrechnungen_arzt = toga.Box(style=Pack(direction=ROW, alignment=CENTER))
        box_formular_arztrechnungen_arzt.add(toga.Label('Arzt: '))
        self.input_formular_arztrechnungen_arzt = toga.Selection(items=self.aerzte_liste)
        box_formular_arztrechnungen_arzt.add(self.input_formular_arztrechnungen_arzt)
        self.box_seite_formular_arztrechnungen.add(box_formular_arztrechnungen_arzt)

        # Bereich zur Auswahl des Beihilfesatzes
        box_formular_arztrechnungen_beihilfesatz = toga.Box(style=Pack(direction=ROW, alignment=CENTER))
        box_formular_arztrechnungen_beihilfesatz.add(toga.Label('Beihilfesatz: '))
        self.input_formular_arztrechnungen_beihilfesatz = toga.NumberInput(min=0, max=100, step=10, value=0)
        box_formular_arztrechnungen_beihilfesatz.add(self.input_formular_arztrechnungen_beihilfesatz)
        self.box_seite_formular_arztrechnungen.add(box_formular_arztrechnungen_beihilfesatz)

        # Bereich zur Eingabe der Notiz
        box_formular_arztrechnungen_notiz = toga.Box(style=Pack(direction=ROW, alignment=CENTER))
        box_formular_arztrechnungen_notiz.add(toga.Label('Notiz: '))
        self.input_formular_arztrechnungen_notiz = toga.MultilineTextInput()
        box_formular_arztrechnungen_notiz.add(self.input_formular_arztrechnungen_notiz)
        self.box_seite_formular_arztrechnungen.add(box_formular_arztrechnungen_notiz)

        # Bereich der Buttons
        box_formular_arztrechnungen_buttons = toga.Box(style=Pack(direction=ROW, alignment=CENTER))
        box_formular_arztrechnungen_buttons.add(toga.Button('Speichern', on_press=self.arztrechnung_speichern))
        box_formular_arztrechnungen_buttons.add(toga.Button('Abbrechen', on_press=self.zeige_seite_liste_arztrechnungen))
        self.box_seite_formular_arztrechnungen.add(box_formular_arztrechnungen_buttons)


    def index_auswahl(self, widget):
        """Ermittelt den Index des ausgewählten Elements in einer Tabelle."""
        if widget.selection is not None:
            zeile = widget.selection
            for i, z in enumerate(widget.data):
                if str(z) == str(zeile):
                    return i
            else:
                print("Ausgewählte Zeile konnte nicht gefunden werden.")
                return None
        else:
            print("Keine Zeile ausgewählt.")
            return None


    def zeige_seite_formular_arztrechnungen_neu(self, widget):
        """Zeigt die Seite zum Erstellen einer Arztrechnung."""
        
        # Setze die Eingabefelder zurück
        self.input_formular_arztrechnungen_betrag.value = 0
        self.input_formular_arztrechnungen_rechnungsdatum.value = datetime.date.today()
        #self.input_formular_arztrechnungen_arzt.value = self.aerzte[0]
        self.input_formular_arztrechnungen_beihilfesatz.value = 0
        self.input_formular_arztrechnungen_notiz.value = ''

        # Zurücksetzen des Flags
        self.flag_bearbeite_arztrechnung = False

        # Setze die Überschrift
        self.label_formular_arztrechnungen.text = 'Neue Arztrechnung'

        # Zeige die Seite
        self.main_window.content = self.box_seite_formular_arztrechnungen

    
    def zeige_seite_formular_arztrechnungen_bearbeiten(self, widget):
        """Zeigt die Seite zum Bearbeiten einer Arztrechnung."""

        # Ermittle den Index der ausgewählten Arztrechnung
        self.arztrechnung_index = self.index_auswahl(self.tabelle_arztrechnungen)

        # Befülle die Eingabefelder
        self.input_formular_arztrechnungen_betrag.value = self.arztrechnungen[self.arztrechnung_index].betrag
        self.input_formular_arztrechnungen_rechnungsdatum.value = self.arztrechnungen[self.arztrechnung_index].rechnungsdatum
        #self.input_formular_arztrechnungen_arzt.value = self.arztrechnungen[self.arztrechnung_index].arzt_id
        self.input_formular_arztrechnungen_beihilfesatz.value = self.arztrechnungen[self.arztrechnung_index].beihilfesatz
        self.input_formular_arztrechnungen_notiz.value = self.arztrechnungen[self.arztrechnung_index].notiz

        # Setze das Flag
        self.flag_bearbeite_arztrechnung = True

        # Setze die Überschrift
        self.label_formular_arztrechnungen.text = 'Arztrechnung bearbeiten'

        # Zeige die Seite
        self.main_window.content = self.box_seite_formular_arztrechnungen


    def arztrechnung_speichern(self, widget):
        """Erstellt und speichert eine neue Arztrechnung."""
        # Ermittle die Id des Arztes
        arzt_id = 0
        for arzt in self.aerzte:
            if arzt.name == self.input_formular_arztrechnungen_arzt.value:
                arzt_id = arzt.db_id
                break

        if not self.flag_bearbeite_arztrechnung:
        # Erstelle eine neue Arztrechnung
            neue_arztrechnung = Arztrechnung()
            neue_arztrechnung.rechnungsdatum = self.input_formular_arztrechnungen_rechnungsdatum.value
            neue_arztrechnung.arzt_id = arzt_id
            neue_arztrechnung.notiz = self.input_formular_arztrechnungen_notiz.value
            neue_arztrechnung.betrag = float(self.input_formular_arztrechnungen_betrag.value)
            neue_arztrechnung.beihilfesatz = float(self.input_formular_arztrechnungen_beihilfesatz.value)

            # Speichere die Arztrechnung in der Datenbank
            neue_arztrechnung.db_id = self.db.neue_arztrechnung(neue_arztrechnung)

            # Füge die Arztrechnung der Liste hinzu
            self.arztrechnungen.append(neue_arztrechnung)
            self.arztrechnungen_liste.append([
                neue_arztrechnung.rechnungsdatum, 
                self.input_formular_arztrechnungen_arzt.value, 
                neue_arztrechnung.notiz, 
                neue_arztrechnung.betrag
            ])
        else:
            # Bearbeite die Arztrechnung
            self.arztrechnungen[self.arztrechnung_index].rechnungsdatum = self.input_formular_arztrechnungen_rechnungsdatum.value
            self.arztrechnungen[self.arztrechnung_index].arzt_id = arzt_id
            self.arztrechnungen[self.arztrechnung_index].notiz = self.input_formular_arztrechnungen_notiz.value
            self.arztrechnungen[self.arztrechnung_index].betrag = float(self.input_formular_arztrechnungen_betrag.value)
            self.arztrechnungen[self.arztrechnung_index].beihilfesatz = float(self.input_formular_arztrechnungen_beihilfesatz.value)

            # Speichere die Arztrechnung in der Datenbank
            self.arztrechnungen[self.arztrechnung_index].speichern(self.db)

            # Aktualisiere die Tabelle
            self.arztrechnungen_liste[self.arztrechnung_index] = [
                self.arztrechnungen[self.arztrechnung_index].rechnungsdatum, 
                self.input_formular_arztrechnungen_arzt.value, 
                self.arztrechnungen[self.arztrechnung_index].notiz, 
                self.arztrechnungen[self.arztrechnung_index].betrag
            ]

            # TODO: Aktualisiere verknüpfte Beihilfe- und PKV-Einreichungen


        # Tabelle der Arztrechnungen aktualisieren
        self.tabelle_arztrechnungen.data = self.arztrechnungen_liste

        # Zeige die Startseite
        self.zeige_seite_liste_arztrechnungen(widget)


    def bestaetige_arztrechnung_loeschen(self, widget):
        """Bestätigt das Löschen einer Arztrechnung."""
        if self.tabelle_arztrechnungen.selection:
            self.main_window.confirm_dialog(
                'Arztrechnung löschen', 
                'Soll die ausgewählte Arztrechnung wirklich gelöscht werden?',
                on_result=self.arztrechnung_loeschen
            )


    def arztrechnung_loeschen(self, widget, result):
        """Löscht eine Arztrechnung."""
        if self.tabelle_arztrechnungen.selection and result:
            index = self.index_auswahl(self.tabelle_arztrechnungen)
            self.arztrechnungen[index].loeschen(self.db)
            del self.arztrechnungen[index]
            del self.arztrechnungen_liste[index]
            self.tabelle_arztrechnungen.data = self.arztrechnungen_liste

            # TODO: Aktualisiere verknüpfte Beihilfe- und PKV-Einreichungen


    def startup(self):
        """Laden der Daten, Erzeugen der GUI-Elemente und des Hauptfensters."""
        self.db = Datenbank()

        # Lade alle Daten aus der Datenbank
        self.arztrechnungen = self.db.lade_arztrechnungen()
        self.aerzte = self.db.lade_aerzte()
        self.beihilfepakete = self.db.lade_beihilfepakete()
        self.pkvpakete = self.db.lade_pkvpakete()

        # Umwandlung der Daten in Listen für die GUI
        self.aerzte_liste = []
        for arzt in self.aerzte:
            self.aerzte_liste.append(arzt.name)

        self.arztrechnungen_liste = []
        for arztrechnung in self.arztrechnungen:
            # Ermittle den Namen des Arztes
            arzt_name = ''
            for arzt in self.aerzte:
                if arzt.db_id == arztrechnung.arzt_id:
                    arzt_name = arzt.name
                    break
            self.arztrechnungen_liste.append([
                arztrechnung.rechnungsdatum, 
                arzt_name,
                arztrechnung.notiz, 
                arztrechnung.betrag
            ])

        self.beihilfepakete_liste = []
        for beihilfepaket in self.beihilfepakete:
            self.beihilfepakete_liste.append([beihilfepaket.datum, beihilfepaket.betrag])

        self.pkvpakete_liste = []
        for pkvpaket in self.pkvpakete:
            self.pkvpakete_liste.append([pkvpaket.datum, pkvpaket.betrag])

        # Erzeuge alle GUI-Elemente
        self.erzeuge_startseite()
        self.erzeuge_seite_liste_arztrechnungen()
        self.erzeuge_seite_formular_arztrechnungen()

        # Erstelle das Hauptfenster
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.zeige_startseite(None)
        self.main_window.show()
        

def main():
    """Hauptschleife der Anwendung"""
    return Kontolupe()
