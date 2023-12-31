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
import datetime
from kontolupe.buchungen import *

# Allgemeine Styles
style_box_column        = Pack(direction=COLUMN, alignment=CENTER)
style_box_row           = Pack(direction=ROW, alignment=CENTER)
style_scroll_container  = Pack(flex=1)
style_label_h1          = Pack(font_size=14, font_weight='bold', text_align=CENTER, padding=5, padding_top=20, color='#222222')
style_label_h2          = Pack(font_size=11, font_weight='bold', text_align=CENTER, padding=5, padding_top=20, color='#222222')
style_label             = Pack(font_weight='normal', text_align=LEFT, padding_left=5, padding_right=5, color='#222222')
style_label_center      = Pack(font_weight='normal', text_align=CENTER, padding_left=5, padding_right=5, color='#222222')
style_button            = Pack(flex=1, padding=5, color='#222222')
style_input             = Pack(flex=2, padding=5, color='#222222') 
style_label_input       = Pack(flex=1, padding=5, text_align=LEFT, color='#222222')
style_table             = Pack(flex=1, padding=5, color='#222222')
style_switch            = Pack(flex=1, padding=5, color='#222222')

# Spezifische Styles
style_box_offene_buchungen      = Pack(direction=COLUMN, alignment=CENTER, background_color='#368ba8')
style_start_summe               = Pack(font_size=14, font_weight='bold', text_align=CENTER, padding=20, color='#ffffff')
style_table_offene_buchungen    = Pack(padding=5, height=200, color='#222222')
style_table_auswahl             = Pack(padding=5, height=200, flex=1, color='#222222')

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
        gruppe_arztrechnungen = toga.Group('Rechnungen', order = 1)

        self.cmd_arztrechnungen_anzeigen = toga.Command(
            self.zeige_seite_liste_arztrechnungen,
            'Rechnungen anzeigen',
            tooltip = 'Zeigt die Liste der Rechnungen an.',
            group = gruppe_arztrechnungen,
            order = 10
        )

        self.cmd_arztrechnungen_neu = toga.Command(
            self.zeige_seite_formular_arztrechnungen_neu,
            'Neue Rechnung',
            tooltip = 'Erstellt eine neue Rechnung.',
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
            self.zeige_seite_liste_pkvpakete,
            'PKV-Einreichungen anzeigen',
            tooltip = 'Zeigt die Liste der PKV-Einreichungen an.',
            group = gruppe_pkvpakete,
            order = 10
        )

        self.cmd_pkvpakete_neu = toga.Command(
            self.zeige_seite_formular_pkvpakete_neu,
            'Neue PKV-Einreichung',
            tooltip = 'Erstellt eine neue PKV-Einreichung.',
            group = gruppe_pkvpakete,
            order = 20
        )

        gruppe_aerzte = toga.Group('Einrichtungen', order = 4)

        self.cmd_aerzte_anzeigen = toga.Command(
            self.zeige_seite_liste_aerzte,
            'Einrichtungen anzeigen',
            tooltip = 'Zeigt die Liste der Einrichtungen an.',
            group = gruppe_aerzte,
            order = 10
        )

        self.cmd_aerzte_neu = toga.Command(
            self.zeige_seite_formular_aerzte_neu,
            'Neue Einrichtung',
            tooltip = 'Erstellt eine neue Einrichtung.',
            group = gruppe_aerzte,
            order = 20
        )

        gruppe_tools = toga.Group('Tools', order = 5)

        self.cmd_archivieren = toga.Command(
            self.archivieren_bestaetigen,
            'Archivieren',
            tooltip = 'Archiviere alle bezahlten und erhaltenen Buchungen.',
            group = gruppe_tools,
            order = 10
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
        self.box_startseite = toga.Box(style=style_box_column)
        self.scroll_container_startseite = toga.ScrollContainer(content=self.box_startseite, style=style_scroll_container)
        
        # Bereich, der die Summe der offenen Buchungen anzeigt
        self.box_startseite_offen = toga.Box(style=style_box_offene_buchungen)
        self.label_start_summe = toga.Label('Offener Betrag: {:.2f} €'.format(self.berechne_summe_offene_buchungen()), style=style_start_summe)
        self.box_startseite_offen.add(self.label_start_summe)
        self.box_startseite.add(self.box_startseite_offen)

        # Tabelle mit allen offenen Buchungen
        self.box_startseite_tabelle_offene_buchungen = toga.Box(style=style_box_column)
        #self.tabelle_offene_buchungen_container = toga.ScrollContainer(style=style_scroll_container)
        self.tabelle_offene_buchungen = toga.Table(
            headings    = ['Info', 'Betrag', 'Datum'],
            accessors   = ['info', 'betrag_euro', 'datum'],
            style       = style_table_offene_buchungen,
            on_activate = self.zeige_info_buchung,
            on_select   = self.button_status
        )
        #self.tabelle_offene_buchungen_container.content = self.tabelle_offene_buchungen
        #self.box_startseite_tabelle_offene_buchungen.add(self.tabelle_offene_buchungen_container)
        self.box_startseite_tabelle_offene_buchungen.add(self.tabelle_offene_buchungen)

        # Button zur Markierung offener Buchungen als bezahlt/erhalten 
        self.box_startseite_tabelle_buttons = toga.Box(style=style_box_row)
        self.startseite_button_erledigt = toga.Button('Markiere als bezahlt/erhalten', on_press=self.bestaetige_bezahlung, style=style_button, enabled=False)
        self.box_startseite_tabelle_buttons.add(self.startseite_button_erledigt)
        self.box_startseite_tabelle_offene_buchungen.add(self.box_startseite_tabelle_buttons)

        # Box der offenen Buchungen zur Startseite hinzufügen
        self.box_startseite.add(self.box_startseite_tabelle_offene_buchungen)
        

        # Bereich der Arztrechnungen
        label_start_arztrechnungen = toga.Label('Rechnungen', style=style_label_h2)
        self.label_start_arztrechnungen_offen = toga.Label(self.text_arztrechnungen_todo(), style=style_label_center)
        button_start_arztrechnungen_anzeigen = toga.Button('Anzeigen', on_press=self.zeige_seite_liste_arztrechnungen, style=style_button)
        button_start_arztrechnungen_neu = toga.Button('Neu', on_press=self.zeige_seite_formular_arztrechnungen_neu, style=style_button)
        box_startseite_arztrechnungen_buttons = toga.Box(style=style_box_row)
        box_startseite_arztrechnungen_buttons.add(button_start_arztrechnungen_anzeigen)
        box_startseite_arztrechnungen_buttons.add(button_start_arztrechnungen_neu)
        box_startseite_arztrechnungen = toga.Box(style=style_box_column)
        box_startseite_arztrechnungen.add(label_start_arztrechnungen)
        box_startseite_arztrechnungen.add(self.label_start_arztrechnungen_offen)
        box_startseite_arztrechnungen.add(box_startseite_arztrechnungen_buttons)
        self.box_startseite.add(box_startseite_arztrechnungen)

        # Bereich der Beihilfe-Einreichungen
        label_start_beihilfe = toga.Label('Beihilfe-Einreichungen', style=style_label_h2)
        self.label_start_beihilfe_offen = toga.Label('', style=style_label_center)
        button_start_beihilfe_anzeigen = toga.Button('Anzeigen', style=style_button, on_press=self.zeige_seite_liste_beihilfepakete)
        self.button_start_beihilfe_neu = toga.Button('Neu', style=style_button, on_press=self.zeige_seite_formular_beihilfepakete_neu, enabled=False)
        box_startseite_beihilfe_buttons = toga.Box(style=style_box_row)
        box_startseite_beihilfe_buttons.add(button_start_beihilfe_anzeigen)
        box_startseite_beihilfe_buttons.add(self.button_start_beihilfe_neu)
        box_startseite_beihilfe = toga.Box(style=style_box_column)
        box_startseite_beihilfe.add(label_start_beihilfe)
        box_startseite_beihilfe.add(self.label_start_beihilfe_offen)
        box_startseite_beihilfe.add(box_startseite_beihilfe_buttons)
        self.box_startseite.add(box_startseite_beihilfe)

        # Bereich der PKV-Einreichungen
        label_start_pkv = toga.Label('PKV-Einreichungen', style=style_label_h2)
        self.label_start_pkv_offen = toga.Label('', style=style_label_center)
        button_start_pkv_anzeigen = toga.Button('Anzeigen', style=style_button, on_press=self.zeige_seite_liste_pkvpakete)
        self.button_start_pkv_neu = toga.Button('Neu', style=style_button, on_press=self.zeige_seite_formular_pkvpakete_neu, enabled=False)
        box_startseite_pkv_buttons = toga.Box(style=style_box_row)
        box_startseite_pkv_buttons.add(button_start_pkv_anzeigen)
        box_startseite_pkv_buttons.add(self.button_start_pkv_neu)
        box_startseite_pkv = toga.Box(style=style_box_column)
        box_startseite_pkv.add(label_start_pkv)
        box_startseite_pkv.add(self.label_start_pkv_offen)
        box_startseite_pkv.add(box_startseite_pkv_buttons)
        self.box_startseite.add(box_startseite_pkv)

        # Bereich für die Archivierungsfunktion
        label_start_archiv = toga.Label('Archivierung', style=style_label_h2)
        self.button_start_archiv = toga.Button('Archivieren', style=style_button, on_press=self.archivieren_bestaetigen, enabled=False)
        self.label_start_archiv_offen = toga.Label('', style=style_label_center)
        box_startseite_archiv = toga.Box(style=style_box_column)
        box_startseite_archiv.add(label_start_archiv)
        box_startseite_archiv.add(self.label_start_archiv_offen)
        box_startseite_archiv.add(self.button_start_archiv)
        self.box_startseite.add(box_startseite_archiv)

    def zeige_startseite(self, widget):
        """Zurück zur Startseite."""
        self.label_start_summe.text = 'Offener Betrag: {:.2f} €'.format(self.berechne_summe_offene_buchungen())
        self.main_window.content = self.scroll_container_startseite

        # Tabelle mit offenen Buchungen aktualisieren
        self.tabelle_offene_buchungen.data = self.erzeuge_liste_offene_buchungen()
        self.label_start_arztrechnungen_offen.text = self.text_arztrechnungen_todo()
        self.label_start_beihilfe_offen.text = self.text_beihilfe_todo()
        self.label_start_pkv_offen.text = self.text_pkv_todo()

        # Button zum Markieren von Buchungen als bezahlt/erhalten aktivieren oder deaktivieren,
        self.startseite_button_erledigt.enabled = False

        # Tabelle mit deaktivierbaren Buchungen aktualisieren
        self.label_start_archiv_offen.text = self.text_archiv_todo()


    def button_status(self, widget):
        """Ändert den Aktivierungszustand der zur aufrufenden Tabelle gehörenden Buttons."""
        status = False
        if widget.selection is not None:
            status = True
        else:
            status = False

        match widget:
            case self.tabelle_offene_buchungen:
                self.startseite_button_erledigt.enabled = status
            case self.tabelle_arztrechnungen:
                self.liste_arztrechnungen_button_loeschen.enabled = status
                self.liste_arztrechnungen_button_bearbeiten.enabled = status
            case self.tabelle_beihilfepakete:
                self.seite_liste_beihilfepakete_button_loeschen.enabled = status
                #self.seite_liste_beihilfepakete_button_bearbeiten.enabled = status
            case self.tabelle_pkvpakete:
                self.seite_liste_pkvpakete_button_loeschen.enabled = status
                #self.seite_liste_pkvpakete_button_bearbeiten.enabled = status
            case self.tabelle_aerzte:
                self.seite_liste_aerzte_button_loeschen.enabled = status
                self.seite_liste_aerzte_button_bearbeiten.enabled = status


    def zeige_info_buchung(self, widget, row):
        """Zeigt die Info einer Buchung."""
        
        titel = ''
        inhalt = ''

        match row.typ:
            case 'Arztrechnung':
                # Finde die gewählte Arztrechnung in self.arztrechnungen_liste
                for arztrechnung in self.arztrechnungen_liste:
                    if arztrechnung.db_id == row.db_id:
                        titel = 'Rechnung'
                        inhalt = 'Vom {} über {:.2f} €'.format(arztrechnung.rechnungsdatum, arztrechnung.betrag)
                        inhalt += '\n\nEinrichtung: {}'.format(arztrechnung.arzt_name)
                        inhalt += '\nNotiz: {}'.format(arztrechnung.notiz)
                        inhalt += '\nBeihilfesatz: {:.0f} %'.format(arztrechnung.beihilfesatz)
                        if arztrechnung.buchungsdatum:
                            inhalt += '\nBuchungsdatum: {}'.format(arztrechnung.buchungsdatum)
                        else:
                            inhalt += '\nBuchungsdatum: -'
                        break
            case 'Beihilfe':
                # Finde die gewählte Beihilfe in self.beihilfepakete_liste
                for beihilfepaket in self.beihilfepakete_liste:
                    if beihilfepaket.db_id == row.db_id:
                        titel = 'Beihilfe-Einreichung'
                        inhalt = 'Vom {} über {:.2f} €'.format(beihilfepaket.datum, beihilfepaket.betrag)
                        # Liste alle Arztrechnungen auf, die zu diesem Beihilfepaket gehören
                        inhalt += '\n\nZugehörige Rechnungen:'
                        for arztrechnung in self.arztrechnungen_liste:
                            if arztrechnung.beihilfe_id == beihilfepaket.db_id:
                                inhalt += '\n- {}\n   vom {} über {:.2f} €'.format(arztrechnung.info, arztrechnung.rechnungsdatum, arztrechnung.betrag)
                        break

            case 'PKV':
                # Finde die gewählte PKV in self.pkvpakete_liste
                for pkvpaket in self.pkvpakete_liste:
                    if pkvpaket.db_id == row.db_id:
                        titel = 'PKV-Einreichung'
                        inhalt = 'Vom {} über {:.2f} €'.format(pkvpaket.datum, pkvpaket.betrag)
                        # Liste alle Arztrechnungen auf, die zu diesem PKV-Paket gehören
                        inhalt += '\n\nZugehörige Rechnungen:'
                        for arztrechnung in self.arztrechnungen_liste:
                            if arztrechnung.pkv_id == pkvpaket.db_id:
                                inhalt += '\n- {}\n   vom {} über {:.2f} €'.format(arztrechnung.info, arztrechnung.rechnungsdatum, arztrechnung.betrag)
                        break

        self.main_window.info_dialog(titel, inhalt)


    def erzeuge_seite_liste_arztrechnungen(self):
        """Erzeugt die Seite, auf der die Arztrechnungen angezeigt werden."""
        self.box_seite_liste_arztrechnungen = toga.Box(style=style_box_column)
        self.box_seite_liste_arztrechnungen.add(toga.Button('Zurück', on_press=self.zeige_startseite))
        self.box_seite_liste_arztrechnungen.add(toga.Label('Rechnungen', style=style_label_h1))

        # Tabelle mit den Arztrechnungen
        #self.tabelle_arztrechnungen_container = toga.ScrollContainer(style=style_scroll_container)
        self.tabelle_arztrechnungen = toga.Table(
            headings    = ['Info', 'Betrag', 'Bezahlt'],
            accessors   = ['info', 'betrag_euro', 'bezahlt_text'],
            data        = self.arztrechnungen_liste,
            style       = style_table,
            on_select   = self.button_status,
        )
        #self.tabelle_arztrechnungen_container.content = self.tabelle_arztrechnungen
        #self.box_seite_liste_arztrechnungen.add(self.tabelle_arztrechnungen_container)
        self.box_seite_liste_arztrechnungen.add(self.tabelle_arztrechnungen)

        # Buttons für die Arztrechnungen
        box_seite_liste_arztrechnungen_buttons = toga.Box(style=style_box_row)
        self.liste_arztrechnungen_button_loeschen = toga.Button('Löschen', on_press=self.bestaetige_arztrechnung_loeschen, style=style_button, enabled=False)
        self.liste_arztrechnungen_button_bearbeiten = toga.Button('Bearbeiten', on_press=self.zeige_seite_formular_arztrechnungen_bearbeiten, style=style_button, enabled=False)
        self.liste_arztrechnungen_button_neu = toga.Button('Neu', on_press=self.zeige_seite_formular_arztrechnungen_neu, style=style_button)
        box_seite_liste_arztrechnungen_buttons.add(self.liste_arztrechnungen_button_loeschen)
        box_seite_liste_arztrechnungen_buttons.add(self.liste_arztrechnungen_button_bearbeiten)
        box_seite_liste_arztrechnungen_buttons.add(self.liste_arztrechnungen_button_neu)
        self.box_seite_liste_arztrechnungen.add(box_seite_liste_arztrechnungen_buttons)    


    def zeige_seite_liste_arztrechnungen(self, widget):
        """Zeigt die Seite mit der Liste der Arztrechnungen."""
        self.main_window.content = self.box_seite_liste_arztrechnungen


    def erzeuge_seite_formular_arztrechnungen(self):
        """ Erzeugt das Formular zum Erstellen und Bearbeiten einer Arztrechnung."""
        self.scroll_container_formular_arztrechnungen = toga.ScrollContainer(style=style_scroll_container)
        self.box_seite_formular_arztrechnungen = toga.Box(style=style_box_column)
        self.scroll_container_formular_arztrechnungen.content = self.box_seite_formular_arztrechnungen
        self.box_seite_formular_arztrechnungen.add(toga.Button('Zurück', on_press=self.zeige_seite_liste_arztrechnungen, style=style_button))
        self.label_formular_arztrechnungen = toga.Label('Neue Rechnung', style=style_label_h1)
        self.box_seite_formular_arztrechnungen.add(self.label_formular_arztrechnungen)

        # Bereich zur Eingabe des Rechnungsdatums
        box_formular_arztrechnungen_rechnungsdatum = toga.Box(style=style_box_row)
        box_formular_arztrechnungen_rechnungsdatum.add(toga.Label('Rechnungsdatum: ', style=style_label_input))
        self.input_formular_arztrechnungen_rechnungsdatum = toga.DateInput(style=style_input)
        box_formular_arztrechnungen_rechnungsdatum.add(self.input_formular_arztrechnungen_rechnungsdatum)
        self.box_seite_formular_arztrechnungen.add(box_formular_arztrechnungen_rechnungsdatum)

        # Bereich zur Eingabe des Betrags
        box_formular_arztrechnungen_betrag = toga.Box(style=style_box_row)
        box_formular_arztrechnungen_betrag.add(toga.Label('Betrag in €: ', style=style_label_input))
        self.input_formular_arztrechnungen_betrag = toga.NumberInput(min=0, step=0.01, value=0, style=style_input)
        box_formular_arztrechnungen_betrag.add(self.input_formular_arztrechnungen_betrag)
        self.box_seite_formular_arztrechnungen.add(box_formular_arztrechnungen_betrag)

        # Bereich zur Auswahl des Arztes
        box_formular_arztrechnungen_arzt = toga.Box(style=style_box_row)
        box_formular_arztrechnungen_arzt.add(toga.Label('Einrichtung: ', style=style_label_input))
        self.input_formular_arztrechnungen_arzt = toga.Selection(items=self.aerzte_liste, accessor='name', style=style_input)
        box_formular_arztrechnungen_arzt.add(self.input_formular_arztrechnungen_arzt)
        self.box_seite_formular_arztrechnungen.add(box_formular_arztrechnungen_arzt)

        # Bereich zur Eingabe der Notiz
        box_formular_arztrechnungen_notiz = toga.Box(style=style_box_row)
        box_formular_arztrechnungen_notiz.add(toga.Label('Notiz: ', style=style_label_input))
        self.input_formular_arztrechnungen_notiz = toga.TextInput(style=style_input)
        box_formular_arztrechnungen_notiz.add(self.input_formular_arztrechnungen_notiz)
        self.box_seite_formular_arztrechnungen.add(box_formular_arztrechnungen_notiz)

        # Bereich zur Auswahl des Beihilfesatzes
        box_formular_arztrechnungen_beihilfesatz = toga.Box(style=style_box_row)
        box_formular_arztrechnungen_beihilfesatz.add(toga.Label('Beihilfesatz in %: ', style=style_label_input))
        self.input_formular_arztrechnungen_beihilfesatz = toga.NumberInput(min=0, max=100, step=10, value=0, style=style_input)
        box_formular_arztrechnungen_beihilfesatz.add(self.input_formular_arztrechnungen_beihilfesatz)
        self.box_seite_formular_arztrechnungen.add(box_formular_arztrechnungen_beihilfesatz)

        # Bereich zur Eingabe des Buchungsdatums
        box_formular_arztrechnungen_buchungsdatum = toga.Box(style=style_box_row)
        box_formular_arztrechnungen_buchungsdatum.add(toga.Label('Datum Überweisung: ', style=style_label_input))
        self.input_formular_arztrechnungen_buchungsdatum = toga.DateInput(style=style_input)
        box_formular_arztrechnungen_buchungsdatum.add(self.input_formular_arztrechnungen_buchungsdatum)
        self.box_seite_formular_arztrechnungen.add(box_formular_arztrechnungen_buchungsdatum)

        # Bereich zur Angabe der Bezahlung
        box_formular_arztrechnungen_bezahlt = toga.Box(style=style_box_row)
        self.input_formular_arztrechnungen_bezahlt = toga.Switch('Bezahlt', style=style_switch)
        box_formular_arztrechnungen_bezahlt.add(self.input_formular_arztrechnungen_bezahlt)
        self.box_seite_formular_arztrechnungen.add(box_formular_arztrechnungen_bezahlt)

        # Bereich der Buttons
        box_formular_arztrechnungen_buttons = toga.Box(style=style_box_row)
        box_formular_arztrechnungen_buttons.add(toga.Button('Abbrechen', on_press=self.zeige_seite_liste_arztrechnungen, style=style_button))
        box_formular_arztrechnungen_buttons.add(toga.Button('Speichern', on_press=self.arztrechnung_speichern, style=style_button))
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
        if len(self.aerzte_liste) > 0:
            self.input_formular_arztrechnungen_arzt.value = self.aerzte_liste[0]
        self.input_formular_arztrechnungen_beihilfesatz.value = 0
        self.input_formular_arztrechnungen_notiz.value = ''
        self.input_formular_arztrechnungen_buchungsdatum.value = None
        self.input_formular_arztrechnungen_bezahlt.value = False

        # Zurücksetzen des Flags
        self.flag_bearbeite_arztrechnung = False

        # Setze die Überschrift
        self.label_formular_arztrechnungen.text = 'Neue Rechnung'

        # Zeige die Seite
        self.main_window.content = self.scroll_container_formular_arztrechnungen

    
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
        elif len(self.aerzte_liste) > 0:
            self.input_formular_arztrechnungen_arzt.value = self.aerzte_liste[0]

        # Setze das Flag
        self.flag_bearbeite_arztrechnung = True

        # Setze die Überschrift
        self.label_formular_arztrechnungen.text = 'Rechnung bearbeiten'

        # Zeige die Seite
        self.main_window.content = self.scroll_container_formular_arztrechnungen


    def arztrechnung_speichern(self, widget):
        """Erstellt und speichert eine neue Arztrechnung."""

        if not self.flag_bearbeite_arztrechnung:
        # Erstelle eine neue Arztrechnung
            neue_arztrechnung = Arztrechnung()
            neue_arztrechnung.rechnungsdatum = self.input_formular_arztrechnungen_rechnungsdatum.value
            if len(self.aerzte_liste) > 0:
                neue_arztrechnung.arzt_id = self.input_formular_arztrechnungen_arzt.value.db_id
            neue_arztrechnung.notiz = self.input_formular_arztrechnungen_notiz.value
            neue_arztrechnung.betrag = float(self.input_formular_arztrechnungen_betrag.value)
            neue_arztrechnung.beihilfesatz = float(self.input_formular_arztrechnungen_beihilfesatz.value)
            neue_arztrechnung.buchungsdatum = self.input_formular_arztrechnungen_buchungsdatum.value
            neue_arztrechnung.bezahlt = self.input_formular_arztrechnungen_bezahlt.value

            # Speichere die Arztrechnung in der Datenbank
            neue_arztrechnung.neu(self.db)

            # Füge die Arztrechnung der Liste hinzu
            self.arztrechnungen.append(neue_arztrechnung)
            self.arztrechnungen_liste_anfuegen(neue_arztrechnung)
        else:
            # flag ob verknüpfte Einreichungen aktualisiert werden können
            # True, wenn betrag oder beihilfesatz geändert wurde
            update_einreichung = False
            
            if self.arztrechnungen[self.arztrechnung_b_id].betrag != float(self.input_formular_arztrechnungen_betrag.value):
                update_einreichung = True
            if self.arztrechnungen[self.arztrechnung_b_id].beihilfesatz != float(self.input_formular_arztrechnungen_beihilfesatz.value):
                update_einreichung = True

            # Bearbeite die Arztrechnung
            self.arztrechnungen[self.arztrechnung_b_id].rechnungsdatum = self.input_formular_arztrechnungen_rechnungsdatum.value
            if len(self.aerzte_liste) > 0:
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

            # check for a associated beihilfepaket and if there is one then create a confirmation dialog
            # that asks if the beihilfepaket should be updated
            if update_einreichung and self.arztrechnungen[self.arztrechnung_b_id].beihilfe_id is not None:
                self.main_window.confirm_dialog(
                    'Zugehörige Beihilfe-Einreichung aktualisieren',
                    'Soll die zugehörige Beihilfe-Einreichung aktualisiert werden?',
                    on_result=self.beihilfepaket_aktualisieren
                )

            # the same for the pkvpaket
            if update_einreichung and self.arztrechnungen[self.arztrechnung_b_id].pkv_id is not None:
                self.main_window.confirm_dialog(
                    'Zugehörige PKV-Einreichung aktualisieren',
                    'Soll die zugehörige PKV-Einreichung aktualisiert werden?',
                    on_result=self.pkvpaket_aktualisieren
                )

        # Zeige die Liste der Arztrechnungen
        self.zeige_seite_liste_arztrechnungen(widget)


    def beihilfepaket_aktualisieren(self, widget, result):
        """Aktualisiert die Beihilfe-Einreichung einer Arztrechnung."""
        if result:
            # find the beihilfepaket
            for beihilfepaket in self.beihilfepakete:
                if beihilfepaket.db_id == self.arztrechnungen[self.arztrechnung_b_id].beihilfe_id:
                    # loop through all arztrechnungen and update the betrag
                    beihilfepaket.betrag = 0
                    for arztrechnung in self.arztrechnungen:
                        if arztrechnung.beihilfe_id == beihilfepaket.db_id:
                            beihilfepaket.betrag += arztrechnung.betrag * (arztrechnung.beihilfesatz / 100)
                    # save the beihilfepaket
                    beihilfepaket.speichern(self.db)
                    self.beihilfepakete_liste_aendern(beihilfepaket, self.beihilfepakete.index(beihilfepaket))
                    break
            

    def pkvpaket_aktualisieren(self, widget, result):
        """Aktualisiert die PKV-Einreichung einer Arztrechnung."""
        if result:
            # find the pkvpaket
            for pkvpaket in self.pkvpakete:
                if pkvpaket.db_id == self.arztrechnungen[self.arztrechnung_b_id].pkv_id:
                    # loop through all arztrechnungen and update the betrag
                    pkvpaket.betrag = 0
                    for arztrechnung in self.arztrechnungen:
                        if arztrechnung.pkv_id == pkvpaket.db_id:
                            pkvpaket.betrag += arztrechnung.betrag * (1 - (arztrechnung.beihilfesatz / 100))
                    # save the pkvpaket
                    pkvpaket.speichern(self.db)
                    self.pkvpakete_liste_aendern(pkvpaket, self.pkvpakete.index(pkvpaket))
                    break            


    def bestaetige_arztrechnung_loeschen(self, widget):
        """Bestätigt das Löschen einer Arztrechnung."""
        if self.tabelle_arztrechnungen.selection:
            self.main_window.confirm_dialog(
                'Rechnung löschen', 
                'Soll die ausgewählte Rechnung wirklich gelöscht werden?',
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
        self.box_seite_liste_aerzte = toga.Box(style=style_box_column)
        self.box_seite_liste_aerzte.add(toga.Button('Zurück', on_press=self.zeige_startseite, style=style_button))
        self.box_seite_liste_aerzte.add(toga.Label('Einrichtungen', style=style_label_h1))

        # Tabelle mit den Ärzten

        #self.tabelle_aerzte_container = toga.ScrollContainer(style=style_scroll_container)
        self.tabelle_aerzte = toga.Table(
            headings    = ['Einrichtung'], 
            accessors   = ['name'],
            data        = self.aerzte_liste,
            style       = style_table,
            on_select   = self.button_status,
        )
        #self.tabelle_aerzte_container.content = self.tabelle_aerzte
        #self.box_seite_liste_aerzte.add(self.tabelle_aerzte_container)
        self.box_seite_liste_aerzte.add(self.tabelle_aerzte)

        # Buttons für die Ärzten
        box_seite_liste_aerzte_buttons = toga.Box(style=style_box_row)
        self.seite_liste_aerzte_button_loeschen = toga.Button('Löschen', on_press=self.bestaetige_arzt_loeschen, style=style_button, enabled=False)
        self.seite_liste_aerzte_button_bearbeiten = toga.Button('Bearbeiten', on_press=self.zeige_seite_formular_aerzte_bearbeiten, style=style_button, enabled=False)
        self.seite_liste_aerzte_button_neu = toga.Button('Neu', on_press=self.zeige_seite_formular_aerzte_neu, style=style_button)
        box_seite_liste_aerzte_buttons.add(self.seite_liste_aerzte_button_loeschen)
        box_seite_liste_aerzte_buttons.add(self.seite_liste_aerzte_button_bearbeiten)
        box_seite_liste_aerzte_buttons.add(self.seite_liste_aerzte_button_neu)
        self.box_seite_liste_aerzte.add(box_seite_liste_aerzte_buttons)   


    def zeige_seite_liste_aerzte(self, widget):
        """Zeigt die Seite mit der Liste der Ärzte."""
        self.main_window.content = self.box_seite_liste_aerzte


    def erzeuge_seite_formular_aerzte(self):
        """Erzeugt das Formular zum Erstellen und Bearbeiten eines Arztes."""
        self.box_seite_formular_aerzte = toga.Box(style=style_box_column)
        self.box_seite_formular_aerzte.add(toga.Button('Zurück', on_press=self.zeige_seite_liste_aerzte, style=style_button))
        self.label_formular_aerzte = toga.Label('Neue Einrichtung', style=style_label_h1)
        self.box_seite_formular_aerzte.add(self.label_formular_aerzte)

        # Bereich zur Eingabe des Namens
        box_formular_aerzte_name = toga.Box(style=style_box_row)
        box_formular_aerzte_name.add(toga.Label('Name der Einrichtung: ', style=style_label_input))
        self.input_formular_aerzte_name = toga.TextInput(style=style_input)
        box_formular_aerzte_name.add(self.input_formular_aerzte_name)
        self.box_seite_formular_aerzte.add(box_formular_aerzte_name)

        # Bereich der Buttons
        box_formular_aerzte_buttons = toga.Box(style=style_box_row)
        box_formular_aerzte_buttons.add(toga.Button('Abbrechen', on_press=self.zeige_seite_liste_aerzte, style=style_button))
        box_formular_aerzte_buttons.add(toga.Button('Speichern', on_press=self.arzt_speichern, style=style_button))
        self.box_seite_formular_aerzte.add(box_formular_aerzte_buttons)


    def zeige_seite_formular_aerzte_neu(self, widget):
        """Zeigt die Seite zum Erstellen eines Arztes."""
        # Setze die Eingabefelder zurück
        self.input_formular_aerzte_name.value = ''

        # Zurücksetzen des Flags
        self.flag_bearbeite_arzt = False

        # Setze die Überschrift
        self.label_formular_aerzte.text = 'Neue Einrichtung'

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
        self.label_formular_aerzte.text = 'Einrichtung bearbeiten'

        # Zeige die Seite
        self.main_window.content = self.box_seite_formular_aerzte


    def arzt_speichern(self, widget):
        """Erstellt und speichert einen neuen Arzt."""
        if not self.flag_bearbeite_arzt:
        # Erstelle einen neuen Arzt
            neuer_arzt = Arzt()
            neuer_arzt.name = self.input_formular_aerzte_name.value

            # Speichere den Arzt in der Datenbank
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

            # Aktualisiere die Liste der Arztrechnungen
            self.arztrechnungen_liste_aktualisieren()

            # Aktualisiere das Auswahlfeld der Ärztenamen
            self.input_formular_aerzte_name.items = self.aerzte_liste


        # Zeige die Liste der Ärzte
        self.zeige_seite_liste_aerzte(widget)

    
    def bestaetige_arzt_loeschen(self, widget):
        """Bestätigt das Löschen eines Arztes."""
        if self.tabelle_aerzte.selection:
            self.main_window.confirm_dialog(
                'Einrichtung löschen', 
                'Soll die ausgewählte Einrichtung wirklich gelöscht werden?',
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
        """Erzeugt die Seite, auf der die Beihilfe-Einreichungen angezeigt werden."""
        self.box_seite_liste_beihilfepakete = toga.Box(style=style_box_column)
        self.box_seite_liste_beihilfepakete.add(toga.Button('Zurück', on_press=self.zeige_startseite, style=style_button))
        self.box_seite_liste_beihilfepakete.add(toga.Label('Beihilfe-Einreichungen', style=style_label_h1))

        # Tabelle mit den Beihilfepaketen
        #self.tabelle_beihilfepakete_container = toga.ScrollContainer(style=style_scroll_container)
        self.tabelle_beihilfepakete = toga.Table(
            headings    = ['Datum', 'Betrag', 'Erhalten'], 
            accessors   = ['datum', 'betrag_euro', 'erhalten_text'],
            data        = self.beihilfepakete_liste,
            style       = style_table,
            on_select   = self.button_status,
        )
        #self.tabelle_beihilfepakete_container.content = self.tabelle_beihilfepakete
        #self.box_seite_liste_beihilfepakete.add(self.tabelle_beihilfepakete_container)
        self.box_seite_liste_beihilfepakete.add(self.tabelle_beihilfepakete)

        # Buttons für die Beihilfepakete
        box_seite_liste_beihilfepakete_buttons = toga.Box(style=style_box_row)
        self.seite_liste_beihilfepakete_button_loeschen = toga.Button('Zurücksetzen', on_press=self.bestaetige_beihilfepaket_loeschen, style=style_button, enabled=False)
        box_seite_liste_beihilfepakete_buttons.add(self.seite_liste_beihilfepakete_button_loeschen)
        # self.seite_liste_beihilfepakete_button_bearbeiten = toga.Button('Bearbeiten', on_press=self.zeige_seite_formular_beihilfepakete_bearbeiten, style=style_button, enabled=False)
        #box_seite_liste_beihilfepakete_buttons.add(self.seite_liste_beihilfepakete_button_bearbeiten)
        self.seite_liste_beihilfepakete_button_neu = toga.Button('Neu', on_press=self.zeige_seite_formular_beihilfepakete_neu, style=style_button)
        box_seite_liste_beihilfepakete_buttons.add(self.seite_liste_beihilfepakete_button_neu)
        self.box_seite_liste_beihilfepakete.add(box_seite_liste_beihilfepakete_buttons)


    def erzeuge_seite_liste_pkvpakete(self):
        """Erzeugt die Seite, auf der die PKV-Einreichungen angezeigt werden."""
        self.box_seite_liste_pkvpakete = toga.Box(style=style_box_column)
        self.box_seite_liste_pkvpakete.add(toga.Button('Zurück', on_press=self.zeige_startseite, style=style_button))
        self.box_seite_liste_pkvpakete.add(toga.Label('PKV-Einreichungen', style=style_label_h1))

        # Tabelle mit den PKV-Einreichungen
        self.tabelle_pkvpakete_container = toga.ScrollContainer(style=style_scroll_container)
        self.tabelle_pkvpakete = toga.Table(
            headings    = ['Datum', 'Betrag', 'Erhalten'], 
            accessors   = ['datum', 'betrag_euro', 'erhalten_text'],
            data        = self.pkvpakete_liste,
            style       = style_table,
            on_select   = self.button_status,
        )
        self.tabelle_pkvpakete_container.content = self.tabelle_pkvpakete
        self.box_seite_liste_pkvpakete.add(self.tabelle_pkvpakete_container)

        # Buttons für die PKV-Einreichungen
        box_seite_liste_pkvpakete_buttons = toga.Box(style=style_box_row)
        self.seite_liste_pkvpakete_button_loeschen = toga.Button('Zurücksetzen', on_press=self.bestaetige_pkvpaket_loeschen, style=style_button, enabled=False)
        box_seite_liste_pkvpakete_buttons.add(self.seite_liste_pkvpakete_button_loeschen)
        # self.seite_liste_pkvpakete_button_bearbeiten = toga.Button('Bearbeiten', on_press=self.zeige_seite_formular_pkvpakete_bearbeiten, style=style_button, enabled=False)
        #box_seite_liste_pkvpakete_buttons.add(self.seite_liste_pkvpakete_button_bearbeiten)
        self.seite_liste_pkvpakete_button_neu = toga.Button('Neu', on_press=self.zeige_seite_formular_pkvpakete_neu, style=style_button)
        box_seite_liste_pkvpakete_buttons.add(self.seite_liste_pkvpakete_button_neu)
        self.box_seite_liste_pkvpakete.add(box_seite_liste_pkvpakete_buttons)


    def zeige_seite_liste_beihilfepakete(self, widget):
        """Zeigt die Seite mit der Liste der Beihilfepakete."""
        # Zum Setzen des Button Status
        self.text_beihilfe_todo()
        self.main_window.content = self.box_seite_liste_beihilfepakete

    
    def zeige_seite_liste_pkvpakete(self, widget):
        """Zeigt die Seite mit der Liste der PKV-Einreichungen."""
        # Zum Setzen des Button Status
        self.text_pkv_todo()
        self.main_window.content = self.box_seite_liste_pkvpakete

    
    def erzeuge_seite_formular_beihilfepakete(self):
        """Erzeugt das Formular zum Erstellen und Bearbeiten einer Beihilfe-Einreichung."""
        self.box_seite_formular_beihilfepakete = toga.Box(style=style_box_column)
        self.box_seite_formular_beihilfepakete.add(toga.Button('Zurück', on_press=self.zeige_seite_liste_beihilfepakete, style=style_button))
        self.label_formular_beihilfepakete = toga.Label('Neue Beihilfe-Einreichung', style=style_label_h1)
        self.box_seite_formular_beihilfepakete.add(self.label_formular_beihilfepakete)

        # Bereich zur Eingabe des Datums
        box_formular_beihilfepakete_datum = toga.Box(style=style_box_row)
        box_formular_beihilfepakete_datum.add(toga.Label('Datum: ', style=style_label_input))
        self.input_formular_beihilfepakete_datum = toga.DateInput(style=style_input)
        box_formular_beihilfepakete_datum.add(self.input_formular_beihilfepakete_datum)
        self.box_seite_formular_beihilfepakete.add(box_formular_beihilfepakete_datum)

        # Bereich zur Auswahl der zugehörigen Arztrechnungen
        #self.formular_beihilfepakete_arztrechnungen_container = toga.ScrollContainer(style=style_scroll_container)
        self.formular_beihilfe_tabelle_arztrechnungen = toga.Table(
            headings        = ['Info', 'Betrag', 'Beihilfe', 'Bezahlt'],
            accessors       = ['info', 'betrag_euro', 'beihilfesatz_prozent', 'bezahlt_text'],
            data            = self.erzeuge_teilliste_arztrechnungen(beihilfe=True),
            multiple_select = True,
            on_select       = self.beihilfe_tabelle_arztrechnungen_auswahl_geaendert,   
            style           = style_table_auswahl
        )
        #self.formular_beihilfepakete_arztrechnungen_container.content = self.formular_beihilfe_tabelle_arztrechnungen
        #self.box_seite_formular_beihilfepakete.add(self.formular_beihilfepakete_arztrechnungen_container)
        self.box_seite_formular_beihilfepakete.add(self.formular_beihilfe_tabelle_arztrechnungen)

        # Bereich zur Eingabe des Betrags
        box_formular_beihilfepakete_betrag = toga.Box(style=style_box_row)
        box_formular_beihilfepakete_betrag.add(toga.Label('Betrag in €: ', style=style_label_input))
        self.input_formular_beihilfepakete_betrag = toga.NumberInput(min=0, step=0.01, value=0, style=style_input, readonly=True)
        box_formular_beihilfepakete_betrag.add(self.input_formular_beihilfepakete_betrag)
        self.box_seite_formular_beihilfepakete.add(box_formular_beihilfepakete_betrag)

        # Bereich zur Angabe der Erstattung
        box_formular_beihilfepakete_erhalten = toga.Box(style=style_box_row)
        self.input_formular_beihilfepakete_erhalten = toga.Switch('Erstattet', style=style_switch)
        box_formular_beihilfepakete_erhalten.add(self.input_formular_beihilfepakete_erhalten)
        self.box_seite_formular_beihilfepakete.add(box_formular_beihilfepakete_erhalten)

        # Bereich der Buttons
        box_formular_beihilfepakete_buttons = toga.Box(style=style_box_row)
        box_formular_beihilfepakete_buttons.add(toga.Button('Abbrechen', on_press=self.zeige_seite_liste_beihilfepakete, style=style_button))
        box_formular_beihilfepakete_buttons.add(toga.Button('Speichern', on_press=self.beihilfepaket_speichern_check, style=style_button))
        self.box_seite_formular_beihilfepakete.add(box_formular_beihilfepakete_buttons)


    def erzeuge_seite_formular_pkvpakete(self):
        """Erzeugt das Formular zum Erstellen und Bearbeiten einer PKV-Einreichung."""
        self.box_seite_formular_pkvpakete = toga.Box(style=style_box_column)
        self.box_seite_formular_pkvpakete.add(toga.Button('Zurück', on_press=self.zeige_seite_liste_pkvpakete, style=style_button))
        self.label_formular_pkvpakete = toga.Label('Neue PKV-Einreichung', style=style_label_h1)
        self.box_seite_formular_pkvpakete.add(self.label_formular_pkvpakete)

        # Bereich zur Eingabe des Datums
        box_formular_pkvpakete_datum = toga.Box(style=style_box_row)
        box_formular_pkvpakete_datum.add(toga.Label('Datum: ', style=style_label_input))
        self.input_formular_pkvpakete_datum = toga.DateInput(style=style_input)
        box_formular_pkvpakete_datum.add(self.input_formular_pkvpakete_datum)
        self.box_seite_formular_pkvpakete.add(box_formular_pkvpakete_datum)

        # Bereich zur Auswahl der zugehörigen Arztrechnungen
        self.formular_pkvpakete_arztrechnungen_container = toga.ScrollContainer(style=style_scroll_container)
        self.formular_pkv_tabelle_arztrechnungen = toga.Table(
            headings        = ['Info', 'Betrag', 'Beihilfe', 'Bezahlt'],
            accessors       = ['info', 'betrag_euro', 'beihilfesatz_prozent', 'bezahlt_text'],
            data            = self.erzeuge_teilliste_arztrechnungen(pkv=True),
            multiple_select = True,
            on_select       = self.pkv_tabelle_arztrechnungen_auswahl_geaendert,   
            style           = style_table_auswahl
        )
        self.formular_pkvpakete_arztrechnungen_container.content = self.formular_pkv_tabelle_arztrechnungen
        self.box_seite_formular_pkvpakete.add(self.formular_pkvpakete_arztrechnungen_container)

        # Bereich zur Eingabe des Betrags
        box_formular_pkvpakete_betrag = toga.Box(style=style_box_row)
        box_formular_pkvpakete_betrag.add(toga.Label('Betrag in €: ', style=style_label_input))
        self.input_formular_pkvpakete_betrag = toga.NumberInput(min=0, step=0.01, value=0, style=style_input, readonly=True)
        box_formular_pkvpakete_betrag.add(self.input_formular_pkvpakete_betrag)
        self.box_seite_formular_pkvpakete.add(box_formular_pkvpakete_betrag)

        # Bereich zur Angabe der Erstattung
        box_formular_pkvpakete_erhalten = toga.Box(style=style_box_row)
        self.input_formular_pkvpakete_erhalten = toga.Switch('Erhalten', style=style_switch)
        box_formular_pkvpakete_erhalten.add(self.input_formular_pkvpakete_erhalten)
        self.box_seite_formular_pkvpakete.add(box_formular_pkvpakete_erhalten)

        # Bereich der Buttons
        box_formular_pkvpakete_buttons = toga.Box(style=style_box_row)
        box_formular_pkvpakete_buttons.add(toga.Button('Abbrechen', on_press=self.zeige_seite_liste_pkvpakete, style=style_button))
        box_formular_pkvpakete_buttons.add(toga.Button('Speichern', on_press=self.pkvpaket_speichern_check, style=style_button))
        self.box_seite_formular_pkvpakete.add(box_formular_pkvpakete_buttons)


    def beihilfe_tabelle_arztrechnungen_auswahl_geaendert(self, widget):
        """Ermittelt die Summe des Beihilfe-Anteils der ausgewählten Arztrechnungen."""
        summe = 0
        for auswahl_rg in widget.selection:
            for rg in self.arztrechnungen:
                if auswahl_rg.db_id == rg.db_id:
                    summe += rg.betrag * rg.beihilfesatz / 100
        self.input_formular_beihilfepakete_betrag.value = summe


    def pkv_tabelle_arztrechnungen_auswahl_geaendert(self, widget):
        """Ermittelt die Summe des PKV-Anteils der ausgewählten Arztrechnungen."""
        summe = 0
        for auswahl_rg in widget.selection:
            for rg in self.arztrechnungen:
                if auswahl_rg.db_id == rg.db_id:
                    summe += rg.betrag * (100 - rg.beihilfesatz) / 100
        self.input_formular_pkvpakete_betrag.value = summe


    def zeige_seite_formular_beihilfepakete_neu(self, widget):
        """Zeigt die Seite zum Erstellen eines Beihilfepakets."""
        # Setze die Eingabefelder zurück
        self.input_formular_beihilfepakete_betrag.value = 0
        self.input_formular_beihilfepakete_datum.value = None
        self.input_formular_beihilfepakete_erhalten.value = False
        self.formular_beihilfe_tabelle_arztrechnungen.data = self.erzeuge_teilliste_arztrechnungen(beihilfe=True)

        # Zurücksetzen des Flags
        self.flag_bearbeite_beihilfepaket = False

        # Setze die Überschrift
        self.label_formular_beihilfepakete.text = 'Neue Beihilfe-Einreichung'

        # Zeige die Seite
        self.main_window.content = self.box_seite_formular_beihilfepakete


    def zeige_seite_formular_pkvpakete_neu(self, widget):
        """Zeigt die Seite zum Erstellen einer PKV-Einreichung."""
        # Setze die Eingabefelder zurück
        self.input_formular_pkvpakete_betrag.value = 0
        self.input_formular_pkvpakete_datum.value = None
        self.input_formular_pkvpakete_erhalten.value = False
        self.formular_pkv_tabelle_arztrechnungen.data = self.erzeuge_teilliste_arztrechnungen(pkv=True)

        # Zurücksetzen des Flags
        self.flag_bearbeite_pkvpaket = False

        # Setze die Überschrift
        self.label_formular_pkvpakete.text = 'Neue PKV-Einreichung'

        # Zeige die Seite
        self.main_window.content = self.box_seite_formular_pkvpakete


    def zeige_seite_formular_beihilfepakete_bearbeiten(self, widget):
        """Zeigt die Seite zum Bearbeiten einer Beihilfe-Einreichung."""
        # Ermittle den Index des ausgewählten Beihilfepakets
        self.beihilfepaket_b_id = self.index_auswahl(self.tabelle_beihilfepakete)

        # Befülle die Eingabefelder
        self.input_formular_beihilfepakete_betrag.value = self.beihilfepakete[self.beihilfepaket_b_id].betrag
        self.input_formular_beihilfepakete_datum.value = self.beihilfepakete[self.beihilfepaket_b_id].datum
        self.input_formular_beihilfepakete_erhalten.value = self.beihilfepakete[self.beihilfepaket_b_id].erhalten

        # Tabelleninhalt aktualisieren
        tabelle_daten = self.erzeuge_teilliste_arztrechnungen(beihilfe=True, beihilfe_id=self.beihilfepakete[self.beihilfepaket_b_id].db_id)
        self.formular_beihilfe_tabelle_arztrechnungen.data = tabelle_daten

        # TODO: Wähle die verknüpften Arztrechnungen in der Tabelle aus
        # self.formular_beihilfe_tabelle_arztrechnungen.selection = []
        # for i, arztrechnung in enumerate(tabelle_daten):
        #     if arztrechnung.beihilfe_id == self.beihilfepakete[self.beihilfepaket_b_id].db_id:
        #         self.formular_beihilfe_tabelle_arztrechnungen.selection.append(self.formular_beihilfe_tabelle_arztrechnungen.data[i])

        # Setze das Flag
        self.flag_bearbeite_beihilfepaket = True

        # Setze die Überschrift
        self.label_formular_beihilfepakete.text = 'Beihilfe-Einreichung bearbeiten'

        # Zeige die Seite
        self.main_window.content = self.box_seite_formular_beihilfepakete


    def zeige_seite_formular_pkvpakete_bearbeiten(self, widget):
        """Zeigt die Seite zum Bearbeiten einer PKV-Einreichung."""
        # Ermittle den Index der ausgewählten PKV-Einreichung
        self.pkvpaket_b_id = self.index_auswahl(self.tabelle_pkvpakete)

        # Befülle die Eingabefelder
        self.input_formular_pkvpakete_betrag.value = self.pkvpakete[self.pkvpaket_b_id].betrag
        self.input_formular_pkvpakete_datum.value = self.pkvpakete[self.pkvpaket_b_id].datum
        self.input_formular_pkvpakete_erhalten.value = self.pkvpakete[self.pkvpaket_b_id].erhalten

        # Tabelleninhalt aktualisieren
        tabelle_daten = self.erzeuge_teilliste_arztrechnungen(pkv=True, pkv_id=self.pkvpakete[self.pkvpaket_b_id].db_id)
        self.formular_pkv_tabelle_arztrechnungen.data = tabelle_daten

        # Setze das Flag
        self.flag_bearbeite_pkvpaket = True

        # Setze die Überschrift
        self.label_formular_pkvpakete.text = 'PKV-Einreichung bearbeiten'

        # Zeige die Seite
        self.main_window.content = self.box_seite_formular_pkvpakete


    def beihilfepaket_speichern_check(self, widget):
        """Prüft, ob Rechnungen für die Beihilfe-Einreichungen ausgewählt sind."""
        if not self.formular_beihilfe_tabelle_arztrechnungen.selection:
            self.main_window.info_dialog(
                'Keine Rechnung ausgewählt', 
                'Es wurde keine Rechnung zum Einreichen ausgewählt.'
            )
        else:
            self.beihilfepaket_speichern(widget)


    def pkvpaket_speichern_check(self, widget):
        """Prüft, ob Rechnungen für die PKV-Einreichungen ausgewählt sind."""
        if not self.formular_pkv_tabelle_arztrechnungen.selection:
            self.main_window.info_dialog(
                'Keine Rechnung ausgewählt', 
                'Es wurde keine Rechnung zum Einreichen ausgewählt.'
            )
        else:
            self.pkvpaket_speichern(widget)


    def beihilfepaket_speichern(self, widget):
        """Erstellt und speichert eine neue Beihilfe-Einreichung oder ändert eine bestehende."""

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
        self.zeige_startseite(widget)


    def pkvpaket_speichern(self, widget):
        """Erstellt und speichert eine neue PKV-Einreichung oder ändert eine bestehende."""

        if not self.flag_bearbeite_pkvpaket:
            # Erstelle ein neues PKV-Paket
            neues_pkvpaket = PKVPaket()
            neues_pkvpaket.datum = self.input_formular_pkvpakete_datum.value
            neues_pkvpaket.betrag = float(self.input_formular_pkvpakete_betrag.value)
            neues_pkvpaket.erhalten = self.input_formular_pkvpakete_erhalten.value

            # Speichere das PKV-Einreichung in der Datenbank
            neues_pkvpaket.neu(self.db)

            # Füge das PKV-Einreichung der Liste hinzu
            self.pkvpakete.append(neues_pkvpaket)
            self.pkvpakete_liste_anfuegen(neues_pkvpaket)

            # Aktualisiere verknüpfte Arztrechnungen
            for auswahl_rg in self.formular_pkv_tabelle_arztrechnungen.selection:
                for rg in self.arztrechnungen:
                    if auswahl_rg.db_id == rg.db_id:
                        rg.pkv_id = neues_pkvpaket.db_id
                        rg.speichern(self.db)

        else:
            # Bearbeite das PKV-Paket
            self.pkvpakete[self.pkvpaket_b_id].datum = self.input_formular_pkvpakete_datum.value
            self.pkvpakete[self.pkvpaket_b_id].betrag = float(self.input_formular_pkvpakete_betrag.value)
            self.pkvpakete[self.pkvpaket_b_id].erhalten = self.input_formular_pkvpakete_erhalten.value

            # Speichere das PKV-Einreichung in der Datenbank
            self.pkvpakete[self.pkvpaket_b_id].speichern(self.db)

            # Aktualisiere die Liste der PKV-Einreichungen
            self.pkvpakete_liste_aendern(self.pkvpakete[self.pkvpaket_b_id], self.pkvpaket_b_id)

            # Flage zurücksetzen
            self.flag_bearbeite_pkvpaket = False

            # Aktualisiere verknüpfte Arztrechnungen
            for auswahl_rg in self.formular_pkv_tabelle_arztrechnungen.selection:
                for rg in self.arztrechnungen:
                    if auswahl_rg.db_id == rg.db_id:
                        rg.pkv_id = self.pkvpakete[self.pkvpaket_b_id].db_id
                        rg.speichern(self.db)

        # Arztrechnungen aktualisieren
        self.arztrechnungen_liste_aktualisieren()

        # Wechsel zur Liste der PKV-Einreichungen
        self.zeige_startseite(widget)


    def bestaetige_beihilfepaket_loeschen(self, widget):
        """Bestätigt das Löschen einer Beihilfe-Einreichung."""
        if self.tabelle_beihilfepakete.selection:
            self.main_window.confirm_dialog(
                'Beihilfe-Einreichung zurücksetzen', 
                'Soll die ausgewählte Beihilfe-Einreichung wirklich zurückgesetzt werden? Die zugehörigen Rechnungen müssen dann erneut eingereicht werden.',
                on_result=self.beihilfepaket_loeschen
            )


    def bestaetige_pkvpaket_loeschen(self, widget):
        """Bestätigt das Löschen einer PKV-Einreichung."""
        if self.tabelle_pkvpakete.selection:
            self.main_window.confirm_dialog(
                'PKV-Einreichung zurücksetzen', 
                'Soll die ausgewählte PKV-Einreichung wirklich zurückgesetzt werden? Die zugehörigen Rechnungen müssen dann erneut eingereicht werden.',
                on_result=self.pkvpaket_loeschen
            )


    def beihilfepaket_loeschen(self, widget, result):
        """Löscht eine Beihilfe-Einreichung."""
        if self.tabelle_beihilfepakete.selection and result:
            index = self.index_auswahl(self.tabelle_beihilfepakete)
            self.beihilfepakete[index].loeschen(self.db)
            del self.beihilfepakete[index]
            del self.beihilfepakete_liste[index]
            self.arztrechnungen_aktualisieren()
            # Zum Setzen des Button Status
            self.text_beihilfe_todo()


    def pkvpaket_loeschen(self, widget, result):
        """Löscht eine PKV-Einreichung."""
        if self.tabelle_pkvpakete.selection and result:
            index = self.index_auswahl(self.tabelle_pkvpakete)
            self.pkvpakete[index].loeschen(self.db)
            del self.pkvpakete[index]
            del self.pkvpakete_liste[index]
            self.arztrechnungen_aktualisieren()
            # Zum Setzen des Button Status
            self.text_pkv_todo()


    def erzeuge_teilliste_arztrechnungen(self, beihilfe=False, pkv=False, beihilfe_id=None, pkv_id=None):
        """Erzeugt die Liste der eingereichten Arztrechnungen für Beihilfe oder PKV."""

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
            'beihilfesatz_prozent',
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
            if (beihilfe and (arztrechnung.beihilfe_id is None or arztrechnung.beihilfe_id == beihilfe_id)) or (pkv and (arztrechnung.pkv_id is None or arztrechnung.pkv_id == pkv_id)):
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
                'beihilfesatz_prozent': '{:.0f} %'.format(arztrechnung.beihilfesatz),
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
    

    def indizes_archivierbare_buchungen(self):
        """Ermittelt die Indizes der archivierbaren Arztrechnungen, Beihilfepakete und PKVpakete und gibt sie zurück."""
        indizes = {
            'Arztrechnung' : [],
            'Beihilfe' : set(),
            'PKV' : set()
        }

        # Create dictionaries for quick lookup of beihilfepakete and pkvpakete by db_id
        beihilfepakete_dict = {paket.db_id: paket for paket in self.beihilfepakete}
        pkvpakete_dict = {paket.db_id: paket for paket in self.pkvpakete}

        for i, arztrechnung in enumerate(self.arztrechnungen):
            if arztrechnung.bezahlt and arztrechnung.beihilfe_id and arztrechnung.pkv_id:
                beihilfepaket = beihilfepakete_dict.get(arztrechnung.beihilfe_id)
                pkvpaket = pkvpakete_dict.get(arztrechnung.pkv_id)
                if beihilfepaket and beihilfepaket.erhalten and pkvpaket and pkvpaket.erhalten:
                    # Check if all other arztrechnungen associated with the beihilfepaket and pkvpaket are paid
                    other_arztrechnungen = [ar for ar in self.arztrechnungen if ar.beihilfe_id == beihilfepaket.db_id or ar.pkv_id == pkvpaket.db_id]
                    if all(ar.bezahlt for ar in other_arztrechnungen):
                        indizes['Arztrechnung'].append(i)
                        indizes['Beihilfe'].add(self.beihilfepakete.index(beihilfepaket))
                        indizes['PKV'].add(self.pkvpakete.index(pkvpaket))

        # Convert sets back to lists
        indizes['Beihilfe'] = list(indizes['Beihilfe'])
        indizes['PKV'] = list(indizes['PKV'])

        # sort the lists in reverse order
        indizes['Arztrechnung'].sort(reverse=True)
        indizes['Beihilfe'].sort(reverse=True)
        indizes['PKV'].sort(reverse=True)

        return indizes
    

    def text_archiv_todo(self):
        """Ermittle den Anzeigetext für die Anzahl noch nicht archivierter Buchungen."""
        indizes = self.indizes_archivierbare_buchungen()

        # Count the number of items in the dictionary indizes
        anzahl = sum(len(v) for v in indizes.values())

        match anzahl:
            case 0:
                # Deaktiviere den Button zum Archivieren
                self.button_start_archiv.enabled = False
                return 'Keine archivierbaren Buchungen vorhanden.'
            case 1:
                # Aktiviere den Button zum Archivieren
                self.button_start_archiv.enabled = True
                return '1 archivierbare Buchung vorhanden.'
            case _:
                # Aktiviere den Button zum Archivieren
                self.button_start_archiv.enabled = True
                return '{} archivierbare Buchungen vorhanden.'.format(anzahl)
            

    def archivieren_bestaetigen(self, widget):
        """Bestätigt das Archivieren von Buchungen."""
        indizes = self.indizes_archivierbare_buchungen()
        if sum(len(v) for v in indizes.values()) > 0:
            self.main_window.confirm_dialog(
                'Buchungen archivieren', 
                'Sollen alle archivierbaren Buchungen wirklich archiviert werden? Sie werden dann in der App nicht mehr angezeigt.',
                on_result=self.archivieren
            )


    def archivieren(self, widget, result):
        """Archiviert alle archivierbaren Buchungen."""
        if result:
            indizes = self.indizes_archivierbare_buchungen()

            for i in indizes['Arztrechnung']:
                self.arztrechnungen[i].aktiv = 0
                self.arztrechnungen[i].speichern(self.db)
                del self.arztrechnungen[i]
                del self.arztrechnungen_liste[i]

            for i in indizes['Beihilfe']:
                self.beihilfepakete[i].aktiv = 0
                self.beihilfepakete[i].speichern(self.db)
                del self.beihilfepakete[i]
                del self.beihilfepakete_liste[i]
                
            for i in indizes['PKV']:
                self.pkvpakete[i].aktiv = 0
                self.pkvpakete[i].speichern(self.db)
                del self.pkvpakete[i]
                del self.pkvpakete_liste[i]
            
            self.zeige_startseite(widget)
    

    def text_arztrechnungen_todo(self):
        """Ermittle den Anzeigetext für die Anzahl noch nicht bezahlter Arztrechnungen."""
        anzahl = 0
        for arztrechnung in self.arztrechnungen:
            if not arztrechnung.bezahlt:
                anzahl += 1

        match anzahl:
            case 0:
                return 'Keine offenen Rechnungen.'
            case 1:
                return '1 Rechnung noch nicht bezahlt.'
            case _:
                return '{} Rechnungen noch nicht bezahlt.'.format(anzahl)
    

    def text_beihilfe_todo(self):
        """Ermittle den Anzeigetext mit der Anzahl der noch nicht bei der Beihilfe eingereichten Arztrechnungen."""
        anzahl = 0
        for arztrechnung in self.arztrechnungen:
            if not arztrechnung.beihilfe_id:
                anzahl += 1

        match anzahl:
            case 0:
                self.button_start_beihilfe_neu.enabled = False
                self.seite_liste_beihilfepakete_button_neu.enabled = False
                return 'Keine offenen Rechnungen.'
            case 1:
                self.button_start_beihilfe_neu.enabled = True
                self.seite_liste_beihilfepakete_button_neu.enabled = True
                return '1 Rechnung noch nicht eingereicht.'
            case _:
                self.button_start_beihilfe_neu.enabled = True
                self.seite_liste_beihilfepakete_button_neu.enabled = True
                return '{} Rechnungen noch nicht eingereicht.'.format(anzahl)
            

    def text_pkv_todo(self):
        """Ermittle den Anzeigetext mit der Anzahl der noch nicht bei der PKV eingereichten Arztrechnungen."""
        anzahl = 0
        for arztrechnung in self.arztrechnungen:
            if not arztrechnung.pkv_id:
                anzahl += 1

        match anzahl:
            case 0:
                self.button_start_pkv_neu.enabled = False
                self.seite_liste_pkvpakete_button_neu.enabled = False
                return 'Keine offenen Rechnungen.'
            case 1:
                self.button_start_pkv_neu.enabled = True
                self.seite_liste_pkvpakete_button_neu.enabled = True
                return '1 Rechnung noch nicht eingereicht.'
            case _:
                self.button_start_pkv_neu.enabled = True
                self.seite_liste_pkvpakete_button_neu.enabled = True
                return '{} Rechnungen noch nicht eingereicht.'.format(anzahl)
            

    def bestaetige_bezahlung(self, widget):
        """Bestätigt die Bezahlung einer Arztrechnung."""
        if self.tabelle_offene_buchungen.selection:
            match self.tabelle_offene_buchungen.selection.typ:
                case 'Arztrechnung':
                    self.main_window.confirm_dialog(
                        'Rechnung als bezahlt markieren', 
                        'Soll die ausgewählte Rechnung wirklich als bezahlt markiert werden?',
                        on_result=self.arztrechnung_bezahlen
                    )
                case 'Beihilfe':
                    self.main_window.confirm_dialog(
                        'Beihilfe als erhalten markieren', 
                        'Soll die ausgewählte Beihilfe wirklich als erhalten markiert werden?',
                        on_result=self.beihilfe_erhalten
                    )
                case 'PKV':
                    self.main_window.confirm_dialog(
                        'PKV-Einreichung als erhalten markieren', 
                        'Soll die ausgewählte PKV-Einreichung wirklich als erhalten markiert werden?',
                        on_result=self.pkv_erhalten
                    )
    

    def arztrechnung_bezahlen(self, widget, result):
        """Markiert eine Arztrechnung als bezahlt."""
        if self.tabelle_offene_buchungen.selection and result:
            # Setze das Flag bezahlt auf True bei der Arztrechnung mit der db_id aus der Tabelle
            for arztrechnung in self.arztrechnungen:
                if arztrechnung.db_id == self.tabelle_offene_buchungen.selection.db_id:
                    arztrechnung.bezahlt = True
                    arztrechnung.speichern(self.db)
                    break
            
            # Aktualisiere die Liste der Arztrechnungen
            self.arztrechnungen_liste_aktualisieren()

            # Aktualisiere die Liste der offenen Buchungen
            self.zeige_startseite(widget)

    
    def beihilfe_erhalten(self, widget, result):
        """Markiert eine Beihilfe als erhalten."""
        if self.tabelle_offene_buchungen.selection and result:
            # Setze das Flag erhalten auf True bei der Beihilfe mit der db_id aus der Tabelle
            for beihilfepaket in self.beihilfepakete:
                if beihilfepaket.db_id == self.tabelle_offene_buchungen.selection.db_id:
                    beihilfepaket.erhalten = True
                    beihilfepaket.speichern(self.db)
                    break
            
            # Aktualisiere die Liste der Beihilfepakete
            self.beihilfepakete_liste_aktualisieren()

            # Aktualisiere die Liste der offenen Buchungen
            self.zeige_startseite(widget)


    def pkv_erhalten(self, widget, result):
        """Markiert eine PKV-Einreichung als erhalten."""
        if self.tabelle_offene_buchungen.selection and result:
            # Setze das Flag erhalten auf True bei der PKV-Einreichung mit der db_id aus der Tabelle
            for pkvpaket in self.pkvpakete:
                if pkvpaket.db_id == self.tabelle_offene_buchungen.selection.db_id:
                    pkvpaket.erhalten = True
                    pkvpaket.speichern(self.db)
                    break
            
            # Aktualisiere die Liste der PKV-Einreichungen
            self.pkvpakete_liste_aktualisieren()

            # Aktualisiere die Liste der offenen Buchungen
            self.zeige_startseite(widget)
    

    def erzeuge_liste_offene_buchungen(self):
        """Erzeugt die Liste der offenen Buchungen für die Tabelle auf der Startseite."""
        offene_buchungen_liste = ListSource(accessors=[
            'db_id',                        # Datenbank-Id des jeweiligen Elements
            'typ',                          # Typ des Elements (Arztrechnung, Beihilfe, PKV)
            'betrag_euro',                  # Betrag der Buchung in Euro
            'datum',                        # Datum der Buchung (Plandatum der Rechnung oder Einreichungsdatum der Beihilfe/PKV)
            'info'                         # Info-Text der Buchung
        ])

        for arztrechnung in self.arztrechnungen:
            if not arztrechnung.bezahlt:
                offene_buchungen_liste.append({
                    'db_id': arztrechnung.db_id,
                    'typ': 'Arztrechnung',
                    'betrag_euro': '-{:.2f} €'.format(arztrechnung.betrag),
                    'datum': arztrechnung.buchungsdatum,
                    'info': self.arzt_name(arztrechnung.arzt_id) + ' - ' + arztrechnung.notiz
                })
    
        for beihilfepaket in self.beihilfepakete:
            if not beihilfepaket.erhalten:
                offene_buchungen_liste.append({
                    'db_id': beihilfepaket.db_id,
                    'typ': 'Beihilfe',
                    'betrag_euro': '+{:.2f} €'.format(beihilfepaket.betrag),
                    'datum': beihilfepaket.datum,
                    'info': 'Beihilfe-Einreichung'
                })

        for pkvpaket in self.pkvpakete:
            if not pkvpaket.erhalten:
                offene_buchungen_liste.append({
                    'db_id': pkvpaket.db_id,
                    'typ': 'PKV',
                    'betrag_euro': '+{:.2f} €'.format(pkvpaket.betrag),
                    'datum': pkvpaket.datum,
                    'info': 'PKV-Einreichung'
                })

        return offene_buchungen_liste

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
            'beihilfesatz_prozent',
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
                'beihilfesatz_prozent': '{:.0f} %'.format(arztrechnung.beihilfesatz),
                'buchungsdatum': arztrechnung.buchungsdatum,
                'bezahlt': arztrechnung.bezahlt,
                'bezahlt_text': 'Ja' if arztrechnung.bezahlt else 'Nein',
                'beihilfe_id': arztrechnung.beihilfe_id,
                'beihilfe_eingereicht': 'Ja' if arztrechnung.beihilfe_id else 'Nein',
                'pkv_id': arztrechnung.pkv_id,
                'pkv_eingereicht': 'Ja' if arztrechnung.pkv_id else 'Nein'
            })
        

    def arztrechnungen_aktualisieren(self):
        """Aktualisiert die referenzierten Werte in den Arztrechnungen und speichert sie in der Datenbank."""

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

    
    def beihilfepakete_liste_aktualisieren(self):
        """Aktualisiert die Liste der Beihilfepakete."""
        for beihilfepaket_id in range(len(self.beihilfepakete_liste)):
            self.beihilfepakete_liste_aendern(self.beihilfepakete[beihilfepaket_id], beihilfepaket_id)

    
    def pkvpakete_liste_aktualisieren(self):
        """Aktualisiert die Liste der PKV-Pakete."""
        for pkvpaket_id in range(len(self.pkvpakete_liste)):
            self.pkvpakete_liste_aendern(self.pkvpakete[pkvpaket_id], pkvpaket_id)
        

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
                'beihilfesatz_prozent': '{:.0f} %'.format(arztrechnung.beihilfesatz),
                'buchungsdatum': arztrechnung.buchungsdatum,
                'bezahlt': arztrechnung.bezahlt,
                'bezahlt_text': 'Ja' if arztrechnung.bezahlt else 'Nein',
                'beihilfe_id': arztrechnung.beihilfe_id,
                'beihilfe_eingereicht': 'Ja' if arztrechnung.beihilfe_id else 'Nein',
                'pkv_id': arztrechnung.pkv_id,
                'pkv_eingereicht': 'Ja' if arztrechnung.pkv_id else 'Nein'
            }
        

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
        self.erzeuge_seite_liste_pkvpakete()
        self.erzeuge_seite_formular_pkvpakete()

        # Erstelle die Menüleiste
        self.commands.add(self.cmd_arztrechnungen_anzeigen)
        self.commands.add(self.cmd_arztrechnungen_neu)
        self.commands.add(self.cmd_beihilfepakete_anzeigen)
        self.commands.add(self.cmd_beihilfepakete_neu)
        self.commands.add(self.cmd_pkvpakete_anzeigen)
        self.commands.add(self.cmd_pkvpakete_neu)
        self.commands.add(self.cmd_aerzte_anzeigen)
        self.commands.add(self.cmd_aerzte_neu)
        self.commands.add(self.cmd_archivieren)

        # Erstelle das Hauptfenster
        self.main_window = toga.MainWindow(title=self.formal_name)      

        # Zeige die Startseite
        self.zeige_startseite(None)
        self.main_window.show()
        

def main():
    """Hauptschleife der Anwendung"""
    return Kontolupe()
