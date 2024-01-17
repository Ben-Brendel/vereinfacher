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
        self.label_start_summe.text = 'Offener Betrag: {:.2f} €'.format(self.daten.get_open_sum()).replace('.', ',')

        # Button zum Markieren von Buchungen als bezahlt/erhalten aktivieren oder deaktivieren,
        self.startseite_button_erledigt.enabled = False
        self.startseite_button_bearbeiten.enabled = False

        # Anzeige und Button der offenen Rechnungen aktualisieren
        anzahl = self.daten.get_number_rechnungen_not_paid()
        match anzahl:
            case 0:
                self.label_start_rechnungen_offen.text = 'Keine offenen Rechnungen.'
            case 1:
                self.label_start_rechnungen_offen.text = '1 Rechnung noch nicht bezahlt.'
            case _:
                self.label_start_rechnungen_offen.text = '{} Rechnungen noch nicht bezahlt.'.format(anzahl)

        # Anzeige und Button der offenen Beihilfe-Einreichungen aktualisieren
        anzahl = self.daten.get_number_rechnungen_not_submitted_beihilfe()
        match anzahl:
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
                self.label_start_beihilfe_offen.text = '{} Rechnungen noch nicht eingereicht.'.format(anzahl)

        # Anzeige und Button der offenen PKV-Einreichungen aktualisieren
        anzahl = self.daten.get_number_rechnungen_not_submitted_pkv()
        match anzahl:
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
                self.label_start_pkv_offen.text = '{} Rechnungen noch nicht eingereicht.'.format(anzahl)

        # Anzeige und Button der archivierbaren Items aktualisieren
        anzahl = self.daten.get_number_archivables()
        match anzahl:
            case 0:
                self.button_start_archiv.enabled = False
                self.cmd_archivieren.enabled = False
                self.button_start_archiv.text = 'Keine archivierbaren Buchungen'
            case 1:
                self.button_start_archiv.enabled = True
                self.cmd_archivieren.enabled = True
                self.button_start_archiv.text = '1 Buchung archivieren'
            case _:
                self.button_start_archiv.enabled = True
                self.cmd_archivieren.enabled = True
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
    

    def geh_zurueck(self, widget):
        """Ermittelt das Ziel der Zurück-Funktion und ruft die entsprechende Seite auf."""
        match self.zurueck:
            case 'startseite':
                self.show_mainpage(widget)
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
                self.show_mainpage(widget)


    def create_webview(self):
        """Erzeugt eine WebView zur Anzeige von Webseiten."""
        self.box_webview = toga.Box(style=style_box_column)
        box_webview_top = toga.Box(style=style_box_column_dunkel)
        box_webview_top.add(toga.Button('Zurück', style=style_button, on_press=self.geh_zurueck))
        self.box_webview.add(box_webview_top)
        self.webview = toga.WebView(style=style_webview)
        self.box_webview.add(self.webview)


    def show_webview(self, widget):
        """Zeigt die WebView zur Anzeige von Webseiten."""
        match widget:
            case self.link_info_einrichtung_webseite:
                self.webview.url = self.daten.list_einrichtungen[self.edit_institution_id].webseite
                self.zurueck = 'info_einrichtung'
            case self.cmd_datenschutz:
                self.webview.url = 'https://kontolupe.biberwerk.net/kontolupe-datenschutz.html'
                self.zurueck = 'startseite'

        self.main_window.content = self.box_webview


    def create_mainpage(self):
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
            data        = self.daten.list_open_bookings,    
            style       = style_table_offene_buchungen,
            on_activate = self.show_info_dialog_booking,
            on_select   = self.update_app
        )
        self.box_startseite_tabelle_offene_buchungen.add(self.tabelle_offene_buchungen)

        # Button zur Markierung offener Buchungen als bezahlt/erhalten 
        self.box_startseite_tabelle_buttons = toga.Box(style=style_box_row)
        self.startseite_button_erledigt = toga.Button('Bezahlt/Erstattet', on_press=self.bestaetige_bezahlung, style=style_button, enabled=False)
        self.startseite_button_bearbeiten = toga.Button('Bearbeiten', on_press=self.edit_open_booking, style=style_button, enabled=False)
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


    def show_mainpage(self, widget):
        """Zurück zur Startseite."""
        
        self.update_app(widget)
        self.main_window.content = self.scroll_container_startseite


    def show_info_dialog_booking(self, widget, row):
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
                        element = self.daten.get_rechnung_by_dbid(row.db_id)
                    case 'Beihilfe':
                        element = self.daten.get_beihilfepaket_by_dbid(row.db_id)
                    case 'PKV':
                        element = self.daten.get_pkvpaket_by_dbid(row.db_id)
                        
            case self.form_beihilfe_bills:
                typ = 'Rechnung'
                element = self.daten.get_rechnung_by_dbid(row.db_id)
            case self.form_pkv_bills:
                typ = 'Rechnung'
                element = self.daten.get_rechnung_by_dbid(row.db_id)
            case self.tabelle_rechnungen:
                typ = 'Rechnung'
                element = self.daten.get_rechnung_by_index(self.index_auswahl(widget))
            case self.tabelle_beihilfepakete:
                typ = 'Beihilfe'
                element = self.daten.get_beihilfepaket_by_index(self.index_auswahl(widget))
            case self.tabelle_pkvpakete:
                typ = 'PKV'
                element = self.daten.get_pkvpaket_by_index(self.index_auswahl(widget))
            case self.tabelle_einrichtungen:
                typ = 'Einrichtung'
                element = self.daten.get_einrichtung_by_index(self.index_auswahl(widget))

        # Ermittlung der Texte
        if typ == 'Rechnung':
            titel = 'Rechnung'
            inhalt = 'Rechnungsdatum: {}\n'.format(element.rechnungsdatum)
            inhalt += 'Betrag: {:.2f} €\n'.format(element.betrag).replace('.', ',')
            inhalt += 'Person: {}\n'.format(element.person_name)
            inhalt += 'Beihilfe: {:.0f} %\n\n'.format(element.beihilfesatz)
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
            for rechnung in self.daten.list_rechnungen:
                if (typ == 'Beihilfe' and rechnung.beihilfe_id == element.db_id) or (typ == 'PKV' and rechnung.pkv_id == element.db_id):
                    inhalt += '\n- {}'.format(rechnung.info)
                    #inhalt += ', {}'.format(rechnung.rechnungsdatum)
                    inhalt += ', {:.2f} €'.format(rechnung.betrag).replace('.', ',')
                    inhalt += ', {:.0f} %'.format(rechnung.beihilfesatz)
        elif typ == 'Einrichtung':
            titel = 'Einrichtung'
            inhalt = 'Name: {}\n'.format(element.name)
            inhalt += 'Straße: {}\n'.format(element.strasse)
            inhalt += 'PLZ: {}\n'.format(element.plz)
            inhalt += 'Ort: {}\n'.format(element.ort)
            inhalt += 'Telefon: {}\n'.format(element.telefon)
            inhalt += 'E-Mail: {}\n'.format(element.email)
            inhalt += 'Webseite: {}\n'.format(element.webseite)
            inhalt += 'Notiz: {}\n'.format(element.notiz)

        self.main_window.info_dialog(titel, inhalt)


    def create_list_bills(self):
        """Erzeugt die Seite, auf der die Rechnungen angezeigt werden."""
        self.box_seite_liste_rechnungen = toga.Box(style=style_box_column)
        box_seite_liste_rechnungen_top = toga.Box(style=style_box_column_rechnungen)
        box_seite_liste_rechnungen_top.add(toga.Button('Zurück', style=style_button, on_press=self.show_mainpage))
        box_seite_liste_rechnungen_top.add(toga.Label('Rechnungen', style=style_label_h1_hell))
        self.box_seite_liste_rechnungen.add(box_seite_liste_rechnungen_top)

        # Tabelle mit den Rechnungen
        self.tabelle_rechnungen = toga.Table(
            headings    = ['Info', 'Betrag', 'Bezahlt'],
            accessors   = ['info', 'betrag_euro', 'bezahlt_text'],
            data        = self.daten.list_rechnungen,
            style       = style_table,
            on_select   = self.update_app,
            on_activate = self.show_info_dialog_booking
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


    def update_form_bill(self, widget):
        """Ermittelt den Beihilfesatz der ausgewählten Person und trägt ihn in das entsprechende Feld ein."""
        self.form_bill_beihilfe.set_value(self.daten.get_beihilfesatz_by_name(widget.value.name))


    def create_form_bill(self):
        """ Erzeugt das Formular zum Erstellen und Bearbeiten einer Rechnung."""
        
        # Container für das Formular
        self.sc_form_bill = toga.ScrollContainer(style=style_scroll_container)
        self.box_form_bill = toga.Box(style=style_box_column)
        self.sc_form_bill.content = self.box_form_bill

        # Erzeuge eine Liste von Dictionaries, welche die Elemente der Seite enthält
        # self.form_bill_elements = [
        #     {'typ': 'TopBox', 'label_text': 'Neue Rechnung', 'style': style_box_column_rechnungen, 'target_back': self.show_list_bills},
        #     {'typ': 'LabeledSelection', 'label_text': 'Person:', 'data': self.daten.list_personen, 'accessor': 'name', 'on_change': self.update_form_bill},
        #     {'typ': 'LabeledPercentInput', 'label_text': 'Beihilfe in %:'},
        #     {'typ': 'Divider', 'style': style_divider},
        #     {'typ': 'LabeledDateInput', 'label_text': 'Rechnungsdatum:'},
        #     {'typ': 'LabeledFloatInput', 'label_text': 'Betrag in €:'},
        #     {'typ': 'LabeledSelection', 'label_text': 'Einrichtung:', 'data': self.list_einrichtungen, 'accessor': 'name'},
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
            data=self.daten.list_personen,
            accessor='name',
            on_change=self.update_form_bill
        )

        self.form_bill_beihilfe = LabeledPercentInput(self.box_form_bill, 'Beihilfe in %:')
        self.box_form_bill.add(toga.Divider(style=style_divider))
        self.form_bill_rechnungsdatum = LabeledDateInput(self.box_form_bill, 'Rechnungsdatum:')
        self.form_bill_betrag = LabeledFloatInput(self.box_form_bill, 'Betrag in €:')

        # Bereich zur Auswahl der Einrichtung
        self.form_bill_einrichtung = LabeledSelection(
            parent=self.box_form_bill,
            label_text='Einrichtung:',
            data=self.daten.list_einrichtungen,
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

        if len(self.daten.list_personen) > 0:
            self.form_bill_person.set_items(self.daten.list_personen)
            self.form_bill_person.set_value(self.daten.list_personen[0])
            self.form_bill_beihilfe.set_value(str(self.daten.list_personen[0].beihilfesatz))
        
        if len(self.daten.list_einrichtungen) > 0:
            self.form_bill_einrichtung.set_items(self.daten.list_einrichtungen)
            self.form_bill_einrichtung.set_value(self.daten.list_einrichtungen[0])

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
            self.edit_bill_id = self.daten.get_rechnung_index_by_dbid(self.tabelle_offene_buchungen.selection.db_id)
        else:
            print('Fehler: Aufrufendes Widget unbekannt.')
            return
        
        # Lade die Rechnung
        rechnung = self.daten.get_rechnung_by_index(self.edit_bill_id, objekt=True)

        # Ermittle den Index der Einrichtung in der Liste der Einrichtungen
        einrichtung_index = self.daten.get_einrichtung_index_by_dbid(rechnung.einrichtung_id)
        person_index = self.daten.get_person_index_by_dbid(rechnung.person_id)

        # Auswahlfeld für die Einrichtung befüllen
        if len(self.daten.list_einrichtungen) > 0:
            self.form_bill_einrichtung.set_items(self.daten.list_einrichtungen)
            if einrichtung_index is not None and einrichtung_index in range(len(self.daten.list_einrichtungen)):
                self.form_bill_einrichtung.set_value(self.daten.list_einrichtungen[einrichtung_index])
            else:      
                self.form_bill_einrichtung.set_value(self.daten.list_einrichtungen[0])

        # Auswahlfeld für die Person befüllen
        if len(self.daten.list_personen) > 0:
            self.form_bill_person.set_items(self.daten.list_personen)
            if person_index is not None and person_index in range(len(self.daten.list_personen)):    
                self.form_bill_person.set_value(self.daten.list_personen[person_index])
            else:
                self.form_bill_person.set_value(self.daten.list_personen[0])

        # Befülle die Eingabefelder
        self.form_bill_betrag.set_value(rechnung.betrag)
        self.form_bill_rechnungsdatum.set_value(rechnung.rechnungsdatum)
        self.form_bill_beihilfe.set_value(rechnung.beihilfesatz)
        self.form_bill_notiz.set_value(rechnung.notiz)
        self.form_bill_buchungsdatum.set_value(rechnung.buchungsdatum)
        self.form_bill_bezahlt.set_value(rechnung.bezahlt)

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
        if len(self.daten.personen) > 0:
            if self.form_bill_person.get_value() is None:
                nachricht += 'Bitte wähle eine Person aus.\n'

        # Prüfe, ob eine Einrichtung ausgewählt wurde
        if len(self.daten.einrichtungen) > 0:
            if self.form_bill_einrichtung.get_value() is None:
                nachricht += 'Bitte wähle eine Einrichtung aus.\n'

        # Prüfe, ob ein Beihilfe eingegeben wurde
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
            if len(self.daten.personen) > 0:
                neue_rechnung.person_id = self.form_bill_person.get_value().db_id
            neue_rechnung.beihilfesatz = self.form_bill_beihilfe.get_value()
            if len(self.daten.einrichtungen) > 0:
                neue_rechnung.einrichtung_id = self.form_bill_einrichtung.get_value().db_id
            neue_rechnung.notiz = self.form_bill_notiz.get_value()
            neue_rechnung.betrag = self.form_bill_betrag.get_value()
            neue_rechnung.buchungsdatum = self.form_bill_buchungsdatum.get_value()
            neue_rechnung.bezahlt = self.form_bill_bezahlt.get_value()

            # Übergebe die Rechnung dem Daten-Interface
            self.daten.new_rechnung(neue_rechnung)
        else:
            # flag ob verknüpfte Einreichungen aktualisiert werden können
            # True, wenn betrag oder beihilfesatz geändert wurde
            update_einreichung = False

            rechnung = self.daten.get_rechnung_by_index(self.edit_bill_id, objekt=True)
            
            if rechnung.betrag != self.form_bill_betrag.get_value():
                update_einreichung = True
            if rechnung.beihilfesatz != self.form_bill_beihilfe.get_value():
                update_einreichung = True

            # Bearbeite die Rechnung
            rechnung.rechnungsdatum = self.form_bill_rechnungsdatum.get_value()

            if len(self.daten.list_personen) > 0:
                rechnung.person_id = self.form_bill_person.get_value().db_id
            
            if len(self.daten.list_einrichtungen) > 0:
                rechnung.einrichtung_id = self.form_bill_einrichtung.get_value().db_id

            rechnung.notiz = self.form_bill_notiz.get_value()
            rechnung.betrag = self.form_bill_betrag.get_value()
            rechnung.beihilfesatz = self.form_bill_beihilfe.get_value()
            rechnung.buchungsdatum = self.form_bill_buchungsdatum.get_value()
            rechnung.bezahlt = self.form_bill_bezahlt.get_value()

            # Übergabe die geänderte Rechnung an das Daten-Interface
            self.daten.edit_rechnung(rechnung, self.edit_bill_id)

            # Flag zurücksetzen
            self.flag_edit_bill = False

            # Überprüfe ob eine verknüpfte Beihilfe-Einreichung existiert
            # und wenn ja, frage, ob diese aktualisiert werden soll
            if update_einreichung and rechnung.beihilfe_id is not None:
                await self.main_window.confirm_dialog(
                    'Zugehörige Beihilfe-Einreichung aktualisieren',
                    'Soll die zugehörige Beihilfe-Einreichung aktualisiert werden?',
                    on_result=self.update_beihilfepaket
                )

            # Überprüfe ob eine verknüpfte PKV-Einreichung existiert
            # und wenn ja, frage, ob diese aktualisiert werden soll
            if update_einreichung and rechnung.pkv_id is not None:
                await self.main_window.confirm_dialog(
                    'Zugehörige PKV-Einreichung aktualisieren',
                    'Soll die zugehörige PKV-Einreichung aktualisiert werden?',
                    on_result=self.update_pkvpaket
                )

        # Zeigt die Liste der Rechnungen an.
        self.show_list_bills(widget)     


    def update_beihilfepaket(self, widget, result):  
        """Aktualisiert die Beihilfe-Einreichung einer Rechnung."""
        if result:
            self.daten.update_beihilfepaket_betrag(self.daten.rechnungen[self.edit_bill_id].beihilfe_id) 


    def update_pkvpaket(self, widget, result):  
        """Aktualisiert die PKV-Einreichung einer Rechnung."""
        if result:
            self.daten.update_pkvpaket_betrag(self.daten.rechnungen[self.edit_bill_id].pkv_id)    


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

            # Setze Betrag der Rechnung auf 0, damit Einreichungen aktualisiert werden können
            self.daten.rechnungen[self.edit_bill_id].betrag = 0

            # Überprüfe, ob Einreichungen existieren
            if self.daten.rechnungen[self.edit_bill_id].beihilfe_id is not None:
                await self.main_window.confirm_dialog(
                    'Zugehörige Beihilfe-Einreichung aktualisieren',
                    'Soll die zugehörige Beihilfe-Einreichung aktualisiert werden?',
                    on_result=self.update_beihilfepaket
                )

            if self.daten.rechnungen[self.edit_bill_id].pkv_id is not None:
                await self.main_window.confirm_dialog(
                    'Zugehörige PKV-Einreichung aktualisieren',
                    'Soll die zugehörige PKV-Einreichung aktualisiert werden?',
                    on_result=self.update_pkvpaket
                )

            # Rechnung löschen
            self.daten.delete_rechnung(self.edit_bill_id)

            # App aktualisieren
            self.update_app(widget)


    def create_list_institutions(self):
        """Erzeugt die Seite, auf der die Einrichtungen angezeigt werden."""
        self.box_seite_liste_einrichtungen = toga.Box(style=style_box_column)
        box_seite_liste_einrichtungen_top = toga.Box(style=style_box_column_dunkel)
        box_seite_liste_einrichtungen_top.add(toga.Button('Zurück', on_press=self.show_mainpage, style=style_button))
        box_seite_liste_einrichtungen_top.add(toga.Label('Einrichtungen', style=style_label_h1_hell))
        self.box_seite_liste_einrichtungen.add(box_seite_liste_einrichtungen_top)

        # Tabelle mit den Einrichtungen

        self.tabelle_einrichtungen = toga.Table(
            headings    = ['Name', 'Ort', 'Telefon'], 
            accessors   = ['name', 'ort', 'telefon'],
            data        = self.daten.list_einrichtungen,
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

            # Hole die Einrichtung
            einrichtung = self.daten.get_einrichtung_by_index(self.edit_institution_id, objekt=True)
            
            # Befülle die Eingabefelder
            self.form_institution_name.set_value(einrichtung.name)
            self.form_institution_strasse.set_value(einrichtung.strasse)
            self.form_institution_plz.set_value(einrichtung.plz)
            self.form_institution_ort.set_value(einrichtung.ort)
            self.form_institution_telefon.set_value(einrichtung.telefon)
            self.form_institution_email.set_value(einrichtung.email)
            self.form_institution_webseite.set_value(einrichtung.webseite)
            self.form_institution_notiz.set_value(einrichtung.notiz)

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
            self.daten.new_einrichtung(neue_einrichtung)
        else:
            print('+++ Einrichtung bearbeiten')
            einrichtung = self.daten.get_einrichtung_by_index(self.edit_institution_id, objekt=True)

            # Bearbeite die Einrichtung
            einrichtung.name = self.form_institution_name.get_value()
            einrichtung.strasse = self.form_institution_strasse.get_value()
            einrichtung.plz = self.form_institution_plz.get_value()
            einrichtung.ort = self.form_institution_ort.get_value()
            einrichtung.telefon = self.form_institution_telefon.get_value()
            einrichtung.email = self.form_institution_email.get_value()
            einrichtung.webseite = self.form_institution_webseite.get_value()
            einrichtung.notiz = self.form_institution_notiz.get_value()

            # Übergabe der geänderten Einrichtung an das Daten-Interface
            self.daten.edit_einrichtung(einrichtung, self.edit_institution_id)

            # Flag zurücksetzen
            self.flag_edit_institution = False


        # Zeige die Liste der Einrichtungen
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
        self.link_info_einrichtung_webseite = toga.Button('', style=style_button_link, on_press=self.show_webview)
        

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

            # Hole die Einrichtung
            einrichtung = self.daten.get_einrichtung_by_index(self.edit_institution_id)

            # Befülle die Labels mit den Details der Einrichtung
            # Die einzutragenden Werte können None sein, daher wird hier mit einem leeren String gearbeitet
            self.label_info_einrichtung_name.text = einrichtung.name
            self.label_info_einrichtung_strasse.text = einrichtung.strasse
            self.label_info_einrichtung_plz_ort.text = einrichtung.plz_ort
            self.label_info_einrichtung_telefon.text = einrichtung.telefon
            self.label_info_einrichtung_email.text = einrichtung.email
            
            # Entferne die Inhalte der Box, damit die Webseite nicht mehrfach angezeigt wird
            if self.link_info_einrichtung_webseite in self.box_seite_info_einrichtung_webseite.children:
                self.box_seite_info_einrichtung_webseite.remove(self.link_info_einrichtung_webseite)

            # Wenn eine gültige Webseite gespeichert ist, füge den Link wieder der Box hinzu
            # und setze den Text des Links auf die Webseite
            if einrichtung.webseite:
                self.box_seite_info_einrichtung_webseite.add(self.link_info_einrichtung_webseite)
                self.link_info_einrichtung_webseite.text = einrichtung.webseite
                
            self.label_info_einrichtung_notiz.text = einrichtung.notiz

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
        """Deaktiviert eine Einrichtung."""
        if self.tabelle_einrichtungen.selection and result:
            if not self.daten.deactivate_einrichtung(self.index_auswahl(self.tabelle_einrichtungen)):
                self.main_window.error_dialog(
                    'Fehler beim Löschen',
                    'Die Einrichtung wird noch in einer aktiven Rechnung verwendet und kann daher nicht gelöscht werden.'
                )
                return

            # Seite mit Liste der Einrichtungen anzeigen
            self.update_app(widget)


    def create_list_persons(self):
        """Erzeugt die Seite, auf der die Personen angezeigt werden."""
        self.box_seite_liste_personen = toga.Box(style=style_box_column)
        box_seite_liste_personen_top = toga.Box(style=style_box_column_dunkel)
        box_seite_liste_personen_top.add(toga.Button('Zurück', on_press=self.show_mainpage, style=style_button))
        box_seite_liste_personen_top.add(toga.Label('Personen', style=style_label_h1_hell))
        self.box_seite_liste_personen.add(box_seite_liste_personen_top)

        # Tabelle mit den Personen
        self.tabelle_personen = toga.Table(
            headings    = ['Name', 'Beihilfe'], 
            accessors   = ['name', 'beihilfesatz_prozent'],
            data        = self.daten.list_personen,
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

            # Hole die Person
            person = self.daten.get_person_by_index(self.edit_person_id, objekt=True)
            
            # Befülle die Eingabefelder
            self.form_person_name.set_value(person.name)
            self.form_person_beihilfe.set_value(person.beihilfesatz)

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

            # Speichere die Person 
            self.daten.new_person(neue_person)
        else:
            person = self.daten.get_person_by_index(self.edit_person_id, objekt=True)

            # Bearbeite die Person
            person.name = self.form_person_name.get_value()
            person.beihilfesatz = self.form_person_beihilfe.get_value()

            # Speichere die Person in der Datenbank
            self.daten.edit_person(person, self.edit_person_id)

            # Flag zurücksetzen
            self.flag_edit_person = False

        # Zeige die Liste der Personen
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
        """Deaktiviert eine Person."""
        if self.tabelle_personen.selection and result:
            if not self.daten.deactivate_person(self.index_auswahl(self.tabelle_personen)):
                self.main_window.error_dialog(
                    'Fehler beim Löschen',
                    'Die Person wird noch in einer aktiven Rechnung verwendet und kann daher nicht gelöscht werden.'
                )
                return

            # App aktualisieren
            self.update_app(widget)


    def create_list_beihilfe(self):
        """Erzeugt die Seite, auf der die Beihilfe-Einreichungen angezeigt werden."""
        self.box_seite_liste_beihilfepakete = toga.Box(style=style_box_column)
        box_seite_liste_beihilfepakete_top = toga.Box(style=style_box_column_beihilfe)
        box_seite_liste_beihilfepakete_top.add(toga.Button('Zurück', on_press=self.show_mainpage, style=style_button))
        box_seite_liste_beihilfepakete_top.add(toga.Label('Beihilfe-Einreichungen', style=style_label_h1_hell))
        self.box_seite_liste_beihilfepakete.add(box_seite_liste_beihilfepakete_top)

        # Tabelle mit den Beihilfepaketen
        self.tabelle_beihilfepakete = toga.Table(
            headings    = ['Datum', 'Betrag', 'Erstattet'], 
            accessors   = ['datum', 'betrag_euro', 'erhalten_text'],
            data        = self.daten.list_beihilfepakete,
            style       = style_table,
            on_select   = self.update_app,
            on_activate = self.show_info_dialog_booking
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
        box_seite_liste_pkvpakete_top.add(toga.Button('Zurück', on_press=self.show_mainpage, style=style_button))
        box_seite_liste_pkvpakete_top.add(toga.Label('PKV-Einreichungen', style=style_label_h1_hell))
        self.box_seite_liste_pkvpakete.add(box_seite_liste_pkvpakete_top)

        # Tabelle mit den PKV-Einreichungen
        self.tabelle_pkvpakete_container = toga.ScrollContainer(style=style_scroll_container)
        self.tabelle_pkvpakete = toga.Table(
            headings    = ['Datum', 'Betrag', 'Erstattet'], 
            accessors   = ['datum', 'betrag_euro', 'erhalten_text'],
            data        = self.daten.list_pkvpakete,
            style       = style_table,
            on_select   = self.update_app,
            on_activate = self.show_info_dialog_booking
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
            data            = self.daten.list_rg_beihilfe,
            multiple_select = True,
            on_select       = self.on_select_beihilfe_bills,
            on_activate     = self.show_info_dialog_booking,
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
            data            = self.daten.list_rg_pkv,
            multiple_select = True,
            on_select       = self.on_select_pkv_bills,   
            on_activate     = self.show_info_dialog_booking,
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
            for rg in self.daten.rechnungen:
                if auswahl_rg.db_id == rg.db_id:
                    summe += rg.betrag * rg.beihilfesatz / 100
        self.form_beihilfe_betrag.set_value(summe)


    def on_select_pkv_bills(self, widget):
        """Ermittelt die Summe des PKV-Anteils der ausgewählten Rechnungen."""
        summe = 0
        for auswahl_rg in widget.selection:
            for rg in self.daten.rechnungen:
                if auswahl_rg.db_id == rg.db_id:
                    summe += rg.betrag * (100 - rg.beihilfesatz) / 100
        self.form_pkv_betrag.set_value(summe)


    def show_form_beihilfe_new(self, widget):
        """Zeigt die Seite zum Erstellen eines Beihilfepakets."""
        # Setze die Eingabefelder zurück
        self.form_beihilfe_betrag.set_value('')
        self.form_beihilfe_datum.set_value(datetime.now())
        self.form_beihilfe_erhalten.set_value(False)

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

            # IDs der Rechnungen in Liste speichern
            rechnungen_db_ids = []
            for auswahl_rg in self.form_beihilfe_bills.selection:
                rechnungen_db_ids.append(auswahl_rg.db_id)

            # Speichere das Beihilfepaket in der Datenbank
            self.daten.new_beihilfepaket(neues_beihilfepaket, rechnungen_db_ids)

        # Wechsel zur Startseite
        self.show_mainpage(widget)


    def save_pkv(self, widget):
        """Erstellt und speichert eine neue PKV-Einreichung oder ändert eine bestehende."""

        if not self.flag_edit_pkv:
            # Erstelle ein neues PKV-Paket
            neues_pkvpaket = PKVPaket()
            neues_pkvpaket.datum = self.form_pkv_datum.get_value()
            neues_pkvpaket.betrag = self.form_pkv_betrag.get_value()
            neues_pkvpaket.erhalten = self.form_pkv_erhalten.get_value()

            # IDs der Rechnungen in Liste speichern
            rechnungen_db_ids = []
            for auswahl_rg in self.form_pkv_bills.selection:
                rechnungen_db_ids.append(auswahl_rg.db_id)

            # Speichere das PKV-Paket in der Datenbank
            self.daten.new_pkvpaket(neues_pkvpaket, rechnungen_db_ids)

        # Wechsel zur Startseite
        self.show_mainpage(widget)


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
            self.daten.delete_beihilfepaket(self.index_auswahl(self.tabelle_beihilfepakete))
            
            # Anzeigen aktualisieren
            self.update_app(widget)


    def delete_pkv(self, widget, result):
        """Löscht eine PKV-Einreichung."""
        if self.tabelle_pkvpakete.selection and result:
            self.daten.delete_pkvpaket(self.index_auswahl(self.tabelle_pkvpakete))
            
            # Anzeigen aktualisieren
            self.update_app(widget)
            

    def archivieren_bestaetigen(self, widget):
        """Bestätigt das Archivieren von Buchungen."""
        if self.daten.get_number_archivables() > 0:
            self.main_window.confirm_dialog(
                'Buchungen archivieren', 
                'Sollen alle archivierbaren Buchungen wirklich archiviert werden? Sie werden dann in der App nicht mehr angezeigt.',
                on_result=self.archivieren
            )


    def archivieren(self, widget, result):
        if result:
            self.daten.archive()
            self.show_mainpage(widget)
            

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
            self.daten.pay_rechnung(self.tabelle_offene_buchungen.selection.db_id)
            self.update_app(widget)

    
    def beihilfe_erhalten(self, widget, result):
        """Markiert eine Beihilfe als erhalten."""
        if self.tabelle_offene_buchungen.selection and result:
            self.daten.receive_beihilfe(self.tabelle_offene_buchungen.selection.db_id)
            self.update_app(widget)


    def pkv_erhalten(self, widget, result):
        """Markiert eine PKV-Einreichung als erhalten."""
        if self.tabelle_offene_buchungen.selection and result:
            self.daten.receive_pkv(self.tabelle_offene_buchungen.selection.db_id)
            self.update_app(widget)
    

    def edit_open_booking(self, widget):
        """Öffnet die Seite zum Bearbeiten einer offenen Buchung."""
        if self.tabelle_offene_buchungen.selection:
            match self.tabelle_offene_buchungen.selection.typ:
                case 'Rechnung':
                    self.show_form_bill_edit(widget)
                # case 'Beihilfe':
                #     self.show_form_beihilfe_edit(widget)
                # case 'PKV':
                #     self.show_form_pkv_edit(widget)


    def create_commands(self):
        """Erzeugt die Menüleiste."""
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
            self.show_webview,
            'Datenschutz',
            tooltip = 'Öffne die Datenschutzerklärung.',
            order = 7,
            enabled=True
        )

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


    def startup(self):
        """Laden der Daten, Erzeugen der GUI-Elemente und des Hauptfensters."""

        # Daten-Interface initialisieren
        self.daten = DatenInterface()

        # Erzeuge alle GUI-Elemente
        self.create_mainpage()
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
        self.create_webview()
        self.create_commands()

        # Erstelle das Hauptfenster
        self.main_window = toga.MainWindow(title=self.formal_name)      

        # Zeige die Startseite
        self.show_mainpage(None)
        self.main_window.show()
        

def main():
    """Hauptschleife der Anwendung"""
    return Kontolupe()