"""
Behalte den Überblick über Deine Rechnungen, Beihilfe- und PKV-Erstattungen.

Mit Kontolupe kannst Du Deine Gesundheitsrechnungen erfassen und verwalten.
Du kannst Beihilfe- und PKV-Einreichungen erstellen und die Erstattungen
überwachen. Die App ist für die private Nutzung kostenlos.
"""

import toga
from datetime import datetime

from kontolupe.database import *
from kontolupe.validator import *
from kontolupe.layout import *
from kontolupe.gui import *
from kontolupe.general import *

class Kontolupe(toga.App):
    """Die Hauptklasse der Anwendung."""

    def __init__(self, *args, **kwargs):
        """Initialisierung der Anwendung."""
        super().__init__(*args, **kwargs)

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

        # Weitere Hilfsvariablen
        self.back_to = 'startseite'


    def show_settings(self, widget):
        """Zeigt die Seite für die Einstellungen der App."""

        # update the switches states
        self.settings_automatic_booking.set_value(self.daten.init.get('automatic_booking', False))
        self.settings_automatic_archive.set_value(self.daten.init.get('automatic_archive', False))

        self.main_window.content = self.sc_settings


    def on_change_setting(self, widget):
        """Reagiert auf die Änderung einer Einstellung."""
        self.daten.init['automatic_booking'] = self.settings_automatic_booking.get_value()
        self.daten.init['automatic_archive'] = self.settings_automatic_archive.get_value()
        self.daten.save_init_file()
        
        print(self.daten.init)


    def create_settings(self):
        """Erstellt die Seite mit den Einstellungen der App."""

        # Container für die Seite
        self.box_settings = toga.Box(style=style_box_column)
        self.sc_settings = toga.ScrollContainer(content=self.box_settings, style=style_scroll_container)

        # Überschrift und Button Zurück
        self.settings_topbox = TopBox(
            label_text  = 'Einstellungen', 
            style_box   = style_box_column_dunkel,
            target_back = self.show_mainpage
        )
        self.box_settings.add(self.settings_topbox)

        self.settings_automatic_booking = LabeledSwitch(
            'Automatische Buchungen:',
            helptitle   = 'Automatische Buchungen',
            helptext    = (
                'Wenn diese Funktion aktiviert ist, werden die Rechnungen automatisch als "bezahlt" markiert, '
                'sobald das geplante Überweisungsdatum erreicht ist.'
            ),
            window      = self.main_window,
            on_change   = self.on_change_setting
        )
        self.box_settings.add(self.settings_automatic_booking)

        self.settings_automatic_archive = LabeledSwitch(
            'Automatische Archivierung:',
            helptitle   = 'Automatische Archivierung',
            helptext    = (
                'Wenn diese Funktion aktiviert ist, werden alle zusammengehörenden '
                'Rechnungen und Einreichungen, die vollständig bezahlt bzw. erstattet '
                'sind, automatisch archiviert und in der App nicht mehr angezeigt.'
            ),
            window      = self.main_window,
            on_change   = self.on_change_setting
        )
        self.box_settings.add(self.settings_automatic_archive)


    async def check_open_bills(self, widget):
        """Aktualisiert den Bezahlstatus der offenen Rechnungen."""
        
        # loop through the list of open bookings
        # if there is a bill, check if there is a payment date set
        # and if the payment date is today or before today
        # then open a question_dialog and ask if the bill has been paid
        # if yes, set the payment date and set the bill to paid
        # if no, do nothing

        # check if self.daten.init (dictionary) contains the key 'queried_payment'
        # if not, set the key 'queried_payment' to 01.01.1900 as a string
        # and save the init file
        if 'queried_payment' not in self.daten.init:
            self.daten.init['queried_payment'] = '01.01.1900'
            self.daten.save_init_file()

        # checks before executing the function
        if widget not in self.mainpage_table_buttons.buttons and not self.daten.init.get('automatic_booking', False) and self.daten.init.get('queried_payment', '01.01.2000') == datetime.today().strftime('%d.%m.%Y'):
            return
        else:
            self.daten.init['queried_payment'] = datetime.today().strftime('%d.%m.%Y')
            self.daten.save_init_file()

        # copy the list of open bookings
        # because we will change the list while looping through it
        # and that is not allowed
        for booking in list(self.daten.open_bookings):
            
            if booking.typ == 'Rechnung' and booking.buchungsdatum:
                booking_date = datetime.strptime(booking.buchungsdatum, '%d.%m.%Y')
                if booking_date.date() <= datetime.today().date():
                    
                    result = self.daten.init.get('automatic_booking', False)

                    if not result:
                        result = await self.main_window.question_dialog(
                            'Rechnung bezahlt?', 
                            'Wurde diese Rechnung bezahlt?\nSie war am {} geplant:\n\n{} wegen {}'.format(booking.buchungsdatum, booking.betrag_euro[1:], booking.info)
                        )
                    
                    if result:
                        self.daten.pay_receive(booking.typ, self.daten.get_element_by_dbid(self.daten.bills, booking.db_id))
                        print('+++ Kontolupe.check_open_bills: Rechnung {} bezahlt.'.format(booking.db_id))


    def update_buttons(self, widget):
        """Aktualisiert die Anzeigen und Aktivierungszustand der Buttons von Tabellen."""

        # Ändert den Aktivierungszustand der zur aufrufenden Tabelle gehörenden Buttons.
        status = False
        if widget and type(widget) == toga.Table and widget.selection is not None:
            status = True
        else:
            status = False

        match widget:
            case self.table_bills:
                self.list_bills_buttons.set_enabled('delete_bill', status)
                self.list_bills_buttons.set_enabled('edit_bill', status)
            case self.table_allowance:
                self.list_allowance_buttons.set_enabled('reset_allowance', status)
                if widget.selection and widget.selection.erhalten:
                    self.list_allowance_buttons.set_enabled('receive_allowance', False)
                else:
                    self.list_allowance_buttons.set_enabled('receive_allowance', status)
            case self.table_insurance:
                self.list_insurance_buttons.set_enabled('reset_insurance', status)
                if widget.selection and widget.selection.erhalten:
                    self.list_insurance_buttons.set_enabled('receive_insurance', False)
                else:
                    self.list_insurance_buttons.set_enabled('receive_insurance', status)
            case self.table_institutions:
                self.list_institutions_buttons.set_enabled('delete_institution', status)
                self.list_institutions_buttons.set_enabled('edit_institution', status)
                self.list_institutions_buttons.set_enabled('info_institution', status)
            case self.table_persons:
                self.list_persons_buttons.set_enabled('delete_person', status)
                self.list_persons_buttons.set_enabled('edit_person', status)


    def info_dialog_booking(self, widget, row=None):
        """Zeigt die Info einer Buchung."""
        
        # Initialisierung Variablen
        titel = ''
        inhalt = ''

        # Ermittlung der Buchungsart
        typ = ''
        element = None

        if row is None:
            # It should be one of the help buttons in the list of open bookings
            booking = self.daten.open_bookings[int(widget.id[1:])]
            typ = booking.typ

            match typ:
                case 'Rechnung':
                    element = self.daten.get_element_by_dbid(self.daten.bills, booking.db_id)
                case 'Beihilfe':
                    element = self.daten.get_element_by_dbid(self.daten.allowances, booking.db_id)
                case 'PKV':
                    element = self.daten.get_element_by_dbid(self.daten.insurances, booking.db_id)
        else:
            match widget:                            
                case self.form_beihilfe_bills:
                    typ = 'Rechnung'
                    element = self.daten.get_element_by_dbid(self.daten.bills, row.db_id)
                case self.form_pkv_bills:
                    typ = 'Rechnung'
                    element = self.daten.get_element_by_dbid(self.daten.bills, row.db_id)
                case self.table_bills:
                    typ = 'Rechnung'
                    element = self.daten.bills[table_index_selection(widget)]
                case self.table_allowance:
                    typ = 'Beihilfe'
                    element = self.daten.allowances[table_index_selection(widget)]
                case self.table_insurance:
                    typ = 'PKV'
                    element = self.daten.insurances[table_index_selection(widget)]
                case self.table_institutions:
                    typ = 'Einrichtung'
                    element = self.daten.institutions[table_index_selection(widget)]

        # Ermittlung der Texte
        if typ == 'Rechnung':
            titel = 'Rechnung'
            inhalt = 'Rechnungsdatum: {}\n'.format(element.rechnungsdatum)
            inhalt += 'Betrag: {:.2f} €\n'.format(element.betrag).replace('.', ',')
            inhalt += 'Abzugsbetrag Beihilfe: {:.2f} €\n'.format(element.abzug_beihilfe).replace('.', ',') if element.abzug_beihilfe else ''
            inhalt += 'Abzugsbetrag Private KV: {:.2f} €\n'.format(element.abzug_pkv).replace('.', ',') if element.abzug_pkv else ''
            inhalt += 'Person: {}\n'.format(element.person_name)
            inhalt += 'Beihilfe: {:.0f} %\n\n'.format(element.beihilfesatz)
            inhalt += 'Einrichtung: {}\n'.format(element.einrichtung_name)
            inhalt += 'Notiz: {}\n'.format(element.notiz)
            inhalt += 'Bezahldatum: {}\n'.format(element.buchungsdatum) if element.buchungsdatum else 'Bezahldatum: -\n'
            inhalt += 'Bezahlt: Ja' if element.bezahlt else 'Bezahlt: Nein'
        elif typ == 'Beihilfe' or typ == 'PKV':
            titel = 'Beihilfe-Einreichung' if typ == 'Beihilfe' else 'PKV-Einreichung'
            inhalt = 'Vom {} '.format(element.datum)
            inhalt += 'über {:.2f} €\n\n'.format(element.betrag).replace('.', ',')
            
            # Liste alle Rechnungen auf, die zu diesem Paket gehören
            inhalt += 'Eingereichte Rechnungen:'
            for rechnung in self.daten.bills:
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


    def go_back(self, widget):
        """Ermittelt das Ziel der Zurück-Funktion und ruft die entsprechende Seite auf."""
        match self.back_to:
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
            case 'formular_pkvpakete_neu':
                self.show_form_pkv_new(widget)
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
        box_webview_top.add(toga.Button('Zurück', style=style_button, on_press=self.go_back))
        self.box_webview.add(box_webview_top)
        self.webview = toga.WebView(style=style_webview)
        self.box_webview.add(self.webview)


    def show_webview(self, widget):
        """Zeigt die WebView zur Anzeige von Webseiten."""

        match widget:
            case self.info_institution_website.button:
                self.webview.url = 'https://' + self.daten.list_einrichtungen[self.edit_institution_id].webseite
                self.back_to = 'info_einrichtung'
            case self.cmd_datenschutz:
                self.webview.url = 'https://kontolupe.biberwerk.net/kontolupe-datenschutz.html'
                self.back_to = 'startseite'

        self.main_window.content = self.box_webview


    def show_statistics(self, widget):
        """Zeigt die Seite mit der Statistik."""
        # Update the items of the type selection
        temp = self.statistics_type.get_value()
        if self.daten.allowance_active():
            self.statistics_type.set_items(['Alle', 'Rechnungen', 'Beihilfe', 'Private KV'])
        else:
            self.statistics_type.set_items(['Alle', 'Rechnungen', 'Private KV'])
        if temp in self.statistics_type.get_items():
            self.statistics_type.set_value(temp)

        # Update the items of the person and einrichtung selections
        temp = self.statistics_person.get_value()
        self.statistics_person.set_items(
            (['Alle'] if len(self.daten.persons) > 1 else []) + [person.name for person in self.daten.persons]
        )
        if temp in self.statistics_person.get_items():
            self.statistics_person.set_value(temp)

        temp = self.statistics_institution.get_value()
        self.statistics_institution.set_items(
            (['Alle'] if len(self.daten.institutions) > 1 else []) + [institution.name for institution in self.daten.institutions]
        )
        if temp in self.statistics_institution.get_items():
            self.statistics_institution.set_value(temp)

        # Check if the current year has changed and add it to the items of the from and to selections
        current_year = datetime.today().year
        try:
            self.statistics_from.get_items(1).find(str(current_year))
            print('+++ Kontolupe.show_statistics: current year already in the list.')
            
        except ValueError:
            print('+++ Kontolupe.show_statistics: current year not in the list, adding it.')
            temp = self.statistics_from.get_value()
            self.statistics_from.add_item(str(current_year), 1)
            self.statistics_to.add_item(str(current_year), 1)
            self.statistics_from.set_value(temp)
        
        self.main_window.content = self.sc_statistics


    def statistics_changed(self, widget):
        """Reagiert auf Änderungen in der Statistik-Auswahl."""
        pass


    def create_statistics(self):
        """Erstellt die Seite mit der Statistik."""
        self.box_statistics = toga.Box(style=style_box_column)
        self.sc_statistics = toga.ScrollContainer(content=self.box_statistics, style=style_scroll_container)

        # Überschrift und Button Zurück
        self.statistics_topbox = TopBox(
            label_text  = 'Statistiken', 
            style_box   = style_box_column_dunkel,
            target_back = self.show_mainpage
        )
        self.box_statistics.add(self.statistics_topbox)

        self.box_statistics.add(SubtextDivider('Datenauswahl'))

        # Selektion des Typs der Buchung
        self.statistics_type = LabeledSelection(
            'Typ(en):', 
            ['Alle', 'Rechnungen', 'Beihilfe', 'Private KV'], 
            on_change=self.statistics_changed
        )
        self.box_statistics.add(self.statistics_type)

        # Selektion der Person
        self.statistics_person = LabeledSelection(
            'Person(en):', 
            ['Alle'], 
            on_change=self.statistics_changed
        )
        self.box_statistics.add(self.statistics_person)

        # Selektion der Einrichtung
        self.statistics_institution = LabeledSelection(
            'Einrichtung(en):', 
            ['Alle'], 
            on_change=self.statistics_changed
        )
        self.box_statistics.add(self.statistics_institution)

        self.box_statistics.add(SubtextDivider('Auswertungszeitraum'))

        # Daten für die Selektion des Zeitraums
        months = ['{:02d}'.format(month) for month in range(1, 13)]
        years = [str(year) for year in range(2020, datetime.today().year + 1)]
        # reverse the years list
        years = years[::-1]

        # Ermittle den aktuellen Monat und das aktuelle Jahr
        current_month = datetime.today().month
        current_year = datetime.today().year

        # Selektion des Zeitraums
        self.statistics_from = LabeledDoubleSelection( 
            'Von:', 
            data = [months, years], 
            values = ['{:02d}'.format(current_month), str(current_year-1)],
            on_change=[self.statistics_changed, self.statistics_changed]
        )
        self.box_statistics.add(self.statistics_from)

        self.statistics_to = LabeledDoubleSelection(
            'Bis:', 
            data = [months, years], 
            values = ['{:02d}'.format(current_month), str(current_year)],
            on_change=[self.statistics_changed, self.statistics_changed]
        )
        self.box_statistics.add(self.statistics_to)

        self.statistics_step = LabeledSelection(
            'Auswertungsschritt:', 
            ['Monat', 'Quartal', 'Jahr'], 
            on_change = self.statistics_changed,
            value = 'Quartal'
        )
        self.box_statistics.add(self.statistics_step)

        # ButtonBox
        self.statistics_buttons = ButtonBox(
            labels  = ['Anzeigen', 'Exportieren'],
            targets = [None, None],
            ids     = ['show_statistic', 'export_statistic'],
            enabled = [True, False]
        )  
        self.box_statistics.add(self.statistics_buttons)

        self.box_statistics.add(toga.Divider(style=style_divider))


    def show_init_page(self, widget):
        """Zeigt die Seite zur Initialisierung der Anwendung."""

        # Aktualisiere die Anzeigen
        self.update_init_page(widget)

        # Zeige die Initialisierungsseite
        self.main_window.content = self.sc_init_page


    def update_init_page(self, widget):
        """Aktualisiert die Initialisierungsseite."""

        # Setze das Formular zurück
        # self.init_persons_name.set_value('')
        # self.init_persons_beihilfe.set_value('')
        # self.init_institutions_name.set_value('')
        # self.init_institutions_city.set_value('')
        self.init_beihilfe.value = self.daten.init.get('beihilfe', True)
        if self.init_beihilfe.value:
            self.box_init_pkv.remove(self.box_init_beihilfe_content)
            self.box_init_beihilfe.add(self.box_init_beihilfe_content)
            self.label_beihilfe.text = 'Private KV und Beihilfe'
        else:
            self.box_init_beihilfe.remove(self.box_init_beihilfe_content)
            self.box_init_pkv.add(self.box_init_beihilfe_content)
            self.label_beihilfe.text = 'Nur private KV'
        
        if self.daten.allowance_active():
            self.init_persons_beihilfe.show()
        else:
            self.init_persons_beihilfe.hide()

        # Ermittle den Status der Eingaben
        status_persons = False
        text_persons = 'Bitte füge mindestens eine Person hinzu.'
        status_institutions = False
        text_institutions = 'Bitte füge mindestens eine Einrichtung hinzu.'

        # Überprüfe die Personen
        if len(self.daten.persons) > 0:
            status_persons = True
            text_persons = ''
            for person in self.daten.persons:
                text_persons += '{}, '.format(person.name)
            text_persons = text_persons.rstrip(', ')

        # Überprüfe die Einrichtungen
        if len(self.daten.institutions) > 0:
            status_institutions = True
            text_institutions = ''
            for institution in self.daten.institutions:
                text_institutions += '{}, '.format(institution.name)
            text_institutions = text_institutions.rstrip(', ')

        # Setze die Anzeigen
        self.init_persons_label.text = add_newlines(text_persons, 40)
        self.init_institutions_label.text = add_newlines(text_institutions, 40)

        # Aktiviere den Button, wenn alle Eingaben korrekt sind
        if self.init_button not in self.box_init_page_button.children and status_persons and status_institutions:
            self.init_button.enabled = True
            self.box_init_page_button.add(self.init_button)
            # Show Info dialog
            self.main_window.info_dialog(
                'Spitze', 
                'Die Eingaben sind ausreichend, um die App zu nutzen. '
                'Klicke auf "Initialisierung abschließen", um fortzufahren '
                'oder füge weitere Personen und Einrichtungen hinzu. '
                'Du kannst die Personen und Einrichtungen später auch noch bearbeiten.'
            )
        elif self.init_button in self.box_init_page_button.children and (not status_persons or not status_institutions):
            self.init_button.enabled = False
            self.box_init_page_button.remove(self.init_button)


    def create_init_page(self):
        """Erzeugt die Seite zur Initialisierung der Anwendung nach dem ersten Start."""

        # Container für die Seite
        self.sc_init_page = toga.ScrollContainer(style=style_scroll_container)
        self.box_init_page = toga.Box(style=style_box_column)
        self.sc_init_page.content = self.box_init_page

        # Überschrift und Begrüßungstext
        box_init_top = toga.Box(style=style_box_headline)
        box_init_top.add(toga.Label("Los geht's!", style=style_label_headline))
        self.box_init_page.add(box_init_top)

        # Angabe der Beihilfeberechtigung
        self.box_init_beihilfe = toga.Box(style=style_box_part_beihilfe)
        self.box_init_pkv = toga.Box(style=style_box_part_pkv)
        self.box_init_page.add(self.box_init_beihilfe)
        self.box_init_page.add(self.box_init_pkv)

        self.box_init_beihilfe_content = toga.Box(style=style_box_column)
        self.box_init_beihilfe.add(self.box_init_beihilfe_content)

        self.label_beihilfe = toga.Label('Private KV und Beihilfe', style=style_label_subline_hell)
        self.box_init_beihilfe_content.add(self.label_beihilfe)
        self.init_beihilfe = toga.Switch('', style=style_switch_center_hell, on_change=self.init_beihilfe_changed, value=True)
        box_init_beihilfe_switch = toga.Box(style=style_switch_box_center, children=[self.init_beihilfe])
        self.box_init_beihilfe_content.add(box_init_beihilfe_switch)
        self.box_init_beihilfe_content.add(toga.Label('Aktiviere diese Funktion, wenn Du beihilfeberechtigt bist.', style=style_description_hell))

        # Eingabebereich der Personen
        box_init_persons = toga.Box(style=style_box_part)
        self.box_init_page.add(box_init_persons)
        box_init_persons.add(toga.Label('Personen', style=style_label_subline))
        self.init_persons_label = toga.Label('Bitte füge mindestens eine Person hinzu.', style=style_description)
        box_init_persons.add(self.init_persons_label)
        
        self.init_persons_name = LabeledTextInput('Name:')
        self.init_persons_beihilfe = LabeledPercentInput('Beihilfe in %:')
        self.init_persons_beihilfe.set_value('')
        box_init_persons.add(self.init_persons_name)
        box_init_persons.add(self.init_persons_beihilfe)

        self.init_persons_buttons = ButtonBox(
            labels=['Speichern und neu'],
            targets=[self.save_person]
        )
        box_init_persons.add(self.init_persons_buttons)

        # Eingabebereich der Einrichtungen
        box_init_institutions = toga.Box(style=style_box_part)
        self.box_init_page.add(box_init_institutions)
        box_init_institutions.add(toga.Label('Einrichtungen', style=style_label_subline))
        self.init_institutions_label = toga.Label('Bitte füge mindestens eine Einrichtung hinzu.', style=style_description)
        box_init_institutions.add(self.init_institutions_label)

        self.init_institutions_name = LabeledTextInput('Einrichtung:')
        self.init_institutions_city = LabeledTextInput('Ort:')
        box_init_institutions.add(self.init_institutions_name)
        box_init_institutions.add(self.init_institutions_city)

        self.init_institutions_buttons = ButtonBox(
            labels=['Speichern und neu'],
            targets=[self.save_institution]
        )
        box_init_institutions.add(self.init_institutions_buttons)

        # Button zum Abschluss der Initialisierung
        self.box_init_page_button = toga.Box(style=style_box_part_button)
        self.init_button = toga.Button('Initialisierung abschließen', style=style_init_button, on_press=self.finish_init, enabled=False)
        self.box_init_page.add(self.box_init_page_button)


    def init_beihilfe_changed(self, widget):
        """Reagiert auf die Änderung der Beihilfeeinstellung während der Initialisierung."""
        self.daten.init['beihilfe'] = widget.value
        self.daten.save_init_file()
        self.update_init_page(widget)


    def finish_init(self, widget):
        """Speichert die Daten und beendet die Initialisierung."""
        
        # Speichere die Daten
        self.daten.init['beihilfe'] = self.init_beihilfe.value
        self.daten.init['initialized'] = True
        self.daten.save_init_file()

        # Erstelle die Menüs
        self.create_commands()

        # Verknüpfe die ListSources mit den Tabellen
        self.table_open_bookings.data = self.daten.open_bookings
        self.table_bills.data = self.daten.bills
        self.table_allowance.data = self.daten.allowances
        self.table_insurance.data = self.daten.insurances
        self.table_institutions.data = self.daten.institutions
        self.table_persons.data = self.daten.persons
        self.form_beihilfe_bills.data = self.daten.allowances_bills
        self.form_pkv_bills.data = self.daten.insurances_bills


        # Zeige die Startseite
        self.show_mainpage(widget)


    def create_mainpage(self):
        """Erzeugt die Startseite der Anwendung."""

        # Container für die Startseite
        self.box_mainpage = toga.Box(style=style_box_column)
        self.sc_mainpage = toga.ScrollContainer(content=self.box_mainpage, style=style_scroll_container)
        
        # Bereich, der die Summe der offenen Buchungen anzeigt
        self.open_sum = SectionOpenSum(
            self.main_window,
            self.daten.open_sum
        )
        self.box_mainpage.add(self.open_sum)

        # Tabelle der offenen Buchungen
        self.table_open_bookings = TableOpenBookings(
            self.daten.open_bookings, 
            self.pay_receive,
            self.info_dialog_booking
        )
        self.box_mainpage.add(self.table_open_bookings)

        # Buttons zur Tabelle der offenen Buchungen
        self.mainpage_table_buttons = ButtonBox(
            labels  = ['Aktualisieren'],
            targets = [self.check_open_bills],
            ids     = ['refresh']
        )
        self.box_mainpage.add(self.mainpage_table_buttons)

        # Section: Rechnungen
        self.mainpage_section_bills = SectionBills(
            self.daten.bills,
            on_press_show   = self.show_list_bills,
            on_press_new    = self.show_form_bill_new
        )
        self.box_mainpage.add(self.mainpage_section_bills)
        
        if self.daten.allowance_active():
            # Section: Beihilfe-Einreichungen
            self.mainpage_section_allowance = SectionAllowance(
                self.daten.allowances_bills,
                on_press_show   = self.show_list_beihilfe,
                on_press_new    = self.show_form_beihilfe_new,
            )
            self.box_mainpage.add(self.mainpage_section_allowance)

        # Section: PKV-Einreichungen
        self.mainpage_section_insurance = SectionInsurance(
            self.daten.insurances_bills,
            on_press_show   = self.show_list_pkv,
            on_press_new    = self.show_form_pkv_new,
        )
        self.box_mainpage.add(self.mainpage_section_insurance)

        # Weitere Funktionen
        self.button_start_personen = toga.Button('Personen verwalten', style=style_button, on_press=self.show_list_persons)
        self.button_start_einrichtungen = toga.Button('Einrichtungen verwalten', style=style_button, on_press=self.show_list_institutions)
        self.button_start_archiv = ArchiveButton(self.daten.archivables, self.archivieren_bestaetigen)

        self.box_startseite_daten = toga.Box(style=style_section_daten)
        self.box_startseite_daten.add(self.button_start_personen)
        self.box_startseite_daten.add(self.button_start_einrichtungen)
        self.box_startseite_daten.add(self.button_start_archiv)
        self.box_mainpage.add(self.box_startseite_daten)


    def show_mainpage(self, widget):
        """Zurück zur Startseite."""

        # Archivieren-Button
        if self.daten.init.get('automatic_archive', False):
            self.box_startseite_daten.remove(self.button_start_archiv)
            self.commands.remove(self.cmd_archivieren)
            self.daten.archive()
        else:
            self.box_startseite_daten.add(self.button_start_archiv)
            self.commands.add(self.cmd_archivieren)

        # Bezahlstatus der offenen Rechnungen abfragen
        self.add_background_task(self.check_open_bills)
        self.main_window.content = self.sc_mainpage


    def create_list_bills(self):
        """Erzeugt die Seite, auf der die Rechnungen angezeigt werden."""

        # Container für die Seite mit der Liste der Rechnungen
        self.box_list_bills = toga.Box(style=style_box_column)

        # Überschrift und Button zurück
        self.list_bills_topbox = TopBox(
            label_text='Rechnungen', 
            style_box=style_box_column_rechnungen,
            target_back=self.show_mainpage
        )
        self.box_list_bills.add(self.list_bills_topbox)

        # Tabelle mit den Rechnungen
        self.table_bills = toga.Table(
            headings    = ['Info', 'Betrag', 'Bezahlt'],
            accessors   = ['info', 'betrag_euro', 'bezahlt_text'],
            data        = self.daten.bills,
            style       = style_table,
            on_select   = self.update_buttons,
            on_activate = self.info_dialog_booking
        )
        self.box_list_bills.add(self.table_bills)

        # ButtonBox mit den Buttons
        self.list_bills_buttons = ButtonBox(
            labels  = ['Löschen', 'Bearbeiten', 'Neu'],
            targets = [self.delete_bill, self.show_form_bill_edit, self.show_form_bill_new],
            ids     = ['delete_bill', 'edit_bill', 'new_bill'],
            enabled = [False, False, True]
        )  
        self.box_list_bills.add(self.list_bills_buttons)


    def show_list_bills(self, widget):
        """Zeigt die Seite mit der Liste der Rechnungen."""
        self.main_window.content = self.box_list_bills


    def create_form_bill(self):
        """ Erzeugt das Formular zum Erstellen und Bearbeiten einer Rechnung."""
        
        # Container für das Formular
        self.sc_form_bill = toga.ScrollContainer(style=style_scroll_container)
        self.box_form_bill = toga.Box(style=style_box_column)
        self.sc_form_bill.content = self.box_form_bill

        # Überschrift und Button zurück
        self.form_bill_topbox = TopBox(
            label_text='Neue Rechnung', 
            style_box=style_box_column_rechnungen,
            target_back=self.show_list_bills
        )
        self.box_form_bill.add(self.form_bill_topbox)

        self.box_form_bill.add(SubtextDivider('Pflichtfelder'))

        # Selection zur Auswahl der Person
        self.form_bill_person = LabeledSelection(
            label_text='Person:',
            data=self.daten.persons,
            accessor='name'
        )
        self.box_form_bill.add(self.form_bill_person)

        self.form_bill_rechnungsdatum = LabeledDateInput('Rechnungsdatum:')
        self.box_form_bill.add(self.form_bill_rechnungsdatum)
        self.form_bill_betrag = LabeledFloatInput('Betrag:', suffix='€')
        self.box_form_bill.add(self.form_bill_betrag)

        # Bereich zur Auswahl der Einrichtung
        self.form_bill_einrichtung = LabeledSelection(
            label_text='Einrichtung:',
            data=self.daten.institutions,
            accessor='name'
        )
        self.box_form_bill.add(self.form_bill_einrichtung)

        self.box_form_bill.add(SubtextDivider('Optionale Felder'))

        self.form_bill_abzug_beihilfe = LabeledFloatInput(
            'Abzug Beihilfe:',
            suffix      = '€',
            helptitle   = 'Abzug Beihilfe',
            helptext    = 'Gib den vollen Betrag der Rechnungspositionen an, die nicht beihilfefähig sind. ',
            window      = self.main_window,
        )
        self.box_form_bill.add(self.form_bill_abzug_beihilfe)

        self.form_bill_abzug_pkv = LabeledFloatInput(
            'Abzug PKV:',
            suffix      = '€',
            helptitle   = 'Abzug Private KV',
            helptext    = 'Gib den vollen Betrag der Rechnungspositionen an, die nicht von Deiner privaten KV übernommen werden. ',
            window      = self.main_window,
        )
        self.box_form_bill.add(self.form_bill_abzug_pkv)

        self.form_bill_bezahlt = LabeledSwitch('Bezahlt:')
        self.box_form_bill.add(self.form_bill_bezahlt)
        
        self.form_bill_buchungsdatum = LabeledDateInput(
            'Bezahldatum:',
            helptitle   = 'Bezahldatum',
            helptext    = 'Gib das Datum der bereits durchgeführten oder der geplanten Überweisung an.',
            window      = self.main_window,
        )
        self.box_form_bill.add(self.form_bill_buchungsdatum)

        self.form_bill_notiz = LabeledMultilineTextInput('Notiz:')
        self.box_form_bill.add(self.form_bill_notiz)

        # Bereich der Buttons
        self.form_bill_buttons = ButtonBox(
            labels=['Abbrechen', 'Speichern'],
            targets=[self.show_list_bills, self.save_bill],
        )
        self.box_form_bill.add(self.form_bill_buttons)


    def show_form_bill_new(self, widget):
        """Zeigt die Seite zum Erstellen einer Rechnung."""
        
        # Setze die Eingabefelder zurück
        self.form_bill_betrag.set_value('')
        self.form_bill_rechnungsdatum.set_value('')
        self.form_bill_abzug_beihilfe.set_value('')
        self.form_bill_abzug_pkv.set_value('')

        if len(self.daten.persons) > 0:
            self.form_bill_person.set_items(self.daten.persons)
            self.form_bill_person.set_value(self.daten.persons[0])
        
        if len(self.daten.institutions) > 0:
            self.form_bill_einrichtung.set_items(self.daten.institutions)
            self.form_bill_einrichtung.set_value(self.daten.institutions[0])

        self.form_bill_notiz.set_value('')
        self.form_bill_buchungsdatum.set_value('')
        self.form_bill_bezahlt.set_value(False)

        # Zurücksetzen von Flag und Überschrift
        self.flag_edit_bill = False
        self.form_bill_topbox.set_label('Neue Rechnung')

        if not self.daten.allowance_active():
            self.form_bill_abzug_beihilfe.hide()
        else:
            self.form_bill_abzug_beihilfe.show()

        # Zeige die Seite
        self.main_window.content = self.sc_form_bill

    
    def show_form_bill_edit(self, widget):
        """Zeigt die Seite zum Bearbeiten einer Rechnung."""

        # Ermittle den Index der ausgewählten Rechnung
        if widget in self.list_bills_buttons.buttons:
            self.edit_bill_id = table_index_selection(self.table_bills)
        else:
            print('Fehler: Aufrufendes Widget unbekannt.')
            return
        
        # Lade die Rechnung
        bill = self.daten.bills[self.edit_bill_id]

        # Ermittle den Index der Auswahlfelder
        institution_index = self.daten.get_element_index_by_dbid(self.daten.institutions, bill.einrichtung_id)
        person_index = self.daten.get_element_index_by_dbid(self.daten.persons, bill.person_id)

        # Auswahlfeld für die Einrichtung befüllen
        if len(self.daten.institutions) > 0:
            self.form_bill_einrichtung.set_items(self.daten.institutions)
            if institution_index is not None and institution_index in range(len(self.daten.institutions)):
                self.form_bill_einrichtung.set_value(self.daten.institutions[institution_index])
            else:      
                self.form_bill_einrichtung.set_value(self.daten.institutions[0])

        # Auswahlfeld für die Person befüllen
        if len(self.daten.persons) > 0:
            self.form_bill_person.set_items(self.daten.persons)
            if person_index is not None and person_index in range(len(self.daten.persons)):    
                self.form_bill_person.set_value(self.daten.persons[person_index])
            else:
                self.form_bill_person.set_value(self.daten.persons[0])

        # Befülle die Eingabefelder
        self.form_bill_betrag.set_value(bill.betrag)
        self.form_bill_rechnungsdatum.set_value(bill.rechnungsdatum)
        self.form_bill_abzug_beihilfe.set_value(bill.abzug_beihilfe)
        self.form_bill_abzug_pkv.set_value(bill.abzug_pkv)
        self.form_bill_notiz.set_value(bill.notiz)
        self.form_bill_buchungsdatum.set_value(bill.buchungsdatum)
        self.form_bill_bezahlt.set_value(bill.bezahlt)

        # Setze das Flag und die Überschrift
        self.flag_edit_bill = True
        self.form_bill_topbox.set_label('Rechnung bearbeiten')

        if not self.daten.allowance_active():
            self.form_bill_abzug_beihilfe.hide()
        else:
            self.form_bill_abzug_beihilfe.show()

        # Zeige die Seite
        self.main_window.content = self.sc_form_bill


    async def save_bill(self, widget):
        """Prüft die Eingaben und speichert die Rechnung."""

        nachricht = ''

        # Prüfe, ob ein Rechnungsdatum eingegeben wurde
        if not self.form_bill_rechnungsdatum.is_valid():
            nachricht += 'Bitte gib ein gültiges Rechnungsdatum ein.\n'

        # Prüfe, ob ein Betrag eingegeben wurde
        if not self.form_bill_betrag.is_valid():
            nachricht += 'Bitte gib einen gültigen Betrag ein.\n'

        # Prüfe, ob eine Person ausgewählt wurde
        if len(self.daten.persons) > 0:
            if self.form_bill_person.get_value() is None:
                nachricht += 'Bitte wähle eine Person aus.\n'

        # Prüfe, ob eine Einrichtung ausgewählt wurde
        if len(self.daten.institutions) > 0:
            if self.form_bill_einrichtung.get_value() is None:
                nachricht += 'Bitte wähle eine Einrichtung aus.\n'

        # Prüfe, ob der Abzug Beihilfe <= des Rechnungsbetrags ist
        if self.daten.allowance_active() and self.form_bill_abzug_beihilfe.get_value() > self.form_bill_betrag.get_value():
            nachricht += 'Der Abzug Beihilfe darf nicht größer als der Rechnungsbetrag sein.\n'

        # Prüfe, ob der Abzug PKV <= des Rechnungsbetrags ist
        if self.form_bill_abzug_pkv.get_value() > self.form_bill_betrag.get_value():
            nachricht += 'Der Abzug PKV darf nicht größer als der Rechnungsbetrag sein.\n'

        if not (self.form_bill_buchungsdatum.is_valid() or self.form_bill_buchungsdatum.is_empty()):
            nachricht += 'Bitte gib ein gültiges Buchungsdatum ein oder lasse das Feld leer.\n'
                
        if nachricht != '':
            self.main_window.error_dialog('Fehlerhafte Eingabe', nachricht)
            return
        
        # Beginn der Speicherroutine
        if not self.flag_edit_bill:
        # Erstelle eine neue Rechnung
            bill = {}
            bill['rechnungsdatum']      = self.form_bill_rechnungsdatum.get_value()
            if len(self.daten.persons) > 0:
                bill['person_id']       = self.form_bill_person.get_value().db_id
            bill['beihilfesatz']        = self.daten.get_allowance_by_name(self.form_bill_person.get_value().name)
            if len(self.daten.institutions) > 0:
                bill['einrichtung_id']  = self.form_bill_einrichtung.get_value().db_id
            bill['notiz']               = self.form_bill_notiz.get_value()
            bill['betrag']              = self.form_bill_betrag.get_value()
            bill['buchungsdatum']       = self.form_bill_buchungsdatum.get_value()
            bill['bezahlt']             = self.form_bill_bezahlt.get_value()
            bill['abzug_beihilfe']      = self.form_bill_abzug_beihilfe.get_value()
            bill['abzug_pkv']           = self.form_bill_abzug_pkv.get_value()

            # Übergebe die Rechnung dem Daten-Interface
            self.daten.new(BILL_OBJECT, bill)
        else:
            # flag ob verknüpfte Einreichungen aktualisiert werden können
            # True, wenn betrag oder beihilfesatz geändert wurde
            update_einreichung = False

            bill = dict_from_row(BILL_OBJECT, self.daten.bills[self.edit_bill_id])

            if bill['betrag'] != self.form_bill_betrag.get_value():
                update_einreichung = True
                bill['betrag'] = self.form_bill_betrag.get_value()

            if self.daten.allowance_active() and bill['beihilfesatz'] != self.daten.get_allowance_by_name(self.form_bill_person.get_value().name):
                update_einreichung = True
                bill['beihilfesatz'] = self.daten.get_allowance_by_name(self.form_bill_person.get_value().name)

            if self.daten.allowance_active() and bill['abzug_beihilfe'] != self.form_bill_abzug_beihilfe.get_value():
                update_einreichung = True
                bill['abzug_beihilfe'] = self.form_bill_abzug_beihilfe.get_value()

            if bill['abzug_pkv'] != self.form_bill_abzug_pkv.get_value():
                update_einreichung = True
                bill['abzug_pkv'] = self.form_bill_abzug_pkv.get_value()

            # Bearbeite die Rechnung
            if bill['rechnungsdatum'] != self.form_bill_rechnungsdatum.get_value():
                bill['rechnungsdatum'] = self.form_bill_rechnungsdatum.get_value()

            if len(self.daten.persons) > 0 and bill['person_id'] != self.form_bill_person.get_value().db_id:
                bill['person_id'] = self.form_bill_person.get_value().db_id

            if len(self.daten.institutions) > 0 and bill['einrichtung_id'] != self.form_bill_einrichtung.get_value().db_id:
                bill['einrichtung_id'] = self.form_bill_einrichtung.get_value().db_id

            if bill['notiz'] != self.form_bill_notiz.get_value():
                bill['notiz'] = self.form_bill_notiz.get_value()

            if bill['buchungsdatum'] != self.form_bill_buchungsdatum.get_value():
                bill['buchungsdatum'] = self.form_bill_buchungsdatum.get_value()

            if bill['bezahlt'] != self.form_bill_bezahlt.get_value():
                bill['bezahlt'] = self.form_bill_bezahlt.get_value()

            # Übergabe die geänderte Rechnung an das Daten-Interface
            self.daten.save(BILL_OBJECT, bill)

            # Flag zurücksetzen
            self.flag_edit_bill = False

            # Überprüfe ob eine verknüpfte Beihilfe-Einreichung existiert
            # und wenn ja, frage, ob diese aktualisiert werden soll
            if self.daten.allowance_active() and update_einreichung and bill['beihilfe_id'] is not None:
                if await self.main_window.question_dialog('Zugehörige Beihilfe-Einreichung aktualisieren', 'Soll die zugehörige Beihilfe-Einreichung aktualisiert werden?'):
                    self.daten.update_submit_amount(ALLOWANCE_OBJECT, self.daten.get_element_by_dbid(self.daten.allowances, bill['beihilfe_id']))

            # Überprüfe ob eine verknüpfte PKV-Einreichung existiert
            # und wenn ja, frage, ob diese aktualisiert werden soll
            if update_einreichung and bill['pkv_id'] is not None:
                if await self.main_window.question_dialog('Zugehörige PKV-Einreichung aktualisieren', 'Soll die zugehörige PKV-Einreichung aktualisiert werden?'):
                    self.daten.update_submit_amount(INSURANCE_OBJECT, self.daten.get_element_by_dbid(self.daten.insurances, bill['pkv_id']))

        # Zeigt die Liste der Rechnungen an.
        self.show_list_bills(widget)     


    async def delete_bill(self, widget):
        """Löscht eine Rechnung."""
        if self.table_bills.selection:
            if await self.main_window.question_dialog('Rechnung löschen', 'Soll die ausgewählte Rechnung wirklich gelöscht werden?'): 
                # Index der ausgewählten Rechnung ermitteln
                self.edit_bill_id = table_index_selection(self.table_bills)

                # Zwischenspeichern der Beihilfe- und PKV-IDs und auf None setzen um Pakete ggf. löschen zu können
                beihilfe_id = self.daten.bills[self.edit_bill_id].beihilfe_id
                pkv_id = self.daten.bills[self.edit_bill_id].pkv_id
                self.daten.bills[self.edit_bill_id].beihilfe_id = None
                self.daten.bills[self.edit_bill_id].pkv_id = None

                # Überprüfe, ob Einreichungen existieren
                if self.daten.allowance_active() and beihilfe_id is not None:
                    if await self.main_window.question_dialog('Zugehörige Beihilfe-Einreichung aktualisieren', 'Soll die zugehörige Beihilfe-Einreichung aktualisiert werden?'):
                        self.daten.update_submit_amount(ALLOWANCE_OBJECT, self.daten.get_element_by_dbid(self.daten.allowances, beihilfe_id))

                if pkv_id is not None:
                    if await self.main_window.question_dialog('Zugehörige PKV-Einreichung aktualisieren', 'Soll die zugehörige PKV-Einreichung aktualisiert werden?'):
                        self.daten.update_submit_amount(INSURANCE_OBJECT, self.daten.get_element_by_dbid(self.daten.insurances, pkv_id))

                # Rechnung löschen
                self.daten.delete(BILL_OBJECT, self.daten.bills[self.edit_bill_id])


    def create_list_institutions(self):
        """Erzeugt die Seite, auf der die Einrichtungen angezeigt werden."""

        # Container
        self.box_list_institutions = toga.Box(style=style_box_column)

        # Überschrift und Button zurück
        self.list_institutions_topbox = TopBox(
            label_text='Einrichtungen', 
            style_box=style_box_column_dunkel,
            target_back=self.show_mainpage
        )
        self.box_list_institutions.add(self.list_institutions_topbox)

        # Tabelle mit den Einrichtungen

        self.table_institutions = toga.Table(
            headings    = ['Name', 'Ort', 'Telefon'], 
            accessors   = ['name', 'ort', 'telefon'],
            data        = self.daten.institutions,
            style       = style_table,
            on_select   = self.update_buttons,
            on_activate = self.show_info_institution
        )
        self.box_list_institutions.add(self.table_institutions)

        # ButtonBox mit den Buttons
        self.list_institutions_buttons = ButtonBox(
            labels  = ['Bearbeiten', 'Neu', 'Löschen', 'Info'],
            targets = [self.show_form_institution_edit, self.show_form_institution_new, self.delete_institution, self.show_info_institution],
            ids     = ['edit_institution', 'new_institution', 'delete_institution', 'info_institution'],
            enabled = [False, True, False, False]
        )
        self.box_list_institutions.add(self.list_institutions_buttons)


    def show_list_institutions(self, widget):
        """Zeigt die Seite mit der Liste der Einrichtungen."""
        self.main_window.content = self.box_list_institutions


    def create_form_institution(self):
        """Erzeugt das Formular zum Erstellen und Bearbeiten einer Einrichtung."""
        self.sc_form_institution = toga.ScrollContainer(style=style_scroll_container)
        self.box_form_institution = toga.Box(style=style_box_column)
        self.sc_form_institution.content = self.box_form_institution

        # TopBox
        self.form_institution_topbox = TopBox(
            label_text='Neue Einrichtung',
            style_box=style_box_column_dunkel,
            target_back=self.show_list_institutions
        )
        self.box_form_institution.add(self.form_institution_topbox)

        # Bereich der Pflichteingaben
        self.box_form_institution.add(SubtextDivider('Pflichtfelder'))
        self.form_institution_name = LabeledTextInput('Name:')
        self.box_form_institution.add(self.form_institution_name)

        # Bereich der optionalen Eingabe
        self.box_form_institution.add(SubtextDivider('Optionale Felder'))
        self.form_institution_strasse = LabeledTextInput('Straße, Hausnr.:')
        self.form_institution_plz = LabeledPostalInput('PLZ:')
        self.form_institution_ort = LabeledTextInput('Ort:')
        self.form_institution_telefon = LabeledPhoneInput('Telefon:')
        self.form_institution_email = LabeledEmailInput('E-Mail:')
        self.form_institution_webseite = LabeledWebsiteInput('Webseite:')
        self.form_institution_notiz = LabeledMultilineTextInput('Notiz:')
        self.box_form_institution.add(self.form_institution_strasse)
        self.box_form_institution.add(self.form_institution_plz)
        self.box_form_institution.add(self.form_institution_ort)
        self.box_form_institution.add(self.form_institution_telefon)
        self.box_form_institution.add(self.form_institution_email)
        self.box_form_institution.add(self.form_institution_webseite)
        self.box_form_institution.add(self.form_institution_notiz)

        # ButtonBox
        self.form_institution_buttons = ButtonBox(
            labels=['Abbrechen', 'Speichern'],
            targets=[self.show_list_institutions, self.save_institution]
        )
        self.box_form_institution.add(self.form_institution_buttons)


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
        if self.table_institutions.selection:
            # Ermittle den Index der ausgewählten Rechnung
            self.edit_institution_id = table_index_selection(self.table_institutions)

            # Hole die Einrichtung
            institution = self.daten.institutions[self.edit_institution_id]
            
            # Befülle die Eingabefelder
            self.form_institution_name.set_value(institution.name)
            self.form_institution_strasse.set_value(institution.strasse)
            self.form_institution_plz.set_value(institution.plz)
            self.form_institution_ort.set_value(institution.ort)
            self.form_institution_telefon.set_value(institution.telefon)
            self.form_institution_email.set_value(institution.email)
            self.form_institution_webseite.set_value(institution.webseite)
            self.form_institution_notiz.set_value(institution.notiz)

            # Setze das Flag und die Überschrift
            self.flag_edit_institution = True
            self.form_institution_topbox.set_label('Einrichtung bearbeiten')

            # Zeige die Seite
            self.main_window.content = self.sc_form_institution


    async def save_institution(self, widget):
        """Prüft die Eingaben und speichert die Einrichtung."""
        nachricht = ''

        # Überprüfe die Eingaben auf Richtigkeit
        if widget in self.form_institution_buttons.buttons:

            # Prüfe, ob ein Name eingegeben wurde
            if self.form_institution_name.is_empty():
                nachricht += 'Bitte gib den Namen der Einrichtung an.\n'

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

        elif widget in self.init_institutions_buttons.buttons:

            # Prüfe, ob ein Name eingegeben wurde
            if self.init_institutions_name.is_empty():
                nachricht += 'Bitte gib den Namen der Einrichtung an.\n'

        if nachricht != '':
            self.main_window.error_dialog('Fehlerhafte Eingabe', nachricht[0:-2])
            return
        
        # Beginn der Speicherroutine
        if widget in self.form_institution_buttons.buttons and not self.flag_edit_institution:
        # Erstelle eine neue Einrichtung
            institution = {}
            institution['name'] = self.form_institution_name.get_value()
            institution['strasse'] = self.form_institution_strasse.get_value()
            institution['plz'] = self.form_institution_plz.get_value()
            institution['ort'] = self.form_institution_ort.get_value()
            institution['telefon'] = self.form_institution_telefon.get_value()
            institution['email'] = self.form_institution_email.get_value()
            institution['webseite'] = self.form_institution_webseite.get_value()
            institution['notiz'] = self.form_institution_notiz.get_value()

            # Speichere die Einrichtung in der Datenbank
            self.daten.new(INSTITUTION_OBJECT, institution)

            # Zeige die Liste der Einrichtungen
            self.show_list_institutions(widget)

        elif widget in self.form_institution_buttons.buttons and self.flag_edit_institution:
            print('+++ Einrichtung bearbeiten')
            institution = self.daten.institutions[self.edit_institution_id]

            # Bearbeite die Einrichtung
            if institution.name != self.form_institution_name.get_value():
                institution.name = self.form_institution_name.get_value()
            
            if institution.strasse != self.form_institution_strasse.get_value():
                institution.strasse = self.form_institution_strasse.get_value()

            if institution.plz != self.form_institution_plz.get_value():
                institution.plz = self.form_institution_plz.get_value()
            
            if institution.ort != self.form_institution_ort.get_value():
                institution.ort = self.form_institution_ort.get_value()
            
            if institution.telefon != self.form_institution_telefon.get_value():
                institution.telefon = self.form_institution_telefon.get_value()
            
            if institution.email != self.form_institution_email.get_value():
                institution.email = self.form_institution_email.get_value()
            
            if institution.webseite != self.form_institution_webseite.get_value():
                institution.webseite = self.form_institution_webseite.get_value()
            
            if institution.notiz != self.form_institution_notiz.get_value():
                institution.notiz = self.form_institution_notiz.get_value()

            # Übergabe der geänderten Einrichtung an das Daten-Interface
            self.daten.save(INSTITUTION_OBJECT, institution)

            # Flag zurücksetzen
            self.flag_edit_institution = False

            # Zeige die Liste der Einrichtungen
            self.show_list_institutions(widget)

        elif widget in self.init_institutions_buttons.buttons:
            print('+++ Einrichtung initialisieren')
            institution = {}
            institution['name'] = self.init_institutions_name.get_value()
            institution['ort'] = self.init_institutions_city.get_value()

            # Speichere die Einrichtung in der Datenbank
            self.daten.new(INSTITUTION_OBJECT, institution)

            # Show Success Message
            await self.main_window.info_dialog('Einrichtung gespeichert', institution.name + ' wurde erfolgreich gespeichert.')

            # Leere Eingabefelder
            self.init_institutions_name.set_value('')
            self.init_institutions_city.set_value('')

            # Aktualisiere die Initialisierungsseite
            self.update_init_page(widget)


    def create_info_institution(self):
        """Erzeugt die Seite, auf der die Details einer Einrichtung angezeigt werden."""

        # Container
        self.sc_info_institution = toga.ScrollContainer(style=style_scroll_container)
        self.box_info_institution = toga.Box(style=style_box_column)
        self.sc_info_institution.content = self.box_info_institution

        # Überschrift und Button zurück
        self.info_institution_topbox = TopBox(
            label_text='Einrichtung',
            style_box=style_box_column_dunkel,
            target_back=self.show_list_institutions
        )
        self.box_info_institution.add(self.info_institution_topbox)

        # Anzeige der Details
        self.info_institution_street = InfoLabel('Straße, Hausnr.:')
        self.info_institution_city = InfoLabel('PLZ, Ort:')
        self.info_institution_phone = InfoLabel('Telefon:')
        self.info_institution_email = InfoLabel('E-Mail:')
        self.info_institution_website = InfoLink('', self.show_webview)
        self.info_institution_note = InfoLabel('Notiz:')
        self.box_info_institution.add(self.info_institution_street)
        self.box_info_institution.add(self.info_institution_city)
        self.box_info_institution.add(self.info_institution_phone)
        self.box_info_institution.add(self.info_institution_email)
        self.box_info_institution.add(self.info_institution_website)
        self.box_info_institution.add(self.info_institution_note)

        # ButtonBox
        self.info_institution_buttons = ButtonBox(
            labels=['Bearbeiten', 'Löschen'],
            targets=[self.show_form_institution_edit, self.delete_institution]
        )
        self.box_info_institution.add(self.info_institution_buttons)


    def show_info_institution(self, widget, row=None):
        """Zeigt die Seite mit den Details einer Einrichtung."""
        # Prüfe, ob eine Einrichtung ausgewählt ist
        if self.table_institutions.selection:

            # Ermittle den Index der ausgewählten Einrichtung
            self.edit_institution_id = table_index_selection(self.table_institutions)

            # Hole die Einrichtung
            institution = self.daten.institutions[self.edit_institution_id]

            # Befülle die Labels mit den Details der Einrichtung
            # Die einzutragenden Werte können None sein, daher wird hier mit einem leeren String gearbeitet
            self.info_institution_topbox.set_label(institution.name)
            self.info_institution_street.set_value(institution.strasse)
            self.info_institution_city.set_value(institution.plz_ort)
            self.info_institution_phone.set_value(institution.telefon)
            self.info_institution_email.set_value(institution.email)
            
            # Nur wenn eine Webseite angegeben wurde, wird der Button angezeigt
            self.info_institution_website.hide_button()
            if institution.webseite:
                self.info_institution_website.show_button()
                self.info_institution_website.set_text(institution.webseite)
                
            self.info_institution_note.set_value(add_newlines(institution.notiz, 40))

            # Zeige die Info-Seite
            self.main_window.content = self.sc_info_institution

    
    async def delete_institution(self, widget):
        """Bestätigt das Löschen einer Einrichtung."""
        if self.table_institutions.selection:
            if await self.main_window.question_dialog('Einrichtung löschen', 'Soll die ausgewählte Einrichtung wirklich gelöscht werden?'):
                if not self.daten.deactivate(INSTITUTION_OBJECT, self.table_institutions.selection):
                    self.main_window.error_dialog(
                        'Fehler beim Löschen',
                        'Die Einrichtung wird noch in einer aktiven Rechnung verwendet und kann daher nicht gelöscht werden.'
                    )
                    return


    def create_list_persons(self):
        """Erzeugt die Seite, auf der die Personen angezeigt werden."""

        # Container
        self.box_list_persons = toga.Box(style=style_box_column)

        # Überschrift und Button zurück
        self.list_persons_topbox = TopBox(
            label_text='Personen', 
            style_box=style_box_column_dunkel,
            target_back=self.show_mainpage
        )
        self.box_list_persons.add(self.list_persons_topbox)

        # Tabelle mit den Personen
        self.table_persons = toga.Table(
            headings    = ['Name', 'Beihilfe'], 
            accessors   = ['name', 'beihilfesatz_prozent'],
            data        = self.daten.persons,
            style       = style_table,
            on_select   = self.update_buttons
        )
        self.box_list_persons.add(self.table_persons)

        # ButtonBox mit den Buttons
        self.list_persons_buttons = ButtonBox(
            labels  = ['Löschen', 'Bearbeiten', 'Neu'],
            targets = [self.delete_person, self.show_form_persons_edit, self.show_form_persons_new],
            ids     = ['delete_person', 'edit_person', 'new_person'],
            enabled = [False, False, True]
        )
        self.box_list_persons.add(self.list_persons_buttons)


    def show_list_persons(self, widget):
        """Zeigt die Seite mit der Liste der Personen."""
        
        if not self.daten.allowance_active() and 'Beihilfe' in self.table_persons.headings:
            self.table_persons.remove_column(1)
        elif self.daten.allowance_active() and 'Beihilfe' not in self.table_persons.headings:
            self.table_persons.insert_column(1, 'Beihilfe', 'beihilfesatz_prozent')

        self.main_window.content = self.box_list_persons


    def create_form_person(self):
        """Erzeugt das Formular zum Erstellen und Bearbeiten einer Person."""

        # Container
        self.sc_form_person = toga.ScrollContainer(style=style_scroll_container)
        self.box_form_person = toga.Box(style=style_box_column)
        self.sc_form_person.content = self.box_form_person

        # TopBox
        self.form_person_topbox = TopBox(
            label_text='Neue Person',
            style_box=style_box_column_dunkel,
            target_back=self.show_list_persons
        )
        self.box_form_person.add(self.form_person_topbox)

        self.box_form_person.add(SubtextDivider('Pflichtfelder'))

        self.form_person_name = LabeledTextInput('Name:')
        self.form_person_beihilfe = LabeledPercentInput('Beihilfe in %:')
        self.box_form_person.add(self.form_person_name)
        self.box_form_person.add(self.form_person_beihilfe)

        # ButtonBox
        self.form_person_buttons = ButtonBox(
            labels=['Abbrechen', 'Speichern'],
            targets=[self.show_list_persons, self.save_person]
        )
        self.box_form_person.add(self.form_person_buttons)


    def show_form_persons_new(self, widget):
        """Zeigt die Seite zum Erstellen einer Person."""
        # Setze die Eingabefelder zurück
        self.form_person_name.set_value('')
        self.form_person_beihilfe.set_value('')

        # Zurücksetzen des Flags und der Überschrift
        self.flag_edit_person = False
        self.form_person_topbox.set_label('Neue Person')

        if self.daten.allowance_active():
            self.form_person_beihilfe.show()
        else:
            self.form_person_beihilfe.hide()

        # Zeige die Seite
        self.main_window.content = self.sc_form_person


    def show_form_persons_edit(self, widget):
        """Zeigt die Seite zum Bearbeiten einer Person."""
            
        # Prüfe ob eine Person ausgewählt ist
        if self.table_persons.selection:
            # Ermittle den Index der ausgewählten Person
            self.edit_person_id = table_index_selection(self.table_persons)

            # Hole die Person
            person = self.daten.persons[self.edit_person_id]
            
            # Befülle die Eingabefelder
            self.form_person_name.set_value(person.name)

            if self.daten.allowance_active():
                self.form_person_beihilfe.show()
                self.form_person_beihilfe.set_value(person.beihilfesatz)
            else:
                self.form_person_beihilfe.hide()

            # Setze das Flag und die Überschrift
            self.flag_edit_person = True
            self.form_person_topbox.set_label('Person bearbeiten')

            # Zeige die Seite
            self.main_window.content = self.sc_form_person


    async def save_person(self, widget):
        """Prüft die Eingaben und speichert die Person."""

        # Überprüfe die Eingaben auf Richtigkeit

        nachricht = ''

        if widget in self.form_person_buttons.buttons:

            # Prüfe, ob ein Name eingegeben wurde
            if self.form_person_name.is_empty():
                nachricht += 'Bitte gib den Namen der Person an.\n'

            # Prüfe, ob eine gültige Prozentzahl eingegeben wurde
            if self.daten.allowance_active() and not self.form_person_beihilfe.is_valid():
                    nachricht += 'Bitte gib einen gültigen Beihilfesatz ein.\n'

        elif widget in self.init_persons_buttons.buttons:
                
                # Prüfe, ob ein Name eingegeben wurde
                if self.init_persons_name.is_empty():
                    nachricht += 'Bitte gib den Namen der Person an.\n'
    
                # Prüfe, ob eine gültige Prozentzahl eingegeben wurde
                if self.daten.allowance_active() and not self.init_persons_beihilfe.is_valid():
                        nachricht += 'Bitte gib einen gültigen Beihilfesatz ein.\n'

        if nachricht != '':
            self.main_window.error_dialog('Fehlerhafte Eingabe', nachricht[0:-2])
            return
        
        # Beginn der Speicherroutine
        if widget in self.form_person_buttons.buttons and not self.flag_edit_person:
            # Create a new person
            person = {}
            person['name'] = self.form_person_name.get_value()
            
            if self.daten.allowance_active():
                person['beihilfesatz'] = self.form_person_beihilfe.get_value()
            else:
                person['beihilfesatz'] = 0

            # Save the person 
            self.daten.new(PERSON_OBJECT, person)

            # Show the list of persons
            self.show_list_persons(widget)

        elif widget in self.form_person_buttons.buttons and  self.flag_edit_person:
            # Edit a person
            person = self.daten.persons[self.edit_person_id]

            # Edit the person
            if person['name'] != self.form_person_name.get_value():
                person['name'] = self.form_person_name.get_value()
            
            if self.daten.allowance_active() and person['beihilfesatz'] != self.form_person_beihilfe.get_value():
                person['beihilfesatz'] = self.form_person_beihilfe.get_value()

            # Save the person in the database
            self.daten.save(PERSON_OBJECT, person)

            # Reset flag
            self.flag_edit_person = False

            # Show the list of persons
            self.show_list_persons(widget)

        elif widget in self.init_persons_buttons.buttons:
            # Create a new person
            person = {}
            person['name'] = self.init_persons_name.get_value()
            
            if self.daten.allowance_active():
                person['beihilfesatz'] = self.init_persons_beihilfe.get_value()
            else:
                person['beihilfesatz'] = 0

            # Save the person 
            self.daten.new(PERSON_OBJECT, person)

            # Show Success Message
            await self.main_window.info_dialog('Person gespeichert', person['name'] + ' wurde erfolgreich gespeichert.')

            # Clear input fields
            self.init_persons_name.set_value('')
            self.init_persons_beihilfe.set_value('')

            # Update the initialization page
            self.update_init_page(widget)


    async def delete_person(self, widget):
        """Bestätigt das Löschen einer Person."""
        if self.table_persons.selection:
            if await self.main_window.question_dialog('Person löschen', 'Soll die ausgewählte Person wirklich gelöscht werden?'):
                if not self.daten.deactivate(PERSON_OBJECT, self.table_persons.selection):
                    self.main_window.error_dialog(
                        'Fehler beim Löschen',
                        'Die Person wird noch in einer aktiven Rechnung verwendet und kann daher nicht gelöscht werden.'
                    )
                    return   


    def create_list_beihilfe(self):
        """Erzeugt die Seite, auf der die Beihilfe-Einreichungen angezeigt werden."""
        
        # Container
        self.box_list_allowance = toga.Box(style=style_box_column)

        # Überschrift und Button zurück
        self.list_allowance_topbox = TopBox(
            label_text='Beihilfe-Einreichungen',
            style_box=style_box_column_beihilfe,
            target_back=self.show_mainpage
        )
        self.box_list_allowance.add(self.list_allowance_topbox)

        # Tabelle mit den Beihilfepaketen
        self.table_allowance = toga.Table(
            headings    = ['Datum', 'Betrag', 'Erstattet'], 
            accessors   = ['datum', 'betrag_euro', 'erhalten_text'],
            data        = self.daten.allowances,
            style       = style_table,
            on_select   = self.update_buttons,
            on_activate = self.info_dialog_booking
        )
        self.box_list_allowance.add(self.table_allowance)

        # Buttons
        self.list_allowance_buttons = ButtonBox(
            labels      = ['Reset', 'Erstattet', 'Neu'],
            targets     = [self.delete_beihilfe, self.pay_receive, self.show_form_beihilfe_new],
            ids         = ['reset_allowance', 'receive_allowance', 'new_allowance'],
            connections = [None, None, self.daten.allowances_bills],
            enabled     = [False, False, True]
        )
        self.box_list_allowance.add(self.list_allowance_buttons)


    def create_list_pkv(self):
        """Erzeugt die Seite, auf der die PKV-Einreichungen angezeigt werden."""

        # Container
        self.box_list_insurance = toga.Box(style=style_box_column)

        # Überschrift und Button zurück
        self.list_insurance_topbox = TopBox(
            label_text='PKV-Einreichungen',
            style_box=style_box_column_pkv,
            target_back=self.show_mainpage
        )
        self.box_list_insurance.add(self.list_insurance_topbox)

        # Tabelle mit den PKV-Einreichungen
        self.table_insurance = toga.Table(
            headings    = ['Datum', 'Betrag', 'Erstattet'], 
            accessors   = ['datum', 'betrag_euro', 'erhalten_text'],
            data        = self.daten.insurances,
            style       = style_table,
            on_select   = self.update_buttons,
            on_activate = self.info_dialog_booking
        )
        self.box_list_insurance.add(self.table_insurance)

        # Buttons
        self.list_insurance_buttons = ButtonBox(
            labels      = ['Reset', 'Erstattet', 'Neu'],
            targets     = [self.delete_pkv, self.pay_receive, self.show_form_pkv_new],
            ids         = ['reset_insurance', 'receive_insurance', 'new_insurance'],
            connections = [None, None, self.daten.insurances_bills],
            enabled     = [False, False, True]
        )
        self.box_list_insurance.add(self.list_insurance_buttons)


    def show_list_beihilfe(self, widget):
        """Zeigt die Seite mit der Liste der Beihilfepakete."""
        self.update_buttons(self.table_allowance)
        self.main_window.content = self.box_list_allowance

    
    def show_list_pkv(self, widget):
        """Zeigt die Seite mit der Liste der PKV-Einreichungen."""
        self.update_buttons(self.table_insurance)
        self.main_window.content = self.box_list_insurance

    
    def create_form_beihilfe(self):
        """Erzeugt das Formular zum Erstellen und Bearbeiten einer Beihilfe-Einreichung."""

        # Container
        self.sc_form_beihilfe = toga.ScrollContainer(style=style_scroll_container)
        self.box_form_beihilfe = toga.Box(style=style_box_column)
        self.sc_form_beihilfe.content = self.box_form_beihilfe

        # TopBox
        self.form_beihilfe_topbox = TopBox(
            label_text='Neue Beihilfe-Einreichung',
            style_box=style_box_column_beihilfe,
            target_back=self.show_list_beihilfe
        )
        self.box_form_beihilfe.add(self.form_beihilfe_topbox)

        self.box_form_beihilfe.add(SubtextDivider('Pflichtfelder'))

        # Bereich zur Auswahl der zugehörigen Rechnungen
        self.form_beihilfe_bills = toga.Table(
            headings        = ['Info', 'Betrag', 'Bezahlt'],
            accessors       = ['info', 'betrag_euro', 'bezahlt_text'],
            data            = self.daten.allowances_bills,
            multiple_select = True,
            on_select       = self.on_select_beihilfe_bills,
            on_activate     = self.info_dialog_booking,
            style           = style_table_auswahl
        )
        self.box_form_beihilfe.add(self.form_beihilfe_bills)

        self.form_beihilfe_datum = LabeledDateInput('Datum:')
        self.box_form_beihilfe.add(self.form_beihilfe_datum)

        self.box_form_beihilfe.add(SubtextDivider('Optionale Felder'))

        self.form_beihilfe_betrag = LabeledFloatInput('Betrag :', suffix='€', readonly=True)
        self.box_form_beihilfe.add(self.form_beihilfe_betrag)
        self.form_beihilfe_erhalten = LabeledSwitch('Erstattet:')
        self.box_form_beihilfe.add(self.form_beihilfe_erhalten)

        # ButtonBox
        self.form_beihilfe_buttons = ButtonBox(
            labels=['Abbrechen', 'Speichern'],
            targets=[self.show_list_beihilfe, self.save_beihilfe]
        )
        self.box_form_beihilfe.add(self.form_beihilfe_buttons)


    def create_form_pkv(self):
        """Erzeugt das Formular zum Erstellen und Bearbeiten einer PKV-Einreichung."""

        # Container
        self.sc_form_pkv = toga.ScrollContainer(style=style_scroll_container)
        self.box_form_pkv = toga.Box(style=style_box_column)
        self.sc_form_pkv.content = self.box_form_pkv

        # TopBox
        self.form_pkv_topbox = TopBox(
            label_text='Neue PKV-Einreichung',
            style_box=style_box_column_pkv,
            target_back=self.show_list_pkv
        )
        self.box_form_pkv.add(self.form_pkv_topbox)

        self.box_form_pkv.add(SubtextDivider('Pflichtfelder'))

        # Bereich zur Auswahl der zugehörigen Rechnungen
        self.form_pkv_bills = toga.Table(
            headings        = ['Info', 'Betrag', 'Bezahlt'],
            accessors       = ['info', 'betrag_euro', 'bezahlt_text'],
            data            = self.daten.insurances_bills,
            multiple_select = True,
            on_select       = self.on_select_pkv_bills,   
            on_activate     = self.info_dialog_booking,
            style           = style_table_auswahl
        )
        self.box_form_pkv.add(self.form_pkv_bills)

        self.form_pkv_datum = LabeledDateInput('Datum:')
        self.box_form_pkv.add(self.form_pkv_datum)

        self.box_form_pkv.add(SubtextDivider('Optionale Felder'))

        self.form_pkv_betrag = LabeledFloatInput('Betrag:',  suffix='€', readonly=True)
        self.box_form_pkv.add(self.form_pkv_betrag)
        self.form_pkv_erhalten = LabeledSwitch('Erstattet:')
        self.box_form_pkv.add(self.form_pkv_erhalten)

        # ButtonBox
        self.form_pkv_buttons = ButtonBox(
            labels=['Abbrechen', 'Speichern'],
            targets=[self.show_list_pkv, self.save_pkv]
        )
        self.box_form_pkv.add(self.form_pkv_buttons)


    def on_select_beihilfe_bills(self, widget):
        """Ermittelt die Summe des Beihilfe-Anteils der ausgewählten Rechnungen."""
        summe = 0
        for sel in widget.selection:
            bill = self.daten.get_element_by_dbid(self.daten.bills, sel.db_id)
            summe += (bill.betrag - bill.abzug_beihilfe) * bill.beihilfesatz / 100
        self.form_beihilfe_betrag.set_value(summe)


    def on_select_pkv_bills(self, widget):
        """Ermittelt die Summe des PKV-Anteils der ausgewählten Rechnungen."""
        summe = 0
        for sel in widget.selection:
            bill = self.daten.get_element_by_dbid(self.daten.bills, sel.db_id)
            if self.daten.allowance_active():
                summe += (bill.betrag - bill.abzug_pkv) * (100 - bill.beihilfesatz) / 100
            else:
                summe += bill.betrag - bill.abzug_pkv
        self.form_pkv_betrag.set_value(summe)


    def show_form_beihilfe_new(self, widget):
        """Zeigt die Seite zum Erstellen eines Beihilfepakets."""
        # Setze die Eingabefelder zurück
        self.on_select_beihilfe_bills(self.form_beihilfe_bills)

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
        self.on_select_pkv_bills(self.form_pkv_bills)
        self.form_pkv_datum.set_value(datetime.now())
        self.form_pkv_erhalten.set_value(False)

        # Zurücksetzen des Flags und der Überschrift
        self.flag_edit_pkv = False
        self.form_pkv_topbox.set_label('Neue PKV-Einreichung')

        # Tabelleninhalt aktualisieren
        if not self.daten.allowance_active() and 'Beihilfe' in self.form_pkv_bills.headings:
            self.form_pkv_bills.remove_column(2)
        elif self.daten.allowance_active() and 'Beihilfe' not in self.form_pkv_bills.headings:
            self.form_pkv_bills.insert_column(2, 'Beihilfe', 'beihilfesatz_prozent')

        # Zeige die Seite
        self.main_window.content = self.sc_form_pkv


    def save_beihilfe(self, widget):
        """Prüft die Eingaben und speichert die Beihilfe-Einreichung."""

        nachricht = ''

        # Prüfe das Datum
        if not self.form_beihilfe_datum.is_valid():
            nachricht += 'Bitte gib ein gültiges Datum ein.\n'

        # Prüfe ob Rechnungen ausgewählt wurden
        if not self.form_beihilfe_bills.selection:
            nachricht += 'Es wurde keine Rechnung zum Einreichen ausgewählt.\n'
            self.form_beihilfe_betrag.set_value(0)

        if nachricht != '':
            self.main_window.error_dialog('Fehlerhafte Eingabe', nachricht)
            return
        
        # Beginn der Speicherroutine
        if not self.flag_edit_beihilfe:
            # Erstelle ein neues Beihilfepaket
            allowance = {}
            allowance['datum'] = self.form_beihilfe_datum.get_value()
            allowance['betrag'] = self.form_beihilfe_betrag.get_value()
            allowance['erhalten'] = self.form_beihilfe_erhalten.get_value()

            # IDs der Rechnungen in Liste speichern
            bill_db_ids = []
            for sel in self.form_beihilfe_bills.selection:
                bill_db_ids.append(sel.db_id)

            # Speichere das Beihilfepaket in der Datenbank
            self.daten.new(ALLOWANCE_OBJECT, allowance, bill_db_ids=bill_db_ids)

        # Wechsel zur Startseite
        self.show_mainpage(widget)


    def save_pkv(self, widget):
        """Prüft die Eingaben und speichert die PKV-Einreichung."""

        nachricht = ''

        # Prüfe das Datum
        if not self.form_pkv_datum.is_valid():
            nachricht += 'Bitte gib ein gültiges Datum ein.\n'

        # Prüfe ob Rechnungen ausgewählt wurden
        if not self.form_pkv_bills.selection:
            nachricht += 'Es wurde keine Rechnung zum Einreichen ausgewählt.\n'
            self.form_pkv_betrag.set_value(0)

        if nachricht != '':
            self.main_window.error_dialog('Fehlerhafte Eingabe', nachricht)
            return

        # Beginn der Speicherroutine
        if not self.flag_edit_pkv:
            # Erstelle ein neues PKV-Paket
            insurance = {}
            insurance['datum'] = self.form_pkv_datum.get_value()
            insurance['betrag'] = self.form_pkv_betrag.get_value()
            insurance['erhalten'] = self.form_pkv_erhalten.get_value()

            # IDs der Rechnungen in Liste speichern
            bill_db_ids = []
            for sel in self.form_pkv_bills.selection:
                bill_db_ids.append(sel.db_id)

            # Speichere das PKV-Paket in der Datenbank
            self.daten.new(INSURANCE_OBJECT, insurance, bill_db_ids=bill_db_ids)

        # Wechsel zur Startseite
        self.show_mainpage(widget)


    async def delete_beihilfe(self, widget):
        """Löscht eine Beihilfe-Einreichung."""
        if self.table_allowance.selection:
            if await self.main_window.question_dialog('Beihilfe-Einreichung zurücksetzen', 'Soll die ausgewählte Beihilfe-Einreichung wirklich zurückgesetzt werden? Die zugehörigen Rechnungen müssen dann erneut eingereicht werden.'):
                self.daten.delete(ALLOWANCE_OBJECT, self.table_allowance.selection)


    async def delete_pkv(self, widget):
        """Löscht eine PKV-Einreichung."""
        if self.table_insurance.selection:
            if await self.main_window.question_dialog('PKV-Einreichung zurücksetzen', 'Soll die ausgewählte PKV-Einreichung wirklich zurückgesetzt werden? Die zugehörigen Rechnungen müssen dann erneut eingereicht werden.'):
                self.daten.delete(INSURANCE_OBJECT, self.table_insurance.selection)
            

    async def archivieren_bestaetigen(self, widget):
        """Bestätigt das Archivieren von Buchungen."""
        if await self.main_window.question_dialog('Buchungen archivieren', 'Sollen alle archivierbaren Buchungen wirklich archiviert werden? Sie werden dann in der App nicht mehr angezeigt.'):
            self.daten.archive()
            self.show_mainpage(widget)
            

    async def pay_receive(self, widget):
        """Bestätigt die Bezahlung einer Rechnung oder Erstattung einer Einreichung."""

        match widget.id:
            case 'receive_allowance':
                db_id = self.table_allowance.selection.db_id
                typ = 'Beihilfe'
            case 'receive_insurance':
                db_id = self.table_insurance.selection.db_id
                typ = 'PKV'
            case _:
                db_id = self.daten.open_bookings[int(widget.id)].db_id
                typ = self.daten.open_bookings[int(widget.id)].typ

        match typ:
            case 'Rechnung':
                booking = self.daten.get_element_by_dbid(self.daten.bills, db_id)
                if await self.main_window.question_dialog('Rechnung bezahlt?', 'Soll die ausgewählte Rechnung wirklich als bezahlt markiert werden?'):
                    self.daten.pay_receive(BILL_OBJECT, booking)
            case 'Beihilfe':
                booking = self.daten.get_element_by_dbid(self.daten.allowances, db_id)
                if await self.main_window.question_dialog('Beihilfe-Einreichung erstattet?', 'Soll die ausgewählte Beihilfe wirklich als erstattet markiert werden?'):
                    self.daten.pay_receive(ALLOWANCE_OBJECT, booking)
            case 'PKV':
                booking = self.daten.get_element_by_dbid(self.daten.insurances, db_id)
                if await self.main_window.question_dialog('PKV-Einreichung erstattet?', 'Soll die ausgewählte PKV-Einreichung wirklich als erstattet markiert werden?'):                        
                    self.daten.pay_receive(INSURANCE_OBJECT, booking)


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
            'Einreichungen anzeigen',
            tooltip = 'Zeigt die Liste der Beihilfe-Einreichungen an.',
            group = gruppe_beihilfe,
            section = 0,
            order = 10,
            enabled=True
        )

        self.cmd_beihilfepakete_neu = toga.Command(
            self.show_form_beihilfe_new,
            'Neue Einreichung',
            tooltip = 'Erstellt eine neue Beihilfe-Einreichung.',
            group = gruppe_beihilfe,
            section = 0,
            order = 20,
            enabled=False
        )

        gruppe_pkv = toga.Group('Private KV', order = 3)

        self.cmd_pkvpakete_anzeigen = toga.Command(
            self.show_list_pkv,
            'Einreichungen anzeigen',
            tooltip = 'Zeigt die Liste der PKV-Einreichungen an.',
            group = gruppe_pkv,
            section = 1,
            order = 30,
            enabled=True
        )

        self.cmd_pkvpakete_neu = toga.Command(
            self.show_form_pkv_new,
            'Neue Einreichung',
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
            enabled = True
        )

        self.cmd_einrichtungen_neu = toga.Command(
            self.show_form_institution_new,
            'Neue Einrichtung',
            tooltip = 'Erstellt eine neue Einrichtung.',
            group = gruppe_einrichtungen,
            section = 0,
            order = 20,
            enabled = True
        )

        gruppe_tools = toga.Group('Tools', order = 6)

        self.cmd_archivieren = toga.Command(
            self.archivieren_bestaetigen,
            'Archivieren',
            tooltip = 'Archiviere alle bezahlten und erhaltenen Buchungen.',
            group = gruppe_tools,
            order = 5,
            section = 1,
            enabled = False
        )

        self.cmd_datenschutz = toga.Command(
            self.show_webview,
            'Datenschutz',
            tooltip = 'Öffne die Datenschutzerklärung.',
            group = gruppe_tools,
            order = 15,
            section = 2,
            enabled = True
        )

        self.cmd_reset = toga.Command(
            self.reset_app,
            'Zurücksetzen',
            tooltip = 'Setzt die Anwendung zurück.',
            group = gruppe_tools,
            order = 20,
            section = 2,
            enabled=True
        )

        self.cmd_settings = toga.Command(
            self.show_settings,
            'Einstellungen',
            tooltip = 'Öffnet die Einstellungen.',
            order = 7,
            enabled=True
        )

        self.cmd_statistics = toga.Command(
            self.show_statistics,
            'Statistiken',
            tooltip = 'Öffnet die Statistiken.',
            order = 8,
            enabled=True
        )

        # Add listeners to the commands
        self.daten.archivables.add_listener(ArchiveCommandListener(self.cmd_archivieren, self.daten.archivables))
        self.daten.allowances_bills.add_listener(CommandListener(self.cmd_beihilfepakete_neu, self.daten.allowances_bills))
        self.daten.insurances_bills.add_listener(CommandListener(self.cmd_pkvpakete_neu, self.daten.insurances_bills))

        # Erstelle die Menüleiste
        self.commands.add(self.cmd_rechnungen_anzeigen)
        self.commands.add(self.cmd_rechnungen_neu)
        if self.daten.allowance_active():
            self.commands.add(self.cmd_beihilfepakete_anzeigen)
            self.commands.add(self.cmd_beihilfepakete_neu)
        self.commands.add(self.cmd_pkvpakete_anzeigen)
        self.commands.add(self.cmd_pkvpakete_neu)
        self.commands.add(self.cmd_personen_anzeigen)
        self.commands.add(self.cmd_personen_neu)
        self.commands.add(self.cmd_einrichtungen_anzeigen)
        self.commands.add(self.cmd_einrichtungen_neu)
        self.commands.add(self.cmd_settings)
        self.commands.add(self.cmd_archivieren)
        self.commands.add(self.cmd_reset)
        self.commands.add(self.cmd_datenschutz)
        self.commands.add(self.cmd_statistics)


    def startup(self):
        """Laden der Daten, Erzeugen der GUI-Elemente und des Hauptfensters."""

        # Erstelle das Hauptfenster
        self.main_window = toga.MainWindow(title=self.formal_name)

        # Daten-Interface initialisieren
        self.daten = DataInterface()

        # Erzeuge alle GUI-Elemente
        self.create_init_page()
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
        self.create_settings()
        self.create_statistics()

        # Zeige die Startseite oder die Init-Seite
        if self.daten.is_first_start():
            self.show_init_page(None)
        else:
            self.create_commands()
            self.show_mainpage(None)
        
        self.main_window.show()


    async def reset_app(self, widget):
        """Setzt die Anwendung zurück."""

        # 1. Abfrage ob wirklich zurückgesetzt werden soll
        if await self.main_window.question_dialog('Zurücksetzen', 'Soll die Anwendung wirklich zurückgesetzt werden? Es werden alle Daten gelöscht.'):
            # 2. Abfrage ob wirklich zurückgesetzt werden soll
            if await self.main_window.question_dialog('Ganz sicher?', 'Wirklich zurücksetzen? Es werden alle Daten gelöscht.'):
                print('+++ Kontolupe.reset_app: Zurücksetzen doppelt bestätigt.')
                self.daten.reset()
                self.commands.clear()  
                self.show_init_page(None)
        

def main():
    """Hauptschleife der Anwendung"""
    return Kontolupe()