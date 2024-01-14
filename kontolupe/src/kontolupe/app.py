"""
Behalte den Überblick über Deine Rechnungen, Beihilfe- und PKV-Erstattungen.

Mit Kontolupe kannst Du Deine Gesundheitsrechnungen erfassen und verwalten.
Du kannst Beihilfe- und PKV-Einreichungen erstellen und die Erstattungen
überwachen. Die App ist für die private Nutzung kostenlos.
"""

import toga
from toga.sources import ListSource
from datetime import datetime

from kontolupe.database import *
from kontolupe.validator import *
from kontolupe.layout import *
from kontolupe.form import *

class Kontolupe(toga.App):
    """Die Hauptklasse der Anwendung."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        """Initialisierung der Anwendung."""

        # Hilfsvariablen zur Bearbeitung von Rechnungen
        self.flag_edit_bill = False
        self.edit_bill_id = 0

        # Hilfsvariablen zur Bearbeitung von Einrichtungen
        self.flag_edit_institution = False
        self.edit_institution_id = 0

        # Hilfsvariablen zur Bearbeitung von Personen
        self.flag_edit_person = False
        self.edit_person_id = 0

        # Hilfsvariablen zur Bearbeitung der Beihilfe-Pakete
        self.flag_edit_beihilfe = False
        self.edit_beihilfe_id = 0

        # Hilfsvariablen zur Bearbeitung der PKV-Pakete
        self.flag_edit_pkv = False
        self.edit_pkv_id = 0

        # Hilfsvariable zur Festlegung des Zurück-Ziels
        self.zurueck = 'startseite'


    def update_app(self, widget):
        """Aktualisiert die Anzeigen und Aktivierungszustand von Buttons und Commands."""

        # Anzeige des offenen Betrags aktualisieren
        self.label_start_summe.text = 'Offener Betrag: {:.2f} €'.format(self.berechne_summe_offene_buchungen()).replace('.', ',')

        # Tabelle mit offenen Buchungen aktualisieren
        if widget != self.tabelle_offene_buchungen:
            self.tabelle_offene_buchungen.data = self.erzeuge_liste_offene_buchungen()

        # Button zum Markieren von Buchungen als bezahlt/erhalten aktivieren oder deaktivieren,
        self.startseite_button_erledigt.enabled = False
        self.startseite_button_bearbeiten.enabled = False

        # Anzahl der je Segment offenen Elemente ermitteln
        anzahl_rg = 0
        anzahl_bh = 0
        anzahl_pkv = 0
        for rechnung in self.rechnungen:
            anzahl_rg += 1 if rechnung.bezahlt == False else 0
            anzahl_bh += 1 if rechnung.beihilfe_id is None else 0
            anzahl_pkv += 1 if rechnung.pkv_id is None else 0

        # Anzeige und Button der offenen Rechnungen aktualisieren
        match anzahl_rg:
            case 0:
                self.label_start_rechnungen_offen.text = 'Keine offenen Rechnungen.'
            case 1:
                self.label_start_rechnungen_offen.text = '1 Rechnung noch nicht bezahlt.'
            case _:
                self.label_start_rechnungen_offen.text = '{} Rechnungen noch nicht bezahlt.'.format(anzahl_rg)

        # Anzeige und Button der offenen Beihilfe-Einreichungen aktualisieren
        match anzahl_bh:
            case 0:
                self.button_start_beihilfe_neu.enabled = False
                self.seite_liste_beihilfepakete_button_neu.enabled = False
                self.cmd_beihilfepakete_neu.enabled = False
                self.label_start_beihilfe_offen.text = 'Keine offenen Rechnungen.'
            case 1:
                self.button_start_beihilfe_neu.enabled = True
                self.seite_liste_beihilfepakete_button_neu.enabled = True
                self.cmd_beihilfepakete_neu.enabled = True
                self.label_start_beihilfe_offen.text = '1 Rechnung noch nicht eingereicht.'
            case _:
                self.button_start_beihilfe_neu.enabled = True
                self.seite_liste_beihilfepakete_button_neu.enabled = True
                self.cmd_beihilfepakete_neu.enabled = True
                self.label_start_beihilfe_offen.text = '{} Rechnungen noch nicht eingereicht.'.format(anzahl_bh)

        # Anzeige und Button der offenen PKV-Einreichungen aktualisieren
        match anzahl_pkv:
            case 0:
                self.button_start_pkv_neu.enabled = False
                self.seite_liste_pkvpakete_button_neu.enabled = False
                self.cmd_pkvpakete_neu.enabled = False
                self.label_start_pkv_offen.text = 'Keine offenen Rechnungen.'
            case 1:
                self.button_start_pkv_neu.enabled = True
                self.seite_liste_pkvpakete_button_neu.enabled = True
                self.cmd_pkvpakete_neu.enabled = True
                self.label_start_pkv_offen.text = '1 Rechnung noch nicht eingereicht.'
            case _:
                self.button_start_pkv_neu.enabled = True
                self.seite_liste_pkvpakete_button_neu.enabled = True
                self.cmd_pkvpakete_neu.enabled = True
                self.label_start_pkv_offen.text = '{} Rechnungen noch nicht eingereicht.'.format(anzahl_pkv)

        # Anzeige und Button der archivierbaren Items aktualisieren
        indizes = self.indizes_archivierbare_buchungen()
        anzahl = sum(len(v) for v in indizes.values())
        match anzahl:
            case 0:
                self.button_start_archiv.enabled = False
                self.cmd_archivieren.enabled = False
                #self.label_start_archiv_offen.text = 'Keine archivierbaren Buchungen vorhanden.'
                self.button_start_archiv.text = 'Keine archivierbaren Buchungen'
            case 1:
                self.button_start_archiv.enabled = True
                self.cmd_archivieren.enabled = True
                #self.label_start_archiv_offen.text = '1 archivierbare Buchung vorhanden.'
                self.button_start_archiv.text = '1 Buchung archivieren'
            case _:
                self.button_start_archiv.enabled = True
                self.cmd_archivieren.enabled = True
                #self.label_start_archiv_offen.text = '{} archivierbare Buchungen vorhanden.'.format(anzahl)
                self.button_start_archiv.text = '{} Buchungen archivieren'.format(anzahl)

        # Ändert den Aktivierungszustand der zur aufrufenden Tabelle gehörenden Buttons.
        status = False
        if widget and type(widget) == toga.Table and widget.selection is not None:
            status = True
        else:
            status = False

        match widget:
            case self.tabelle_offene_buchungen:
                self.startseite_button_erledigt.enabled = status
                if self.tabelle_offene_buchungen.selection and self.tabelle_offene_buchungen.selection.typ == 'Rechnung':
                    self.startseite_button_bearbeiten.enabled = True
            case self.tabelle_rechnungen:
                self.liste_rechnungen_button_loeschen.enabled = status
                self.liste_rechnungen_button_bearbeiten.enabled = status
            case self.tabelle_beihilfepakete:
                self.seite_liste_beihilfepakete_button_loeschen.enabled = status
                #self.seite_liste_beihilfepakete_button_bearbeiten.enabled = status
            case self.tabelle_pkvpakete:
                self.seite_liste_pkvpakete_button_loeschen.enabled = status
                #self.seite_liste_pkvpakete_button_bearbeiten.enabled = status
            case self.tabelle_einrichtungen:
                self.seite_liste_einrichtungen_button_loeschen.enabled = status
                self.seite_liste_einrichtungen_button_bearbeiten.enabled = status
                self.seite_liste_einrichtungen_button_info.enabled = status
            case self.tabelle_personen:
                self.seite_liste_personen_button_loeschen.enabled = status
                self.seite_liste_personen_button_bearbeiten.enabled = status

    
    def index_auswahl(self, widget):
        """Ermittelt den Index des ausgewählten Elements einer Tabelle."""
        if type(widget) == toga.Table and widget.selection is not None:
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
        

    def index_liste_von_id(self, liste, id):
        """Ermittelt den Index eines Elements einer Liste anhand der ID."""
        for i, element in enumerate(liste):
            if element.db_id == id:
                return i
        else:
            print("Element mit der ID {} konnte nicht gefunden werden.".format(id))
            return None


    def berechne_summe_offene_buchungen(self):
        """Berechnet die Summe der offenen Buchungen."""
        
        summe = 0
        for rechnung in self.rechnungen:
            if rechnung.bezahlt == False:
                summe -= rechnung.betrag
            if rechnung.beihilfe_id == None:
                summe += rechnung.betrag * (rechnung.beihilfesatz / 100)
            if rechnung.pkv_id == None:
                summe += rechnung.betrag * (1 - (rechnung.beihilfesatz / 100))
        
        for beihilfepaket in self.beihilfepakete:
            if beihilfepaket.erhalten == False:
                summe += beihilfepaket.betrag

        for pkvpaket in self.pkvpakete:
            if pkvpaket.erhalten == False:
                summe += pkvpaket.betrag

        return summe
    

    def geh_zurueck(self, widget):
        """Ermittelt das Ziel der Zurück-Funktion und ruft die entsprechende Seite auf."""
        match self.zurueck:
            case 'startseite':
                self.zeige_startseite(widget)
            case 'liste_rechnungen':
                self.show_list_bills(widget)
            case 'liste_beihilfepakete':
                self.show_list_beihilfe(widget)
            case 'liste_pkvpakete':
                self.show_list_pkv(widget)
            case 'liste_einrichtungen':
                self.show_list_institutions(widget)
            case 'formular_rechnungen_neu':
                self.show_form_bill_new(widget)
            case 'formular_rechnungen_bearbeiten':
                self.show_form_bill_edit(widget)
            case 'formular_beihilfepakete_neu':
                self.show_form_beihilfe_new(widget)
            case 'formular_beihilfepakete_bearbeiten':
                self.show_form_beihilfe_edit(widget)
            case 'formular_pkvpakete_neu':
                self.show_form_pkv_new(widget)
            case 'formular_pkvpakete_bearbeiten':
                self.show_form_pkv_edit(widget)
            case 'formular_einrichtungen_neu':
                self.show_form_institution_new(widget)
            case 'formular_einrichtungen_bearbeiten':
                self.show_form_institution_edit(widget)
            case 'info_einrichtung':
                self.show_info_institution(widget)
            case _:
                self.zeige_startseite(widget)


    def erzeuge_webview(self):
        """Erzeugt eine WebView zur Anzeige von Webseiten."""
        self.box_webview = toga.Box(style=style_box_column)
        box_webview_top = toga.Box(style=style_box_column_dunkel)
        box_webview_top.add(toga.Button('Zurück', style=style_button, on_press=self.geh_zurueck))
        self.box_webview.add(box_webview_top)
        self.webview = toga.WebView(style=style_webview)
        self.box_webview.add(self.webview)


    def zeige_webview(self, widget):
        """Zeigt die WebView zur Anzeige von Webseiten."""
        match widget:
            case self.link_info_einrichtung_webseite:
                self.webview.url = self.einrichtungen_liste[self.edit_institution_id].webseite
                self.zurueck = 'info_einrichtung'
            case self.cmd_datenschutz:
                self.webview.url = 'https://kontolupe.biberwerk.net/kontolupe-datenschutz.html'
                self.zurueck = 'startseite'

        self.main_window.content = self.box_webview


    def erzeuge_startseite(self):
        """Erzeugt die Startseite der Anwendung."""

        # Container für die Startseite
        self.box_startseite = toga.Box(style=style_box_column)
        self.scroll_container_startseite = toga.ScrollContainer(content=self.box_startseite, style=style_scroll_container)
        
        # Bereich, der die Summe der offenen Buchungen anzeigt
        self.box_startseite_offen = toga.Box(style=style_box_offene_buchungen)
        self.label_start_summe = toga.Label('Offener Betrag: ', style=style_start_summe)
        self.box_startseite_offen.add(self.label_start_summe)
        self.box_startseite.add(self.box_startseite_offen)

        # Tabelle mit allen offenen Buchungen
        self.box_startseite_tabelle_offene_buchungen = toga.Box(style=style_section_start)
        self.tabelle_offene_buchungen = toga.Table(
            headings    = ['Info', 'Betrag', 'Datum'],
            accessors   = ['info', 'betrag_euro', 'datum'],
            style       = style_table_offene_buchungen,
            on_activate = self.zeige_info_buchung,
            on_select   = self.update_app
        )
        self.box_startseite_tabelle_offene_buchungen.add(self.tabelle_offene_buchungen)

        # Button zur Markierung offener Buchungen als bezahlt/erhalten 
        self.box_startseite_tabelle_buttons = toga.Box(style=style_box_row)
        self.startseite_button_erledigt = toga.Button('Bezahlt/Erstattet', on_press=self.bestaetige_bezahlung, style=style_button, enabled=False)
        self.startseite_button_bearbeiten = toga.Button('Bearbeiten', on_press=self.bearbeite_offene_buchung, style=style_button, enabled=False)
        self.box_startseite_tabelle_buttons.add(self.startseite_button_erledigt)
        self.box_startseite_tabelle_buttons.add(self.startseite_button_bearbeiten)
        self.box_startseite_tabelle_offene_buchungen.add(self.box_startseite_tabelle_buttons)

        # Box der offenen Buchungen zur Startseite hinzufügen
        self.box_startseite.add(self.box_startseite_tabelle_offene_buchungen)
        
        # Bereich der Rechnungen
        label_start_rechnungen = toga.Label('Rechnungen', style=style_label_h2_start)
        self.label_start_rechnungen_offen = toga.Label('', style=style_label_section)
        button_start_rechnungen_anzeigen = toga.Button('Anzeigen', on_press=self.show_list_bills, style=style_button)
        button_start_rechnungen_neu = toga.Button('Neu', on_press=self.show_form_bill_new, style=style_button)
        box_startseite_rechnungen_buttons = toga.Box(style=style_box_buttons_start)
        box_startseite_rechnungen_buttons.add(button_start_rechnungen_anzeigen)
        box_startseite_rechnungen_buttons.add(button_start_rechnungen_neu)
        box_startseite_rechnungen = toga.Box(style=style_section_rechnungen)
        box_startseite_rechnungen.add(label_start_rechnungen)
        box_startseite_rechnungen.add(self.label_start_rechnungen_offen)
        box_startseite_rechnungen.add(box_startseite_rechnungen_buttons)
        self.box_startseite.add(box_startseite_rechnungen)

        # Bereich der Beihilfe-Einreichungen
        label_start_beihilfe = toga.Label('Beihilfe-Einreichungen', style=style_label_h2_start)
        self.label_start_beihilfe_offen = toga.Label('', style=style_label_section)
        button_start_beihilfe_anzeigen = toga.Button('Anzeigen', style=style_button, on_press=self.show_list_beihilfe)
        self.button_start_beihilfe_neu = toga.Button('Neu', style=style_button, on_press=self.show_form_beihilfe_new, enabled=False)
        box_startseite_beihilfe_buttons = toga.Box(style=style_box_buttons_start)
        box_startseite_beihilfe_buttons.add(button_start_beihilfe_anzeigen)
        box_startseite_beihilfe_buttons.add(self.button_start_beihilfe_neu)
        box_startseite_beihilfe = toga.Box(style=style_section_beihilfe)
        box_startseite_beihilfe.add(label_start_beihilfe)
        box_startseite_beihilfe.add(self.label_start_beihilfe_offen)
        box_startseite_beihilfe.add(box_startseite_beihilfe_buttons)
        self.box_startseite.add(box_startseite_beihilfe)

        # Bereich der PKV-Einreichungen
        label_start_pkv = toga.Label('PKV-Einreichungen', style=style_label_h2_start)
        self.label_start_pkv_offen = toga.Label('', style=style_label_section)
        button_start_pkv_anzeigen = toga.Button('Anzeigen', style=style_button, on_press=self.show_list_pkv)
        self.button_start_pkv_neu = toga.Button('Neu', style=style_button, on_press=self.show_form_pkv_new, enabled=False)
        box_startseite_pkv_buttons = toga.Box(style=style_box_buttons_start)
        box_startseite_pkv_buttons.add(button_start_pkv_anzeigen)
        box_startseite_pkv_buttons.add(self.button_start_pkv_neu)
        box_startseite_pkv = toga.Box(style=style_section_pkv)
        box_startseite_pkv.add(label_start_pkv)
        box_startseite_pkv.add(self.label_start_pkv_offen)
        box_startseite_pkv.add(box_startseite_pkv_buttons)
        self.box_startseite.add(box_startseite_pkv)

        # Bereich für die Archivierungsfunktion
        # label_start_archiv = toga.Label('Archivierung', style=style_label_h2)
        # self.button_start_archiv = toga.Button('Archivieren', style=style_button, on_press=self.archivieren_bestaetigen, enabled=False)
        # self.label_start_archiv_offen = toga.Label('', style=style_label_center)
        # box_startseite_archiv = toga.Box(style=style_box_column)
        # box_startseite_archiv.add(label_start_archiv)
        # box_startseite_archiv.add(self.label_start_archiv_offen)
        # box_startseite_archiv.add(self.button_start_archiv)
        # self.box_startseite.add(box_startseite_archiv)

        self.button_start_personen = toga.Button('Personen verwalten', style=style_button, on_press=self.show_list_persons)
        self.button_start_einrichtungen = toga.Button('Einrichtungen verwalten', style=style_button, on_press=self.show_list_institutions)
        self.button_start_archiv = toga.Button('Keine archivierbaren Buchungen', style=style_button, on_press=self.archivieren_bestaetigen, enabled=False)

        box_startseite_daten = toga.Box(style=style_section_daten)
        box_startseite_daten.add(self.button_start_personen)
        box_startseite_daten.add(self.button_start_einrichtungen)
        box_startseite_daten.add(self.button_start_archiv)
        self.box_startseite.add(box_startseite_daten)


    def zeige_startseite(self, widget):
        """Zurück zur Startseite."""
        
        self.update_app(widget)
        self.main_window.content = self.scroll_container_startseite


    def zeige_info_buchung(self, widget, row):
        """Zeigt die Info einer Buchung."""
        
        # Initialisierung Variablen
        titel = ''
        inhalt = ''

        # Ermittlung der Buchungsart
        typ = ''
        element = None
        match widget:
            case self.tabelle_offene_buchungen:
                typ = row.typ
                match typ:
                    case 'Rechnung':
                        for rechnung in self.rechnungen_liste:
                            if rechnung.db_id == row.db_id:
                                element = rechnung
                                break
                    case 'Beihilfe':
                        for beihilfepaket in self.beihilfepakete_liste:
                            if beihilfepaket.db_id == row.db_id:
                                element = beihilfepaket
                                break
                    case 'PKV':
                        for pkvpaket in self.pkvpakete_liste:
                            if pkvpaket.db_id == row.db_id:
                                element = pkvpaket
                                break
            case self.form_beihilfe_bills:
                typ = 'Rechnung'
                for rechnung in self.rechnungen_liste:
                    if rechnung.db_id == row.db_id:
                        element = rechnung
                        break
            case self.form_pkv_bills:
                typ = 'Rechnung'
                for rechnung in self.rechnungen_liste:
                    if rechnung.db_id == row.db_id:
                        element = rechnung
                        break
            case self.tabelle_rechnungen:
                typ = 'Rechnung'
                element = self.rechnungen_liste[self.index_auswahl(widget)]
            case self.tabelle_beihilfepakete:
                typ = 'Beihilfe'
                element = self.beihilfepakete_liste[self.index_auswahl(widget)]
            case self.tabelle_pkvpakete:
                typ = 'PKV'
                element = self.pkvpakete_liste[self.index_auswahl(widget)]
            case self.tabelle_einrichtungen:
                typ = 'Einrichtung'
                element = self.einrichtungen_liste[self.index_auswahl(widget)]

        # Ermittlung der Texte
        if typ == 'Rechnung':
            titel = 'Rechnung'
            inhalt = 'Rechnungsdatum: {}\n'.format(element.rechnungsdatum)
            inhalt += 'Betrag: {:.2f} €\n'.format(element.betrag).replace('.', ',')
            inhalt += 'Person: {}\n'.format(element.person_name)
            inhalt += 'Beihilfesatz: {:.0f} %\n\n'.format(element.beihilfesatz)
            inhalt += 'Einrichtung: {}\n'.format(element.einrichtung_name)
            inhalt += 'Notiz: {}\n'.format(element.notiz)
            inhalt += 'Buchungsdatum: {}\n'.format(element.buchungsdatum) if element.buchungsdatum else 'Buchungsdatum: -\n'
            inhalt += 'Bezahlt: Ja' if element.bezahlt else 'Bezahlt: Nein'
        elif typ == 'Beihilfe' or typ == 'PKV':
            titel = 'Beihilfe-Einreichung' if typ == 'Beihilfe' else 'PKV-Einreichung'
            inhalt = 'Vom {} '.format(element.datum)
            inhalt += 'über {:.2f} €\n\n'.format(element.betrag).replace('.', ',')
            
            # Liste alle Rechnungen auf, die zu diesem Paket gehören
            inhalt += 'Eingereichte Rechnungen:'
            for rechnung in self.rechnungen_liste:
                if (typ == 'Beihilfe' and rechnung.beihilfe_id == element.db_id) or (typ == 'PKV' and rechnung.pkv_id == element.db_id):
                    inhalt += '\n- {}'.format(rechnung.info)
                    #inhalt += ', {}'.format(rechnung.rechnungsdatum)
                    inhalt += ', {:.2f} €'.format(rechnung.betrag).replace('.', ',')
                    inhalt += ', {:.0f} %'.format(rechnung.beihilfesatz)
        elif typ == 'Einrichtung':
            titel = 'Einrichtung'
            inhalt = 'Name: {}\n'.format(element.name)
            # inhalt += 'Straße: {}\n'.format(element.strasse)
            # inhalt += 'PLZ: {}\n'.format(element.plz)
            # inhalt += 'Ort: {}\n'.format(element.ort)
            # inhalt += 'Notiz: {}'.format(element.notiz)

        self.main_window.info_dialog(titel, inhalt)


    def create_list_bills(self):
        """Erzeugt die Seite, auf der die Rechnungen angezeigt werden."""
        self.box_seite_liste_rechnungen = toga.Box(style=style_box_column)
        box_seite_liste_rechnungen_top = toga.Box(style=style_box_column_rechnungen)
        box_seite_liste_rechnungen_top.add(toga.Button('Zurück', style=style_button, on_press=self.zeige_startseite))
        box_seite_liste_rechnungen_top.add(toga.Label('Rechnungen', style=style_label_h1_hell))
        self.box_seite_liste_rechnungen.add(box_seite_liste_rechnungen_top)

        # Tabelle mit den Rechnungen
        self.tabelle_rechnungen = toga.Table(
            headings    = ['Info', 'Betrag', 'Bezahlt'],
            accessors   = ['info', 'betrag_euro', 'bezahlt_text'],
            data        = self.rechnungen_liste,
            style       = style_table,
            on_select   = self.update_app,
            on_activate = self.zeige_info_buchung
        )
        self.box_seite_liste_rechnungen.add(self.tabelle_rechnungen)

        # Buttons für die Rechnungen
        box_seite_liste_rechnungen_buttons = toga.Box(style=style_box_row)
        self.liste_rechnungen_button_loeschen = toga.Button('Löschen', on_press=self.confirm_delete_bill, style=style_button, enabled=False)
        self.liste_rechnungen_button_bearbeiten = toga.Button('Bearbeiten', on_press=self.show_form_bill_edit, style=style_button, enabled=False)
        self.liste_rechnungen_button_neu = toga.Button('Neu', on_press=self.show_form_bill_new, style=style_button)
        box_seite_liste_rechnungen_buttons.add(self.liste_rechnungen_button_loeschen)
        box_seite_liste_rechnungen_buttons.add(self.liste_rechnungen_button_bearbeiten)
        box_seite_liste_rechnungen_buttons.add(self.liste_rechnungen_button_neu)
        self.box_seite_liste_rechnungen.add(box_seite_liste_rechnungen_buttons)    


    def show_list_bills(self, widget):
        """Zeigt die Seite mit der Liste der Rechnungen."""
        self.update_app(widget)
        self.main_window.content = self.box_seite_liste_rechnungen


    def update_form_bill_beihilfe(self, widget):
        """Ermittelt den Beihilfesatz der ausgewählten Person und trägt ihn in das entsprechende Feld ein."""
        for person in self.personen_liste:
            if person.name == widget.value.name:
                self.form_bill_beihilfe.set_value(person.beihilfesatz)
                break


    def create_form_bill(self):
        """ Erzeugt das Formular zum Erstellen und Bearbeiten einer Rechnung."""
        
        # Container für das Formular
        self.sc_form_bill = toga.ScrollContainer(style=style_scroll_container)
        self.box_form_bill = toga.Box(style=style_box_column)
        self.sc_form_bill.content = self.box_form_bill

        # Erzeuge eine Liste von Dictionaries, welche die Elemente der Seite enthält
        # self.form_bill_elements = [
        #     {'typ': 'TopBox', 'label_text': 'Neue Rechnung', 'style': style_box_column_rechnungen, 'target_back': self.show_list_bills},
        #     {'typ': 'LabeledSelection', 'label_text': 'Person:', 'data': self.personen_liste, 'accessor': 'name', 'on_change': self.update_form_bill_beihilfe},
        #     {'typ': 'LabeledPercentInput', 'label_text': 'Beihilfesatz in %:'},
        #     {'typ': 'Divider', 'style': style_divider},
        #     {'typ': 'LabeledDateInput', 'label_text': 'Rechnungsdatum:'},
        #     {'typ': 'LabeledFloatInput', 'label_text': 'Betrag in €:'},
        #     {'typ': 'LabeledSelection', 'label_text': 'Einrichtung:', 'data': self.einrichtungen_liste, 'accessor': 'name'},
        #     {'typ': 'Divider', 'style': style_divider},
        #     {'typ': 'LabeledDateInput', 'label_text': 'Bezahldatum:'},
        #     {'typ': 'LabeledSwitch', 'label_text': 'Bezahlt:'},
        #     {'typ': 'Divider', 'style': style_divider},
        #     {'typ': 'LabeledMultilineTextInput', 'label_text': 'Notiz:'},
        #     {'typ': 'BottomBox', 'labels': ['Abbrechen', 'Speichern'], 'targets': [self.show_list_bills, self.check_save_bill]},
        # ]

        # Überschrift und Button zurück
        self.form_bill_topbox = TopBox(
            parent=self.box_form_bill,
            label_text='Neue Rechnung', 
            style_box=style_box_column_rechnungen,
            target_back=self.show_list_bills
        )

        # Selection zur Auswahl der Person
        self.form_bill_person = LabeledSelection(
            parent=self.box_form_bill,
            label_text='Person:',
            data=self.personen_liste,
            accessor='name',
            on_change=self.update_form_bill_beihilfe
        )

        self.form_bill_beihilfe = LabeledPercentInput(self.box_form_bill, 'Beihilfesatz in %:')
        self.box_form_bill.add(toga.Divider(style=style_divider))
        self.form_bill_rechnungsdatum = LabeledDateInput(self.box_form_bill, 'Rechnungsdatum:')
        self.form_bill_betrag = LabeledFloatInput(self.box_form_bill, 'Betrag in €:')

        # Bereich zur Auswahl der Einrichtung
        self.form_bill_einrichtung = LabeledSelection(
            parent=self.box_form_bill,
            label_text='Einrichtung:',
            data=self.einrichtungen_liste,
            accessor='name'
        )

        self.box_form_bill.add(toga.Divider(style=style_divider))
        self.form_bill_buchungsdatum = LabeledDateInput(self.box_form_bill, 'Bezahldatum:')
        self.form_bill_bezahlt = LabeledSwitch(self.box_form_bill, 'Bezahlt:')
        self.box_form_bill.add(toga.Divider(style=style_divider))
        self.form_bill_notiz = LabeledMultilineTextInput(self.box_form_bill, 'Notiz:')

        # Bereich der Buttons
        self.form_bill_bottombox = BottomBox(
            parent=self.box_form_bill,
            labels=['Abbrechen', 'Speichern'],
            targets=[self.show_list_bills, self.check_save_bill],
        )


    def show_form_bill_new(self, widget):
        """Zeigt die Seite zum Erstellen einer Rechnung."""
        
        # Setze die Eingabefelder zurück
        self.form_bill_betrag.set_value('')
        self.form_bill_rechnungsdatum.set_value('')

        if len(self.personen_liste) > 0:
            self.form_bill_person.set_value(self.personen_liste[0])
            self.form_bill_beihilfe.set_value(str(self.personen_liste[0].beihilfesatz))
        
        if len(self.einrichtungen_liste) > 0:
            self.form_bill_einrichtung.set_value(self.einrichtungen_liste[0])

        self.form_bill_notiz.set_value('')
        self.form_bill_buchungsdatum.set_value('')
        self.form_bill_bezahlt.set_value(False)

        # Zurücksetzen von Flag und Überschrift
        self.flag_edit_bill = False
        self.form_bill_topbox.set_label('Neue Rechnung')

        # Zeige die Seite
        self.main_window.content = self.sc_form_bill

    
    def show_form_bill_edit(self, widget):
        """Zeigt die Seite zum Bearbeiten einer Rechnung."""

        # Ermittle den Index der ausgewählten Rechnung
        if widget == self.liste_rechnungen_button_bearbeiten:
            self.edit_bill_id = self.index_auswahl(self.tabelle_rechnungen)
        elif widget == self.startseite_button_bearbeiten:
            self.edit_bill_id = self.index_liste_von_id(self.rechnungen, self.tabelle_offene_buchungen.selection.db_id)
        else:
            print('Fehler: Aufrufendes Widget unbekannt.')
            return

        # Ermittle den Index der Einrichtung in der Liste der Einrichtungen
        einrichtung_index = self.index_liste_von_id(self.einrichtungen, self.rechnungen[self.edit_bill_id].einrichtung_id)

        # Auswahlfeld für die Einrichtung befüllen
        if einrichtung_index is not None:
            self.form_bill_einrichtung.set_value(self.einrichtungen_liste[einrichtung_index])
        elif len(self.einrichtungen_liste) > 0:
            self.form_bill_einrichtung.set_value(self.einrichtungen_liste[0])

        # Ermittle den Index der Person in der Liste der Personen
        person_index = self.index_liste_von_id(self.personen, self.rechnungen[self.edit_bill_id].person_id)

        # Auswahlfeld für die Person befüllen
        if person_index is not None:    
            self.form_bill_person.set_value(self.personen_liste[person_index])
        elif len(self.personen_liste) > 0:
            self.form_bill_person.set_value(self.personen_liste[0])

        # Befülle die Eingabefelder
        self.form_bill_betrag.set_value(self.rechnungen[self.edit_bill_id].betrag)
        self.form_bill_rechnungsdatum.set_value(self.rechnungen[self.edit_bill_id].rechnungsdatum)
        self.form_bill_beihilfe.set_value(self.rechnungen[self.edit_bill_id].beihilfesatz)
        self.form_bill_notiz.set_value(self.rechnungen[self.edit_bill_id].notiz)
        self.form_bill_buchungsdatum.set_value(self.rechnungen[self.edit_bill_id].buchungsdatum)
        self.form_bill_bezahlt.set_value(self.rechnungen[self.edit_bill_id].bezahlt)

        # Setze das Flag und die Überschrift
        self.flag_edit_bill = True
        self.form_bill_topbox.set_label('Rechnung bearbeiten')

        # Zeige die Seite
        self.main_window.content = self.sc_form_bill


    async def check_save_bill(self, widget):
        """Prüft, ob die Rechnung gespeichert werden soll."""

        nachricht = ''

        # Prüfe, ob ein Rechnungsdatum eingegeben wurde
        if not self.form_bill_rechnungsdatum.is_valid():
            nachricht += 'Bitte gib ein gültiges Rechnungsdatum ein.\n'

        # Prüfe, ob ein Betrag eingegeben wurde
        if not self.form_bill_betrag.is_valid():
            nachricht += 'Bitte gib einen gültigen Betrag ein.\n'

        # Prüfe, ob eine Person ausgewählt wurde
        if len(self.personen_liste) > 0:
            if self.form_bill_person.get_value() is None:
                nachricht += 'Bitte wähle eine Person aus.\n'

        # Prüfe, ob eine Einrichtung ausgewählt wurde
        if len(self.einrichtungen_liste) > 0:
            if self.form_bill_einrichtung.get_value() is None:
                nachricht += 'Bitte wähle eine Einrichtung aus.\n'

        # Prüfe, ob ein Beihilfesatz eingegeben wurde
        if not self.form_bill_beihilfe.is_valid():
            nachricht += 'Bitte gib einen gültigen Beihilfesatz ein.\n'

        if not (self.form_bill_buchungsdatum.is_valid() or self.form_bill_buchungsdatum.is_empty()):
            nachricht += 'Bitte gib ein gültiges Buchungsdatum ein oder lasse das Feld leer.\n'
                
        if nachricht != '':
            self.main_window.error_dialog('Fehlerhafte Eingabe', nachricht)
        else:
            await self.save_bill(widget)


    async def save_bill(self, widget):
        """Erstellt und speichert eine neue Rechnung."""

        if not self.flag_edit_bill:
        # Erstelle eine neue Rechnung
            neue_rechnung = Rechnung()
            neue_rechnung.rechnungsdatum = self.form_bill_rechnungsdatum.get_value()
            if len(self.personen_liste) > 0:
                neue_rechnung.person_id = self.form_bill_person.get_value().db_id
            neue_rechnung.beihilfesatz = self.form_bill_beihilfe.get_value()
            if len(self.einrichtungen_liste) > 0:
                neue_rechnung.einrichtung_id = self.form_bill_einrichtung.get_value().db_id
            neue_rechnung.notiz = self.form_bill_notiz.get_value()
            neue_rechnung.betrag = self.form_bill_betrag.get_value()
            neue_rechnung.buchungsdatum = self.form_bill_buchungsdatum.get_value()
            neue_rechnung.bezahlt = self.form_bill_bezahlt.get_value()

            # Speichere die Rechnung in der Datenbank
            neue_rechnung.neu(self.db)

            # Füge die Rechnung der Liste hinzu
            self.rechnungen.append(neue_rechnung)
            self.rechnungen_liste_anfuegen(neue_rechnung)

            # Kehrt zurück zur Startseite
            self.update_app(widget)
            self.zeige_startseite(widget)
        else:
            # flag ob verknüpfte Einreichungen aktualisiert werden können
            # True, wenn betrag oder beihilfesatz geändert wurde
            update_einreichung = False
            
            if self.rechnungen[self.edit_bill_id].betrag != self.form_bill_betrag.get_value():
                update_einreichung = True
            if self.rechnungen[self.edit_bill_id].beihilfesatz != self.form_bill_beihilfe.get_value():
                update_einreichung = True

            # Bearbeite die Rechnung
            self.rechnungen[self.edit_bill_id].rechnungsdatum = self.form_bill_rechnungsdatum.get_value()

            if len(self.personen_liste) > 0:
                self.rechnungen[self.edit_bill_id].person_id = self.form_bill_person.get_value().db_id
            
            if len(self.einrichtungen_liste) > 0:
                self.rechnungen[self.edit_bill_id].einrichtung_id = self.form_bill_einrichtung.get_value().db_id
            self.rechnungen[self.edit_bill_id].notiz = self.form_bill_notiz.get_value()
            self.rechnungen[self.edit_bill_id].betrag = self.form_bill_betrag.get_value()
            self.rechnungen[self.edit_bill_id].beihilfesatz = self.form_bill_beihilfe.get_value()
            self.rechnungen[self.edit_bill_id].buchungsdatum = self.form_bill_buchungsdatum.get_value()
            self.rechnungen[self.edit_bill_id].bezahlt = self.form_bill_bezahlt.get_value()

            # Speichere die Rechnung in der Datenbank
            self.rechnungen[self.edit_bill_id].speichern(self.db)

            # Aktualisiere die Liste der Rechnungen
            self.rechnungen_liste_aendern(self.rechnungen[self.edit_bill_id], self.edit_bill_id)

            # Flag zurücksetzen
            self.flag_edit_bill = False

            # Überprüfe ob eine verknüpfte Beihilfe-Einreichung existiert
            # und wenn ja, frage, ob diese aktualisiert werden soll
            if update_einreichung and self.rechnungen[self.edit_bill_id].beihilfe_id is not None:
                await self.main_window.confirm_dialog(
                    'Zugehörige Beihilfe-Einreichung aktualisieren',
                    'Soll die zugehörige Beihilfe-Einreichung aktualisiert werden?',
                    on_result=self.beihilfepaket_aktualisieren
                )

            # Überprüfe ob eine verknüpfte PKV-Einreichung existiert
            # und wenn ja, frage, ob diese aktualisiert werden soll
            if update_einreichung and self.rechnungen[self.edit_bill_id].pkv_id is not None:
                await self.main_window.confirm_dialog(
                    'Zugehörige PKV-Einreichung aktualisieren',
                    'Soll die zugehörige PKV-Einreichung aktualisiert werden?',
                    on_result=self.pkvpaket_aktualisieren
                )

            # Zeigt die Liste der Rechnungen an.
            self.update_app(widget)
            self.show_list_bills(widget)


    def beihilfepaket_aktualisieren(self, widget, result):
        """Aktualisiert die Beihilfe-Einreichung einer Rechnung."""
        if result:
            # Finde die Beihilfe-Einreichung
            for beihilfepaket in self.beihilfepakete:
                if beihilfepaket.db_id == self.rechnungen[self.edit_bill_id].beihilfe_id:
                    # Alle Rechnungen durchlaufen und den Betrag aktualisieren
                    beihilfepaket.betrag = 0
                    for rechnung in self.rechnungen:
                        if rechnung.beihilfe_id == beihilfepaket.db_id:
                            beihilfepaket.betrag += rechnung.betrag * (rechnung.beihilfesatz / 100)
                    # Die Beihilfe-Einreichung speichern
                    beihilfepaket.speichern(self.db)
                    self.beihilfepakete_liste_aendern(beihilfepaket, self.beihilfepakete.index(beihilfepaket))
                    break
            

    def pkvpaket_aktualisieren(self, widget, result):
        """Aktualisiert die PKV-Einreichung einer Rechnung."""
        if result:
            # Finde die PKV-Einreichung
            for pkvpaket in self.pkvpakete:
                if pkvpaket.db_id == self.rechnungen[self.edit_bill_id].pkv_id:
                    # ALle Rechnungen durchlaufen und den Betrag aktualisieren
                    pkvpaket.betrag = 0
                    for rechnung in self.rechnungen:
                        if rechnung.pkv_id == pkvpaket.db_id:
                            pkvpaket.betrag += rechnung.betrag * (1 - (rechnung.beihilfesatz / 100))
                    # Die PKV-Einreichung speichern
                    pkvpaket.speichern(self.db)
                    self.pkvpakete_liste_aendern(pkvpaket, self.pkvpakete.index(pkvpaket))
                    break            


    def confirm_delete_bill(self, widget):
        """Bestätigt das Löschen einer Rechnung."""
        if self.tabelle_rechnungen.selection:
            self.main_window.confirm_dialog(
                'Rechnung löschen', 
                'Soll die ausgewählte Rechnung wirklich gelöscht werden?',
                on_result=self.delete_bill
            )


    async def delete_bill(self, widget, result):
        """Löscht eine Rechnung."""
        if self.tabelle_rechnungen.selection and result:
            
            # Index der ausgewählten Rechnung ermitteln
            self.edit_bill_id = self.index_auswahl(self.tabelle_rechnungen)
            
            # Betrag der Rechnung auf 0 setzen um die Einreichungen aktualisieren zu können
            self.rechnungen[self.edit_bill_id].betrag = 0
    
            # Auf Wunsch Beihilfe-Einreichung aktualisieren
            if self.rechnungen[self.edit_bill_id].beihilfe_id is not None:
                await self.main_window.confirm_dialog(
                    'Zugehörige Beihilfe-Einreichung aktualisieren',
                    'Soll die zugehörige Beihilfe-Einreichung aktualisiert werden?',
                    on_result=self.beihilfepaket_aktualisieren
                )

            # Auf Wunsch PKV-Einreichung aktualisieren
            if self.rechnungen[self.edit_bill_id].pkv_id is not None:
                await self.main_window.confirm_dialog(
                    'Zugehörige PKV-Einreichung aktualisieren',
                    'Soll die zugehörige PKV-Einreichung aktualisiert werden?',
                    on_result=self.pkvpaket_aktualisieren
                )

            # Rechnung löschen
            self.rechnungen[self.edit_bill_id].loeschen(self.db)  
            del self.rechnungen[self.edit_bill_id]
            del self.rechnungen_liste[self.edit_bill_id]   


    def create_list_institutions(self):
        """Erzeugt die Seite, auf der die Einrichtungen angezeigt werden."""
        self.box_seite_liste_einrichtungen = toga.Box(style=style_box_column)
        box_seite_liste_einrichtungen_top = toga.Box(style=style_box_column_dunkel)
        box_seite_liste_einrichtungen_top.add(toga.Button('Zurück', on_press=self.zeige_startseite, style=style_button))
        box_seite_liste_einrichtungen_top.add(toga.Label('Einrichtungen', style=style_label_h1_hell))
        self.box_seite_liste_einrichtungen.add(box_seite_liste_einrichtungen_top)

        # Tabelle mit den Einrichtungen

        self.tabelle_einrichtungen = toga.Table(
            headings    = ['Name', 'Ort', 'Telefon'], 
            accessors   = ['name', 'ort', 'telefon'],
            data        = self.einrichtungen_liste,
            style       = style_table,
            on_select   = self.update_app,
            on_activate = self.show_info_institution
        )
        self.box_seite_liste_einrichtungen.add(self.tabelle_einrichtungen)

        # Buttons für die Einrichtungen
        box_seite_liste_einrichtungen_buttons1 = toga.Box(style=style_box_row)
        box_seite_liste_einrichtungen_buttons2 = toga.Box(style=style_box_row)
        self.seite_liste_einrichtungen_button_bearbeiten = toga.Button('Bearbeiten', on_press=self.show_form_institution_edit, style=style_button, enabled=False)
        self.seite_liste_einrichtungen_button_neu = toga.Button('Neu', on_press=self.show_form_institution_new, style=style_button)
        self.seite_liste_einrichtungen_button_loeschen = toga.Button('Löschen', on_press=self.confirm_delete_institution, style=style_button, enabled=False)
        self.seite_liste_einrichtungen_button_info = toga.Button('Info', on_press=self.show_info_institution, style=style_button, enabled=False)
        box_seite_liste_einrichtungen_buttons1.add(self.seite_liste_einrichtungen_button_bearbeiten)
        box_seite_liste_einrichtungen_buttons1.add(self.seite_liste_einrichtungen_button_neu)
        box_seite_liste_einrichtungen_buttons2.add(self.seite_liste_einrichtungen_button_loeschen)
        box_seite_liste_einrichtungen_buttons2.add(self.seite_liste_einrichtungen_button_info)
        self.box_seite_liste_einrichtungen.add(box_seite_liste_einrichtungen_buttons1)   
        self.box_seite_liste_einrichtungen.add(box_seite_liste_einrichtungen_buttons2)


    def show_list_institutions(self, widget):
        """Zeigt die Seite mit der Liste der Einrichtungen."""
        self.update_app(widget)
        self.main_window.content = self.box_seite_liste_einrichtungen


    def create_form_institution(self):
        """Erzeugt das Formular zum Erstellen und Bearbeiten einer Einrichtung."""
        self.sc_form_institution = toga.ScrollContainer(style=style_scroll_container)
        self.box_form_institution = toga.Box(style=style_box_column)
        self.sc_form_institution.content = self.box_form_institution

        # TopBox
        self.form_institution_topbox = TopBox(
            parent=self.box_form_institution,
            label_text='Neue Einrichtung',
            style_box=style_box_column_dunkel,
            target_back=self.show_list_institutions
        )

        self.form_institution_name = LabeledTextInput(self.box_form_institution, 'Name:')
        self.form_institution_strasse = LabeledTextInput(self.box_form_institution, 'Straße, Hausnr.:')
        self.form_institution_plz = LabeledPostalInput(self.box_form_institution, 'PLZ:')
        self.form_institution_ort = LabeledTextInput(self.box_form_institution, 'Ort:')
        self.box_form_institution.add(toga.Divider(style=style_divider))
        self.form_institution_telefon = LabeledPhoneInput(self.box_form_institution, 'Telefon:')
        self.form_institution_email = LabeledEmailInput(self.box_form_institution, 'E-Mail:')
        self.form_institution_webseite = LabeledWebsiteInput(self.box_form_institution, 'Webseite:')
        self.box_form_institution.add(toga.Divider(style=style_divider))
        self.form_institution_notiz = LabeledMultilineTextInput(self.box_form_institution, 'Notiz:')

        # BottomBox
        self.form_institution_bottombox = BottomBox(
            parent=self.box_form_institution,
            labels=['Abbrechen', 'Speichern'],
            targets=[self.show_list_institutions, self.check_save_institution]
        )


    def show_form_institution_new(self, widget):
        """Zeigt die Seite zum Erstellen einer Einrichtung."""
        # Setze die Eingabefelder zurück
        self.form_institution_name.set_value('')
        self.form_institution_strasse.set_value('')
        self.form_institution_plz.set_value('')
        self.form_institution_ort.set_value('')
        self.form_institution_telefon.set_value('')
        self.form_institution_email.set_value('')
        self.form_institution_webseite.set_value('')
        self.form_institution_notiz.set_value('')

        # Zurücksetzen des Flags und der Überschrift
        self.flag_edit_institution = False
        self.form_institution_topbox.set_label('Neue Einrichtung')

        # Zeige die Seite
        self.main_window.content = self.sc_form_institution


    def show_form_institution_edit(self, widget):
        """Zeigt die Seite zum Bearbeiten einer Einrichtung."""
        
        # Prüfe ob eine Einrichtung ausgewählt ist
        if self.tabelle_einrichtungen.selection:
            # Ermittle den Index der ausgewählten Rechnung
            self.edit_institution_id = self.index_auswahl(self.tabelle_einrichtungen)
            
            # Befülle die Eingabefelder
            self.form_institution_name.set_value(self.einrichtungen[self.edit_institution_id].name)
            self.form_institution_strasse.set_value(self.einrichtungen[self.edit_institution_id].strasse)
            self.form_institution_plz.set_value(self.einrichtungen[self.edit_institution_id].plz)
            self.form_institution_ort.set_value(self.einrichtungen[self.edit_institution_id].ort)
            self.form_institution_telefon.set_value(self.einrichtungen[self.edit_institution_id].telefon)
            self.form_institution_email.set_value(self.einrichtungen[self.edit_institution_id].email)
            self.form_institution_webseite.set_value(self.einrichtungen[self.edit_institution_id].webseite)
            self.form_institution_notiz.set_value(self.einrichtungen[self.edit_institution_id].notiz)

            # Setze das Flag und die Überschrift
            self.flag_edit_institution = True
            self.form_institution_topbox.set_label('Einrichtung bearbeiten')

            # Zeige die Seite
            self.main_window.content = self.sc_form_institution


    def check_save_institution(self, widget):
        """Prüft die Eingaben im Formular der Einrichtungen."""
        nachricht = ''

        # Prüfe, ob ein Name eingegeben wurde
        if self.form_institution_name.is_empty():
            nachricht += 'Bitte gib einen Namen ein.\n'

        # Prüfe, ob nichts oder eine gültige PLZ eingegeben wurde
        if not (self.form_institution_plz.is_valid() or self.form_institution_plz.is_empty()):
                nachricht += 'Bitte gib eine gültige PLZ ein oder lasse das Feld leer.\n'

        # Prüfe, ob nichts oder eine gültige Telefonnummer eingegeben wurde
        if not (self.form_institution_telefon.is_valid() or self.form_institution_telefon.is_empty()):
                nachricht += 'Bitte gib eine gültige Telefonnummer ein oder lasse das Feld leer.\n'

        # Prüfe, ob nichts oder eine gültige E-Mail-Adresse eingegeben wurde
        if not (self.form_institution_email.is_valid() or  self.form_institution_email.is_empty()):
                nachricht += 'Bitte gib eine gültige E-Mail-Adresse ein oder lasse das Feld leer.\n'

        # Prüfe, ob nichts oder eine gültige Webseite eingegeben wurde
        if not (self.form_institution_webseite.is_valid() or self.form_institution_webseite.is_empty()):
                nachricht += 'Bitte gib eine gültige Webseite ein oder lasse das Feld leer.\n'

        if nachricht != '':
            self.main_window.error_dialog('Fehlerhafte Eingabe', nachricht)
        else:
            self.save_institution(widget)


    def save_institution(self, widget):
        """Erstellt und speichert eine neue Einrichtung."""
        if not self.flag_edit_institution:
        # Erstelle eine neue Einrichtung
            neue_einrichtung = Einrichtung()
            neue_einrichtung.name = self.form_institution_name.get_value()
            neue_einrichtung.strasse = self.form_institution_strasse.get_value()
            neue_einrichtung.plz = self.form_institution_plz.get_value()
            neue_einrichtung.ort = self.form_institution_ort.get_value()
            neue_einrichtung.telefon = self.form_institution_telefon.get_value()
            neue_einrichtung.email = self.form_institution_email.get_value()
            neue_einrichtung.webseite = self.form_institution_webseite.get_value()
            neue_einrichtung.notiz = self.form_institution_notiz.get_value()

            # Speichere die Einrichtung in der Datenbank
            neue_einrichtung.neu(self.db)

            # Füge die Einrichtung der Liste hinzu
            self.einrichtungen.append(neue_einrichtung)
            self.einrichtungen_liste_anfuegen(neue_einrichtung)
        else:
            # Bearbeite die Einrichtung
            self.einrichtungen[self.edit_institution_id].name = self.form_institution_name.get_value()
            self.einrichtungen[self.edit_institution_id].strasse = self.form_institution_strasse.get_value()
            self.einrichtungen[self.edit_institution_id].plz = self.form_institution_plz.get_value()
            self.einrichtungen[self.edit_institution_id].ort = self.form_institution_ort.get_value()
            self.einrichtungen[self.edit_institution_id].telefon = self.form_institution_telefon.get_value()
            self.einrichtungen[self.edit_institution_id].email = self.form_institution_email.get_value()
            self.einrichtungen[self.edit_institution_id].webseite = self.form_institution_webseite.get_value()
            self.einrichtungen[self.edit_institution_id].notiz = self.form_institution_notiz.get_value()

            # Speichere die Einrichtung in der Datenbank
            self.einrichtungen[self.edit_institution_id].speichern(self.db)

            # Aktualisiere die Liste der Einrichtungen
            self.einrichtungen_liste_aendern(self.einrichtungen[self.edit_institution_id], self.edit_institution_id)

            # Flag zurücksetzen
            self.flag_edit_institution = False

            # Aktualisiere die Liste der Rechnungen
            self.rechnungen_liste_aktualisieren()

        # Zeige die Liste der Einrichtungen
        self.update_app(widget)
        self.show_list_institutions(widget)


    def create_info_institution(self):
        """Erzeugt die Seite, auf der die Details einer Einrichtung angezeigt werden."""
        box_seite_info_einrichtung_button_zurueck = toga.Button('Zurück', on_press=self.show_list_institutions, style=style_button)
        self.label_info_einrichtung_name = toga.Label('', style=style_label_h1_hell)
        box_seite_info_einrichtung_top = toga.Box(style=style_box_column_dunkel)
        box_seite_info_einrichtung_top.add(box_seite_info_einrichtung_button_zurueck)
        box_seite_info_einrichtung_top.add(self.label_info_einrichtung_name)

        # Bereich mit den Details zur Straße
        box_seite_info_einrichtung_strasse = toga.Box(style=style_box_row)
        box_seite_info_einrichtung_strasse.add(toga.Label('Straße, Hausnr.: ', style=style_label_info))
        self.label_info_einrichtung_strasse = toga.Label('', style=style_label_detail)
        box_seite_info_einrichtung_strasse.add(self.label_info_einrichtung_strasse)

        # Bereich mit den Details zum Ort
        box_seite_info_einrichtung_plz_ort = toga.Box(style=style_box_row)
        box_seite_info_einrichtung_plz_ort.add(toga.Label('PLZ, Ort: ', style=style_label_info))
        self.label_info_einrichtung_plz_ort = toga.Label('', style=style_label_detail)
        box_seite_info_einrichtung_plz_ort.add(self.label_info_einrichtung_plz_ort)

        # Bereich mit den Details zur Telefonnummer
        box_seite_info_einrichtung_telefon = toga.Box(style=style_box_row)
        box_seite_info_einrichtung_telefon.add(toga.Label('Telefon: ', style=style_label_info))
        self.label_info_einrichtung_telefon = toga.Label('', style=style_label_detail)
        box_seite_info_einrichtung_telefon.add(self.label_info_einrichtung_telefon)
        #self.display_info_einrichtung_telefon = toga.TextInput(style=style_display, readonly=True)
        #box_seite_info_einrichtung_telefon.add(self.display_info_einrichtung_telefon)
        
        # Bereich mit den Details zur E-Mail-Adresse
        box_seite_info_einrichtung_email = toga.Box(style=style_box_row)
        box_seite_info_einrichtung_email.add(toga.Label('E-Mail: ', style=style_label_info))
        self.label_info_einrichtung_email = toga.Label('', style=style_label_detail)
        box_seite_info_einrichtung_email.add(self.label_info_einrichtung_email)
        #self.display_info_einrichtung_email = toga.TextInput(style=style_display, readonly=True)
        #box_seite_info_einrichtung_email.add(self.display_info_einrichtung_email)

        # Bereich mit den Details zur Webseite
        self.box_seite_info_einrichtung_webseite = toga.Box(style=style_box_row)
        # box_seite_info_einrichtung_webseite.add(toga.Label('Webseite: ', style=style_label_info))
        # self.label_info_einrichtung_webseite = toga.Label('', style=style_label_detail)
        # box_seite_info_einrichtung_webseite.add(self.label_info_einrichtung_webseite)
        label_info_einrichtung_website = toga.Label('Webseite:', style=style_label_info)
        self.link_info_einrichtung_webseite = toga.Button('', style=style_button_link, on_press=self.zeige_webview)
        

        # Bereich mit den Details zur Notiz
        box_seite_info_einrichtung_notiz = toga.Box(style=style_box_row)
        box_seite_info_einrichtung_notiz.add(toga.Label('Notiz: ', style=style_label_info))
        self.label_info_einrichtung_notiz = toga.Label('', style=style_label_detail)
        box_seite_info_einrichtung_notiz.add(self.label_info_einrichtung_notiz)

        # Bereich mit den Buttons
        box_seite_info_einrichtung_buttons = toga.Box(style=style_box_row)
        self.seite_info_einrichtung_button_bearbeiten = toga.Button('Bearbeiten', on_press=self.show_form_institution_edit, style=style_button)
        box_seite_info_einrichtung_buttons.add(self.seite_info_einrichtung_button_bearbeiten)
        self.seite_info_einrichtung_button_loeschen = toga.Button('Löschen', on_press=self.confirm_delete_institution, style=style_button)
        box_seite_info_einrichtung_buttons.add(self.seite_info_einrichtung_button_loeschen)

        # Inhaltselemente zur Seite hinzufügen
        self.scroll_container_info_einrichtung = toga.ScrollContainer(style=style_scroll_container)
        box_seite_info_einrichtung = toga.Box(
            style=style_box_column,
            children = [
                box_seite_info_einrichtung_top,
                box_seite_info_einrichtung_strasse,
                box_seite_info_einrichtung_plz_ort,
                toga.Divider(style=style_divider),
                box_seite_info_einrichtung_telefon,
                box_seite_info_einrichtung_email,
                self.box_seite_info_einrichtung_webseite,
                #label_info_einrichtung_website,
                #self.link_info_einrichtung_webseite,
                toga.Divider(style=style_divider),
                box_seite_info_einrichtung_notiz,
                box_seite_info_einrichtung_buttons
            ]
        )
        self.scroll_container_info_einrichtung.content = box_seite_info_einrichtung


    def show_info_institution(self, widget, row=None):
        """Zeigt die Seite mit den Details einer Einrichtung."""
        # Prüfe, ob eine Einrichtung ausgewählt ist
        if self.tabelle_einrichtungen.selection:

            # Ermittle den Index der ausgewählten Einrichtung
            self.edit_institution_id = self.index_auswahl(self.tabelle_einrichtungen)

            # Befülle die Labels mit den Details der Einrichtung
            # Die einzutragenden Werte können None sein, daher wird hier mit einem leeren String gearbeitet
            self.label_info_einrichtung_name.text = self.einrichtungen_liste[self.edit_institution_id].name
            self.label_info_einrichtung_strasse.text = self.einrichtungen_liste[self.edit_institution_id].strasse
            self.label_info_einrichtung_plz_ort.text = self.einrichtungen_liste[self.edit_institution_id].plz_ort
            self.label_info_einrichtung_telefon.text = self.einrichtungen_liste[self.edit_institution_id].telefon
            self.label_info_einrichtung_email.text = self.einrichtungen_liste[self.edit_institution_id].email
            
            # Entferne die Inhalte der Box, damit die Webseite nicht mehrfach angezeigt wird
            if self.link_info_einrichtung_webseite in self.box_seite_info_einrichtung_webseite.children:
                self.box_seite_info_einrichtung_webseite.remove(self.link_info_einrichtung_webseite)

            # Wenn eine gültige Webseite gespeichert ist, füge den Link wieder der Box hinzu
            # und setze den Text des Links auf die Webseite
            if self.einrichtungen_liste[self.edit_institution_id].webseite:
                self.box_seite_info_einrichtung_webseite.add(self.link_info_einrichtung_webseite)
                self.link_info_einrichtung_webseite.text = self.einrichtungen_liste[self.edit_institution_id].webseite
                
            self.label_info_einrichtung_notiz.text = self.einrichtungen_liste[self.edit_institution_id].notiz

            # Zeige die Seite
            self.main_window.content = self.scroll_container_info_einrichtung

    
    def confirm_delete_institution(self, widget):
        """Bestätigt das Löschen einer Einrichtung."""
        if self.tabelle_einrichtungen.selection:
            self.main_window.confirm_dialog(
                'Einrichtung löschen', 
                'Soll die ausgewählte Einrichtung wirklich gelöscht werden?',
                on_result=self.delete_institution
            )


    def delete_institution(self, widget, result):
        """Löscht eine Einrichtung."""
        if self.tabelle_einrichtungen.selection and result:
            index = self.index_auswahl(self.tabelle_einrichtungen)

            # Prüfe, ob die Einrichtung in einer Rechnung verwendet wird
            for rechnung in self.rechnungen:
                if rechnung.einrichtung_id == self.einrichtungen[index].db_id:
                    self.main_window.error_dialog(
                        'Fehler beim Löschen',
                        'Die Einrichtung wird noch in einer aktiven Rechnung verwendet und kann daher nicht gelöscht werden.'
                    )
                    return
            
            # Einrichtung wird deaktiviert
            self.einrichtungen[index].aktiv = False
            self.einrichtungen[index].speichern(self.db)
            del self.einrichtungen[index]
            del self.einrichtungen_liste[index]

            # Seite mit Liste der Einrichtungen anzeigen
            self.update_app(widget)
            self.show_list_institutions(widget)


    def create_list_persons(self):
        """Erzeugt die Seite, auf der die Personen angezeigt werden."""
        self.box_seite_liste_personen = toga.Box(style=style_box_column)
        box_seite_liste_personen_top = toga.Box(style=style_box_column_dunkel)
        box_seite_liste_personen_top.add(toga.Button('Zurück', on_press=self.zeige_startseite, style=style_button))
        box_seite_liste_personen_top.add(toga.Label('Personen', style=style_label_h1_hell))
        self.box_seite_liste_personen.add(box_seite_liste_personen_top)

        # Tabelle mit den Personen
        self.tabelle_personen = toga.Table(
            headings    = ['Name', 'Beihilfesatz'], 
            accessors   = ['name', 'beihilfesatz_prozent'],
            data        = self.personen_liste,
            style       = style_table,
            on_select   = self.update_app
        )
        self.box_seite_liste_personen.add(self.tabelle_personen)

        # Buttons für die Personen
        box_seite_liste_personen_buttons = toga.Box(style=style_box_row)
        self.seite_liste_personen_button_bearbeiten = toga.Button('Bearbeiten', on_press=self.show_form_persons_edit, style=style_button, enabled=False)
        self.seite_liste_personen_button_neu = toga.Button('Neu', on_press=self.show_form_persons_new, style=style_button)
        self.seite_liste_personen_button_loeschen = toga.Button('Löschen', on_press=self.confirm_delete_person, style=style_button, enabled=False)
        box_seite_liste_personen_buttons.add(self.seite_liste_personen_button_loeschen)
        box_seite_liste_personen_buttons.add(self.seite_liste_personen_button_bearbeiten)
        box_seite_liste_personen_buttons.add(self.seite_liste_personen_button_neu)
        self.box_seite_liste_personen.add(box_seite_liste_personen_buttons)


    def show_list_persons(self, widget):
        """Zeigt die Seite mit der Liste der Personen."""
        self.update_app(widget)
        self.main_window.content = self.box_seite_liste_personen


    def create_form_person(self):
        """Erzeugt das Formular zum Erstellen und Bearbeiten einer Person."""

        # Container
        self.sc_form_person = toga.ScrollContainer(style=style_scroll_container)
        self.box_form_person = toga.Box(style=style_box_column)
        self.sc_form_person.content = self.box_form_person

        # TopBox
        self.form_person_topbox = TopBox(
            parent=self.box_form_person,
            label_text='Neue Person',
            style_box=style_box_column_dunkel,
            target_back=self.show_list_persons
        )

        self.form_person_name = LabeledTextInput(self.box_form_person, 'Name:')
        self.form_person_beihilfe = LabeledPercentInput(self.box_form_person, 'Beihilfe in %:')

        # BottomBox
        self.form_person_bottombox = BottomBox(
            parent=self.box_form_person,
            labels=['Abbrechen', 'Speichern'],
            targets=[self.show_list_persons, self.check_save_person]
        )


    def show_form_persons_new(self, widget):
        """Zeigt die Seite zum Erstellen einer Person."""
        # Setze die Eingabefelder zurück
        self.form_person_name.set_value('')
        self.form_person_beihilfe.set_value('')

        # Zurücksetzen des Flags und der Überschrift
        self.flag_edit_person = False
        self.form_person_topbox.set_label('Neue Person')

        # Zeige die Seite
        self.main_window.content = self.sc_form_person


    def show_form_persons_edit(self, widget):
        """Zeigt die Seite zum Bearbeiten einer Person."""
            
        # Prüfe ob eine Person ausgewählt ist
        if self.tabelle_personen.selection:
            # Ermittle den Index der ausgewählten Person
            self.edit_person_id = self.index_auswahl(self.tabelle_personen)
            
            # Befülle die Eingabefelder
            self.form_person_name.set_value(self.personen[self.edit_person_id].name)
            self.form_person_beihilfe.set_value(self.personen[self.edit_person_id].beihilfesatz)

            # Setze das Flag und die Überschrift
            self.flag_edit_person = True
            self.form_person_topbox.set_label('Person bearbeiten')

            # Zeige die Seite
            self.main_window.content = self.sc_form_person


    def check_save_person(self, widget):
        """Prüft die Eingaben im Formular der Personen."""
        nachricht = ''

        # Prüfe, ob ein Name eingegeben wurde
        if self.form_person_name.is_empty():
            nachricht += 'Bitte gib einen Namen ein.\n'

        # Prüfe, ob eine gültige Prozentzahl eingegeben wurde
        if not self.form_person_beihilfe.is_valid():
                nachricht += 'Bitte gib einen gültigen Beihilfesatz ein.\n'

        if nachricht != '':
            self.main_window.error_dialog('Fehlerhafte Eingabe', nachricht)
        else:
            self.save_person(widget)


    def save_person(self, widget):
        """Erstellt und speichert eine neue Person."""
        if not self.flag_edit_person:
        # Erstelle eine neue Person
            neue_person = Person()
            neue_person.name = self.form_person_name.get_value()
            neue_person.beihilfesatz = self.form_person_beihilfe.get_value()

            # Speichere die Person in der Datenbank
            neue_person.neu(self.db)

            # Füge die Person der Liste hinzu
            self.personen.append(neue_person)
            self.personen_liste_anfuegen(neue_person)
        else:
            # Bearbeite die Person
            self.personen[self.edit_person_id].name = self.form_person_name.get_value()
            self.personen[self.edit_person_id].beihilfesatz = self.form_person_beihilfe.get_value()

            # Speichere die Person in der Datenbank
            self.personen[self.edit_person_id].speichern(self.db)

            # Aktualisiere die Liste der Personen
            self.personen_liste_aendern(self.personen[self.edit_person_id], self.edit_person_id)

            # Flag zurücksetzen
            self.flag_edit_person = False

        # Zeige die Liste der Personen
        self.update_app(widget)
        self.show_list_persons(widget)


    def confirm_delete_person(self, widget):
        """Bestätigt das Löschen einer Person."""
        if self.tabelle_personen.selection:
            self.main_window.confirm_dialog(
                'Person löschen', 
                'Soll die ausgewählte Person wirklich gelöscht werden?',
                on_result=self.delete_person
            )


    def delete_person(self, widget, result):
        """Löscht eine Person."""
        if self.tabelle_personen.selection and result:
            index = self.index_auswahl(self.tabelle_personen)

            # Prüfe, ob die Person in einer Rechnung verwendet wird
            for rechnung in self.rechnungen:
                if rechnung.person_id == self.personen[index].db_id:
                    self.main_window.error_dialog(
                        'Fehler beim Löschen',
                        'Die Person wird noch in einer aktiven Rechnung verwendet und kann daher nicht gelöscht werden.'
                    )
                    return
            
            # Person wird deaktiviert
            self.personen[index].aktiv = False
            self.personen[index].speichern(self.db)
            del self.personen[index]
            del self.personen_liste[index]

            # Seite mit Liste der Personen anzeigen
            self.update_app(widget)
            self.show_list_persons(widget)


    def create_list_beihilfe(self):
        """Erzeugt die Seite, auf der die Beihilfe-Einreichungen angezeigt werden."""
        self.box_seite_liste_beihilfepakete = toga.Box(style=style_box_column)
        box_seite_liste_beihilfepakete_top = toga.Box(style=style_box_column_beihilfe)
        box_seite_liste_beihilfepakete_top.add(toga.Button('Zurück', on_press=self.zeige_startseite, style=style_button))
        box_seite_liste_beihilfepakete_top.add(toga.Label('Beihilfe-Einreichungen', style=style_label_h1_hell))
        self.box_seite_liste_beihilfepakete.add(box_seite_liste_beihilfepakete_top)

        # Tabelle mit den Beihilfepaketen
        self.tabelle_beihilfepakete = toga.Table(
            headings    = ['Datum', 'Betrag', 'Erstattet'], 
            accessors   = ['datum', 'betrag_euro', 'erhalten_text'],
            data        = self.beihilfepakete_liste,
            style       = style_table,
            on_select   = self.update_app,
            on_activate = self.zeige_info_buchung
        )
        self.box_seite_liste_beihilfepakete.add(self.tabelle_beihilfepakete)

        # Buttons für die Beihilfepakete
        box_seite_liste_beihilfepakete_buttons = toga.Box(style=style_box_row)
        self.seite_liste_beihilfepakete_button_loeschen = toga.Button('Zurücksetzen', on_press=self.confirm_delete_beihilfe, style=style_button, enabled=False)
        box_seite_liste_beihilfepakete_buttons.add(self.seite_liste_beihilfepakete_button_loeschen)
        #self.seite_liste_beihilfepakete_button_bearbeiten = toga.Button('Bearbeiten', on_press=self.show_form_beihilfe_edit, style=style_button, enabled=False)
        #box_seite_liste_beihilfepakete_buttons.add(self.seite_liste_beihilfepakete_button_bearbeiten)
        self.seite_liste_beihilfepakete_button_neu = toga.Button('Neu', on_press=self.show_form_beihilfe_new, style=style_button)
        box_seite_liste_beihilfepakete_buttons.add(self.seite_liste_beihilfepakete_button_neu)
        self.box_seite_liste_beihilfepakete.add(box_seite_liste_beihilfepakete_buttons)


    def create_list_pkv(self):
        """Erzeugt die Seite, auf der die PKV-Einreichungen angezeigt werden."""
        self.box_seite_liste_pkvpakete = toga.Box(style=style_box_column)
        box_seite_liste_pkvpakete_top = toga.Box(style=style_box_column_pkv)
        box_seite_liste_pkvpakete_top.add(toga.Button('Zurück', on_press=self.zeige_startseite, style=style_button))
        box_seite_liste_pkvpakete_top.add(toga.Label('PKV-Einreichungen', style=style_label_h1_hell))
        self.box_seite_liste_pkvpakete.add(box_seite_liste_pkvpakete_top)

        # Tabelle mit den PKV-Einreichungen
        self.tabelle_pkvpakete_container = toga.ScrollContainer(style=style_scroll_container)
        self.tabelle_pkvpakete = toga.Table(
            headings    = ['Datum', 'Betrag', 'Erstattet'], 
            accessors   = ['datum', 'betrag_euro', 'erhalten_text'],
            data        = self.pkvpakete_liste,
            style       = style_table,
            on_select   = self.update_app,
            on_activate = self.zeige_info_buchung
        )
        self.tabelle_pkvpakete_container.content = self.tabelle_pkvpakete
        self.box_seite_liste_pkvpakete.add(self.tabelle_pkvpakete_container)

        # Buttons für die PKV-Einreichungen
        box_seite_liste_pkvpakete_buttons = toga.Box(style=style_box_row)
        self.seite_liste_pkvpakete_button_loeschen = toga.Button('Zurücksetzen', on_press=self.confirm_delete_pkv, style=style_button, enabled=False)
        box_seite_liste_pkvpakete_buttons.add(self.seite_liste_pkvpakete_button_loeschen)
        #self.seite_liste_pkvpakete_button_bearbeiten = toga.Button('Bearbeiten', on_press=self.show_form_pkv_edit, style=style_button, enabled=False)
        #box_seite_liste_pkvpakete_buttons.add(self.seite_liste_pkvpakete_button_bearbeiten)
        self.seite_liste_pkvpakete_button_neu = toga.Button('Neu', on_press=self.show_form_pkv_new, style=style_button)
        box_seite_liste_pkvpakete_buttons.add(self.seite_liste_pkvpakete_button_neu)
        self.box_seite_liste_pkvpakete.add(box_seite_liste_pkvpakete_buttons)


    def show_list_beihilfe(self, widget):
        """Zeigt die Seite mit der Liste der Beihilfepakete."""
        # Zum Setzen des Button Status
        self.update_app(widget)
        self.main_window.content = self.box_seite_liste_beihilfepakete

    
    def show_list_pkv(self, widget):
        """Zeigt die Seite mit der Liste der PKV-Einreichungen."""
        # Zum Setzen des Button Status
        self.update_app(widget)
        self.main_window.content = self.box_seite_liste_pkvpakete

    
    def create_form_beihilfe(self):
        """Erzeugt das Formular zum Erstellen und Bearbeiten einer Beihilfe-Einreichung."""

        # Container
        self.sc_form_beihilfe = toga.ScrollContainer(style=style_scroll_container)
        self.box_form_beihilfe = toga.Box(style=style_box_column)
        self.sc_form_beihilfe.content = self.box_form_beihilfe

        # TopBox
        self.form_beihilfe_topbox = TopBox(
            parent=self.box_form_beihilfe,
            label_text='Neue Beihilfe-Einreichung',
            style_box=style_box_column_beihilfe,
            target_back=self.show_list_beihilfe
        )

        self.form_beihilfe_datum = LabeledDateInput(self.box_form_beihilfe, 'Datum:')

        # Bereich zur Auswahl der zugehörigen Rechnungen
        self.form_beihilfe_bills = toga.Table(
            headings        = ['Info', 'Betrag', 'Beihilfe', 'Bezahlt'],
            accessors       = ['info', 'betrag_euro', 'beihilfesatz_prozent', 'bezahlt_text'],
            data            = self.erzeuge_teilliste_rechnungen(beihilfe=True),
            multiple_select = True,
            on_select       = self.on_select_beihilfe_bills,
            on_activate     = self.zeige_info_buchung,
            style           = style_table_auswahl
        )
        self.box_form_beihilfe.add(self.form_beihilfe_bills)

        self.box_form_beihilfe.add(toga.Divider(style=style_divider))
        self.form_beihilfe_betrag = LabeledFloatInput(self.box_form_beihilfe, 'Betrag in €:', readonly=True)
        self.form_beihilfe_erhalten = LabeledSwitch(self.box_form_beihilfe, 'Erstattet:')

        # BottomBox
        self.form_beihilfe_bottombox = BottomBox(
            parent=self.box_form_beihilfe,
            labels=['Abbrechen', 'Speichern'],
            targets=[self.show_list_beihilfe, self.check_save_beihilfe]
        )


    def create_form_pkv(self):
        """Erzeugt das Formular zum Erstellen und Bearbeiten einer PKV-Einreichung."""

        # Container
        self.sc_form_pkv = toga.ScrollContainer(style=style_scroll_container)
        self.box_form_pkv = toga.Box(style=style_box_column)
        self.sc_form_pkv.content = self.box_form_pkv

        # TopBox
        self.form_pkv_topbox = TopBox(
            parent=self.box_form_pkv,
            label_text='Neue PKV-Einreichung',
            style_box=style_box_column_pkv,
            target_back=self.show_list_pkv
        )

        self.form_pkv_datum = LabeledDateInput(self.box_form_pkv, 'Datum:')

        # Bereich zur Auswahl der zugehörigen Rechnungen
        self.form_pkv_bills = toga.Table(
            headings        = ['Info', 'Betrag', 'Beihilfe', 'Bezahlt'],
            accessors       = ['info', 'betrag_euro', 'beihilfesatz_prozent', 'bezahlt_text'],
            data            = self.erzeuge_teilliste_rechnungen(pkv=True),
            multiple_select = True,
            on_select       = self.on_select_pkv_bills,   
            on_activate     = self.zeige_info_buchung,
            style           = style_table_auswahl
        )
        self.box_form_pkv.add(self.form_pkv_bills)

        self.box_form_pkv.add(toga.Divider(style=style_divider))
        self.form_pkv_betrag = LabeledFloatInput(self.box_form_pkv, 'Betrag in €:', readonly=True)
        self.form_pkv_erhalten = LabeledSwitch(self.box_form_pkv, 'Erstattet:')

        # BottomBox
        self.form_pkv_bottombox = BottomBox(
            parent=self.box_form_pkv,
            labels=['Abbrechen', 'Speichern'],
            targets=[self.show_list_pkv, self.check_save_pkv]
        )


    def on_select_beihilfe_bills(self, widget):
        """Ermittelt die Summe des Beihilfe-Anteils der ausgewählten Rechnungen."""
        summe = 0
        for auswahl_rg in widget.selection:
            for rg in self.rechnungen:
                if auswahl_rg.db_id == rg.db_id:
                    summe += rg.betrag * rg.beihilfesatz / 100
        self.form_beihilfe_betrag.set_value(summe)


    def on_select_pkv_bills(self, widget):
        """Ermittelt die Summe des PKV-Anteils der ausgewählten Rechnungen."""
        summe = 0
        for auswahl_rg in widget.selection:
            for rg in self.rechnungen:
                if auswahl_rg.db_id == rg.db_id:
                    summe += rg.betrag * (100 - rg.beihilfesatz) / 100
        self.form_pkv_betrag.set_value(summe)


    def show_form_beihilfe_new(self, widget):
        """Zeigt die Seite zum Erstellen eines Beihilfepakets."""
        # Setze die Eingabefelder zurück
        self.form_beihilfe_betrag.set_value('')
        self.form_beihilfe_datum.set_value(datetime.now())
        self.form_beihilfe_erhalten.set_value(False)
        self.form_beihilfe_bills.data = self.erzeuge_teilliste_rechnungen(beihilfe=True)

        # Zurücksetzen des Flags und der Überschrift
        self.flag_edit_beihilfe = False
        self.form_beihilfe_topbox.set_label('Neue Beihilfe-Einreichung')

        # Zeige die Seite
        self.main_window.content = self.sc_form_beihilfe


    def show_form_pkv_new(self, widget):
        """Zeigt die Seite zum Erstellen einer PKV-Einreichung."""
        # Setze die Eingabefelder zurück
        self.form_pkv_betrag.set_value('')
        self.form_pkv_datum.set_value(datetime.now())
        self.form_pkv_erhalten.set_value(False)
        self.form_pkv_bills.data = self.erzeuge_teilliste_rechnungen(pkv=True)

        # Zurücksetzen des Flags und der Überschrift
        self.flag_edit_pkv = False
        self.form_pkv_topbox.set_label('Neue PKV-Einreichung')

        # Zeige die Seite
        self.main_window.content = self.sc_form_pkv


    def check_save_beihilfe(self, widget):
        """Prüft, ob die Eingaben für eine neue Beihilfe-Einreichung korrekt sind."""

        nachricht = ''

        # Prüfe das Datum
        if not self.form_beihilfe_datum.is_valid():
            nachricht += 'Bitte gib ein gültiges Datum ein.\n'

        # Prüfe ob Rechnungen ausgewählt wurden
        if not self.form_beihilfe_bills.selection:
            nachricht += 'Es wurde keine Rechnung zum Einreichen ausgewählt.\n'

        if nachricht != '':
            self.main_window.error_dialog('Fehlerhafte Eingabe', nachricht)
        else:
            self.save_beihilfe(widget)


    def check_save_pkv(self, widget):
        """Prüft, ob Rechnungen für die PKV-Einreichungen ausgewählt sind."""
        nachricht = ''

        # Prüfe das Datum
        if not self.form_pkv_datum.is_valid():
            nachricht += 'Bitte gib ein gültiges Datum ein.\n'

        # Prüfe ob Rechnungen ausgewählt wurden
        if not self.form_pkv_bills.selection:
            nachricht += 'Es wurde keine Rechnung zum Einreichen ausgewählt.\n'

        if nachricht != '':
            self.main_window.error_dialog('Fehlerhafte Eingabe', nachricht)
        else:
            self.save_pkv(widget)


    def save_beihilfe(self, widget):
        """Erstellt und speichert eine neue Beihilfe-Einreichung oder ändert eine bestehende."""

        if not self.flag_edit_beihilfe:
            # Erstelle ein neues Beihilfepaket
            neues_beihilfepaket = BeihilfePaket()
            neues_beihilfepaket.datum = self.form_beihilfe_datum.get_value()
            neues_beihilfepaket.betrag = self.form_beihilfe_betrag.get_value()
            neues_beihilfepaket.erhalten = self.form_beihilfe_erhalten.get_value()

            # Speichere das Beihilfepaket in der Datenbank
            neues_beihilfepaket.neu(self.db)

            # Füge das Beihilfepaket der Liste hinzu
            self.beihilfepakete.append(neues_beihilfepaket)
            self.beihilfepakete_liste_anfuegen(neues_beihilfepaket)

            # Aktualisiere verknüpfte Rechnungen
            for auswahl_rg in self.form_beihilfe_bills.selection:
                for rg in self.rechnungen:
                    if auswahl_rg.db_id == rg.db_id:
                        rg.beihilfe_id = neues_beihilfepaket.db_id
                        rg.speichern(self.db)

        else:
            # Bearbeite das Beihilfepaket
            self.beihilfepakete[self.edit_beihilfe_id].datum = self.form_beihilfe_datum.get_value()
            self.beihilfepakete[self.edit_beihilfe_id].betrag = self.form_beihilfe_betrag.get_value()
            self.beihilfepakete[self.edit_beihilfe_id].erhalten = self.form_beihilfe_erhalten.get_value()

            # Speichere das Beihilfepaket in der Datenbank
            self.beihilfepakete[self.edit_beihilfe_id].speichern(self.db)

            # Aktualisiere die Liste der Beihilfepakete
            self.beihilfepakete_liste_aendern(self.beihilfepakete[self.edit_beihilfe_id], self.edit_beihilfe_id)

            # Flage zurücksetzen
            self.flag_edit_beihilfe = False

            # Aktualisiere verknüpfte Rechnungen
            for auswahl_rg in self.form_beihilfe_bills.selection:
                for rg in self.rechnungen:
                    if auswahl_rg.db_id == rg.db_id:
                        rg.beihilfe_id = self.beihilfepakete[self.edit_beihilfe_id].db_id
                        rg.speichern(self.db)

        # Rechnungen aktualisieren
        self.rechnungen_liste_aktualisieren()

        # Wechsel zur Liste der Beihilfepakete
        self.update_app(widget)
        self.zeige_startseite(widget)


    def save_pkv(self, widget):
        """Erstellt und speichert eine neue PKV-Einreichung oder ändert eine bestehende."""

        if not self.flag_edit_pkv:
            # Erstelle ein neues PKV-Paket
            neues_pkvpaket = PKVPaket()
            neues_pkvpaket.datum = self.form_pkv_datum.get_value()
            neues_pkvpaket.betrag = self.form_pkv_betrag.get_value()
            neues_pkvpaket.erhalten = self.form_pkv_erhalten.get_value()

            # Speichere das PKV-Einreichung in der Datenbank
            neues_pkvpaket.neu(self.db)

            # Füge das PKV-Einreichung der Liste hinzu
            self.pkvpakete.append(neues_pkvpaket)
            self.pkvpakete_liste_anfuegen(neues_pkvpaket)

            # Aktualisiere verknüpfte Rechnungen
            for auswahl_rg in self.form_pkv_bills.selection:
                for rg in self.rechnungen:
                    if auswahl_rg.db_id == rg.db_id:
                        rg.pkv_id = neues_pkvpaket.db_id
                        rg.speichern(self.db)

        else:
            # Bearbeite das PKV-Paket
            self.pkvpakete[self.edit_pkv_id].datum = self.form_pkv_datum.get_value()
            self.pkvpakete[self.edit_pkv_id].betrag = self.form_pkv_betrag.get_value()
            self.pkvpakete[self.edit_pkv_id].erhalten = self.form_pkv_erhalten.get_value()

            # Speichere das PKV-Einreichung in der Datenbank
            self.pkvpakete[self.edit_pkv_id].speichern(self.db)

            # Aktualisiere die Liste der PKV-Einreichungen
            self.pkvpakete_liste_aendern(self.pkvpakete[self.edit_pkv_id], self.edit_pkv_id)

            # Flage zurücksetzen
            self.flag_edit_pkv = False

            # Aktualisiere verknüpfte Rechnungen
            for auswahl_rg in self.form_pkv_bills.selection:
                for rg in self.rechnungen:
                    if auswahl_rg.db_id == rg.db_id:
                        rg.pkv_id = self.pkvpakete[self.edit_pkv_id].db_id
                        rg.speichern(self.db)

        # Rechnungen aktualisieren
        self.rechnungen_liste_aktualisieren()

        # Wechsel zur Liste der PKV-Einreichungen
        self.update_app(widget)
        self.zeige_startseite(widget)


    def confirm_delete_beihilfe(self, widget):
        """Bestätigt das Löschen einer Beihilfe-Einreichung."""
        if self.tabelle_beihilfepakete.selection:
            self.main_window.confirm_dialog(
                'Beihilfe-Einreichung zurücksetzen', 
                'Soll die ausgewählte Beihilfe-Einreichung wirklich zurückgesetzt werden? Die zugehörigen Rechnungen müssen dann erneut eingereicht werden.',
                on_result=self.delete_beihilfe
            )


    def confirm_delete_pkv(self, widget):
        """Bestätigt das Löschen einer PKV-Einreichung."""
        if self.tabelle_pkvpakete.selection:
            self.main_window.confirm_dialog(
                'PKV-Einreichung zurücksetzen', 
                'Soll die ausgewählte PKV-Einreichung wirklich zurückgesetzt werden? Die zugehörigen Rechnungen müssen dann erneut eingereicht werden.',
                on_result=self.delete_pkv
            )


    def delete_beihilfe(self, widget, result):
        """Löscht eine Beihilfe-Einreichung."""
        if self.tabelle_beihilfepakete.selection and result:
            index = self.index_auswahl(self.tabelle_beihilfepakete)
            self.beihilfepakete[index].loeschen(self.db)
            del self.beihilfepakete[index]
            del self.beihilfepakete_liste[index]
            self.rechnungen_aktualisieren()
            
            # Anzeigen aktualisieren
            self.update_app(widget)


    def delete_pkv(self, widget, result):
        """Löscht eine PKV-Einreichung."""
        if self.tabelle_pkvpakete.selection and result:
            index = self.index_auswahl(self.tabelle_pkvpakete)
            self.pkvpakete[index].loeschen(self.db)
            del self.pkvpakete[index]
            del self.pkvpakete_liste[index]
            self.rechnungen_aktualisieren()
            
            # Anzeigen aktualisieren
            self.update_app(widget)


    def erzeuge_teilliste_rechnungen(self, beihilfe=False, pkv=False, beihilfe_id=None, pkv_id=None):
        """Erzeugt die Liste der eingereichten Rechnungen für Beihilfe oder PKV."""

        data = ListSource(accessors=[
            'db_id', 
            'betrag', 
            'betrag_euro',
            'rechnungsdatum', 
            'einrichtung_id',
            'einrichtung_name',
            'notiz', 
            'person_id',
            'person_name',
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

        if self.rechnungen_liste is None:
            return data

        for rechnung in self.rechnungen_liste:
            if (beihilfe and (rechnung.beihilfe_id is None or rechnung.beihilfe_id == beihilfe_id)) or (pkv and (rechnung.pkv_id is None or rechnung.pkv_id == pkv_id)):
                data.append({
                'db_id': rechnung.db_id,
                'betrag': rechnung.betrag,
                'betrag_euro': '{:.2f} €'.format(rechnung.betrag).replace('.', ','),
                'rechnungsdatum': rechnung.rechnungsdatum,
                'einrichtung_id': rechnung.einrichtung_id,
                'einrichtung_name': self.einrichtung_name(rechnung.einrichtung_id),
                'notiz': rechnung.notiz,
                'person_id': rechnung.person_id,
                'person_name': self.person_name(rechnung.person_id),
                'info': (self.person_name(rechnung.person_id) + ', ' if self.person_name(rechnung.person_id) else '') + self.einrichtung_name(rechnung.einrichtung_id),
                'beihilfesatz': rechnung.beihilfesatz,
                'beihilfesatz_prozent': '{:.0f} %'.format(rechnung.beihilfesatz),
                'buchungsdatum': rechnung.buchungsdatum,
                'bezahlt': rechnung.bezahlt,
                'bezahlt_text': 'Ja' if rechnung.bezahlt else 'Nein',
                'beihilfe_id': rechnung.beihilfe_id,
                'beihilfe_eingereicht': 'Ja' if rechnung.beihilfe_id else 'Nein',
                'pkv_id': rechnung.pkv_id,
                'pkv_eingereicht': 'Ja' if rechnung.pkv_id else 'Nein'
            })

        return data


    def einrichtung_name(self, einrichtung_id):
        """Ermittelt den Namen einer Einrichtung anhand ihrer Id."""
        for einrichtung in self.einrichtungen:
            if einrichtung.db_id == einrichtung_id:
                return einrichtung.name
        return ''
    

    def person_name(self, person_id):
        """Ermittelt den Namen einer Person anhand ihrer Id."""
        for person in self.personen:
            if person.db_id == person_id:
                return person.name
        return ''
    

    def indizes_archivierbare_buchungen(self):
        """Ermittelt die Indizes der archivierbaren Rechnungen, Beihilfepakete und PKVpakete und gibt sie zurück."""
        indizes = {
            'Rechnung' : [],
            'Beihilfe' : set(),
            'PKV' : set()
        }

        # Create dictionaries for quick lookup of beihilfepakete and pkvpakete by db_id
        beihilfepakete_dict = {paket.db_id: paket for paket in self.beihilfepakete}
        pkvpakete_dict = {paket.db_id: paket for paket in self.pkvpakete}

        for i, rechnung in enumerate(self.rechnungen):
            if rechnung.bezahlt and rechnung.beihilfe_id and rechnung.pkv_id:
                beihilfepaket = beihilfepakete_dict.get(rechnung.beihilfe_id)
                pkvpaket = pkvpakete_dict.get(rechnung.pkv_id)
                if beihilfepaket and beihilfepaket.erhalten and pkvpaket and pkvpaket.erhalten:
                    # Check if all other rechnungen associated with the beihilfepaket and pkvpaket are paid
                    other_rechnungen = [ar for ar in self.rechnungen if ar.beihilfe_id == beihilfepaket.db_id or ar.pkv_id == pkvpaket.db_id]
                    if all(ar.bezahlt for ar in other_rechnungen):
                        indizes['Rechnung'].append(i)
                        indizes['Beihilfe'].add(self.beihilfepakete.index(beihilfepaket))
                        indizes['PKV'].add(self.pkvpakete.index(pkvpaket))

        # Convert sets back to lists
        indizes['Beihilfe'] = list(indizes['Beihilfe'])
        indizes['PKV'] = list(indizes['PKV'])

        # sort the lists in reverse order
        indizes['Rechnung'].sort(reverse=True)
        indizes['Beihilfe'].sort(reverse=True)
        indizes['PKV'].sort(reverse=True)

        return indizes
            

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

            for i in indizes['Rechnung']:
                self.rechnungen[i].aktiv = 0
                self.rechnungen[i].speichern(self.db)
                del self.rechnungen[i]
                del self.rechnungen_liste[i]

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
            
            self.update_app(widget)
            self.zeige_startseite(widget)
            

    def bestaetige_bezahlung(self, widget):
        """Bestätigt die Bezahlung einer Rechnung."""
        if self.tabelle_offene_buchungen.selection:
            match self.tabelle_offene_buchungen.selection.typ:
                case 'Rechnung':
                    self.main_window.confirm_dialog(
                        'Rechnung bezahlt?', 
                        'Soll die ausgewählte Rechnung wirklich als bezahlt markiert werden?',
                        on_result=self.rechnung_bezahlen
                    )
                case 'Beihilfe':
                    self.main_window.confirm_dialog(
                        'Beihilfe-Einreichung erstattet?', 
                        'Soll die ausgewählte Beihilfe wirklich als erstattet markiert werden?',
                        on_result=self.beihilfe_erhalten
                    )
                case 'PKV':
                    self.main_window.confirm_dialog(
                        'PKV-Einreichung erstattet?', 
                        'Soll die ausgewählte PKV-Einreichung wirklich als erstattet markiert werden?',
                        on_result=self.pkv_erhalten
                    )
    

    def rechnung_bezahlen(self, widget, result):
        """Markiert eine Rechnung als bezahlt."""
        if self.tabelle_offene_buchungen.selection and result:
            # Setze das Flag bezahlt auf True bei der Rechnung mit der db_id aus der Tabelle
            for rechnung in self.rechnungen:
                if rechnung.db_id == self.tabelle_offene_buchungen.selection.db_id:
                    rechnung.bezahlt = True
                    rechnung.speichern(self.db)
                    break
            
            # Aktualisiere die Liste der Rechnungen
            self.rechnungen_liste_aktualisieren()

            # Aktualisiere die Liste der offenen Buchungen
            self.update_app(widget)
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
            self.update_app(widget)
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
            self.update_app(widget)
            self.zeige_startseite(widget)
    

    def erzeuge_liste_offene_buchungen(self):
        """Erzeugt die Liste der offenen Buchungen für die Tabelle auf der Startseite."""
        offene_buchungen_liste = ListSource(accessors=[
            'db_id',                        # Datenbank-Id des jeweiligen Elements
            'typ',                          # Typ des Elements (Rechnung, Beihilfe, PKV)
            'betrag_euro',                  # Betrag der Buchung in Euro
            'datum',                        # Datum der Buchung (Plandatum der Rechnung oder Einreichungsdatum der Beihilfe/PKV)
            'info'                          # Info-Text der Buchung
        ])

        for rechnung in self.rechnungen_liste:
            if not rechnung.bezahlt:
                offene_buchungen_liste.append({
                    'db_id': rechnung.db_id,
                    'typ': 'Rechnung',
                    'betrag_euro': '-{:.2f} €'.format(rechnung.betrag).replace('.', ','),
                    'datum': rechnung.buchungsdatum,
                    'info': rechnung.info
                })
    
        for beihilfepaket in self.beihilfepakete:
            if not beihilfepaket.erhalten:
                offene_buchungen_liste.append({
                    'db_id': beihilfepaket.db_id,
                    'typ': 'Beihilfe',
                    'betrag_euro': '+{:.2f} €'.format(beihilfepaket.betrag).replace('.', ','),
                    'datum': beihilfepaket.datum,
                    'info': 'Beihilfe-Einreichung'
                })

        for pkvpaket in self.pkvpakete:
            if not pkvpaket.erhalten:
                offene_buchungen_liste.append({
                    'db_id': pkvpaket.db_id,
                    'typ': 'PKV',
                    'betrag_euro': '+{:.2f} €'.format(pkvpaket.betrag).replace('.', ','),
                    'datum': pkvpaket.datum,
                    'info': 'PKV-Einreichung'
                })

        return offene_buchungen_liste
    

    def bearbeite_offene_buchung(self, widget):
        """Öffnet die Seite zum Bearbeiten einer offenen Buchung."""
        if self.tabelle_offene_buchungen.selection:
            match self.tabelle_offene_buchungen.selection.typ:
                case 'Rechnung':
                    self.show_form_bill_edit(widget)
                # case 'Beihilfe':
                #     self.show_form_beihilfe_edit(widget)
                # case 'PKV':
                #     self.show_form_pkv_edit(widget)


    def rechnungen_liste_erzeugen(self):
        """Erzeugt die Liste für die Rechnungen."""
        self.rechnungen_liste = ListSource(accessors=[
            'db_id', 
            'betrag', 
            'betrag_euro',
            'rechnungsdatum', 
            'einrichtung_id', 
            'notiz', 
            'einrichtung_name', 
            'info', 
            'person_id',
            'person_name',
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

        for rechnung in self.rechnungen:            
            self.rechnungen_liste_anfuegen(rechnung)


    def einrichtungen_liste_erzeugen(self):
        """Erzeugt die Liste für die Einrichtungen."""
        self.einrichtungen_liste = ListSource(accessors=[
            'db_id',
            'name',
            'strasse',
            'plz',
            'ort',
            'plz_ort',
            'telefon',
            'email',
            'webseite',
            'notiz'
        ])

        for einrichtung in self.einrichtungen:            
            self.einrichtungen_liste_anfuegen(einrichtung)


    def personen_liste_erzeugen(self): 
        """Erzeugt die Liste für die Personen."""
        self.personen_liste = ListSource(accessors=[
            'db_id',
            'name',
            'beihilfesatz',
            'beihilfesatz_prozent',
        ])

        for person in self.personen:            
            self.personen_liste_anfuegen(person)


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


    def rechnungen_liste_anfuegen(self, rechnung):
        """Fügt der Liste der Rechnungen eine neue Rechnung hinzu."""
        self.rechnungen_liste.append({
                'db_id': rechnung.db_id,
                'betrag': rechnung.betrag,
                'betrag_euro': '{:.2f} €'.format(rechnung.betrag).replace('.', ','),
                'rechnungsdatum': rechnung.rechnungsdatum,
                'einrichtung_id': rechnung.einrichtung_id,
                'notiz': rechnung.notiz,
                'person_id': rechnung.person_id,
                'person_name': self.person_name(rechnung.person_id),
                'einrichtung_name': self.einrichtung_name(rechnung.einrichtung_id),
                'info': (self.person_name(rechnung.person_id) + ', ' if self.person_name(rechnung.person_id) else '') + self.einrichtung_name(rechnung.einrichtung_id),
                'beihilfesatz': rechnung.beihilfesatz,
                'beihilfesatz_prozent': '{:.0f} %'.format(rechnung.beihilfesatz),
                'buchungsdatum': rechnung.buchungsdatum,
                'bezahlt': rechnung.bezahlt,
                'bezahlt_text': 'Ja' if rechnung.bezahlt else 'Nein',
                'beihilfe_id': rechnung.beihilfe_id,
                'beihilfe_eingereicht': 'Ja' if rechnung.beihilfe_id else 'Nein',
                'pkv_id': rechnung.pkv_id,
                'pkv_eingereicht': 'Ja' if rechnung.pkv_id else 'Nein'
            })
        

    def rechnungen_aktualisieren(self):
        """Aktualisiert die referenzierten Werte in den Rechnungen und speichert sie in der Datenbank."""

        for rechnung in self.rechnungen:

            # Aktualisiere die Beihilfe
            if rechnung.beihilfe_id:
                # Überprüfe ob die Beihilfe noch existiert
                beihilfepaket_vorhanden = False
                for beihilfepaket in self.beihilfepakete:
                    if beihilfepaket.db_id == rechnung.beihilfe_id:
                        beihilfepaket_vorhanden = True
                        break
                
                # Wenn die Beihilfe nicht mehr existiert, setze die Beihilfe zurück
                if not beihilfepaket_vorhanden:
                    rechnung.beihilfe_id = None

            # Aktualisiere die PKV
            if rechnung.pkv_id:
                # Überprüfe ob die PKV noch existiert
                pkvpaket_vorhanden = False
                for pkvpaket in self.pkvpakete:
                    if pkvpaket.db_id == rechnung.pkv_id:
                        pkvpaket_vorhanden = True
                        break
                
                # Wenn die PKV nicht mehr existiert, setze die PKV zurück
                if not pkvpaket_vorhanden:
                    rechnung.pkv_id = None

            # Aktualisiere die Einrichtung
            if rechnung.einrichtung_id:
                # Überprüfe ob die Einrichtung noch existiert
                einrichtung_vorhanden = False
                for einrichtung in self.einrichtungen:
                    if einrichtung.db_id == rechnung.einrichtung_id:
                        einrichtung_vorhanden = True
                        break
                
                # Wenn die Einrichtung nicht mehr existiert, setze die Einrichtung zurück
                if not einrichtung_vorhanden:
                    rechnung.einrichtung_id = None

            # Aktualisiere die Person
            if rechnung.person_id:
                # Überprüfe ob die Person noch existiert
                person_vorhanden = False
                for person in self.personen:
                    if person.db_id == rechnung.person_id:
                        person_vorhanden = True
                        break
                
                # Wenn die Person nicht mehr existiert, setze die Person zurück
                if not person_vorhanden:
                    rechnung.person_id = None
            
            # Aktualisierte Rechnung speichern
            rechnung.speichern(self.db)

        # Aktualisiere die Liste der Rechnungen
        self.rechnungen_liste_aktualisieren()


    def rechnungen_liste_aktualisieren(self):
        """Aktualisiert die referenzierten Werte in der Liste der Rechnungen."""
        for rg_id in range(len(self.rechnungen_liste)):
            self.rechnungen_liste_aendern(self.rechnungen[rg_id], rg_id)

    
    def beihilfepakete_liste_aktualisieren(self):
        """Aktualisiert die Liste der Beihilfepakete."""
        for beihilfepaket_id in range(len(self.beihilfepakete_liste)):
            self.beihilfepakete_liste_aendern(self.beihilfepakete[beihilfepaket_id], beihilfepaket_id)

    
    def pkvpakete_liste_aktualisieren(self):
        """Aktualisiert die Liste der PKV-Pakete."""
        for pkvpaket_id in range(len(self.pkvpakete_liste)):
            self.pkvpakete_liste_aendern(self.pkvpakete[pkvpaket_id], pkvpaket_id)
        

    def einrichtungen_liste_anfuegen(self, einrichtung):
        """Fügt der Liste der Einrichtungen eine neue Einrichtung hinzu."""
        self.einrichtungen_liste.append({
                'db_id': einrichtung.db_id,
                'name': einrichtung.name or '',
                'strasse': einrichtung.strasse or '',
                'plz': einrichtung.plz or '',
                'ort': einrichtung.ort or '',
                'plz_ort': (einrichtung.plz or '') + (' ' if einrichtung.plz else '') + (einrichtung.ort or ''),
                'telefon': einrichtung.telefon or '',
                'email': einrichtung.email or '',
                'webseite': einrichtung.webseite or '',
                'notiz': einrichtung.notiz or ''
            })
        

    def personen_liste_anfuegen(self, person):
        """Fügt der Liste der Personen eine neue Person hinzu."""
        self.personen_liste.append({
                'db_id': person.db_id,
                'name': person.name or '',
                'beihilfesatz': person.beihilfesatz or '',
                'beihilfesatz_prozent': '{:.0f} %'.format(person.beihilfesatz) if person.beihilfesatz else '0 %'
            })


    def beihilfepakete_liste_anfuegen(self, beihilfepaket):
        """Fügt der Liste der Beihilfepakete ein neues Beihilfepaket hinzu."""
        self.beihilfepakete_liste.append({
                'db_id': beihilfepaket.db_id,
                'betrag': beihilfepaket.betrag,
                'betrag_euro': '{:.2f} €'.format(beihilfepaket.betrag).replace('.', ','),
                'datum': beihilfepaket.datum,
                'erhalten': beihilfepaket.erhalten,
                'erhalten_text': 'Ja' if beihilfepaket.erhalten else 'Nein'
            })
        

    def pkvpakete_liste_anfuegen(self, pkvpaket):
        """Fügt der Liste der PKV-Pakete ein neues PKV-Paket hinzu."""
        self.pkvpakete_liste.append({
                'db_id': pkvpaket.db_id,
                'betrag': pkvpaket.betrag,
                'betrag_euro': '{:.2f} €'.format(pkvpaket.betrag).replace('.', ','),
                'datum': pkvpaket.datum,
                'erhalten': pkvpaket.erhalten,
                'erhalten_text': 'Ja' if pkvpaket.erhalten else 'Nein'
            })


    def rechnungen_liste_aendern(self, rechnung, rg_id):
        """Ändert ein Element der Liste der Rechnungen."""
        self.rechnungen_liste[rg_id] = {
                'db_id': rechnung.db_id,
                'betrag': rechnung.betrag,
                'betrag_euro': '{:.2f} €'.format(rechnung.betrag).replace('.', ','),
                'rechnungsdatum': rechnung.rechnungsdatum,
                'einrichtung_id': rechnung.einrichtung_id,
                'notiz': rechnung.notiz,
                'person_id': rechnung.person_id,
                'person_name': self.person_name(rechnung.person_id),
                'einrichtung_name': self.einrichtung_name(rechnung.einrichtung_id),
                'info': (self.person_name(rechnung.person_id) + ', ' if self.person_name(rechnung.person_id) else '') + self.einrichtung_name(rechnung.einrichtung_id),
                'beihilfesatz': rechnung.beihilfesatz,
                'beihilfesatz_prozent': '{:.0f} %'.format(rechnung.beihilfesatz),
                'buchungsdatum': rechnung.buchungsdatum,
                'bezahlt': rechnung.bezahlt,
                'bezahlt_text': 'Ja' if rechnung.bezahlt else 'Nein',
                'beihilfe_id': rechnung.beihilfe_id,
                'beihilfe_eingereicht': 'Ja' if rechnung.beihilfe_id else 'Nein',
                'pkv_id': rechnung.pkv_id,
                'pkv_eingereicht': 'Ja' if rechnung.pkv_id else 'Nein'
            }
        

    def einrichtungen_liste_aendern(self, einrichtung, einrichtung_id):
        """Ändert ein Element der Liste der Einrichtungen."""
        self.einrichtungen_liste[einrichtung_id] = {
                'db_id': einrichtung.db_id,
                'name': einrichtung.name or '',
                'strasse': einrichtung.strasse or '',
                'plz': einrichtung.plz or '',
                'ort': einrichtung.ort or '',
                'plz_ort': (einrichtung.plz or '') + (' ' if einrichtung.plz else '') + (einrichtung.ort or ''),
                'telefon': einrichtung.telefon or '',
                'email': einrichtung.email or '',
                'webseite': einrichtung.webseite or '',
                'notiz': einrichtung.notiz or ''
            }
        
        # Rechnungen aktualisieren
        self.rechnungen_liste_aktualisieren()


    def personen_liste_aendern(self, person, person_id):    
        """Ändert ein Element der Liste der Personen."""
        self.personen_liste[person_id] = {
                'db_id': person.db_id,
                'name': person.name or '',
                'beihilfesatz': person.beihilfesatz or None,
                'beihilfesatz_prozent': '{:.0f} %'.format(person.beihilfesatz) if person.beihilfesatz else '0 %'
            }

    
    def beihilfepakete_liste_aendern(self, beihilfepaket, beihilfepaket_id):
        """Ändert ein Element der Liste der Beihilfepakete."""
        self.beihilfepakete_liste[beihilfepaket_id] = {
                'db_id': beihilfepaket.db_id,
                'betrag': beihilfepaket.betrag,
                'betrag_euro': '{:.2f} €'.format(beihilfepaket.betrag).replace('.', ','),
                'datum': beihilfepaket.datum,
                'erhalten': beihilfepaket.erhalten,
                'erhalten_text': 'Ja' if beihilfepaket.erhalten else 'Nein'
            }
        

    def pkvpakete_liste_aendern(self, pkvpaket, pkvpaket_id):
        """Ändert ein Element der Liste der PKV-Pakete."""
        self.pkvpakete_liste[pkvpaket_id] = {
                'db_id': pkvpaket.db_id,
                'betrag': pkvpaket.betrag,
                'betrag_euro': '{:.2f} €'.format(pkvpaket.betrag).replace('.', ','),
                'datum': pkvpaket.datum,
                'erhalten': pkvpaket.erhalten,
                'erhalten_text': 'Ja' if pkvpaket.erhalten else 'Nein'
            }


    def startup(self):
        """Laden der Daten, Erzeugen der GUI-Elemente und des Hauptfensters."""

        # Erzeuge die Menüleiste
        gruppe_rechnungen = toga.Group('Rechnungen', order = 1)

        self.cmd_rechnungen_anzeigen = toga.Command(
            self.show_list_bills,
            'Rechnungen anzeigen',
            tooltip = 'Zeigt die Liste der Rechnungen an.',
            group = gruppe_rechnungen,
            order = 10,
            enabled=True
        )

        self.cmd_rechnungen_neu = toga.Command(
            self.show_form_bill_new,
            'Neue Rechnung',
            tooltip = 'Erstellt eine neue Rechnung.',
            group = gruppe_rechnungen,
            order = 20,
            enabled=True
        )

        gruppe_beihilfe = toga.Group('Beihilfe', order = 2)

        self.cmd_beihilfepakete_anzeigen = toga.Command(
            self.show_list_beihilfe,
            'Beihilfe anzeigen',
            tooltip = 'Zeigt die Liste der Beihilfe-Einreichungen an.',
            group = gruppe_beihilfe,
            section = 0,
            order = 10,
            enabled=True
        )

        self.cmd_beihilfepakete_neu = toga.Command(
            self.show_form_beihilfe_new,
            'Neue Beihilfe',
            tooltip = 'Erstellt eine neue Beihilfe-Einreichung.',
            group = gruppe_beihilfe,
            section = 0,
            order = 20,
            enabled=False
        )

        gruppe_pkv = toga.Group('PKV', order = 3)

        self.cmd_pkvpakete_anzeigen = toga.Command(
            self.show_list_pkv,
            'PKV anzeigen',
            tooltip = 'Zeigt die Liste der PKV-Einreichungen an.',
            group = gruppe_pkv,
            section = 1,
            order = 30,
            enabled=True
        )

        self.cmd_pkvpakete_neu = toga.Command(
            self.show_form_pkv_new,
            'Neue PKV',
            tooltip = 'Erstellt eine neue PKV-Einreichung.',
            group = gruppe_pkv,
            section = 1,
            order = 40,
            enabled=False
        )

        gruppe_personen = toga.Group('Personen', order = 4)

        self.cmd_personen_anzeigen = toga.Command(
            self.show_list_persons,
            'Personen anzeigen',
            tooltip = 'Zeigt die Liste der Personen an.',
            group = gruppe_personen,
            section = 0,
            order = 10,
            enabled=True
        )

        self.cmd_personen_neu = toga.Command(
            self.show_form_persons_new,
            'Neue Person',
            tooltip = 'Erstellt eine neue Person.',
            group = gruppe_personen,
            section = 0,
            order = 20,
            enabled=True
        )

        gruppe_einrichtungen = toga.Group('Einrichtungen', order = 5)

        self.cmd_einrichtungen_anzeigen = toga.Command(
            self.show_list_institutions,
            'Einrichtungen anzeigen',
            tooltip = 'Zeigt die Liste der Einrichtungen an.',
            group = gruppe_einrichtungen,
            section = 0,
            order = 10,
            enabled=True
        )

        self.cmd_einrichtungen_neu = toga.Command(
            self.show_form_institution_new,
            'Neue Einrichtung',
            tooltip = 'Erstellt eine neue Einrichtung.',
            group = gruppe_einrichtungen,
            section = 0,
            order = 20,
            enabled=True
        )

        gruppe_tools = toga.Group('Tools', order = 6)

        self.cmd_archivieren = toga.Command(
            self.archivieren_bestaetigen,
            'Archivieren',
            tooltip = 'Archiviere alle bezahlten und erhaltenen Buchungen.',
            group = gruppe_tools,
            order = 10,
            enabled=False
        )

        self.cmd_datenschutz = toga.Command(
            self.zeige_webview,
            'Datenschutz',
            tooltip = 'Öffne die Datenschutzerklärung.',
            order = 7,
            enabled=True
        )

        # Datenbank initialisieren
        self.db = Datenbank()

        # Lade alle Daten aus der Datenbank
        self.rechnungen = self.db.lade_rechnungen()
        self.einrichtungen = self.db.lade_einrichtungen()
        self.beihilfepakete = self.db.lade_beihilfepakete()
        self.pkvpakete = self.db.lade_pkvpakete()
        self.personen = self.db.lade_personen()

        # Erzeuge die ListSources für die GUI
        self.rechnungen_liste_erzeugen()
        self.einrichtungen_liste_erzeugen()
        self.beihilfepakete_liste_erzeugen()
        self.pkvpakete_liste_erzeugen()
        self.personen_liste_erzeugen()

        # Erzeuge alle GUI-Elemente
        self.erzeuge_startseite()
        self.create_list_bills()
        self.create_form_bill()
        self.create_list_institutions()
        self.create_form_institution()
        self.create_info_institution()
        self.create_list_beihilfe()
        self.create_form_beihilfe()
        self.create_list_pkv()
        self.create_form_pkv()
        self.create_list_persons()
        self.create_form_person()
        self.erzeuge_webview()

        # Erstelle die Menüleiste
        self.commands.add(self.cmd_rechnungen_anzeigen)
        self.commands.add(self.cmd_rechnungen_neu)
        self.commands.add(self.cmd_beihilfepakete_anzeigen)
        self.commands.add(self.cmd_beihilfepakete_neu)
        self.commands.add(self.cmd_pkvpakete_anzeigen)
        self.commands.add(self.cmd_pkvpakete_neu)
        self.commands.add(self.cmd_personen_anzeigen)
        self.commands.add(self.cmd_personen_neu)
        self.commands.add(self.cmd_einrichtungen_anzeigen)
        self.commands.add(self.cmd_einrichtungen_neu)
        self.commands.add(self.cmd_archivieren)
        self.commands.add(self.cmd_datenschutz)

        # Erstelle das Hauptfenster
        self.main_window = toga.MainWindow(title=self.formal_name)      

        # Zeige die Startseite
        self.update_app(None)
        self.zeige_startseite(None)
        self.main_window.show()
        

def main():
    """Hauptschleife der Anwendung"""
    return Kontolupe()