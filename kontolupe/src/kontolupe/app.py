"""
Behalte den Überblick über Deine Rechnungen, Beihilfe- und PKV-Erstattungen.

Mit Kontolupe kannst Du Deine Gesundheits-Rechnungen erfassen und verwalten.
Du kannst Beihilfe- und PKV-Einreichungen erstellen und die Erstattungen
überwachen. Die App ist für die private Nutzung kostenlos.
"""

import toga
from toga.style.pack import COLUMN, LEFT, RIGHT, ROW, TOP, BOTTOM, CENTER, Pack
from toga.sources import ListSource
from toga.validators import *
from kontolupe.buchungen import *
from datetime import datetime

# Allgemeine Styles
style_box_column                = Pack(direction=COLUMN, alignment=CENTER)
style_box_row                   = Pack(direction=ROW, alignment=CENTER)
style_scroll_container          = Pack(flex=1)
style_label_h1                  = Pack(font_size=14, font_weight='bold', text_align=CENTER, padding=5, padding_top=20, color='#222222')
style_label_h2                  = Pack(font_size=11, font_weight='bold', text_align=CENTER, padding=5, padding_top=20, color='#222222')
style_label                     = Pack(font_weight='normal', text_align=LEFT, padding_left=5, padding_right=5, color='#222222')
style_label_center              = Pack(font_weight='normal', text_align=CENTER, padding_left=5, padding_right=5, color='#222222')
style_button                    = Pack(flex=1, padding=5, color='#222222')
style_input                     = Pack(flex=1, padding=5, color='#222222') 
style_label_input               = Pack(flex=1, padding=5, text_align=LEFT, color='#222222')
style_table                     = Pack(flex=1, padding=5, color='#222222')
style_switch                    = Pack(flex=1, padding=5, color='#222222')

# Spezifische Styles
style_box_offene_buchungen      = Pack(direction=COLUMN, alignment=CENTER, background_color='#368ba8')
style_start_summe               = Pack(font_size=14, font_weight='bold', text_align=CENTER, padding=20, color='#ffffff', background_color='#368ba8')
style_table_offene_buchungen    = Pack(padding=5, height=200, color='#222222')
style_table_auswahl             = Pack(padding=5, height=200, flex=1, color='#222222')

class Kontolupe(toga.App):
    """Die Hauptklasse der Anwendung."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        """Initialisierung der Anwendung."""

        # Hilfsvariablen zur Bearbeitung von Rechnungen
        self.flag_bearbeite_rechnung = False
        self.rechnung_b_id = 0

        # Hilfsvariablen zur Bearbeitung von Einrichtungen
        self.flag_bearbeite_einrichtung = False
        self.einrichtung_b_id = 0

        # Hilfsvariablen zur Bearbeitung der Beihilfe-Pakete
        self.flag_bearbeite_beihilfepaket = False
        self.beihilfepaket_b_id = 0

        # Hilfsvariablen zur Bearbeitung der PKV-Pakete
        self.flag_bearbeite_pkvpaket = False
        self.pkvpaket_b_id = 0


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
                self.label_start_archiv_offen.text = 'Keine archivierbaren Buchungen vorhanden.'
            case 1:
                self.button_start_archiv.enabled = True
                self.cmd_archivieren.enabled = True
                self.label_start_archiv_offen.text = '1 archivierbare Buchung vorhanden.'
            case _:
                self.button_start_archiv.enabled = True
                self.cmd_archivieren.enabled = True
                self.label_start_archiv_offen.text = '{} archivierbare Buchungen vorhanden.'.format(anzahl)

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
    

    def pruefe_zahl(self, widget):
        """Prüft, ob die Eingabe eine Zahl ist und korrigiert sie entsprechend."""

        # Entferne alle Zeichen, die keine Zahl von 0 bis 9 oder ein , sind.
        eingabe = ''.join(c for c in widget.value if c in '0123456789,')
        
        # entferne alle , außer dem letzten
        if eingabe.count(',') > 1:
            eingabe = eingabe.replace(',', '', eingabe.count(',') - 1)

        widget.value = eingabe

        # replace , with .
        eingabe = eingabe.replace(',', '.')

        try:
            float(eingabe)
            return True
        except ValueError:
            #widget.value = ''
            #self.main_window.error_dialog('Fehler', 'Kein gültiger Betrag eingegeben.')
            return False

    
    def pruefe_prozent(self, widget):
        """Prüft, ob die Eingabe eine ganze Zahl zwischen 0 und 100 ist und korrigiert sie entsprechend."""

        # Entferne alle Zeichen, die keine Zahl von 0 bis 9 oder ein , sind.
        eingabe = ''.join(c for c in widget.value if c in '0123456789')
        widget.value = eingabe

        try:
            zahl = int(eingabe)
            if zahl > 100:
                widget.value = '100'
            if zahl not in range(0, 101, 5):
                #self.main_window.info_dialog('Bitte überprüfen', 'Der Beihilfesatz ist üblicherweise ein Vielfaches von 5 und nicht 0 oder 100.')
                return False
            return True
        except ValueError:
            widget.value = ''
            #self.main_window.error_dialog('Fehler', 'Kein gültiger Prozentsatz eingegeben.')
            return False


    def pruefe_datum(self, widget):
        """ Prüft, ob die Eingabe ein gültiges Datum ist und korrigiert die Eingabe."""

        eingabe = ''.join(c for c in widget.value if c in '0123456789.')
        widget.value = eingabe

        if widget.value == '':
            return True

        error = False            
        # check if there are 3 parts
        if widget.value.count('.') != 2:
            # check if the entry is numeric
            if not widget.value.isnumeric():
                error = True
            # check if the entry is 6 digits long and insert 20 after the first four digits
            elif len(widget.value) == 6:
                widget.value = widget.value[:4] + '20' + widget.value[4:]
            elif len(widget.value) != 8:
                error = True
        
            if not error:
                # add a . after the first two digits and after the second two digits
                widget.value = widget.value[:2] + '.' + widget.value[2:4] + '.' + widget.value[4:]
            
            # check if the date is valid
            try:
                datetime.strptime(widget.value, '%d.%m.%Y')
            except ValueError:
                error = True

        else:
            # check if all parts are numbers
            parts = widget.value.split('.')
            for part in parts:
                if not part.isnumeric():
                    error = True
                    break
            
            # first and second part must be two digits long, if not add a leading 0
            if not error and len(parts[0]) != 2:
                parts[0] = '0' + parts[0]
            if not error and len(parts[1]) != 2:
                parts[1] = '0' + parts[1]
            # third part must be 4 or 2 digits long. if 2 digits long, add 20 to the beginning
            if not error and len(parts[2]) == 2:
                parts[2] = '20' + parts[2]
            elif not error and len(parts[2]) != 4:
                error = True

            # put the parts back together
            if not error:
                widget.value = '.'.join(parts)
            
            # check if the date is valid
            try:
                datetime.strptime(widget.value, '%d.%m.%Y')
            except ValueError:
                error = True

        # if error:
        #     widget.value = ''

        return not error
    

    def pruefe_plz(self, widget):
        """Prüft, ob die Eingabe eine gültige Postleitzahl ist und korrigiert sie entsprechend."""

        # Entferne alle Zeichen, die keine Zahl von 0 bis 9 sind.
        eingabe = ''.join(c for c in widget.value if c in '0123456789')
        widget.value = eingabe

        if widget.value == '':
            return True

        if len(widget.value) != 5:
            return False
        

    def pruefe_email(self, widget):
        """Prüft, ob die Eingabe eine gültige E-Mail-Adresse ist und korrigiert sie entsprechend."""

        # Entferne alle Zeichen, die nicht in einer E-Mail-Adresse vorkommen dürfen
        eingabe = ''.join(c for c in widget.value if c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@.-_')
        widget.value = eingabe

        if widget.value == '':
            return True

        # Überprüfe ob die Struktur der Mail-Adresse korrekt ist
        if eingabe.count('@') != 1:
            return False
        if eingabe.count('.') < 1:
            return False
        if eingabe.count('.') > 2:
            return False
        if eingabe[0] == '@':
            return False   
        if eingabe[-1] == '@':
            return False
        if eingabe[0] == '.': 
            return False
        if eingabe[-1] == '.':
            return False
        if eingabe[-1] == '-':
            return False
        if eingabe[-1] == '_':
            return False
        
        return True
    

    def pruefe_webseite(self, widget):
        """Prüft, ob die Eingabe eine gültige Webseite ist und korrigiert sie entsprechend."""

        # Entferne alle Zeichen, die nicht in einer Webadresse vorkommen dürfen
        eingabe = ''.join(c for c in widget.value if c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@.-_/:?%=&')
        widget.value = eingabe

        if widget.value == '':
            return True

        # Überprüfe ob die Struktur der Webadresse korrekt ist
        if eingabe.count('.') < 1:
            return False
        if eingabe[0] == '.':
            return False
        if eingabe[-1] == '.':
            return False
        
        return True


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
        self.box_startseite_tabelle_offene_buchungen = toga.Box(style=style_box_column)
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
        label_start_rechnungen = toga.Label('Rechnungen', style=style_label_h2)
        self.label_start_rechnungen_offen = toga.Label('', style=style_label_center)
        button_start_rechnungen_anzeigen = toga.Button('Anzeigen', on_press=self.zeige_seite_liste_rechnungen, style=style_button)
        button_start_rechnungen_neu = toga.Button('Neu', on_press=self.zeige_seite_formular_rechnungen_neu, style=style_button)
        box_startseite_rechnungen_buttons = toga.Box(style=style_box_row)
        box_startseite_rechnungen_buttons.add(button_start_rechnungen_anzeigen)
        box_startseite_rechnungen_buttons.add(button_start_rechnungen_neu)
        box_startseite_rechnungen = toga.Box(style=style_box_column)
        box_startseite_rechnungen.add(label_start_rechnungen)
        box_startseite_rechnungen.add(self.label_start_rechnungen_offen)
        box_startseite_rechnungen.add(box_startseite_rechnungen_buttons)
        self.box_startseite.add(box_startseite_rechnungen)

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
            case self.formular_beihilfe_tabelle_rechnungen:
                typ = 'Rechnung'
                for rechnung in self.rechnungen_liste:
                    if rechnung.db_id == row.db_id:
                        element = rechnung
                        break
            case self.formular_pkv_tabelle_rechnungen:
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


    def erzeuge_seite_liste_rechnungen(self):
        """Erzeugt die Seite, auf der die Rechnungen angezeigt werden."""
        self.box_seite_liste_rechnungen = toga.Box(style=style_box_column)
        self.box_seite_liste_rechnungen.add(toga.Button('Zurück', on_press=self.zeige_startseite))
        self.box_seite_liste_rechnungen.add(toga.Label('Rechnungen', style=style_label_h1))

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
        self.liste_rechnungen_button_loeschen = toga.Button('Löschen', on_press=self.bestaetige_rechnung_loeschen, style=style_button, enabled=False)
        self.liste_rechnungen_button_bearbeiten = toga.Button('Bearbeiten', on_press=self.zeige_seite_formular_rechnungen_bearbeiten, style=style_button, enabled=False)
        self.liste_rechnungen_button_neu = toga.Button('Neu', on_press=self.zeige_seite_formular_rechnungen_neu, style=style_button)
        box_seite_liste_rechnungen_buttons.add(self.liste_rechnungen_button_loeschen)
        box_seite_liste_rechnungen_buttons.add(self.liste_rechnungen_button_bearbeiten)
        box_seite_liste_rechnungen_buttons.add(self.liste_rechnungen_button_neu)
        self.box_seite_liste_rechnungen.add(box_seite_liste_rechnungen_buttons)    


    def zeige_seite_liste_rechnungen(self, widget):
        """Zeigt die Seite mit der Liste der Rechnungen."""
        self.update_app(widget)
        self.main_window.content = self.box_seite_liste_rechnungen


    def erzeuge_seite_formular_rechnungen(self):
        """ Erzeugt das Formular zum Erstellen und Bearbeiten einer Rechnung."""
        self.scroll_container_formular_rechnungen = toga.ScrollContainer(style=style_scroll_container)
        self.box_seite_formular_rechnungen = toga.Box(style=style_box_column)
        self.scroll_container_formular_rechnungen.content = self.box_seite_formular_rechnungen
        self.box_seite_formular_rechnungen.add(toga.Button('Zurück', on_press=self.zeige_seite_liste_rechnungen, style=style_button))
        self.label_formular_rechnungen = toga.Label('Neue Rechnung', style=style_label_h1)
        self.box_seite_formular_rechnungen.add(self.label_formular_rechnungen)

        # Bereich zur Eingabe des Rechnungsdatums
        box_formular_rechnungen_rechnungsdatum = toga.Box(style=style_box_row)
        box_formular_rechnungen_rechnungsdatum.add(toga.Label('Rechnungsdatum: ', style=style_label_input))
        self.input_formular_rechnungen_rechnungsdatum = toga.TextInput(style=style_input, on_lose_focus=self.pruefe_datum, placeholder='TT.MM.JJJJ')
        box_formular_rechnungen_rechnungsdatum.add(self.input_formular_rechnungen_rechnungsdatum)
        self.box_seite_formular_rechnungen.add(box_formular_rechnungen_rechnungsdatum)

        box_formular_rechnungen_betrag = toga.Box(style=style_box_row)
        box_formular_rechnungen_betrag.add(toga.Label('Betrag in €: ', style=style_label_input))
        self.input_formular_rechnungen_betrag = toga.TextInput(style=style_input, on_lose_focus=self.pruefe_zahl)
        box_formular_rechnungen_betrag.add(self.input_formular_rechnungen_betrag)
        self.box_seite_formular_rechnungen.add(box_formular_rechnungen_betrag)

        # Bereich zur Auswahl der Einrichtung
        box_formular_rechnungen_einrichtung = toga.Box(style=style_box_row)
        box_formular_rechnungen_einrichtung.add(toga.Label('Einrichtung: ', style=style_label_input))
        self.input_formular_rechnungen_einrichtung = toga.Selection(items=self.einrichtungen_liste, accessor='name', style=style_input)
        box_formular_rechnungen_einrichtung.add(self.input_formular_rechnungen_einrichtung)
        self.box_seite_formular_rechnungen.add(box_formular_rechnungen_einrichtung)

        # Bereich zur Eingabe der Notiz
        box_formular_rechnungen_notiz = toga.Box(style=style_box_row)
        box_formular_rechnungen_notiz.add(toga.Label('Notiz: ', style=style_label_input))
        self.input_formular_rechnungen_notiz = toga.TextInput(style=style_input)
        box_formular_rechnungen_notiz.add(self.input_formular_rechnungen_notiz)
        self.box_seite_formular_rechnungen.add(box_formular_rechnungen_notiz)

        # Bereich zur Auswahl des Beihilfesatzes
        box_formular_rechnungen_beihilfesatz = toga.Box(style=style_box_row)
        box_formular_rechnungen_beihilfesatz.add(toga.Label('Beihilfesatz in %: ', style=style_label_input))
        self.input_formular_rechnungen_beihilfesatz = toga.TextInput(style=style_input, on_lose_focus=self.pruefe_prozent)
        box_formular_rechnungen_beihilfesatz.add(self.input_formular_rechnungen_beihilfesatz)
        self.box_seite_formular_rechnungen.add(box_formular_rechnungen_beihilfesatz)

        # Bereich zur Eingabe des Buchungsdatums
        box_formular_rechnungen_buchungsdatum = toga.Box(style=style_box_row)
        box_formular_rechnungen_buchungsdatum.add(toga.Label('Datum Überweisung: ', style=style_label_input))
        self.input_formular_rechnungen_buchungsdatum = toga.TextInput(style=style_input, on_lose_focus=self.pruefe_datum, placeholder='TT.MM.JJJJ')
        box_formular_rechnungen_buchungsdatum.add(self.input_formular_rechnungen_buchungsdatum)
        self.box_seite_formular_rechnungen.add(box_formular_rechnungen_buchungsdatum)

        # Bereich zur Angabe der Bezahlung
        box_formular_rechnungen_bezahlt = toga.Box(style=style_box_row)
        self.input_formular_rechnungen_bezahlt = toga.Switch('Bezahlt:', style=style_switch)
        box_formular_rechnungen_bezahlt.add(self.input_formular_rechnungen_bezahlt)
        self.box_seite_formular_rechnungen.add(box_formular_rechnungen_bezahlt)

        # Bereich der Buttons
        box_formular_rechnungen_buttons = toga.Box(style=style_box_row)
        box_formular_rechnungen_buttons.add(toga.Button('Abbrechen', on_press=self.zeige_seite_liste_rechnungen, style=style_button))
        box_formular_rechnungen_buttons.add(toga.Button('Speichern', on_press=self.rechnung_speichern_check, style=style_button))
        self.box_seite_formular_rechnungen.add(box_formular_rechnungen_buttons)


    def zeige_seite_formular_rechnungen_neu(self, widget):
        """Zeigt die Seite zum Erstellen einer Rechnung."""
        
        # Setze die Eingabefelder zurück
        self.input_formular_rechnungen_betrag.value = ''
        self.input_formular_rechnungen_rechnungsdatum.value = ''
        if len(self.einrichtungen_liste) > 0:
            self.input_formular_rechnungen_einrichtung.value = self.einrichtungen_liste[0]
        self.input_formular_rechnungen_beihilfesatz.value = ''
        self.input_formular_rechnungen_notiz.value = ''
        self.input_formular_rechnungen_buchungsdatum.value = ''
        self.input_formular_rechnungen_bezahlt.value = False

        # Zurücksetzen des Flags
        self.flag_bearbeite_rechnung = False

        # Setze die Überschrift
        self.label_formular_rechnungen.text = 'Neue Rechnung'

        # Zeige die Seite
        self.main_window.content = self.scroll_container_formular_rechnungen

    
    def zeige_seite_formular_rechnungen_bearbeiten(self, widget):
        """Zeigt die Seite zum Bearbeiten einer Rechnung."""

        # Ermittle den Index der ausgewählten Rechnung
        if widget == self.liste_rechnungen_button_bearbeiten:
            self.rechnung_b_id = self.index_auswahl(self.tabelle_rechnungen)
        elif widget == self.startseite_button_bearbeiten:
            self.rechnung_b_id = self.index_liste_von_id(self.rechnungen, self.tabelle_offene_buchungen.selection.db_id)
        else:
            print('Fehler: Aufrufendes Widget unbekannt.')
            return

        # Ermittle den Index der Einrichtung in der Liste der Einrichtungen
        einrichtung_index = self.index_liste_von_id(self.einrichtungen, self.rechnungen[self.rechnung_b_id].einrichtung_id)

        # Befülle die Eingabefelder
        self.input_formular_rechnungen_betrag.value = format(float(self.rechnungen[self.rechnung_b_id].betrag), '.2f').replace('.', ',')
        self.input_formular_rechnungen_rechnungsdatum.value = self.rechnungen[self.rechnung_b_id].rechnungsdatum
        self.input_formular_rechnungen_beihilfesatz.value = str(int(self.rechnungen[self.rechnung_b_id].beihilfesatz))
        self.input_formular_rechnungen_notiz.value = self.rechnungen[self.rechnung_b_id].notiz
        self.input_formular_rechnungen_buchungsdatum.value = self.rechnungen[self.rechnung_b_id].buchungsdatum
        self.input_formular_rechnungen_bezahlt.value = self.rechnungen[self.rechnung_b_id].bezahlt

        # Auswahlfeld für die Einrichtung befüllen
        if einrichtung_index is not None:
            self.input_formular_rechnungen_einrichtung.value = self.einrichtungen_liste[einrichtung_index]
        elif len(self.einrichtungen_liste) > 0:
            self.input_formular_rechnungen_einrichtung.value = self.einrichtungen_liste[0]

        # Setze das Flag
        self.flag_bearbeite_rechnung = True

        # Setze die Überschrift
        self.label_formular_rechnungen.text = 'Rechnung bearbeiten'

        # Zeige die Seite
        self.main_window.content = self.scroll_container_formular_rechnungen


    async def rechnung_speichern_check(self, widget):
        """Prüft, ob die Rechnung gespeichert werden soll."""

        nachricht = ''

        # Prüfe, ob ein Rechnungsdatum eingegeben wurde
        if not self.pruefe_datum(self.input_formular_rechnungen_rechnungsdatum) or self.input_formular_rechnungen_rechnungsdatum.value == '':
            nachricht += 'Bitte gib ein gültiges Rechnungsdatum ein.\n'

        # Prüfe, ob ein Betrag eingegeben wurde
        if not self.pruefe_zahl(self.input_formular_rechnungen_betrag) or self.input_formular_rechnungen_betrag.value == '':
            nachricht += 'Bitte gib einen gültigen Betrag ein.\n'

        # Prüfe, ob eine Einrichtung ausgewählt wurde
        if len(self.einrichtungen_liste) > 0:
            if self.input_formular_rechnungen_einrichtung.value is None:
                nachricht += 'Bitte wähle eine Einrichtung aus.\n'

        # Prüfe, ob ein Beihilfesatz eingegeben wurde
        if not self.pruefe_prozent(self.input_formular_rechnungen_beihilfesatz) or self.input_formular_rechnungen_beihilfesatz.value == '':
            nachricht += 'Bitte gib einen gültigen Beihilfesatz ein.\n'

        if not self.pruefe_datum(self.input_formular_rechnungen_buchungsdatum):
            nachricht += 'Bitte gib ein gültiges Buchungsdatum ein oder lasse das Feld leer.\n'
                
        if nachricht != '':
            self.main_window.error_dialog('Fehlerhafte Eingabe', nachricht)
        else:
            await self.rechnung_speichern(widget)


    async def rechnung_speichern(self, widget):
        """Erstellt und speichert eine neue Rechnung."""

        if not self.flag_bearbeite_rechnung:
        # Erstelle eine neue Rechnung
            neue_rechnung = Rechnung()
            neue_rechnung.rechnungsdatum = self.input_formular_rechnungen_rechnungsdatum.value
            if len(self.einrichtungen_liste) > 0:
                neue_rechnung.einrichtung_id = self.input_formular_rechnungen_einrichtung.value.db_id
            neue_rechnung.notiz = self.input_formular_rechnungen_notiz.value
            neue_rechnung.betrag = float(self.input_formular_rechnungen_betrag.value.replace(',', '.') or 0)
            neue_rechnung.beihilfesatz = float(self.input_formular_rechnungen_beihilfesatz.value or 0)
            neue_rechnung.buchungsdatum = self.input_formular_rechnungen_buchungsdatum.value
            neue_rechnung.bezahlt = self.input_formular_rechnungen_bezahlt.value

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
            
            if self.rechnungen[self.rechnung_b_id].betrag != float(self.input_formular_rechnungen_betrag.value.replace(',', '.')):
                update_einreichung = True
            if self.rechnungen[self.rechnung_b_id].beihilfesatz != float(self.input_formular_rechnungen_beihilfesatz.value):
                update_einreichung = True

            # Bearbeite die Rechnung
            self.rechnungen[self.rechnung_b_id].rechnungsdatum = self.input_formular_rechnungen_rechnungsdatum.value
            
            if len(self.einrichtungen_liste) > 0:
                self.rechnungen[self.rechnung_b_id].einrichtung_id = self.input_formular_rechnungen_einrichtung.value.db_id
            self.rechnungen[self.rechnung_b_id].notiz = self.input_formular_rechnungen_notiz.value
            self.rechnungen[self.rechnung_b_id].betrag = float(self.input_formular_rechnungen_betrag.value.replace(',', '.') or 0)
            self.rechnungen[self.rechnung_b_id].beihilfesatz = float(self.input_formular_rechnungen_beihilfesatz.value or 0)
            self.rechnungen[self.rechnung_b_id].buchungsdatum = self.input_formular_rechnungen_buchungsdatum.value
            self.rechnungen[self.rechnung_b_id].bezahlt = self.input_formular_rechnungen_bezahlt.value

            # Speichere die Rechnung in der Datenbank
            self.rechnungen[self.rechnung_b_id].speichern(self.db)

            # Aktualisiere die Liste der Rechnungen
            self.rechnungen_liste_aendern(self.rechnungen[self.rechnung_b_id], self.rechnung_b_id)

            # Flag zurücksetzen
            self.flag_bearbeite_rechnung = False

            # Überprüfe ob eine verknüpfte Beihilfe-Einreichung existiert
            # und wenn ja, frage, ob diese aktualisiert werden soll
            if update_einreichung and self.rechnungen[self.rechnung_b_id].beihilfe_id is not None:
                await self.main_window.confirm_dialog(
                    'Zugehörige Beihilfe-Einreichung aktualisieren',
                    'Soll die zugehörige Beihilfe-Einreichung aktualisiert werden?',
                    on_result=self.beihilfepaket_aktualisieren
                )

            # Überprüfe ob eine verknüpfte PKV-Einreichung existiert
            # und wenn ja, frage, ob diese aktualisiert werden soll
            if update_einreichung and self.rechnungen[self.rechnung_b_id].pkv_id is not None:
                await self.main_window.confirm_dialog(
                    'Zugehörige PKV-Einreichung aktualisieren',
                    'Soll die zugehörige PKV-Einreichung aktualisiert werden?',
                    on_result=self.pkvpaket_aktualisieren
                )

            # Zeigt die Liste der Rechnungen an.
            self.update_app(widget)
            self.zeige_seite_liste_rechnungen(widget)


    def beihilfepaket_aktualisieren(self, widget, result):
        """Aktualisiert die Beihilfe-Einreichung einer Rechnung."""
        if result:
            # Finde die Beihilfe-Einreichung
            for beihilfepaket in self.beihilfepakete:
                if beihilfepaket.db_id == self.rechnungen[self.rechnung_b_id].beihilfe_id:
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
                if pkvpaket.db_id == self.rechnungen[self.rechnung_b_id].pkv_id:
                    # ALle Rechnungen durchlaufen und den Betrag aktualisieren
                    pkvpaket.betrag = 0
                    for rechnung in self.rechnungen:
                        if rechnung.pkv_id == pkvpaket.db_id:
                            pkvpaket.betrag += rechnung.betrag * (1 - (rechnung.beihilfesatz / 100))
                    # Die PKV-Einreichung speichern
                    pkvpaket.speichern(self.db)
                    self.pkvpakete_liste_aendern(pkvpaket, self.pkvpakete.index(pkvpaket))
                    break            


    def bestaetige_rechnung_loeschen(self, widget):
        """Bestätigt das Löschen einer Rechnung."""
        if self.tabelle_rechnungen.selection:
            self.main_window.confirm_dialog(
                'Rechnung löschen', 
                'Soll die ausgewählte Rechnung wirklich gelöscht werden?',
                on_result=self.rechnung_loeschen
            )


    async def rechnung_loeschen(self, widget, result):
        """Löscht eine Rechnung."""
        if self.tabelle_rechnungen.selection and result:
            
            # Index der ausgewählten Rechnung ermitteln
            self.rechnung_b_id = self.index_auswahl(self.tabelle_rechnungen)
            
            # Betrag der Rechnung auf 0 setzen um die Einreichungen aktualisieren zu können
            self.rechnungen[self.rechnung_b_id].betrag = 0
    
            # Auf Wunsch Beihilfe-Einreichung aktualisieren
            if self.rechnungen[self.rechnung_b_id].beihilfe_id is not None:
                await self.main_window.confirm_dialog(
                    'Zugehörige Beihilfe-Einreichung aktualisieren',
                    'Soll die zugehörige Beihilfe-Einreichung aktualisiert werden?',
                    on_result=self.beihilfepaket_aktualisieren
                )

            # Auf Wunsch PKV-Einreichung aktualisieren
            if self.rechnungen[self.rechnung_b_id].pkv_id is not None:
                await self.main_window.confirm_dialog(
                    'Zugehörige PKV-Einreichung aktualisieren',
                    'Soll die zugehörige PKV-Einreichung aktualisiert werden?',
                    on_result=self.pkvpaket_aktualisieren
                )

            # Rechnung löschen
            self.rechnungen[self.rechnung_b_id].loeschen(self.db)  
            del self.rechnungen[self.rechnung_b_id]
            del self.rechnungen_liste[self.rechnung_b_id]   


    def erzeuge_seite_liste_einrichtungen(self):
        """Erzeugt die Seite, auf der die Einrichtungen angezeigt werden."""
        self.box_seite_liste_einrichtungen = toga.Box(style=style_box_column)
        self.box_seite_liste_einrichtungen.add(toga.Button('Zurück', on_press=self.zeige_startseite, style=style_button))
        self.box_seite_liste_einrichtungen.add(toga.Label('Einrichtungen', style=style_label_h1))

        # Tabelle mit den Einrichtungen

        self.tabelle_einrichtungen = toga.Table(
            headings    = ['Einrichtung'], 
            accessors   = ['name'],
            data        = self.einrichtungen_liste,
            style       = style_table,
            on_select   = self.update_app,
            on_activate = self.zeige_info_einrichtung
        )
        self.box_seite_liste_einrichtungen.add(self.tabelle_einrichtungen)

        # Buttons für die Einrichtungen
        box_seite_liste_einrichtungen_buttons = toga.Box(style=style_box_row)
        self.seite_liste_einrichtungen_button_loeschen = toga.Button('Löschen', on_press=self.bestaetige_einrichtung_loeschen, style=style_button, enabled=False)
        self.seite_liste_einrichtungen_button_bearbeiten = toga.Button('Bearbeiten', on_press=self.zeige_seite_formular_einrichtungen_bearbeiten, style=style_button, enabled=False)
        self.seite_liste_einrichtungen_button_neu = toga.Button('Neu', on_press=self.zeige_seite_formular_einrichtungen_neu, style=style_button)
        box_seite_liste_einrichtungen_buttons.add(self.seite_liste_einrichtungen_button_loeschen)
        box_seite_liste_einrichtungen_buttons.add(self.seite_liste_einrichtungen_button_bearbeiten)
        box_seite_liste_einrichtungen_buttons.add(self.seite_liste_einrichtungen_button_neu)
        self.box_seite_liste_einrichtungen.add(box_seite_liste_einrichtungen_buttons)   


    def zeige_seite_liste_einrichtungen(self, widget):
        """Zeigt die Seite mit der Liste der Einrichtungen."""
        self.update_app(widget)
        self.main_window.content = self.box_seite_liste_einrichtungen


    def erzeuge_seite_formular_einrichtungen(self):
        """Erzeugt das Formular zum Erstellen und Bearbeiten einer Einrichtung."""
        self.scroll_container_formular_einrichtungen = toga.ScrollContainer(style=style_scroll_container)
        self.box_seite_formular_einrichtungen = toga.Box(style=style_box_column)
        self.scroll_container_formular_einrichtungen.content = self.box_seite_formular_einrichtungen
        self.box_seite_formular_einrichtungen.add(toga.Button('Zurück', on_press=self.zeige_seite_liste_einrichtungen, style=style_button))
        self.label_formular_einrichtungen = toga.Label('Neue Einrichtung', style=style_label_h1)
        self.box_seite_formular_einrichtungen.add(self.label_formular_einrichtungen)

        # Bereich zur Eingabe des Namens
        box_formular_einrichtungen_name = toga.Box(style=style_box_row)
        box_formular_einrichtungen_name.add(toga.Label('Name: ', style=style_label_input))
        self.input_formular_einrichtungen_name = toga.TextInput(style=style_input)
        box_formular_einrichtungen_name.add(self.input_formular_einrichtungen_name)
        self.box_seite_formular_einrichtungen.add(box_formular_einrichtungen_name)

        # Bereich zur Eingabe der Strasse
        box_formular_einrichtungen_strasse = toga.Box(style=style_box_row)
        box_formular_einrichtungen_strasse.add(toga.Label('Straße, Hausnr.: ', style=style_label_input))
        self.input_formular_einrichtungen_strasse = toga.TextInput(style=style_input)
        box_formular_einrichtungen_strasse.add(self.input_formular_einrichtungen_strasse)
        self.box_seite_formular_einrichtungen.add(box_formular_einrichtungen_strasse)

        # Bereich zur Eingabe der PLZ
        box_formular_einrichtungen_plz = toga.Box(style=style_box_row)
        box_formular_einrichtungen_plz.add(toga.Label('PLZ: ', style=style_label_input))
        self.input_formular_einrichtungen_plz = toga.TextInput(style=style_input)
        box_formular_einrichtungen_plz.add(self.input_formular_einrichtungen_plz)
        self.box_seite_formular_einrichtungen.add(box_formular_einrichtungen_plz)

        # Bereich zur Eingabe des Ortes
        box_formular_einrichtungen_ort = toga.Box(style=style_box_row)
        box_formular_einrichtungen_ort.add(toga.Label('Ort: ', style=style_label_input))
        self.input_formular_einrichtungen_ort = toga.TextInput(style=style_input)
        box_formular_einrichtungen_ort.add(self.input_formular_einrichtungen_ort)
        self.box_seite_formular_einrichtungen.add(box_formular_einrichtungen_ort)

        # Bereich zur Eingabe der Telefonnummer
        box_formular_einrichtungen_telefon = toga.Box(style=style_box_row)
        box_formular_einrichtungen_telefon.add(toga.Label('Telefon: ', style=style_label_input))
        self.input_formular_einrichtungen_telefon = toga.TextInput(style=style_input)
        box_formular_einrichtungen_telefon.add(self.input_formular_einrichtungen_telefon)
        self.box_seite_formular_einrichtungen.add(box_formular_einrichtungen_telefon)

        # Bereich zur Eingabe der E-Mail-Adresse
        box_formular_einrichtungen_email = toga.Box(style=style_box_row)
        box_formular_einrichtungen_email.add(toga.Label('E-Mail: ', style=style_label_input))
        self.input_formular_einrichtungen_email = toga.TextInput(style=style_input)
        box_formular_einrichtungen_email.add(self.input_formular_einrichtungen_email)
        self.box_seite_formular_einrichtungen.add(box_formular_einrichtungen_email)

        # Bereich zur Eingabe der Webseite
        box_formular_einrichtungen_webseite = toga.Box(style=style_box_row)
        box_formular_einrichtungen_webseite.add(toga.Label('Webseite: ', style=style_label_input))
        self.input_formular_einrichtungen_webseite = toga.TextInput(style=style_input)
        box_formular_einrichtungen_webseite.add(self.input_formular_einrichtungen_webseite)
        self.box_seite_formular_einrichtungen.add(box_formular_einrichtungen_webseite)

        # Bereich zur Eingabe der Notiz
        box_formular_einrichtungen_notiz = toga.Box(style=style_box_row)
        box_formular_einrichtungen_notiz.add(toga.Label('Notiz: ', style=style_label_input))
        self.input_formular_einrichtungen_notiz = toga.TextInput(style=style_input)
        box_formular_einrichtungen_notiz.add(self.input_formular_einrichtungen_notiz)
        self.box_seite_formular_einrichtungen.add(box_formular_einrichtungen_notiz)

        # Bereich der Buttons
        box_formular_einrichtungen_buttons = toga.Box(style=style_box_row)
        box_formular_einrichtungen_buttons.add(toga.Button('Abbrechen', on_press=self.zeige_seite_liste_einrichtungen, style=style_button))
        box_formular_einrichtungen_buttons.add(toga.Button('Speichern', on_press=self.einrichtung_speichern_check, style=style_button))
        self.box_seite_formular_einrichtungen.add(box_formular_einrichtungen_buttons)


    def zeige_seite_formular_einrichtungen_neu(self, widget):
        """Zeigt die Seite zum Erstellen einer Einrichtung."""
        # Setze die Eingabefelder zurück
        self.input_formular_einrichtungen_name.value = ''
        self.input_formular_einrichtungen_strasse.value = ''
        self.input_formular_einrichtungen_plz.value = ''
        self.input_formular_einrichtungen_ort.value = ''
        self.input_formular_einrichtungen_telefon.value = ''
        self.input_formular_einrichtungen_email.value = ''
        self.input_formular_einrichtungen_webseite.value = ''
        self.input_formular_einrichtungen_notiz.value = ''

        # Zurücksetzen des Flags
        self.flag_bearbeite_einrichtung = False

        # Setze die Überschrift
        self.label_formular_einrichtungen.text = 'Neue Einrichtung'

        # Zeige die Seite
        self.main_window.content = self.scroll_container_formular_einrichtungen


    def zeige_seite_formular_einrichtungen_bearbeiten(self, widget):
        """Zeigt die Seite zum Bearbeiten einer Einrichtung."""
        
        # Prüfe ob eine Einrichtung ausgewählt ist
        if self.tabelle_einrichtungen.selection:
            # Ermittle den Index der ausgewählten Rechnung
            self.einrichtung_b_id = self.index_auswahl(self.tabelle_einrichtungen)
            
            # Befülle die Eingabefelder
            self.input_formular_einrichtungen_name.value = self.einrichtungen[self.einrichtung_b_id].name
            self.input_formular_einrichtungen_strasse.value = self.einrichtungen[self.einrichtung_b_id].strasse
            self.input_formular_einrichtungen_plz.value = self.einrichtungen[self.einrichtung_b_id].plz
            self.input_formular_einrichtungen_ort.value = self.einrichtungen[self.einrichtung_b_id].ort
            self.input_formular_einrichtungen_telefon.value = self.einrichtungen[self.einrichtung_b_id].telefon
            self.input_formular_einrichtungen_email.value = self.einrichtungen[self.einrichtung_b_id].email
            self.input_formular_einrichtungen_webseite.value = self.einrichtungen[self.einrichtung_b_id].webseite
            self.input_formular_einrichtungen_notiz.value = self.einrichtungen[self.einrichtung_b_id].notiz

            # Setze das Flag
            self.flag_bearbeite_einrichtung = True

            # Setze die Überschrift
            self.label_formular_einrichtungen.text = 'Einrichtung bearbeiten'

            # Zeige die Seite
            self.main_window.content = self.scroll_container_formular_einrichtungen


    def einrichtung_speichern_check(self, widget):
        """Prüft die Eingaben im Formular der Einrichtungen."""
        nachricht = ''

        # Prüfe, ob ein Name eingegeben wurde
        if self.input_formular_einrichtungen_name.value == '':
            nachricht += 'Bitte gib einen Namen ein.\n'

        # Prüfe, ob nichts oder eine gültige PLZ eingegeben wurde
        if not self.pruefe_plz(self.input_formular_einrichtungen_plz):
                nachricht += 'Bitte gib eine gültige PLZ ein oder lasse das Feld leer.\n'

        # Prüfe, ob nichts oder eine gültige E-Mail-Adresse eingegeben wurde
        if not self.pruefe_email(self.input_formular_einrichtungen_email):
                nachricht += 'Bitte gib eine gültige E-Mail-Adresse ein oder lasse das Feld leer.\n'

        # Prüfe, ob nichts oder eine gültige Webseite eingegeben wurde
        if not self.pruefe_webseite(self.input_formular_einrichtungen_webseite):
                nachricht += 'Bitte gib eine gültige Webseite ein oder lasse das Feld leer.\n'

        if nachricht != '':
            self.main_window.error_dialog('Fehlerhafte Eingabe', nachricht)
        else:
            self.einrichtung_speichern(widget)


    def einrichtung_speichern(self, widget):
        """Erstellt und speichert eine neue Einrichtung."""
        if not self.flag_bearbeite_einrichtung:
        # Erstelle eine neue Einrichtung
            neue_einrichtung = Einrichtung()
            neue_einrichtung.name = self.input_formular_einrichtungen_name.value
            neue_einrichtung.strasse = self.input_formular_einrichtungen_strasse.value
            neue_einrichtung.plz = self.input_formular_einrichtungen_plz.value
            neue_einrichtung.ort = self.input_formular_einrichtungen_ort.value
            neue_einrichtung.telefon = self.input_formular_einrichtungen_telefon.value
            neue_einrichtung.email = self.input_formular_einrichtungen_email.value
            neue_einrichtung.webseite = self.input_formular_einrichtungen_webseite.value
            neue_einrichtung.notiz = self.input_formular_einrichtungen_notiz.value

            # Speichere die Einrichtung in der Datenbank
            neue_einrichtung.neu(self.db)

            # Füge die Einrichtung der Liste hinzu
            self.einrichtungen.append(neue_einrichtung)
            self.einrichtungen_liste_anfuegen(neue_einrichtung)
        else:
            # Bearbeite die Einrichtung
            self.einrichtungen[self.einrichtung_b_id].name = self.input_formular_einrichtungen_name.value
            self.einrichtungen[self.einrichtung_b_id].strasse = self.input_formular_einrichtungen_strasse.value
            self.einrichtungen[self.einrichtung_b_id].plz = self.input_formular_einrichtungen_plz.value
            self.einrichtungen[self.einrichtung_b_id].ort = self.input_formular_einrichtungen_ort.value
            self.einrichtungen[self.einrichtung_b_id].telefon = self.input_formular_einrichtungen_telefon.value
            self.einrichtungen[self.einrichtung_b_id].email = self.input_formular_einrichtungen_email.value
            self.einrichtungen[self.einrichtung_b_id].webseite = self.input_formular_einrichtungen_webseite.value
            self.einrichtungen[self.einrichtung_b_id].notiz = self.input_formular_einrichtungen_notiz.value

            # Speichere die Einrichtung in der Datenbank
            self.einrichtungen[self.einrichtung_b_id].speichern(self.db)

            # Aktualisiere die Liste der Einrichtungen
            self.einrichtungen_liste_aendern(self.einrichtungen[self.einrichtung_b_id], self.einrichtung_b_id)

            # Flag zurücksetzen
            self.flag_bearbeite_einrichtung = False

            # Aktualisiere die Liste der Rechnungen
            self.rechnungen_liste_aktualisieren()

        # Zeige die Liste der Einrichtungen
        self.update_app(widget)
        self.zeige_seite_liste_einrichtungen(widget)


    def erzeuge_seite_info_einrichtung(self):
        """Erzeugt die Seite, auf der die Details einer Einrichtung angezeigt werden."""
        self.scroll_container_info_einrichtung = toga.ScrollContainer(style=style_scroll_container)
        box_seite_info_einrichtung = toga.Box(style=style_box_column)
        self.scroll_container_info_einrichtung.content = box_seite_info_einrichtung
        box_seite_info_einrichtung.add(toga.Button('Zurück', on_press=self.zeige_seite_liste_einrichtungen, style=style_button))
        self.label_info_einrichtung_name = toga.Label('', style=style_label_h1)
        box_seite_info_einrichtung.add(self.label_info_einrichtung_name)

        # Bereich mit den Details zur Straße
        box_seite_info_einrichtung_strasse = toga.Box(style=style_box_row)
        box_seite_info_einrichtung_strasse.add(toga.Label('Straße, Hausnr.: ', style=style_label_input))
        self.label_info_einrichtung_strasse = toga.Label('', style=style_label_input)
        box_seite_info_einrichtung_strasse.add(self.label_info_einrichtung_strasse)
        box_seite_info_einrichtung.add(box_seite_info_einrichtung_strasse)

        # Bereich mit den Details zum Ort
        box_seite_info_einrichtung_plz_ort = toga.Box(style=style_box_row)
        box_seite_info_einrichtung_plz_ort.add(toga.Label('PLZ, Ort: ', style=style_label_input))
        self.label_info_einrichtung_plz_ort = toga.Label('', style=style_label_input)
        box_seite_info_einrichtung_plz_ort.add(self.label_info_einrichtung_plz_ort)
        box_seite_info_einrichtung.add(box_seite_info_einrichtung_plz_ort)

        # Bereich mit den Details zur Telefonnummer
        box_seite_info_einrichtung_telefon = toga.Box(style=style_box_row)
        box_seite_info_einrichtung_telefon.add(toga.Label('Telefon: ', style=style_label_input))
        self.label_info_einrichtung_telefon = toga.Label('', style=style_label_input)
        box_seite_info_einrichtung_telefon.add(self.label_info_einrichtung_telefon)
        box_seite_info_einrichtung.add(box_seite_info_einrichtung_telefon)
        
        # Bereich mit den Details zur E-Mail-Adresse
        box_seite_info_einrichtung_email = toga.Box(style=style_box_row)
        box_seite_info_einrichtung_email.add(toga.Label('E-Mail: ', style=style_label_input))
        self.label_info_einrichtung_email = toga.Label('', style=style_label_input)
        box_seite_info_einrichtung_email.add(self.label_info_einrichtung_email)
        box_seite_info_einrichtung.add(box_seite_info_einrichtung_email)

        # Bereich mit den Details zur Webseite
        box_seite_info_einrichtung_webseite = toga.Box(style=style_box_row)
        box_seite_info_einrichtung_webseite.add(toga.Label('Webseite: ', style=style_label_input))
        self.label_info_einrichtung_webseite = toga.Label('', style=style_label_input)
        box_seite_info_einrichtung_webseite.add(self.label_info_einrichtung_webseite)
        box_seite_info_einrichtung.add(box_seite_info_einrichtung_webseite)

        # Bereich mit den Details zur Notiz
        box_seite_info_einrichtung_notiz = toga.Box(style=style_box_row)
        box_seite_info_einrichtung_notiz.add(toga.Label('Notiz: ', style=style_label_input))
        self.label_info_einrichtung_notiz = toga.Label('', style=style_label_input)
        box_seite_info_einrichtung_notiz.add(self.label_info_einrichtung_notiz)
        box_seite_info_einrichtung.add(box_seite_info_einrichtung_notiz)

        # Bereich mit den Buttons
        box_seite_info_einrichtung_buttons = toga.Box(style=style_box_row)
        self.seite_info_einrichtung_button_bearbeiten = toga.Button('Bearbeiten', on_press=self.zeige_seite_formular_einrichtungen_bearbeiten, style=style_button)
        box_seite_info_einrichtung_buttons.add(self.seite_info_einrichtung_button_bearbeiten)
        self.seite_info_einrichtung_button_loeschen = toga.Button('Löschen', on_press=self.bestaetige_einrichtung_loeschen, style=style_button)
        box_seite_info_einrichtung_buttons.add(self.seite_info_einrichtung_button_loeschen)
        box_seite_info_einrichtung.add(box_seite_info_einrichtung_buttons)


    def zeige_info_einrichtung(self, widget, row=None):
        """Zeigt die Seite mit den Details einer Einrichtung."""
        # Prüfe, ob eine Einrichtung ausgewählt ist
        if self.tabelle_einrichtungen.selection:

            # Ermittle den Index der ausgewählten Einrichtung
            self.einrichtung_b_id = self.index_auswahl(self.tabelle_einrichtungen)

            # Befülle die Labels mit den Details der Einrichtung
            # Die einzutragenden Werte können None sein, daher wird hier mit einem leeren String gearbeitet
            self.label_info_einrichtung_name.text = self.einrichtungen[self.einrichtung_b_id].name or ''
            self.label_info_einrichtung_strasse.text = self.einrichtungen[self.einrichtung_b_id].strasse or ''

            # PLZ und Ort werden in einem Label zusammengefasst
            # Dabei werden beide Variablen auf None geprüft und ggf. durch einen leeren String ersetzt
            # Wenn PLZ None ist, dann entfällt das Leerzeichen vor dem Ort
            self.label_info_einrichtung_plz_ort.text = (self.einrichtungen[self.einrichtung_b_id].plz or '') + (' ' if self.einrichtungen[self.einrichtung_b_id].plz else '') + (self.einrichtungen[self.einrichtung_b_id].ort or '')
            
            self.label_info_einrichtung_telefon.text = self.einrichtungen[self.einrichtung_b_id].telefon or ''
            self.label_info_einrichtung_email.text = self.einrichtungen[self.einrichtung_b_id].email or ''
            self.label_info_einrichtung_webseite.text = self.einrichtungen[self.einrichtung_b_id].webseite or ''
            self.label_info_einrichtung_notiz.text = self.einrichtungen[self.einrichtung_b_id].notiz or ''

            # Zeige die Seite
            self.main_window.content = self.scroll_container_info_einrichtung

    
    def bestaetige_einrichtung_loeschen(self, widget):
        """Bestätigt das Löschen einer Einrichtung."""
        if self.tabelle_einrichtungen.selection:
            self.main_window.confirm_dialog(
                'Einrichtung löschen', 
                'Soll die ausgewählte Einrichtung wirklich gelöscht werden?',
                on_result=self.einrichtung_loeschen
            )


    def einrichtung_loeschen(self, widget, result):
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
            self.zeige_seite_liste_einrichtungen(widget)


    def erzeuge_seite_liste_beihilfepakete(self):
        """Erzeugt die Seite, auf der die Beihilfe-Einreichungen angezeigt werden."""
        self.box_seite_liste_beihilfepakete = toga.Box(style=style_box_column)
        self.box_seite_liste_beihilfepakete.add(toga.Button('Zurück', on_press=self.zeige_startseite, style=style_button))
        self.box_seite_liste_beihilfepakete.add(toga.Label('Beihilfe-Einreichungen', style=style_label_h1))

        # Tabelle mit den Beihilfepaketen
        self.tabelle_beihilfepakete = toga.Table(
            headings    = ['Datum', 'Betrag', 'Erhalten'], 
            accessors   = ['datum', 'betrag_euro', 'erhalten_text'],
            data        = self.beihilfepakete_liste,
            style       = style_table,
            on_select   = self.update_app,
            on_activate = self.zeige_info_buchung
        )
        self.box_seite_liste_beihilfepakete.add(self.tabelle_beihilfepakete)

        # Buttons für die Beihilfepakete
        box_seite_liste_beihilfepakete_buttons = toga.Box(style=style_box_row)
        self.seite_liste_beihilfepakete_button_loeschen = toga.Button('Zurücksetzen', on_press=self.bestaetige_beihilfepaket_loeschen, style=style_button, enabled=False)
        box_seite_liste_beihilfepakete_buttons.add(self.seite_liste_beihilfepakete_button_loeschen)
        #self.seite_liste_beihilfepakete_button_bearbeiten = toga.Button('Bearbeiten', on_press=self.zeige_seite_formular_beihilfepakete_bearbeiten, style=style_button, enabled=False)
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
            on_select   = self.update_app,
            on_activate = self.zeige_info_buchung
        )
        self.tabelle_pkvpakete_container.content = self.tabelle_pkvpakete
        self.box_seite_liste_pkvpakete.add(self.tabelle_pkvpakete_container)

        # Buttons für die PKV-Einreichungen
        box_seite_liste_pkvpakete_buttons = toga.Box(style=style_box_row)
        self.seite_liste_pkvpakete_button_loeschen = toga.Button('Zurücksetzen', on_press=self.bestaetige_pkvpaket_loeschen, style=style_button, enabled=False)
        box_seite_liste_pkvpakete_buttons.add(self.seite_liste_pkvpakete_button_loeschen)
        #self.seite_liste_pkvpakete_button_bearbeiten = toga.Button('Bearbeiten', on_press=self.zeige_seite_formular_pkvpakete_bearbeiten, style=style_button, enabled=False)
        #box_seite_liste_pkvpakete_buttons.add(self.seite_liste_pkvpakete_button_bearbeiten)
        self.seite_liste_pkvpakete_button_neu = toga.Button('Neu', on_press=self.zeige_seite_formular_pkvpakete_neu, style=style_button)
        box_seite_liste_pkvpakete_buttons.add(self.seite_liste_pkvpakete_button_neu)
        self.box_seite_liste_pkvpakete.add(box_seite_liste_pkvpakete_buttons)


    def zeige_seite_liste_beihilfepakete(self, widget):
        """Zeigt die Seite mit der Liste der Beihilfepakete."""
        # Zum Setzen des Button Status
        self.update_app(widget)
        self.main_window.content = self.box_seite_liste_beihilfepakete

    
    def zeige_seite_liste_pkvpakete(self, widget):
        """Zeigt die Seite mit der Liste der PKV-Einreichungen."""
        # Zum Setzen des Button Status
        self.update_app(widget)
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
        self.input_formular_beihilfepakete_datum = toga.TextInput(style=style_input, on_lose_focus=self.pruefe_datum, placeholder='TT.MM.JJJJ')
        box_formular_beihilfepakete_datum.add(self.input_formular_beihilfepakete_datum)
        self.box_seite_formular_beihilfepakete.add(box_formular_beihilfepakete_datum)

        # Bereich zur Auswahl der zugehörigen Rechnungen
        self.formular_beihilfe_tabelle_rechnungen = toga.Table(
            headings        = ['Info', 'Betrag', 'Beihilfe', 'Bezahlt'],
            accessors       = ['info', 'betrag_euro', 'beihilfesatz_prozent', 'bezahlt_text'],
            data            = self.erzeuge_teilliste_rechnungen(beihilfe=True),
            multiple_select = True,
            on_select       = self.beihilfe_tabelle_rechnungen_auswahl_geaendert,
            on_activate     = self.zeige_info_buchung,
            style           = style_table_auswahl
        )
        self.box_seite_formular_beihilfepakete.add(self.formular_beihilfe_tabelle_rechnungen)

        # Bereich zur Eingabe des Betrags
        box_formular_beihilfepakete_betrag = toga.Box(style=style_box_row)
        box_formular_beihilfepakete_betrag.add(toga.Label('Betrag in €: ', style=style_label_input))
        self.input_formular_beihilfepakete_betrag = toga.TextInput(style=style_input, readonly=True)
        box_formular_beihilfepakete_betrag.add(self.input_formular_beihilfepakete_betrag)
        self.box_seite_formular_beihilfepakete.add(box_formular_beihilfepakete_betrag)

        # Bereich zur Angabe der Erstattung
        box_formular_beihilfepakete_erhalten = toga.Box(style=style_box_row)
        self.input_formular_beihilfepakete_erhalten = toga.Switch('Erstattet:', style=style_switch)
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
        self.input_formular_pkvpakete_datum = toga.TextInput(style=style_input, on_lose_focus=self.pruefe_datum, placeholder='TT.MM.JJJJ')
        box_formular_pkvpakete_datum.add(self.input_formular_pkvpakete_datum)
        self.box_seite_formular_pkvpakete.add(box_formular_pkvpakete_datum)

        # Bereich zur Auswahl der zugehörigen Rechnungen
        self.formular_pkvpakete_rechnungen_container = toga.ScrollContainer(style=style_scroll_container)
        self.formular_pkv_tabelle_rechnungen = toga.Table(
            headings        = ['Info', 'Betrag', 'Beihilfe', 'Bezahlt'],
            accessors       = ['info', 'betrag_euro', 'beihilfesatz_prozent', 'bezahlt_text'],
            data            = self.erzeuge_teilliste_rechnungen(pkv=True),
            multiple_select = True,
            on_select       = self.pkv_tabelle_rechnungen_auswahl_geaendert,   
            on_activate     = self.zeige_info_buchung,
            style           = style_table_auswahl
        )
        self.formular_pkvpakete_rechnungen_container.content = self.formular_pkv_tabelle_rechnungen
        self.box_seite_formular_pkvpakete.add(self.formular_pkvpakete_rechnungen_container)

        # Bereich zur Eingabe des Betrags
        box_formular_pkvpakete_betrag = toga.Box(style=style_box_row)
        box_formular_pkvpakete_betrag.add(toga.Label('Betrag in €: ', style=style_label_input))
        self.input_formular_pkvpakete_betrag = toga.TextInput(style=style_input, readonly=True)
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


    def beihilfe_tabelle_rechnungen_auswahl_geaendert(self, widget):
        """Ermittelt die Summe des Beihilfe-Anteils der ausgewählten Rechnungen."""
        summe = 0
        for auswahl_rg in widget.selection:
            for rg in self.rechnungen:
                if auswahl_rg.db_id == rg.db_id:
                    summe += rg.betrag * rg.beihilfesatz / 100
        self.input_formular_beihilfepakete_betrag.value = format(summe, '.2f').replace('.', ',')


    def pkv_tabelle_rechnungen_auswahl_geaendert(self, widget):
        """Ermittelt die Summe des PKV-Anteils der ausgewählten Rechnungen."""
        summe = 0
        for auswahl_rg in widget.selection:
            for rg in self.rechnungen:
                if auswahl_rg.db_id == rg.db_id:
                    summe += rg.betrag * (100 - rg.beihilfesatz) / 100
        self.input_formular_pkvpakete_betrag.value = format(summe, '.2f').replace('.', ',')


    def zeige_seite_formular_beihilfepakete_neu(self, widget):
        """Zeigt die Seite zum Erstellen eines Beihilfepakets."""
        # Setze die Eingabefelder zurück
        self.input_formular_beihilfepakete_betrag.value = ''
        self.input_formular_beihilfepakete_datum.value = datetime.now().strftime('%d.%m.%Y')
        self.input_formular_beihilfepakete_erhalten.value = False
        self.formular_beihilfe_tabelle_rechnungen.data = self.erzeuge_teilliste_rechnungen(beihilfe=True)

        # Zurücksetzen des Flags
        self.flag_bearbeite_beihilfepaket = False

        # Setze die Überschrift
        self.label_formular_beihilfepakete.text = 'Neue Beihilfe-Einreichung'

        # Zeige die Seite
        self.main_window.content = self.box_seite_formular_beihilfepakete


    def zeige_seite_formular_pkvpakete_neu(self, widget):
        """Zeigt die Seite zum Erstellen einer PKV-Einreichung."""
        # Setze die Eingabefelder zurück
        self.input_formular_pkvpakete_betrag.value = ''
        self.input_formular_pkvpakete_datum.value = datetime.now().strftime('%d.%m.%Y')
        self.input_formular_pkvpakete_erhalten.value = False
        self.formular_pkv_tabelle_rechnungen.data = self.erzeuge_teilliste_rechnungen(pkv=True)

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
        self.input_formular_beihilfepakete_betrag.value = format(self.beihilfepakete[self.beihilfepaket_b_id].betrag, '.2f').replace('.', ',')
        self.input_formular_beihilfepakete_datum.value = self.beihilfepakete[self.beihilfepaket_b_id].datum
        self.input_formular_beihilfepakete_erhalten.value = self.beihilfepakete[self.beihilfepaket_b_id].erhalten

        # Tabelleninhalt aktualisieren
        tabelle_daten = self.erzeuge_teilliste_rechnungen(beihilfe=True, beihilfe_id=self.beihilfepakete[self.beihilfepaket_b_id].db_id)
        self.formular_beihilfe_tabelle_rechnungen.data = tabelle_daten

        # TODO: Wähle die verknüpften Rechnungen in der Tabelle aus
        # self.formular_beihilfe_tabelle_rechnungen.selection = []
        # for i, rechnung in enumerate(tabelle_daten):
        #     if rechnung.beihilfe_id == self.beihilfepakete[self.beihilfepaket_b_id].db_id:
        #         self.formular_beihilfe_tabelle_rechnungen.selection.append(self.formular_beihilfe_tabelle_rechnungen.data[i])

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
        self.input_formular_pkvpakete_betrag.value = format(self.pkvpakete[self.pkvpaket_b_id].betrag, '.2f').replace('.', ',')
        self.input_formular_pkvpakete_datum.value = self.pkvpakete[self.pkvpaket_b_id].datum
        self.input_formular_pkvpakete_erhalten.value = self.pkvpakete[self.pkvpaket_b_id].erhalten

        # Tabelleninhalt aktualisieren
        tabelle_daten = self.erzeuge_teilliste_rechnungen(pkv=True, pkv_id=self.pkvpakete[self.pkvpaket_b_id].db_id)
        self.formular_pkv_tabelle_rechnungen.data = tabelle_daten

        # Setze das Flag
        self.flag_bearbeite_pkvpaket = True

        # Setze die Überschrift
        self.label_formular_pkvpakete.text = 'PKV-Einreichung bearbeiten'

        # Zeige die Seite
        self.main_window.content = self.box_seite_formular_pkvpakete


    def beihilfepaket_speichern_check(self, widget):
        """Prüft, ob die Eingaben für eine neue Beihilfe-Einreichung korrekt sind."""

        nachricht = ''

        # Prüfe das Datum
        if not self.pruefe_datum(self.input_formular_beihilfepakete_datum) or self.input_formular_beihilfepakete_datum.value == '':
            nachricht += 'Bitte gib ein gültiges Datum ein.\n'

        # Prüfe ob Rechnungen ausgewählt wurden
        if not self.formular_beihilfe_tabelle_rechnungen.selection:
            nachricht += 'Es wurde keine Rechnung zum Einreichen ausgewählt.\n'

        if nachricht != '':
            self.main_window.error_dialog('Fehlerhafte Eingabe', nachricht)
        else:
            self.beihilfepaket_speichern(widget)


    def pkvpaket_speichern_check(self, widget):
        """Prüft, ob Rechnungen für die PKV-Einreichungen ausgewählt sind."""
        nachricht = ''

        # Prüfe das Datum
        if not self.pruefe_datum(self.input_formular_pkvpakete_datum) or self.input_formular_pkvpakete_datum.value == '':
            nachricht += 'Bitte gib ein gültiges Datum ein.\n'

        # Prüfe ob Rechnungen ausgewählt wurden
        if not self.formular_pkv_tabelle_rechnungen.selection:
            nachricht += 'Es wurde keine Rechnung zum Einreichen ausgewählt.\n'

        if nachricht != '':
            self.main_window.error_dialog('Fehlerhafte Eingabe', nachricht)
        else:
            self.pkvpaket_speichern(widget)


    def beihilfepaket_speichern(self, widget):
        """Erstellt und speichert eine neue Beihilfe-Einreichung oder ändert eine bestehende."""

        if not self.flag_bearbeite_beihilfepaket:
            # Erstelle ein neues Beihilfepaket
            neues_beihilfepaket = BeihilfePaket()
            neues_beihilfepaket.datum = self.input_formular_beihilfepakete_datum.value
            neues_beihilfepaket.betrag = float(self.input_formular_beihilfepakete_betrag.value.replace(',', '.') or 0)
            neues_beihilfepaket.erhalten = self.input_formular_beihilfepakete_erhalten.value

            # Speichere das Beihilfepaket in der Datenbank
            neues_beihilfepaket.neu(self.db)

            # Füge das Beihilfepaket der Liste hinzu
            self.beihilfepakete.append(neues_beihilfepaket)
            self.beihilfepakete_liste_anfuegen(neues_beihilfepaket)

            # Aktualisiere verknüpfte Rechnungen
            for auswahl_rg in self.formular_beihilfe_tabelle_rechnungen.selection:
                for rg in self.rechnungen:
                    if auswahl_rg.db_id == rg.db_id:
                        rg.beihilfe_id = neues_beihilfepaket.db_id
                        rg.speichern(self.db)

        else:
            # Bearbeite das Beihilfepaket
            self.beihilfepakete[self.beihilfepaket_b_id].datum = self.input_formular_beihilfepakete_datum.value
            self.beihilfepakete[self.beihilfepaket_b_id].betrag = float(self.input_formular_beihilfepakete_betrag.value.replace(',', '.') or 0)
            self.beihilfepakete[self.beihilfepaket_b_id].erhalten = self.input_formular_beihilfepakete_erhalten.value

            # Speichere das Beihilfepaket in der Datenbank
            self.beihilfepakete[self.beihilfepaket_b_id].speichern(self.db)

            # Aktualisiere die Liste der Beihilfepakete
            self.beihilfepakete_liste_aendern(self.beihilfepakete[self.beihilfepaket_b_id], self.beihilfepaket_b_id)

            # Flage zurücksetzen
            self.flag_bearbeite_beihilfepaket = False

            # Aktualisiere verknüpfte Rechnungen
            for auswahl_rg in self.formular_beihilfe_tabelle_rechnungen.selection:
                for rg in self.rechnungen:
                    if auswahl_rg.db_id == rg.db_id:
                        rg.beihilfe_id = self.beihilfepakete[self.beihilfepaket_b_id].db_id
                        rg.speichern(self.db)

        # Rechnungen aktualisieren
        self.rechnungen_liste_aktualisieren()

        # Wechsel zur Liste der Beihilfepakete
        self.update_app(widget)
        self.zeige_startseite(widget)


    def pkvpaket_speichern(self, widget):
        """Erstellt und speichert eine neue PKV-Einreichung oder ändert eine bestehende."""

        if not self.flag_bearbeite_pkvpaket:
            # Erstelle ein neues PKV-Paket
            neues_pkvpaket = PKVPaket()
            neues_pkvpaket.datum = self.input_formular_pkvpakete_datum.value
            neues_pkvpaket.betrag = float(self.input_formular_pkvpakete_betrag.value.replace(',', '.') or 0)
            neues_pkvpaket.erhalten = self.input_formular_pkvpakete_erhalten.value

            # Speichere das PKV-Einreichung in der Datenbank
            neues_pkvpaket.neu(self.db)

            # Füge das PKV-Einreichung der Liste hinzu
            self.pkvpakete.append(neues_pkvpaket)
            self.pkvpakete_liste_anfuegen(neues_pkvpaket)

            # Aktualisiere verknüpfte Rechnungen
            for auswahl_rg in self.formular_pkv_tabelle_rechnungen.selection:
                for rg in self.rechnungen:
                    if auswahl_rg.db_id == rg.db_id:
                        rg.pkv_id = neues_pkvpaket.db_id
                        rg.speichern(self.db)

        else:
            # Bearbeite das PKV-Paket
            self.pkvpakete[self.pkvpaket_b_id].datum = self.input_formular_pkvpakete_datum.value
            self.pkvpakete[self.pkvpaket_b_id].betrag = float(self.input_formular_pkvpakete_betrag.value.replace(',', '.') or 0)
            self.pkvpakete[self.pkvpaket_b_id].erhalten = self.input_formular_pkvpakete_erhalten.value

            # Speichere das PKV-Einreichung in der Datenbank
            self.pkvpakete[self.pkvpaket_b_id].speichern(self.db)

            # Aktualisiere die Liste der PKV-Einreichungen
            self.pkvpakete_liste_aendern(self.pkvpakete[self.pkvpaket_b_id], self.pkvpaket_b_id)

            # Flage zurücksetzen
            self.flag_bearbeite_pkvpaket = False

            # Aktualisiere verknüpfte Rechnungen
            for auswahl_rg in self.formular_pkv_tabelle_rechnungen.selection:
                for rg in self.rechnungen:
                    if auswahl_rg.db_id == rg.db_id:
                        rg.pkv_id = self.pkvpakete[self.pkvpaket_b_id].db_id
                        rg.speichern(self.db)

        # Rechnungen aktualisieren
        self.rechnungen_liste_aktualisieren()

        # Wechsel zur Liste der PKV-Einreichungen
        self.update_app(widget)
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
            self.rechnungen_aktualisieren()
            
            # Anzeigen aktualisieren
            self.update_app(widget)


    def pkvpaket_loeschen(self, widget, result):
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
            'notiz', 
            'einrichtung_name', 
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
                'notiz': rechnung.notiz,
                'einrichtung_name': self.einrichtung_name(rechnung.einrichtung_id),
                'info': self.einrichtung_name(rechnung.einrichtung_id) + ', ' + rechnung.notiz,
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
                        'Rechnung als bezahlt markieren', 
                        'Soll die ausgewählte Rechnung wirklich als bezahlt markiert werden?',
                        on_result=self.rechnung_bezahlen
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

        for rechnung in self.rechnungen:
            if not rechnung.bezahlt:
                offene_buchungen_liste.append({
                    'db_id': rechnung.db_id,
                    'typ': 'Rechnung',
                    'betrag_euro': '-{:.2f} €'.format(rechnung.betrag).replace('.', ','),
                    'datum': rechnung.buchungsdatum,
                    'info': self.einrichtung_name(rechnung.einrichtung_id) + ' - ' + rechnung.notiz
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
                    self.zeige_seite_formular_rechnungen_bearbeiten(widget)
                # case 'Beihilfe':
                #     self.zeige_seite_formular_beihilfepakete_bearbeiten(widget)
                # case 'PKV':
                #     self.zeige_seite_formular_pkvpakete_bearbeiten(widget)


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
            'telefon',
            'email',
            'webseite',
            'notiz'
        ])

        for einrichtung in self.einrichtungen:            
            self.einrichtungen_liste_anfuegen(einrichtung)


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
                'einrichtung_name': self.einrichtung_name(rechnung.einrichtung_id),
                'info': self.einrichtung_name(rechnung.einrichtung_id) + ', ' + rechnung.notiz,
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
                'name': einrichtung.name,
                'strasse': einrichtung.strasse,
                'plz': einrichtung.plz,
                'ort': einrichtung.ort,
                'telefon': einrichtung.telefon,
                'email': einrichtung.email,
                'webseite': einrichtung.webseite,
                'notiz': einrichtung.notiz
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
                'einrichtung_name': self.einrichtung_name(rechnung.einrichtung_id),
                'info': self.einrichtung_name(rechnung.einrichtung_id) + ', ' + rechnung.notiz,
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
                'name': einrichtung.name,
                'strasse': einrichtung.strasse,
                'plz': einrichtung.plz,
                'ort': einrichtung.ort,
                'telefon': einrichtung.telefon,
                'email': einrichtung.email,
                'webseite': einrichtung.webseite,
                'notiz': einrichtung.notiz
            }
        
        # Rechnungen aktualisieren
        self.rechnungen_liste_aktualisieren()

    
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
            self.zeige_seite_liste_rechnungen,
            'Rechnungen anzeigen',
            tooltip = 'Zeigt die Liste der Rechnungen an.',
            group = gruppe_rechnungen,
            order = 10,
            enabled=True
        )

        self.cmd_rechnungen_neu = toga.Command(
            self.zeige_seite_formular_rechnungen_neu,
            'Neue Rechnung',
            tooltip = 'Erstellt eine neue Rechnung.',
            group = gruppe_rechnungen,
            order = 20,
            enabled=True
        )

        gruppe_beihilfepakete = toga.Group('Beihilfe-Einreichungen', order = 2)

        self.cmd_beihilfepakete_anzeigen = toga.Command(
            self.zeige_seite_liste_beihilfepakete,
            'Beihilfe-Einreichungen anzeigen',
            tooltip = 'Zeigt die Liste der Beihilfe-Einreichungen an.',
            group = gruppe_beihilfepakete,
            order = 10,
            enabled=True
        )

        self.cmd_beihilfepakete_neu = toga.Command(
            self.zeige_seite_formular_beihilfepakete_neu,
            'Neue Beihilfe-Einreichung',
            tooltip = 'Erstellt eine neue Beihilfe-Einreichung.',
            group = gruppe_beihilfepakete,
            order = 20,
            enabled=False
        )

        gruppe_pkvpakete = toga.Group('PKV-Einreichungen', order = 3)

        self.cmd_pkvpakete_anzeigen = toga.Command(
            self.zeige_seite_liste_pkvpakete,
            'PKV-Einreichungen anzeigen',
            tooltip = 'Zeigt die Liste der PKV-Einreichungen an.',
            group = gruppe_pkvpakete,
            order = 10,
            enabled=True
        )

        self.cmd_pkvpakete_neu = toga.Command(
            self.zeige_seite_formular_pkvpakete_neu,
            'Neue PKV-Einreichung',
            tooltip = 'Erstellt eine neue PKV-Einreichung.',
            group = gruppe_pkvpakete,
            order = 20,
            enabled=False
        )

        gruppe_einrichtungen = toga.Group('Einrichtungen', order = 4)

        self.cmd_einrichtungen_anzeigen = toga.Command(
            self.zeige_seite_liste_einrichtungen,
            'Einrichtungen anzeigen',
            tooltip = 'Zeigt die Liste der Einrichtungen an.',
            group = gruppe_einrichtungen,
            order = 10,
            enabled=True
        )

        self.cmd_einrichtungen_neu = toga.Command(
            self.zeige_seite_formular_einrichtungen_neu,
            'Neue Einrichtung',
            tooltip = 'Erstellt eine neue Einrichtung.',
            group = gruppe_einrichtungen,
            order = 20,
            enabled=True
        )

        gruppe_tools = toga.Group('Tools', order = 5)

        self.cmd_archivieren = toga.Command(
            self.archivieren_bestaetigen,
            'Archivieren',
            tooltip = 'Archiviere alle bezahlten und erhaltenen Buchungen.',
            group = gruppe_tools,
            order = 10,
            enabled=False
        )

        # Datenbank initialisieren
        self.db = Datenbank()

        # Lade alle Daten aus der Datenbank
        self.rechnungen = self.db.lade_rechnungen()
        self.einrichtungen = self.db.lade_einrichtungen()
        self.beihilfepakete = self.db.lade_beihilfepakete()
        self.pkvpakete = self.db.lade_pkvpakete()

        # Erzeuge die ListSources für die GUI
        self.rechnungen_liste_erzeugen()
        self.einrichtungen_liste_erzeugen()
        self.beihilfepakete_liste_erzeugen()
        self.pkvpakete_liste_erzeugen()

        # Erzeuge alle GUI-Elemente
        self.erzeuge_startseite()
        self.erzeuge_seite_liste_rechnungen()
        self.erzeuge_seite_formular_rechnungen()
        self.erzeuge_seite_liste_einrichtungen()
        self.erzeuge_seite_formular_einrichtungen()
        self.erzeuge_seite_info_einrichtung()
        self.erzeuge_seite_liste_beihilfepakete()
        self.erzeuge_seite_formular_beihilfepakete()
        self.erzeuge_seite_liste_pkvpakete()
        self.erzeuge_seite_formular_pkvpakete()

        # Erstelle die Menüleiste
        self.commands.add(self.cmd_rechnungen_anzeigen)
        self.commands.add(self.cmd_rechnungen_neu)
        self.commands.add(self.cmd_beihilfepakete_anzeigen)
        self.commands.add(self.cmd_beihilfepakete_neu)
        self.commands.add(self.cmd_pkvpakete_anzeigen)
        self.commands.add(self.cmd_pkvpakete_neu)
        self.commands.add(self.cmd_einrichtungen_anzeigen)
        self.commands.add(self.cmd_einrichtungen_neu)
        self.commands.add(self.cmd_archivieren)

        # Erstelle das Hauptfenster
        self.main_window = toga.MainWindow(title=self.formal_name)      

        # Zeige die Startseite
        self.update_app(None)
        self.zeige_startseite(None)
        self.main_window.show()
        

def main():
    """Hauptschleife der Anwendung"""
    return Kontolupe()