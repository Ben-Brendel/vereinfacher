"""
Behalte den Überblick über Deine Arztrechnungen, wenn Du beihilfeberechtigt bist.

Mit Kontolupe kannst Du Deine Arztrechnungen erfassen und verwalten.
Du kannst Beihilfe- und PKV-Einreichungen erstellen und die Erstattungen
überwachen. Die App ist für die private Nutzung kostenlos.
"""

import toga
from toga.app import AppStartupMethod, OnExitHandler
from toga.icons import Icon
from toga.style.pack import COLUMN, LEFT, RIGHT, ROW, TOP, BOTTOM, CENTER, Pack
from toga.sources import ListSource
import itertools
import datetime
from kontolupe.buchungen import *

# set localization 
#import locale
#locale.setlocale(locale.LC_ALL, '')

# Styles erzeugen
style_h1 = Pack(font_size=16, font_weight='bold')
style_h2 = Pack(font_size=12, font_weight='bold')

class Kontolupe(toga.App):
    """Die Hauptklasse der Anwendung."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        """Initialisierung der Anwendung."""

        # Hilfsvariablen zur Bearbeitung von Arztrechnungen
        self.flag_bearbeite_arztrechnung = False
        self.arztrechnung_b_id = 0

        # Hilfsvariablen zur Bearbeitung von Ärzten
        self.flag_bearbeite_arzt = False
        self.arzt_b_id = 0

        # Hilfsvariablen zur Bearbeitung der Beihilfe-Pakete
        self.flag_bearbeite_beihilfepaket = False
        self.beihilfepaket_b_id = 0

        # Hilfsvariablen zur Bearbeitung der PKV-Pakete
        self.flag_bearbeite_pkvpaket = False
        self.pkvpaket_b_id = 0

        # Erzeuge die Menüleiste
        gruppe_arztrechnungen = toga.Group('Arztrechnungen', order = 1)

        self.cmd_arztrechnungen_anzeigen = toga.Command(
            self.zeige_seite_liste_arztrechnungen,
            'Arztrechnungen anzeigen',
            tooltip = 'Zeigt die Liste der Arztrechnungen an.',
            group = gruppe_arztrechnungen,
            order = 10
        )

        self.cmd_arztrechnungen_neu = toga.Command(
            self.zeige_seite_formular_arztrechnungen_neu,
            'Neue Arztrechnung',
            tooltip = 'Erstellt eine neue Arztrechnung.',
            group = gruppe_arztrechnungen,
            order = 20
        )

        gruppe_beihilfepakete = toga.Group('Beihilfe-Einreichungen', order = 2)

        self.cmd_beihilfepakete_anzeigen = toga.Command(
            self.zeige_seite_liste_beihilfepakete,
            'Beihilfe-Einreichungen anzeigen',
            tooltip = 'Zeigt die Liste der Beihilfe-Einreichungen an.',
            group = gruppe_beihilfepakete,
            order = 10
        )

        self.cmd_beihilfepakete_neu = toga.Command(
            self.zeige_seite_formular_beihilfepakete_neu,
            'Neue Beihilfe-Einreichung',
            tooltip = 'Erstellt eine neue Beihilfe-Einreichung.',
            group = gruppe_beihilfepakete,
            order = 20
        )

        gruppe_pkvpakete = toga.Group('PKV-Einreichungen', order = 3)

        self.cmd_pkvpakete_anzeigen = toga.Command(
            None,
            'PKV-Einreichungen anzeigen',
            tooltip = 'Zeigt die Liste der PKV-Einreichungen an.',
            group = gruppe_pkvpakete,
            order = 10
        )

        self.cmd_pkvpakete_neu = toga.Command(
            None,
            'Neue PKV-Einreichung',
            tooltip = 'Erstellt eine neue PKV-Einreichung.',
            group = gruppe_pkvpakete,
            order = 20
        )

        gruppe_aerzte = toga.Group('Ärzte', order = 4)

        self.cmd_aerzte_anzeigen = toga.Command(
            self.zeige_seite_liste_aerzte,
            'Ärzte anzeigen',
            tooltip = 'Zeigt die Liste der Ärzte an.',
            group = gruppe_aerzte,
            order = 10
        )

        self.cmd_aerzte_neu = toga.Command(
            self.zeige_seite_formular_aerzte_neu,
            'Neuer Arzt',
            tooltip = 'Erstellt einen neuen Arzt.',
            group = gruppe_aerzte,
            order = 20
        )

    def berechne_summe_offene_buchungen(self):
        """Berechnet die Summe der offenen Buchungen."""
        
        summe = 0
        for arztrechnung in self.arztrechnungen:
            if arztrechnung.bezahlt == False:
                summe -= arztrechnung.betrag
            if arztrechnung.beihilfe_id == None:
                summe += arztrechnung.betrag * (arztrechnung.beihilfesatz / 100)
            if arztrechnung.pkv_id == None:
                summe += arztrechnung.betrag * (1 - (arztrechnung.beihilfesatz / 100))
        
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
        label_start_summe_text = toga.Label('Offener Betrag: ', style=style_h1)
        self.label_start_summe_zahl = toga.Label('{:.2f} €'.format(self.berechne_summe_offene_buchungen()), style=style_h1)
        box_startseite_summe = toga.Box(style=Pack(direction=ROW, alignment=CENTER))
        box_startseite_summe.add(label_start_summe_text)
        box_startseite_summe.add(self.label_start_summe_zahl)
        self.box_startseite.add(box_startseite_summe)

        # Bereich der Arztrechnungen
        label_start_arztrechnungen = toga.Label('Arztrechnungen', style=style_h2)
        button_start_arztrechnungen_anzeigen = toga.Button('Anzeigen', on_press=self.zeige_seite_liste_arztrechnungen, style=Pack(width=200))
        button_start_arztrechnungen_neu = toga.Button('Neu', on_press=self.zeige_seite_formular_arztrechnungen_neu, style=Pack(width=200))
        box_startseite_arztrechnungen_buttons = toga.Box(style=Pack(direction=ROW, alignment=CENTER))
        box_startseite_arztrechnungen_buttons.add(button_start_arztrechnungen_anzeigen)
        box_startseite_arztrechnungen_buttons.add(button_start_arztrechnungen_neu)
        box_startseite_arztrechnungen = toga.Box(style=Pack(direction=COLUMN, alignment=CENTER))
        box_startseite_arztrechnungen.add(label_start_arztrechnungen)
        box_startseite_arztrechnungen.add(box_startseite_arztrechnungen_buttons)
        self.box_startseite.add(box_startseite_arztrechnungen)

        # Bereich der Beihilfe-Einreichungen
        label_start_beihilfe = toga.Label('Beihilfe-Einreichungen', style=style_h2)
        button_start_beihilfe_anzeigen = toga.Button('Anzeigen', style=Pack(width=200), on_press=self.zeige_seite_liste_beihilfepakete)
        button_start_beihilfe_neu = toga.Button('Neu', style=Pack(width=200), on_press=self.zeige_seite_formular_beihilfepakete_neu)
        box_startseite_beihilfe_buttons = toga.Box(style=Pack(direction=ROW, alignment=CENTER))
        box_startseite_beihilfe_buttons.add(button_start_beihilfe_anzeigen)
        box_startseite_beihilfe_buttons.add(button_start_beihilfe_neu)
        box_startseite_beihilfe = toga.Box(style=Pack(direction=COLUMN, alignment=CENTER))
        box_startseite_beihilfe.add(label_start_beihilfe)
        box_startseite_beihilfe.add(box_startseite_beihilfe_buttons)
        self.box_startseite.add(box_startseite_beihilfe)

        # Bereich der PKV-Einreichungen
        label_start_pkv = toga.Label('PKV-Einreichungen', style=style_h2)
        button_start_pkv_anzeigen = toga.Button('Anzeigen', style=Pack(width=200))
        button_start_pkv_neu = toga.Button('Neu', style=Pack(width=200))
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
        self.box_seite_liste_arztrechnungen.add(toga.Label('Arztrechnungen', style=style_h1))

        # Tabelle mit den Arztrechnungen
        self.tabelle_arztrechnungen_container = toga.ScrollContainer(style=Pack(flex=1))
        self.tabelle_arztrechnungen = toga.Table(
            headings    = ['Info', 'Betrag', 'Bezahlt', 'Beihilfe', 'PKV'],
            accessors   = ['info', 'betrag_euro', 'bezahlt_text', 'beihilfe_eingereicht', 'pkv_eingereicht'],
            data        = self.arztrechnungen_liste,
            style=Pack(width=600, flex=1)
        )
        self.tabelle_arztrechnungen_container.content = self.tabelle_arztrechnungen
        self.box_seite_liste_arztrechnungen.add(self.tabelle_arztrechnungen_container)

        # Buttons für die Arztrechnungen
        box_seite_liste_arztrechnungen_buttons = toga.Box(style=Pack(direction=ROW, alignment=CENTER))
        box_seite_liste_arztrechnungen_buttons.add(toga.Button('Neu', on_press=self.zeige_seite_formular_arztrechnungen_neu, style=Pack(flex=1)))
        box_seite_liste_arztrechnungen_buttons.add(toga.Button('Bearbeiten', on_press=self.zeige_seite_formular_arztrechnungen_bearbeiten, style=Pack(flex=1)))
        box_seite_liste_arztrechnungen_buttons.add(toga.Button('Löschen', on_press=self.bestaetige_arztrechnung_loeschen, style=Pack(flex=1)))
        self.box_seite_liste_arztrechnungen.add(box_seite_liste_arztrechnungen_buttons)    


    def zeige_seite_liste_arztrechnungen(self, widget):
        """Zeigt die Seite mit der Liste der Arztrechnungen."""
        self.main_window.content = self.box_seite_liste_arztrechnungen


    def erzeuge_seite_formular_arztrechnungen(self):
        """ Erzeugt das Formular zum Erstellen und Bearbeiten einer Arztrechnung."""
        self.box_seite_formular_arztrechnungen = toga.Box(style=Pack(direction=COLUMN))
        self.box_seite_formular_arztrechnungen.add(toga.Button('Zurück', on_press=self.zeige_seite_liste_arztrechnungen))
        self.label_formular_arztrechnungen = toga.Label('Neue Arztrechnung', style=style_h1)
        self.box_seite_formular_arztrechnungen.add(self.label_formular_arztrechnungen)

        # Bereich zur Eingabe des Rechnungsdatums
        box_formular_arztrechnungen_rechnungsdatum = toga.Box(style=Pack(direction=ROW, alignment=CENTER))
        box_formular_arztrechnungen_rechnungsdatum.add(toga.Label('Rechnungsdatum: ', style=Pack(flex=1)))
        self.input_formular_arztrechnungen_rechnungsdatum = toga.DateInput(style=Pack(flex=2))
        box_formular_arztrechnungen_rechnungsdatum.add(self.input_formular_arztrechnungen_rechnungsdatum)
        self.box_seite_formular_arztrechnungen.add(box_formular_arztrechnungen_rechnungsdatum)

        # Bereich zur Eingabe des Betrags
        box_formular_arztrechnungen_betrag = toga.Box(style=Pack(direction=ROW, alignment=CENTER))
        box_formular_arztrechnungen_betrag.add(toga.Label('Betrag in €: ', style=Pack(flex=1)))
        self.input_formular_arztrechnungen_betrag = toga.NumberInput(min=0, step=0.01, value=0, style=Pack(flex=2))
        box_formular_arztrechnungen_betrag.add(self.input_formular_arztrechnungen_betrag)
        self.box_seite_formular_arztrechnungen.add(box_formular_arztrechnungen_betrag)

        # Bereich zur Auswahl des Arztes
        box_formular_arztrechnungen_arzt = toga.Box(style=Pack(direction=ROW, alignment=CENTER))
        box_formular_arztrechnungen_arzt.add(toga.Label('Arzt: ', style=Pack(flex=1)))
        self.input_formular_arztrechnungen_arzt = toga.Selection(items=self.aerzte_liste, accessor='name', style=Pack(flex=2))
        box_formular_arztrechnungen_arzt.add(self.input_formular_arztrechnungen_arzt)
        self.box_seite_formular_arztrechnungen.add(box_formular_arztrechnungen_arzt)

        # Bereich zur Eingabe der Notiz
        box_formular_arztrechnungen_notiz = toga.Box(style=Pack(direction=ROW, alignment=CENTER))
        box_formular_arztrechnungen_notiz.add(toga.Label('Notiz: ', style=Pack(flex=1)))
        self.input_formular_arztrechnungen_notiz = toga.TextInput(style=Pack(flex=2))
        box_formular_arztrechnungen_notiz.add(self.input_formular_arztrechnungen_notiz)
        self.box_seite_formular_arztrechnungen.add(box_formular_arztrechnungen_notiz)

        # Bereich zur Auswahl des Beihilfesatzes
        box_formular_arztrechnungen_beihilfesatz = toga.Box(style=Pack(direction=ROW, alignment=CENTER))
        box_formular_arztrechnungen_beihilfesatz.add(toga.Label('Beihilfesatz in %: ', style=Pack(flex=1)))
        self.input_formular_arztrechnungen_beihilfesatz = toga.NumberInput(min=0, max=100, step=10, value=0, style=Pack(flex=2))
        box_formular_arztrechnungen_beihilfesatz.add(self.input_formular_arztrechnungen_beihilfesatz)
        self.box_seite_formular_arztrechnungen.add(box_formular_arztrechnungen_beihilfesatz)

        # Bereich zur Eingabe des Buchungsdatums
        box_formular_arztrechnungen_buchungsdatum = toga.Box(style=Pack(direction=ROW, alignment=CENTER))
        box_formular_arztrechnungen_buchungsdatum.add(toga.Label('Datum Überweisung: ', style=Pack(flex=1)))
        self.input_formular_arztrechnungen_buchungsdatum = toga.DateInput(style=Pack(flex=2))
        box_formular_arztrechnungen_buchungsdatum.add(self.input_formular_arztrechnungen_buchungsdatum)
        self.box_seite_formular_arztrechnungen.add(box_formular_arztrechnungen_buchungsdatum)

        # Bereich zur Angabe der Bezahlung
        box_formular_arztrechnungen_bezahlt = toga.Box(style=Pack(direction=ROW, alignment=CENTER))
        #box_formular_arztrechnungen_bezahlt.add(toga.Label('Bezahlt: ', style=Pack(flex=1)))
        self.input_formular_arztrechnungen_bezahlt = toga.Switch('Bezahlt')
        box_formular_arztrechnungen_bezahlt.add(self.input_formular_arztrechnungen_bezahlt)
        self.box_seite_formular_arztrechnungen.add(box_formular_arztrechnungen_bezahlt)

        # Bereich der Buttons
        box_formular_arztrechnungen_buttons = toga.Box(style=Pack(direction=ROW, alignment=CENTER))
        box_formular_arztrechnungen_buttons.add(toga.Button('Speichern', on_press=self.arztrechnung_speichern, style=Pack(flex=1)))
        box_formular_arztrechnungen_buttons.add(toga.Button('Abbrechen', on_press=self.zeige_seite_liste_arztrechnungen, style=Pack(flex=1)))
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
        self.input_formular_arztrechnungen_rechnungsdatum.value = None
        self.input_formular_arztrechnungen_arzt.value = self.aerzte_liste[0]
        self.input_formular_arztrechnungen_beihilfesatz.value = 0
        self.input_formular_arztrechnungen_notiz.value = ''
        self.input_formular_arztrechnungen_buchungsdatum.value = None
        self.input_formular_arztrechnungen_bezahlt.value = False

        # Zurücksetzen des Flags
        self.flag_bearbeite_arztrechnung = False

        # Setze die Überschrift
        self.label_formular_arztrechnungen.text = 'Neue Arztrechnung'

        # Zeige die Seite
        self.main_window.content = self.box_seite_formular_arztrechnungen

    
    def zeige_seite_formular_arztrechnungen_bearbeiten(self, widget):
        """Zeigt die Seite zum Bearbeiten einer Arztrechnung."""

        # Ermittle den Index der ausgewählten Arztrechnung
        self.arztrechnung_b_id = self.index_auswahl(self.tabelle_arztrechnungen)

        # Ermittle den Index des Arztes in der Ärzteliste
        arzt_index = None
        for i, arzt in enumerate(self.aerzte):
            if arzt.db_id == self.arztrechnungen[self.arztrechnung_b_id].arzt_id:
                arzt_index = i
                break

        # Befülle die Eingabefelder
        self.input_formular_arztrechnungen_betrag.value = self.arztrechnungen[self.arztrechnung_b_id].betrag
        self.input_formular_arztrechnungen_rechnungsdatum.value = self.arztrechnungen[self.arztrechnung_b_id].rechnungsdatum
        self.input_formular_arztrechnungen_beihilfesatz.value = self.arztrechnungen[self.arztrechnung_b_id].beihilfesatz
        self.input_formular_arztrechnungen_notiz.value = self.arztrechnungen[self.arztrechnung_b_id].notiz
        self.input_formular_arztrechnungen_buchungsdatum.value = self.arztrechnungen[self.arztrechnung_b_id].buchungsdatum
        self.input_formular_arztrechnungen_bezahlt.value = self.arztrechnungen[self.arztrechnung_b_id].bezahlt

        # Auswahlfeld für den Arzt befüllen
        if arzt_index is not None:
            self.input_formular_arztrechnungen_arzt.value = self.aerzte_liste[arzt_index]
        else:
            self.input_formular_arztrechnungen_arzt.value = self.aerzte_liste[0]

        # Setze das Flag
        self.flag_bearbeite_arztrechnung = True

        # Setze die Überschrift
        self.label_formular_arztrechnungen.text = 'Arztrechnung bearbeiten'

        # Zeige die Seite
        self.main_window.content = self.box_seite_formular_arztrechnungen


    def arztrechnung_speichern(self, widget):
        """Erstellt und speichert eine neue Arztrechnung."""

        if not self.flag_bearbeite_arztrechnung:
        # Erstelle eine neue Arztrechnung
            neue_arztrechnung = Arztrechnung()
            neue_arztrechnung.rechnungsdatum = self.input_formular_arztrechnungen_rechnungsdatum.value
            neue_arztrechnung.arzt_id = self.input_formular_arztrechnungen_arzt.value.db_id
            neue_arztrechnung.notiz = self.input_formular_arztrechnungen_notiz.value
            neue_arztrechnung.betrag = float(self.input_formular_arztrechnungen_betrag.value)
            neue_arztrechnung.beihilfesatz = float(self.input_formular_arztrechnungen_beihilfesatz.value)
            neue_arztrechnung.buchungsdatum = self.input_formular_arztrechnungen_buchungsdatum.value
            neue_arztrechnung.bezahlt = self.input_formular_arztrechnungen_bezahlt.value

            # Speichere die Arztrechnung in der Datenbank
            #neue_arztrechnung.db_id = self.db.neue_arztrechnung(neue_arztrechnung)
            neue_arztrechnung.neu(self.db)

            # Füge die Arztrechnung der Liste hinzu
            self.arztrechnungen.append(neue_arztrechnung)
            self.arztrechnungen_liste_anfuegen(neue_arztrechnung)
        else:
            # Bearbeite die Arztrechnung
            self.arztrechnungen[self.arztrechnung_b_id].rechnungsdatum = self.input_formular_arztrechnungen_rechnungsdatum.value
            self.arztrechnungen[self.arztrechnung_b_id].arzt_id = self.input_formular_arztrechnungen_arzt.value.db_id
            self.arztrechnungen[self.arztrechnung_b_id].notiz = self.input_formular_arztrechnungen_notiz.value
            self.arztrechnungen[self.arztrechnung_b_id].betrag = float(self.input_formular_arztrechnungen_betrag.value)
            self.arztrechnungen[self.arztrechnung_b_id].beihilfesatz = float(self.input_formular_arztrechnungen_beihilfesatz.value)
            self.arztrechnungen[self.arztrechnung_b_id].buchungsdatum = self.input_formular_arztrechnungen_buchungsdatum.value
            self.arztrechnungen[self.arztrechnung_b_id].bezahlt = self.input_formular_arztrechnungen_bezahlt.value

            # Speichere die Arztrechnung in der Datenbank
            self.arztrechnungen[self.arztrechnung_b_id].speichern(self.db)

            # Aktualisiere die Liste der Arztrechnungen
            self.arztrechnungen_liste_aendern(self.arztrechnungen[self.arztrechnung_b_id], self.arztrechnung_b_id)

            # Flag zurücksetzen
            self.flag_bearbeite_arztrechnung = False

            # TODO: Aktualisiere verknüpfte Beihilfe- und PKV-Einreichungen

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

            # TODO: Aktualisiere verknüpfte Beihilfe- und PKV-Einreichungen


    def erzeuge_seite_liste_aerzte(self):
        """Erzeugt die Seite, auf der die Ärzte angezeigt werden."""
        self.box_seite_liste_aerzte = toga.Box(style=Pack(direction=COLUMN))
        self.box_seite_liste_aerzte.add(toga.Button('Zurück', on_press=self.zeige_startseite))
        self.box_seite_liste_aerzte.add(toga.Label('Ärzte', style=style_h1))

        # Tabelle mit den Ärzten

        self.tabelle_aerzte_container = toga.ScrollContainer(style=Pack(flex=1))
        self.tabelle_aerzte = toga.Table(
            headings    = ['Arzt'], 
            accessors   = ['name'],
            data        = self.aerzte_liste,
            style       = Pack(flex=1)
        )
        self.tabelle_aerzte_container.content = self.tabelle_aerzte
        self.box_seite_liste_aerzte.add(self.tabelle_aerzte_container)

        # Buttons für die Ärzten
        box_seite_liste_aerzte_buttons = toga.Box(style=Pack(direction=ROW, alignment=CENTER))
        box_seite_liste_aerzte_buttons.add(toga.Button('Neu', on_press=self.zeige_seite_formular_aerzte_neu, style=Pack(flex=1)))
        box_seite_liste_aerzte_buttons.add(toga.Button('Bearbeiten', on_press=self.zeige_seite_formular_aerzte_bearbeiten, style=Pack(flex=1)))
        box_seite_liste_aerzte_buttons.add(toga.Button('Löschen', on_press=self.bestaetige_arzt_loeschen, style=Pack(flex=1)))
        self.box_seite_liste_aerzte.add(box_seite_liste_aerzte_buttons)   


    def zeige_seite_liste_aerzte(self, widget):
        """Zeigt die Seite mit der Liste der Ärzte."""
        self.main_window.content = self.box_seite_liste_aerzte


    def erzeuge_seite_formular_aerzte(self):
        """Erzeugt das Formular zum Erstellen und Bearbeiten eines Arztes."""
        self.box_seite_formular_aerzte = toga.Box(style=Pack(direction=COLUMN))
        self.box_seite_formular_aerzte.add(toga.Button('Zurück', on_press=self.zeige_seite_liste_aerzte))
        self.label_formular_aerzte = toga.Label('Neuer Arzt', style=style_h1)
        self.box_seite_formular_aerzte.add(self.label_formular_aerzte)

        # Bereich zur Eingabe des Namens
        box_formular_aerzte_name = toga.Box(style=Pack(direction=ROW, alignment=CENTER))
        box_formular_aerzte_name.add(toga.Label('Name des Arztes: ', style=Pack(flex=1)))
        self.input_formular_aerzte_name = toga.TextInput(style=Pack(flex=2))
        box_formular_aerzte_name.add(self.input_formular_aerzte_name)
        self.box_seite_formular_aerzte.add(box_formular_aerzte_name)

        # Bereich der Buttons
        box_formular_aerzte_buttons = toga.Box(style=Pack(direction=ROW, alignment=CENTER))
        box_formular_aerzte_buttons.add(toga.Button('Speichern', on_press=self.arzt_speichern, style=Pack(flex=1)))
        box_formular_aerzte_buttons.add(toga.Button('Abbrechen', on_press=self.zeige_seite_liste_aerzte, style=Pack(flex=1)))
        self.box_seite_formular_aerzte.add(box_formular_aerzte_buttons)


    def zeige_seite_formular_aerzte_neu(self, widget):
        """Zeigt die Seite zum Erstellen eines Arztes."""
        # Setze die Eingabefelder zurück
        self.input_formular_aerzte_name.value = ''

        # Zurücksetzen des Flags
        self.flag_bearbeite_arzt = False

        # Setze die Überschrift
        self.label_formular_aerzte.text = 'Neuer Arzt'

        # Zeige die Seite
        self.main_window.content = self.box_seite_formular_aerzte


    def zeige_seite_formular_aerzte_bearbeiten(self, widget):
        """Zeigt die Seite zum Bearbeiten eines Arztes."""
        # Ermittle den Index der ausgewählten Arztrechnung
        self.arzt_b_id = self.index_auswahl(self.tabelle_aerzte)

        # Befülle die Eingabefelder
        self.input_formular_aerzte_name.value = self.aerzte[self.arzt_b_id].name

        # Setze das Flag
        self.flag_bearbeite_arzt = True

        # Setze die Überschrift
        self.label_formular_aerzte.text = 'Arzt bearbeiten'

        # Zeige die Seite
        self.main_window.content = self.box_seite_formular_aerzte


    def arzt_speichern(self, widget):
        """Erstellt und speichert einen neuen Arzt."""
        if not self.flag_bearbeite_arzt:
        # Erstelle einen neuen Arzt
            neuer_arzt = Arzt()
            neuer_arzt.name = self.input_formular_aerzte_name.value

            # Speichere den Arzt in der Datenbank
            #neuer_arzt.db_id = self.db.neuer_arzt(neuer_arzt)
            neuer_arzt.neu(self.db)

            # Füge den Arzt der Liste hinzu
            self.aerzte.append(neuer_arzt)
            self.aerzte_liste_anfuegen(neuer_arzt)
        else:
            # Bearbeite den Arzt
            self.aerzte[self.arzt_b_id].name = self.input_formular_aerzte_name.value

            # Speichere den Arzt in der Datenbank
            self.aerzte[self.arzt_b_id].speichern(self.db)

            # Aktualisiere die Liste der Ärzte
            self.aerzte_liste_aendern(self.aerzte[self.arzt_b_id], self.arzt_b_id)

            # Flage zurücksetzen
            self.flag_bearbeite_arzt = False

            # TODO: Aktualisiere verknüpfte Arztrechnungen


        # Zeige die Liste der Ärzte
        self.zeige_seite_liste_aerzte(widget)

    
    def bestaetige_arzt_loeschen(self, widget):
        """Bestätigt das Löschen eines Arztes."""
        if self.tabelle_aerzte.selection:
            self.main_window.confirm_dialog(
                'Arzt löschen', 
                'Soll der ausgewählte Arzt wirklich gelöscht werden?',
                on_result=self.arzt_loeschen
            )

    def arzt_loeschen(self, widget, result):
        """Löscht einen Arzt."""
        if self.tabelle_aerzte.selection and result:
            index = self.index_auswahl(self.tabelle_aerzte)
            self.aerzte[index].loeschen(self.db)
            del self.aerzte[index]
            del self.aerzte_liste[index]

            # Arztrechnungen aktualisieren
            self.arztrechnungen_aktualisieren()
            self.input_formular_aerzte_name.items = self.aerzte_liste


    def erzeuge_seite_liste_beihilfepakete(self):
        """Erzeugt die Seite, auf der die Beihilfepakete angezeigt werden."""
        self.box_seite_liste_beihilfepakete = toga.Box(style=Pack(direction=COLUMN))
        self.box_seite_liste_beihilfepakete.add(toga.Button('Zurück', on_press=self.zeige_startseite))
        self.box_seite_liste_beihilfepakete.add(toga.Label('Beihilfepakete', style=style_h1))

        # Tabelle mit den Beihilfepaketen
        self.tabelle_beihilfepakete_container = toga.ScrollContainer(style=Pack(flex=1))
        self.tabelle_beihilfepakete = toga.Table(
            headings    = ['Datum', 'Betrag', 'Erhalten'], 
            accessors   = ['datum', 'betrag_euro', 'erhalten_text'],
            data        = self.beihilfepakete_liste,
            style       = Pack(flex=1)
        )
        self.tabelle_beihilfepakete_container.content = self.tabelle_beihilfepakete
        self.box_seite_liste_beihilfepakete.add(self.tabelle_beihilfepakete_container)

        # Buttons für die Beihilfepakete
        box_seite_liste_beihilfepakete_buttons = toga.Box(style=Pack(direction=ROW, alignment=CENTER))
        box_seite_liste_beihilfepakete_buttons.add(toga.Button('Neu', on_press=self.zeige_seite_formular_beihilfepakete_neu, style=Pack(flex=1)))
        box_seite_liste_beihilfepakete_buttons.add(toga.Button('Bearbeiten', on_press=self.zeige_seite_formular_beihilfepakete_bearbeiten, style=Pack(flex=1)))
        box_seite_liste_beihilfepakete_buttons.add(toga.Button('Löschen', on_press=self.bestaetige_beihilfepaket_loeschen, style=Pack(flex=1)))
        self.box_seite_liste_beihilfepakete.add(box_seite_liste_beihilfepakete_buttons)


    def zeige_seite_liste_beihilfepakete(self, widget):
        """Zeigt die Seite mit der Liste der Beihilfepakete."""
        self.main_window.content = self.box_seite_liste_beihilfepakete

    
    def erzeuge_seite_formular_beihilfepakete(self):
        """Erzeugt das Formular zum Erstellen und Bearbeiten eines Beihilfepakets."""
        self.box_seite_formular_beihilfepakete = toga.Box(style=Pack(direction=COLUMN))
        self.box_seite_formular_beihilfepakete.add(toga.Button('Zurück', on_press=self.zeige_seite_liste_beihilfepakete))
        self.label_formular_beihilfepakete = toga.Label('Neues Beihilfepaket', style=style_h1)
        self.box_seite_formular_beihilfepakete.add(self.label_formular_beihilfepakete)

        # Bereich zur Eingabe des Datums
        box_formular_beihilfepakete_datum = toga.Box(style=Pack(direction=ROW, alignment=CENTER))
        box_formular_beihilfepakete_datum.add(toga.Label('Datum: ', style=Pack(flex=1)))
        self.input_formular_beihilfepakete_datum = toga.DateInput(style=Pack(flex=2))
        box_formular_beihilfepakete_datum.add(self.input_formular_beihilfepakete_datum)
        self.box_seite_formular_beihilfepakete.add(box_formular_beihilfepakete_datum)

        # Bereich zur Auswahl der zugehörigen Arztrechnungen
        self.formular_beihilfepakete_arztrechnungen_container = toga.ScrollContainer(style=Pack(flex=1))
        self.formular_beihilfe_tabelle_arztrechnungen = toga.Table(
            headings        = ['Info', 'Betrag', 'Bezahlt'],
            accessors       = ['info', 'betrag_euro', 'bezahlt_text'],
            data            = self.erzeuge_liste_beihilfe_tabelle_arztrechnungen(),
            multiple_select = True,
            style           = Pack(height=300, flex=1)
        )
        self.formular_beihilfepakete_arztrechnungen_container.content = self.formular_beihilfe_tabelle_arztrechnungen
        self.box_seite_formular_beihilfepakete.add(self.formular_beihilfepakete_arztrechnungen_container)

        # Bereich zur Eingabe des Betrags
        box_formular_beihilfepakete_betrag = toga.Box(style=Pack(direction=ROW, alignment=CENTER))
        box_formular_beihilfepakete_betrag.add(toga.Label('Betrag in €: ', style=Pack(flex=1)))
        self.input_formular_beihilfepakete_betrag = toga.NumberInput(min=0, step=0.01, value=0, style=Pack(flex=2))
        box_formular_beihilfepakete_betrag.add(self.input_formular_beihilfepakete_betrag)
        self.box_seite_formular_beihilfepakete.add(box_formular_beihilfepakete_betrag)

        # Bereich zur Angabe der Erhaltung
        box_formular_beihilfepakete_erhalten = toga.Box(style=Pack(direction=ROW, alignment=CENTER))
        self.input_formular_beihilfepakete_erhalten = toga.Switch('Erhalten')
        box_formular_beihilfepakete_erhalten.add(self.input_formular_beihilfepakete_erhalten)
        self.box_seite_formular_beihilfepakete.add(box_formular_beihilfepakete_erhalten)

        # Bereich der Buttons
        box_formular_beihilfepakete_buttons = toga.Box(style=Pack(direction=ROW, alignment=CENTER))
        box_formular_beihilfepakete_buttons.add(toga.Button('Speichern', on_press=self.beihilfepaket_speichern, style=Pack(flex=1)))
        box_formular_beihilfepakete_buttons.add(toga.Button('Abbrechen', on_press=self.zeige_seite_liste_beihilfepakete, style=Pack(flex=1)))
        self.box_seite_formular_beihilfepakete.add(box_formular_beihilfepakete_buttons)


    def zeige_seite_formular_beihilfepakete_neu(self, widget):
        """Zeigt die Seite zum Erstellen eines Beihilfepakets."""
        # Setze die Eingabefelder zurück
        self.input_formular_beihilfepakete_betrag.value = 0
        self.input_formular_beihilfepakete_datum.value = None
        self.input_formular_beihilfepakete_erhalten.value = False
        self.formular_beihilfe_tabelle_arztrechnungen.data = self.erzeuge_liste_beihilfe_tabelle_arztrechnungen()

        # Zurücksetzen des Flags
        self.flag_bearbeite_beihilfepaket = False

        # Setze die Überschrift
        self.label_formular_beihilfepakete.text = 'Neues Beihilfepaket'

        # Zeige die Seite
        self.main_window.content = self.box_seite_formular_beihilfepakete


    def zeige_seite_formular_beihilfepakete_bearbeiten(self, widget):
        """Zeigt die Seite zum Bearbeiten eines Beihilfepakets."""
        # Ermittle den Index des ausgewählten Beihilfepakets
        self.beihilfepaket_b_id = self.index_auswahl(self.tabelle_beihilfepakete)

        # Befülle die Eingabefelder
        self.input_formular_beihilfepakete_betrag.value = self.beihilfepakete[self.beihilfepaket_b_id].betrag
        self.input_formular_beihilfepakete_datum.value = self.beihilfepakete[self.beihilfepaket_b_id].datum
        self.input_formular_beihilfepakete_erhalten.value = self.beihilfepakete[self.beihilfepaket_b_id].erhalten

        # Tabelleninhalt aktualisieren
        tabelle_daten = self.erzeuge_liste_beihilfe_tabelle_arztrechnungen(self.beihilfepakete[self.beihilfepaket_b_id].db_id)
        self.formular_beihilfe_tabelle_arztrechnungen.data = tabelle_daten

        # TODO: Wähle die verknüpften Arztrechnungen in der Tabelle aus
        # self.formular_beihilfe_tabelle_arztrechnungen.selection = []
        # for i, arztrechnung in enumerate(tabelle_daten):
        #     if arztrechnung.beihilfe_id == self.beihilfepakete[self.beihilfepaket_b_id].db_id:
        #         self.formular_beihilfe_tabelle_arztrechnungen.selection.append(self.formular_beihilfe_tabelle_arztrechnungen.data[i])

        # Setze das Flag
        self.flag_bearbeite_beihilfepaket = True

        # Setze die Überschrift
        self.label_formular_beihilfepakete.text = 'Beihilfepaket bearbeiten'

        # Zeige die Seite
        self.main_window.content = self.box_seite_formular_beihilfepakete


    def beihilfepaket_speichern(self, widget):
        """Erstellt und speichert ein neues Beihilfepaket oder ändert ein zur Bearbeitung gewähltes."""
        if not self.flag_bearbeite_beihilfepaket:
            # Erstelle ein neues Beihilfepaket
            neues_beihilfepaket = BeihilfePaket()
            neues_beihilfepaket.datum = self.input_formular_beihilfepakete_datum.value
            neues_beihilfepaket.betrag = float(self.input_formular_beihilfepakete_betrag.value)
            neues_beihilfepaket.erhalten = self.input_formular_beihilfepakete_erhalten.value

            # Speichere das Beihilfepaket in der Datenbank
            neues_beihilfepaket.neu(self.db)

            # Füge das Beihilfepaket der Liste hinzu
            self.beihilfepakete.append(neues_beihilfepaket)
            self.beihilfepakete_liste_anfuegen(neues_beihilfepaket)

            # Aktualisiere verknüpfte Arztrechnungen
            for auswahl_rg in self.formular_beihilfe_tabelle_arztrechnungen.selection:
                for rg in self.arztrechnungen:
                    if auswahl_rg.db_id == rg.db_id:
                        rg.beihilfe_id = neues_beihilfepaket.db_id
                        rg.speichern(self.db)

        else:
            # Bearbeite das Beihilfepaket
            self.beihilfepakete[self.beihilfepaket_b_id].datum = self.input_formular_beihilfepakete_datum.value
            self.beihilfepakete[self.beihilfepaket_b_id].betrag = float(self.input_formular_beihilfepakete_betrag.value)
            self.beihilfepakete[self.beihilfepaket_b_id].erhalten = self.input_formular_beihilfepakete_erhalten.value

            # Speichere das Beihilfepaket in der Datenbank
            self.beihilfepakete[self.beihilfepaket_b_id].speichern(self.db)

            # Aktualisiere die Liste der Beihilfepakete
            self.beihilfepakete_liste_aendern(self.beihilfepakete[self.beihilfepaket_b_id], self.beihilfepaket_b_id)

            # Flage zurücksetzen
            self.flag_bearbeite_beihilfepaket = False

            # Aktualisiere verknüpfte Arztrechnungen
            for auswahl_rg in self.formular_beihilfe_tabelle_arztrechnungen.selection:
                for rg in self.arztrechnungen:
                    if auswahl_rg.db_id == rg.db_id:
                        rg.beihilfe_id = self.beihilfepakete[self.beihilfepaket_b_id].db_id
                        rg.speichern(self.db)

        # Arztrechnungen aktualisieren
        self.arztrechnungen_liste_aktualisieren()

        # Wechsel zur Liste der Beihilfepakete
        self.zeige_seite_liste_beihilfepakete(widget)


    def bestaetige_beihilfepaket_loeschen(self, widget):
        """Bestätigt das Löschen eines Beihilfepakets."""
        if self.tabelle_beihilfepakete.selection:
            self.main_window.confirm_dialog(
                'Beihilfepaket löschen', 
                'Soll das ausgewählte Beihilfepaket wirklich gelöscht werden?',
                on_result=self.beihilfepaket_loeschen
            )


    def beihilfepaket_loeschen(self, widget, result):
        """Löscht ein Beihilfepaket."""
        if self.tabelle_beihilfepakete.selection and result:
            index = self.index_auswahl(self.tabelle_beihilfepakete)
            self.beihilfepakete[index].loeschen(self.db)
            del self.beihilfepakete[index]
            del self.beihilfepakete_liste[index]
            self.arztrechnungen_aktualisieren()


    def erzeuge_liste_beihilfe_tabelle_arztrechnungen(self, beihilfe_id=None):
        """Erzeugt die Liste der Arztrechnungen im Formular für die Beihilfepakete."""

        data = ListSource(accessors=[
            'db_id', 
            'betrag', 
            'betrag_euro',
            'rechnungsdatum', 
            'arzt_id', 
            'notiz', 
            'arzt_name', 
            'info', 
            'beihilfesatz', 
            'buchungsdatum', 
            'bezahlt', 
            'bezahlt_text',
            'beihilfe_id', 
            'beihilfe_eingereicht',
            'pkv_id'
            'pkv_eingereicht'
        ])

        if self.arztrechnungen_liste is None:
            return data

        for arztrechnung in self.arztrechnungen_liste:
            if arztrechnung.beihilfe_id is None or arztrechnung.beihilfe_id == beihilfe_id:
                data.append({
                'db_id': arztrechnung.db_id,
                'betrag': arztrechnung.betrag,
                'betrag_euro': '{:.2f} €'.format(arztrechnung.betrag),
                'rechnungsdatum': arztrechnung.rechnungsdatum,
                'arzt_id': arztrechnung.arzt_id,
                'notiz': arztrechnung.notiz,
                'arzt_name': self.arzt_name(arztrechnung.arzt_id),
                'info': self.arzt_name(arztrechnung.arzt_id) + ' - ' + arztrechnung.notiz,
                'beihilfesatz': arztrechnung.beihilfesatz,
                'buchungsdatum': arztrechnung.buchungsdatum,
                'bezahlt': arztrechnung.bezahlt,
                'bezahlt_text': 'Ja' if arztrechnung.bezahlt else 'Nein',
                'beihilfe_id': arztrechnung.beihilfe_id,
                'beihilfe_eingereicht': 'Ja' if arztrechnung.beihilfe_id else 'Nein',
                'pkv_id': arztrechnung.pkv_id,
                'pkv_eingereicht': 'Ja' if arztrechnung.pkv_id else 'Nein'
            })

        return data

    def arzt_name(self, arzt_id):
        """Ermittelt den Namen eines Arztes anhand seiner Id."""
        for arzt in self.aerzte:
            if arzt.db_id == arzt_id:
                return arzt.name
        return ''
    

    def arztrechnungen_liste_erzeugen(self):
        """Erzeugt die Liste für die Arztrechnungen."""
        self.arztrechnungen_liste = ListSource(accessors=[
            'db_id', 
            'betrag', 
            'betrag_euro',
            'rechnungsdatum', 
            'arzt_id', 
            'notiz', 
            'arzt_name', 
            'info', 
            'beihilfesatz', 
            'buchungsdatum', 
            'bezahlt', 
            'bezahlt_text',
            'beihilfe_id', 
            'beihilfe_eingereicht',
            'pkv_id'
            'pkv_eingereicht'
        ])

        for arztrechnung in self.arztrechnungen:            
            self.arztrechnungen_liste_anfuegen(arztrechnung)


    def aerzte_liste_erzeugen(self):
        """Erzeugt die Liste für die Ärzte."""
        self.aerzte_liste = ListSource(accessors=[
            'db_id',
            'name',
        ])

        for arzt in self.aerzte:            
            self.aerzte_liste_anfuegen(arzt)


    def beihilfepakete_liste_erzeugen(self):
        """Erzeugt die Liste für die Beihilfepakete."""
        self.beihilfepakete_liste = ListSource(accessors=[
            'db_id',
            'betrag',
            'betrag_euro',
            'datum',
            'erhalten',
            'erhalten_text'
        ])

        for beihilfepaket in self.beihilfepakete:            
            self.beihilfepakete_liste_anfuegen(beihilfepaket)


    def pkvpakete_liste_erzeugen(self):
        """Erzeugt die Liste für die PKV-Pakete."""
        self.pkvpakete_liste = ListSource(accessors=[
            'db_id',
            'betrag',
            'betrag_euro',
            'datum',
            'erhalten',
            'erhalten_text'
        ])

        for pkvpaket in self.pkvpakete:            
            self.pkvpakete_liste_anfuegen(pkvpaket)


    def arztrechnungen_liste_anfuegen(self, arztrechnung):
        """Fügt der Liste der Arztrechnungen eine neue Arztrechnung hinzu."""
        self.arztrechnungen_liste.append({
                'db_id': arztrechnung.db_id,
                'betrag': arztrechnung.betrag,
                'betrag_euro': '{:.2f} €'.format(arztrechnung.betrag),
                'rechnungsdatum': arztrechnung.rechnungsdatum,
                'arzt_id': arztrechnung.arzt_id,
                'notiz': arztrechnung.notiz,
                'arzt_name': self.arzt_name(arztrechnung.arzt_id),
                'info': self.arzt_name(arztrechnung.arzt_id) + ' - ' + arztrechnung.notiz,
                'beihilfesatz': arztrechnung.beihilfesatz,
                'buchungsdatum': arztrechnung.buchungsdatum,
                'bezahlt': arztrechnung.bezahlt,
                'bezahlt_text': 'Ja' if arztrechnung.bezahlt else 'Nein',
                'beihilfe_id': arztrechnung.beihilfe_id,
                'beihilfe_eingereicht': 'Ja' if arztrechnung.beihilfe_id else 'Nein',
                'pkv_id': arztrechnung.pkv_id,
                'pkv_eingereicht': 'Ja' if arztrechnung.pkv_id else 'Nein'
            })
        

    def arztrechnungen_aktualisieren(self):
        """Aktualisiert die referenzierten Werte in dden Arztrechnungen und speichert sie in der Datenbank."""

        for arztrechnung in self.arztrechnungen:

            # Aktualisiere die Beihilfe
            if arztrechnung.beihilfe_id:
                # Überprüfe ob die Beihilfe noch existiert
                beihilfepaket_vorhanden = False
                for beihilfepaket in self.beihilfepakete:
                    if beihilfepaket.db_id == arztrechnung.beihilfe_id:
                        beihilfepaket_vorhanden = True
                        break
                
                # Wenn die Beihilfe nicht mehr existiert, setze die Beihilfe zurück
                if not beihilfepaket_vorhanden:
                    arztrechnung.beihilfe_id = None

            # Aktualisiere die PKV
            if arztrechnung.pkv_id:
                # Überprüfe ob die PKV noch existiert
                pkvpaket_vorhanden = False
                for pkvpaket in self.pkvpakete:
                    if pkvpaket.db_id == arztrechnung.pkv_id:
                        pkvpaket_vorhanden = True
                        break
                
                # Wenn die PKV nicht mehr existiert, setze die PKV zurück
                if not pkvpaket_vorhanden:
                    arztrechnung.pkv_id = None

            # Aktualisiere den Arzt
            if arztrechnung.arzt_id:
                # Überprüfe ob der Arzt noch existiert
                arzt_vorhanden = False
                for arzt in self.aerzte:
                    if arzt.db_id == arztrechnung.arzt_id:
                        arzt_vorhanden = True
                        break
                
                # Wenn der Arzt nicht mehr existiert, setze den Arzt zurück
                if not arzt_vorhanden:
                    arztrechnung.arzt_id = None
            
            # Aktualisierte Arztrechnung speichern
            arztrechnung.speichern(self.db)

        # Aktualisiere die Liste der Arztrechnungen
        self.arztrechnungen_liste_aktualisieren()


    def arztrechnungen_liste_aktualisieren(self):
        """Aktualisiert die referenzierten Werte in der Liste der Arztrechnungen."""
        for rg_id in range(len(self.arztrechnungen_liste)):
            self.arztrechnungen_liste_aendern(self.arztrechnungen[rg_id], rg_id)
        

    def aerzte_liste_anfuegen(self, arzt):
        """Fügt der Liste der Ärzte einen neuen Arzt hinzu."""
        self.aerzte_liste.append({
                'db_id': arzt.db_id,
                'name': arzt.name,
            })
        

    def beihilfepakete_liste_anfuegen(self, beihilfepaket):
        """Fügt der Liste der Beihilfepakete ein neues Beihilfepaket hinzu."""
        self.beihilfepakete_liste.append({
                'db_id': beihilfepaket.db_id,
                'betrag': beihilfepaket.betrag,
                'betrag_euro': '{:.2f} €'.format(beihilfepaket.betrag),
                'datum': beihilfepaket.datum,
                'erhalten': beihilfepaket.erhalten,
                'erhalten_text': 'Ja' if beihilfepaket.erhalten else 'Nein'
            })
        

    def pkvpakete_liste_anfuegen(self, pkvpaket):
        """Fügt der Liste der PKV-Pakete ein neues PKV-Paket hinzu."""
        self.pkvpakete_liste.append({
                'db_id': pkvpaket.db_id,
                'betrag': pkvpaket.betrag,
                'betrag_euro': '{:.2f} €'.format(pkvpaket.betrag),
                'datum': pkvpaket.datum,
                'erhalten': pkvpaket.erhalten,
                'erhalten_text': 'Ja' if pkvpaket.erhalten else 'Nein'
            })


    def arztrechnungen_liste_aendern(self, arztrechnung, rg_id):
        """Ändert ein Element der Liste der Arztrechnungen."""
        self.arztrechnungen_liste[rg_id] = {
                'db_id': arztrechnung.db_id,
                'betrag': arztrechnung.betrag,
                'betrag_euro': '{:.2f} €'.format(arztrechnung.betrag),
                'rechnungsdatum': arztrechnung.rechnungsdatum,
                'arzt_id': arztrechnung.arzt_id,
                'notiz': arztrechnung.notiz,
                'arzt_name': self.arzt_name(arztrechnung.arzt_id),
                'info': self.arzt_name(arztrechnung.arzt_id) + ' - ' + arztrechnung.notiz,
                'beihilfesatz': arztrechnung.beihilfesatz,
                'buchungsdatum': arztrechnung.buchungsdatum,
                'bezahlt': arztrechnung.bezahlt,
                'bezahlt_text': 'Ja' if arztrechnung.bezahlt else 'Nein',
                'beihilfe_id': arztrechnung.beihilfe_id,
                'beihilfe_eingereicht': 'Ja' if arztrechnung.beihilfe_id else 'Nein',
                'pkv_id': arztrechnung.pkv_id,
                'pkv_eingereicht': 'Ja' if arztrechnung.pkv_id else 'Nein'
            }
        print(str(self.arztrechnungen_liste[rg_id].beihilfe_id) + ' - ' + self.arztrechnungen_liste[rg_id].beihilfe_eingereicht)
        

    def aerzte_liste_aendern(self, arzt, arzt_id):
        """Ändert ein Element der Liste der Ärzte."""
        self.aerzte_liste[arzt_id] = {
                'db_id': arzt.db_id,
                'name': arzt.name,
            }
        
        # Arztrechnungen aktualisieren
        self.arztrechnungen_liste_aktualisieren()

    
    def beihilfepakete_liste_aendern(self, beihilfepaket, beihilfepaket_id):
        """Ändert ein Element der Liste der Beihilfepakete."""
        self.beihilfepakete_liste[beihilfepaket_id] = {
                'db_id': beihilfepaket.db_id,
                'betrag': beihilfepaket.betrag,
                'betrag_euro': '{:.2f} €'.format(beihilfepaket.betrag),
                'datum': beihilfepaket.datum,
                'erhalten': beihilfepaket.erhalten,
                'erhalten_text': 'Ja' if beihilfepaket.erhalten else 'Nein'
            }
        

    def pkvpakete_liste_aendern(self, pkvpaket, pkvpaket_id):
        """Ändert ein Element der Liste der PKV-Pakete."""
        self.pkvpakete_liste[pkvpaket_id] = {
                'db_id': pkvpaket.db_id,
                'betrag': pkvpaket.betrag,
                'betrag_euro': '{:.2f} €'.format(pkvpaket.betrag),
                'datum': pkvpaket.datum,
                'erhalten': pkvpaket.erhalten,
                'erhalten_text': 'Ja' if pkvpaket.erhalten else 'Nein'
            }


    def startup(self):
        """Laden der Daten, Erzeugen der GUI-Elemente und des Hauptfensters."""
        self.db = Datenbank()

        # Lade alle Daten aus der Datenbank
        self.arztrechnungen = self.db.lade_arztrechnungen()
        self.aerzte = self.db.lade_aerzte()
        self.beihilfepakete = self.db.lade_beihilfepakete()
        self.pkvpakete = self.db.lade_pkvpakete()

        # Erzeuge die ListSources für die GUI
        self.arztrechnungen_liste_erzeugen()
        self.aerzte_liste_erzeugen()
        self.beihilfepakete_liste_erzeugen()
        self.pkvpakete_liste_erzeugen()

        # Erzeuge alle GUI-Elemente
        self.erzeuge_startseite()
        self.erzeuge_seite_liste_arztrechnungen()
        self.erzeuge_seite_formular_arztrechnungen()
        self.erzeuge_seite_liste_aerzte()
        self.erzeuge_seite_formular_aerzte()
        self.erzeuge_seite_liste_beihilfepakete()
        self.erzeuge_seite_formular_beihilfepakete()

        # Erstelle die Menüleiste
        self.commands.add(self.cmd_arztrechnungen_anzeigen)
        self.commands.add(self.cmd_arztrechnungen_neu)
        self.commands.add(self.cmd_beihilfepakete_anzeigen)
        self.commands.add(self.cmd_beihilfepakete_neu)
        self.commands.add(self.cmd_pkvpakete_anzeigen)
        self.commands.add(self.cmd_pkvpakete_neu)
        self.commands.add(self.cmd_aerzte_anzeigen)
        self.commands.add(self.cmd_aerzte_neu)

        # Erstelle das Hauptfenster
        self.main_window = toga.MainWindow(title=self.formal_name)      

        # Alle Widgets in eine Liste packen
        all_children = itertools.chain(
            self.box_startseite.children,
            self.box_seite_liste_arztrechnungen.children,
            self.box_seite_formular_arztrechnungen.children,
            self.box_seite_liste_aerzte.children,
            self.box_seite_formular_aerzte.children,
            self.box_seite_liste_beihilfepakete.children,
            self.box_seite_formular_beihilfepakete.children
        )           

        # Alle Widgets mit Padding versehen
        for w in all_children:
            w.style.padding = 10 

        # Zeige die Startseite
        self.zeige_startseite(None)
        self.main_window.show()
        

def main():
    """Hauptschleife der Anwendung"""
    return Kontolupe()
