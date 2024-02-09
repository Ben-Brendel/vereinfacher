"""GUI-Objekte für die Kontolupe-App."""

import toga
from kontolupe.layout import *
from kontolupe.validator import *
from kontolupe.database import *
from kontolupe.general import *
from datetime import datetime


class SectionOpenSum(toga.Box):
    """Erzeugt den Anzeigebereich für den offenen Betrag."""

    def __init__(self, window, value_source=True, **kwargs):
        self.value_source = value_source
        self.listener = SectionListener(self)
        self.value_source.add_listener(self.listener)
        super().__init__(style=style_box_offene_buchungen)

        self.box = toga.Box(style=style_box_row)
        self.add(self.box)
        self.info = toga.Label('Offener Betrag: ', style=style_start_summe)
        self.box.add(self.info)
        self.box.add(HelpButton(
            window      = window,
            helptitle   = 'Offener Betrag',
            helptext    = (
                'Dieser Wert zeigt Dir an, wie viel Geld Dir in Summe noch zusteht,'
                ' oder Du noch bezahlen musst.\n\n'
                'Er berechnet sich so:\n'
                '- Nicht bezahlte Rechnungen werden abgezogen.\n'
                '- Nicht eingereichte Rechnungen werden hinzugezählt.\n'
                '- Nicht erstattete Einreichungen werden hinzugezählt.\n'
            )
        ))

        self.update_info()

    def update_info(self, *args):
        result = round(self.value_source.value, 2)
        result = 0.00 if result == -0.00 else result
        self.info.text = 'Offener Betrag: ' + format(result, '.2f').replace('.', ',') + ' €'

class Section(toga.Box):
    """Create a section on the mainpage."""

    def __init__(self, list_source, style, title, on_press_show=None, on_press_new=None, new_enabled=True):

        self.list_source = list_source
        self.listener = SectionListener(self)
        self.list_source.add_listener(self.listener)
        super().__init__(style=style)

        self.button_box = toga.Box(style=style_box_buttons_start)
        self.title = toga.Label(title, style=style_label_h2_start)
        self.info = toga.Label('', style=style_label_section)
        self.button_show = toga.Button('Anzeigen', on_press=on_press_show, style=style_button)
        self.button_new = toga.Button('Neu', on_press=on_press_new, style=style_button, enabled=new_enabled)
        self.button_box.add(self.button_show)
        self.button_box.add(self.button_new)
        self.add(self.title)
        self.add(self.info)
        self.add(self.button_box)

        self.update_info()

    def hide(self):
        self.remove(self.title)
        self.remove(self.info)
        self.remove(self.button_box)

    def show(self):
        self.add(self.title)
        self.add(self.info)
        self.add(self.button_box)

    def set_info(self, info_text):
        self.info.text = info_text

    def update_info(self, *args):
        pass

    def set_enabled_new(self, status):
        self.button_new.enabled = status


class SectionBills(Section):
    """Create the section for the bills."""

    def __init__(self, list_source, on_press_show=None, on_press_new=None, **kwargs):
        super().__init__(
            list_source = list_source,
            style = kwargs.get('style', style_section_rechnungen),
            title = 'Rechnungen', 
            on_press_show = on_press_show, 
            on_press_new = on_press_new,
            new_enabled = True
        )
    
    def update_info(self, *args):
        count = len([item for item in self.list_source if not item.bezahlt])

        match count:
            case 0:
                self.info.text = 'Keine offenen Rechnungen.'
            case 1:
                self.info.text = '1 Rechnung noch nicht bezahlt.'
            case _:
                self.info.text = f'{count} Rechnungen noch nicht bezahlt.'


class SectionAllowance(Section):
    """Create the section for the allowance."""

    def __init__(self, list_source, on_press_show=None, on_press_new=None, **kwargs):
        super().__init__(
            list_source = list_source,
            style = style_section_beihilfe, 
            title = 'Beihilfe', 
            on_press_show = on_press_show, 
            on_press_new = on_press_new,
            new_enabled = False
        )

    def update_info(self, *args):
        count = len(self.list_source)
        
        match count:
            case 0:
                self.info.text = 'Keine offenen Rechnungen.'
                self.button_new.enabled = False
            case 1:
                self.info.text = '1 Rechnung noch nicht eingereicht.'
                self.button_new.enabled = True
            case _:
                self.info.text = f'{count} Rechnungen noch nicht eingereicht.'
                self.button_new.enabled = True


class SectionInsurance(Section):
    """Create the section for the insurance."""

    def __init__(self, list_source, on_press_show=None, on_press_new=None, **kwargs):
        super().__init__(
            list_source = list_source,
            style = style_section_pkv, 
            title = 'Private KV', 
            on_press_show = on_press_show, 
            on_press_new = on_press_new,
            new_enabled = False
        )

    def update_info(self, *args):
        # Anzeige und Buttons der offenen Rechnungen aktualisieren
        count = len(self.list_source)
        
        match count:
            case 0:
                self.info.text = 'Keine offenen Rechnungen.'
                self.button_new.enabled = False
            case 1:
                self.info.text = '1 Rechnung noch nicht eingereicht.'
                self.button_new.enabled = True
            case _:
                self.info.text = f'{count} Rechnungen noch nicht eingereicht.'
                self.button_new.enabled = True


class ConnectedButton(toga.Button):
    """Erzeugt einen Button, dessen Status von einer Datenquelle abhängt."""

    def __init__(self, list_source, **kwargs):
        super().__init__(kwargs.get('text', ''), style=kwargs.get('style', style_button), on_press=kwargs.get('on_press', None), enabled=kwargs.get('enabled', True))
        self.list_source = list_source
        self.listener = ButtonListener(self)
        self.list_source.add_listener(self.listener)
        self.update_status()

    def update_status(self, *args):
        if self.list_source:
            self.enabled = True
        else:
            self.enabled = False


class ArchiveButton(ConnectedButton):
    """Erzeugt den Button für die Archivierung auf der Startseite."""

    def __init__(self, list_source, on_press, **kwargs):

        super().__init__(
            list_source = list_source,
            text = '',
            style = style_button,
            on_press = on_press,
            enabled = False,
            **kwargs
        )

    def update_status(self, *args):
        if self.list_source:
            count = len(self.list_source[0].rechnung) + len(self.list_source[0].beihilfe) + len(self.list_source[0].pkv)
        else:
            count = 0

        match count:
            case 0:
                self.enabled = False
                self.text = 'Keine archivierbaren Buchungen'
            case 1:
                self.enabled = True
                self.text = '1 Buchung archivieren'
            case _:
                self.enabled = True
                self.text = f'{count} Buchungen archivieren'

        

class TopBox(toga.Box):
    """Create a box with a label and a button at the top of a window."""

    def __init__(self, label_text, style_box, target_back):
        super().__init__(style=style_box)
        self.button = toga.Button('Zurück', on_press=target_back, style=style_button)
        self.label = toga.Label(label_text, style=style_label_h1_hell)
        self.add(self.button)
        self.add(self.label)

    def set_label(self, label_text):
        self.label.text = label_text

    def _set_on_press(self, target_back):
        self.button.on_press = target_back


class InfoLabel(toga.Box):
    """Create two labels in a row with a title and a value."""

    def __init__(self, title, value=''):
        super().__init__(style=style_box_row)
        self.label_title = toga.Label(title, style=style_label_info)
        self.label_value = toga.Label(value, style=style_label_detail)
        self.add(self.label_title)
        self.add(self.label_value)

    def set_value(self, value):
        self.label_value.text = value


class InfoLink(toga.Box):
    """"Create a button with a hyperlink."""

    def __init__(self, text, on_press=None):
        super().__init__(style=style_box_row)
        self.button = toga.Button(text, on_press=on_press, style=style_button_link)
        self.add(self.button)

    def hide_button(self):
        self.remove(self.button)

    def show_button(self):
        self.add(self.button)

    def set_text(self, text):
        self.button.text = text


class HelpButton(toga.Button):
    """Create a button with a help text."""

    def __init__(self, **kwargs):
        super().__init__(
            '?', 
            on_press=lambda widget: kwargs.get('window', None).info_dialog(kwargs.get('helptitle', 'Hilfe'), kwargs.get('helptext', 'Keine Hilfe verfügbar.')), 
            style=style_button_help
        )


class TableEntry(toga.Box):
    """Erstellt eine Zeile der app-eigenen Tabellenklasse."""

    def __init__(
            self, 
            even = False, 
            texts = ['', '', ''],
            buttons = {'text': [''], 'button_id': [None], 'style': [None], 'on_press': [None]}, 
            **kwargs
        ):

        if even:
            style_box = style_table_box_even
        else:
            style_box = style_table_box_odd

        super().__init__(style=style_box)
    
        # create the elements        
        self.label_box = toga.Box(style=style_table_label_box)
        self.label_inner_box = toga.Box(style=style_box_column_left)
        self.label_inner_upper_box = toga.Box(style=style_box_row)
        self.button_box = toga.Box(style=style_table_button_box)

        self.label_top_left = toga.Label(texts[0], style=style_table_label_top_left)
        self.label_top_right = toga.Label(texts[1], style=style_table_label_top_right)
        self.label_bottom = toga.Label(texts[2], style=style_table_label_bottom) 

        self.label_box.add(self.label_inner_box)
        self.label_inner_box.add(self.label_inner_upper_box)
        self.label_inner_upper_box.add(self.label_top_left)
        self.label_inner_upper_box.add(self.label_top_right)
        self.label_inner_box.add(self.label_bottom)

        # get the maximum number of buttons in the dictionary
        number_of_buttons = max([len(buttons[key]) for key in buttons.keys()])

        # prepare the dictionary for the buttons
        # if the key text is not present or shorter than number_of_buttons fill it up with empty strings
        # if the key on_press is not present or shorter than number_of_buttons fill it up with None
        # if the key button_id is not present or shorter than number_of_buttons fill it up with None
        # if the key style is not present or shorter than number_of_buttons fill it up with style_table_button
        for key in buttons.keys():
            if key == 'text':
                if len(buttons[key]) < number_of_buttons:
                    buttons[key] += [''] * (number_of_buttons - len(buttons[key]))
            elif key == 'button_id':
                if len(buttons[key]) < number_of_buttons:
                    buttons[key] += [None] * (number_of_buttons - len(buttons[key]))
            elif key == 'style':
                if len(buttons[key]) < number_of_buttons:
                    buttons[key] += [style_table_button] * (number_of_buttons - len(buttons[key]))
            elif key == 'on_press':
                if len(buttons[key]) < number_of_buttons:
                    buttons[key] += [None] * (number_of_buttons - len(buttons[key]))
            else:
                print('+++ Kontolupe: Unbekannter Key in TableEntry.__init__(): ' + key)

        # if the key 'text' is not present in the dictionary, add it with empty strings of length number_of_buttons
        if 'text' not in buttons.keys():
            buttons['text'] = [''] * number_of_buttons

        # if the key 'button_id' is not present in the dictionary, add it with None of length number_of_buttons
        if 'button_id' not in buttons.keys():
            buttons['button_id'] = [None] * number_of_buttons

        # if the key 'style' is not present in the dictionary, add it with style_table_button of length number_of_buttons
        if 'style' not in buttons.keys():
            buttons['style'] = [style_table_button] * number_of_buttons

        # if any of the values in the list with the key 'style' is None, replace it with style_table_button
        for i in range(number_of_buttons):
            if buttons['style'][i] is None:
                buttons['style'][i] = style_table_button

        # if the key 'on_press' is not present in the dictionary, add it with None of length number_of_buttons
        if 'on_press' not in buttons.keys():
            buttons['on_press'] = [None] * number_of_buttons

        # create the buttons
        for i in range(number_of_buttons):
            self.button_box.add(toga.Button(
                buttons['text'][i], 
                id=buttons['button_id'][i], 
                style=buttons['style'][i],
                on_press=buttons['on_press'][i]
            ))

        self.add(self.label_box)
        self.add(self.button_box)

    def show(self):
        self.add(self.label_box)
        self.add(self.button_box)

    def hide(self):
        self.remove(self.label_box)
        self.remove(self.button_box)


class Table(toga.Box):
    """Grundklasse für eine app-eigene Tabelle."""

    def __init__(self, list_source, **kwargs):
        super().__init__(style=style_box_column)
        self.list_source = list_source
        self.listener = TableListener(self)
        self.list_source.add_listener(self.listener)
        self.create()

    def create(self):
        for index in range(len(self.list_source)):
            row = self.convert(index)
            self.add(TableEntry(
                texts   = row[0],
                even    = (index % 2 == 0),
                buttons = row[1]
            ))

    def convert(self, index):
        texts = ['', '', '']
        button = {
            'text': [''],
            'button_id': [str(index)],
            'style': [None],
            'on_press': [None]
        }
        return [texts, button]
    
    def clear(self):
        while len(self.children) > 0:
            self.remove(self.children[0])

    def change_row(self, item):
        index = self.list_source.index(item)
        row = self.convert(index)
        self.remove(self.children[index])
        self.insert(index, row)

    def insert_row(self, index, item):
        row = self.convert(index)
        self.insert(
            index,
            TableEntry(
                texts   = row[0],
                even    = (index % 2 == 0),
                buttons = row[1]
            )
        )

    def remove_row(self, index, item):
        self.remove(self.children[index])

    def update(self):
        self.clear()
        self.create()


class TableOpenBookings(Table):
    """Erstellt die Tabelle zur Anzeige der offenen Buchungen."""

    def __init__(self, list_bookings, on_press_pay, on_press_info, **kwargs):
        self.on_press_pay = on_press_pay
        self.on_press_info = on_press_info
        super().__init__(list_bookings, **kwargs)
    
    def convert(self, index):
        booking = self.list_source[index]
        texts = ['', '', '']
        button = {
            'button_id': [str(index), 'i'+str(index)],
            'style': [None, style_button_help],
            'on_press': [self.on_press_pay, self.on_press_info]
        }
        match booking.typ:
            case 'Rechnung':
                texts[0] = 'Rg. ' + booking.info
                texts[1] = ''
                texts[2] = booking.betrag_euro + (', geplant am ' + booking.buchungsdatum if booking.buchungsdatum else '')
                button['text'] = ['Bezahlt', '?']
            case 'Beihilfe':
                texts[0] = 'Beihilfe'
                texts[1] = ' vom ' + booking.datum	
                texts[2] = 'über ' + booking.betrag_euro 
                button['text'] = ['Erstattet', '?']
            case 'PKV':
                texts[0] = 'Private KV' 
                texts[1] = ' vom ' + booking.datum
                texts[2] = 'über ' + booking.betrag_euro
                button['text'] = ['Erstattet', '?']
            case _:
                texts[0] = 'Unbekannter Buchungstyp'
                texts[1] = ''
                texts[2] = 'vom ' + booking.datum + ' über ' + booking.betrag_euro
                button['text'] = ['Gebucht', '?']

        return [texts, button]


class LabeledTextInput(toga.Box):
    """Create a box with a label and a text input."""

    def __init__(self, label_text, **kwargs):
        super().__init__(style=style_box_row)
        self.validator = Validator(kwargs.get('validator', None))
        self.label_box = toga.Box(style=style_flex_box)
        self.input_box = toga.Box(style=style_flex_box)
        self.label = toga.Label(label_text, style=style_label_input_noflex)
        self.text_input = toga.TextInput(
            style=kwargs.get('style_input', style_input), 
            placeholder=kwargs.get('placeholder', None), 
            on_lose_focus=self.validator.rectify, 
            readonly=kwargs.get('readonly', False),
            on_change=kwargs.get('on_change', None)
        )

        self.label_box.add(self.label)
        self.input_box.add(self.text_input)

        if kwargs.get('suffix', None):
            self.input_box.add(toga.Label(kwargs.get('suffix'), style=style_label_input_suffix))

        self.add(self.label_box)
        self.add(self.input_box)

        if 'helptext' in kwargs and 'window' in kwargs:
            self.label_box.add(HelpButton(**kwargs))

    def _set_label(self, label_text):
        self.label.text = label_text

    def _get_label(self):
        return self.label.text
    
    def hide(self):
        self.remove(self.label_box)
        self.remove(self.input_box)

    def show(self):
        self.add(self.label_box)
        self.add(self.input_box)

    def set_value(self, value):
        self.text_input.value = value
        self.validator.rectify(self.text_input)

    def get_value(self):
        self.validator.rectify(self.text_input)
        return self.text_input.value
    
    def _set_on_lose_focus(self, on_lose_focus):
        self.text_input.on_lose_focus = on_lose_focus

    def is_empty(self):
        return not self.text_input or not self.text_input.value
    
    def is_valid(self):
        return self.validator.is_valid(self.text_input)
    

class LabeledDateInput(LabeledTextInput):
    """Create a box with a label and a text input for dates."""

    def __init__(self, label_text, **kwargs):
        super().__init__(
            label_text, 
            placeholder = 'TT.MM.JJJJ', 
            validator   = 'date', 
            on_change   = self.__on_textinput_change,
            style_input = style_input_datepicker,
            **kwargs
        )

        self.datepicker = toga.DateInput(style=style_datepicker, on_change=self.__on_datepicker_change)
        self.input_box.insert(0, self.datepicker)

    def __on_datepicker_change(self, widget):
        self.set_value(widget.value)

    def __on_textinput_change(self, widget):
        # self.datepicker.value = self.get_value_as_date()
        pass

    def get_value_as_date(self):
        return None if not self.text_input.value else datetime.strptime(self.text_input.value, '%d.%m.%Y').date()

    def get_value(self):
        self.validator.rectify(self.text_input)
        return self.text_input.value
        
    def set_value(self, value):
        if value is None:
            self.text_input.value = ''
        elif isinstance(value, str):
            self.text_input.value = value
        elif isinstance(value, datetime):
            self.text_input.value = value.strftime('%d.%m.%Y')
        else:
            self.text_input.value = value

        self.validator.rectify(self.text_input)


class LabeledFloatInput(LabeledTextInput):
    """Create a box with a label and a text input for floats."""

    def __init__(self, label_text, suffix=None, **kwargs):
        super().__init__(label_text, suffix=suffix, validator='float', **kwargs)

    def get_value(self):
        self.validator.rectify(self.text_input)
        return 0.0 if not self.text_input.value else float(self.text_input.value.replace(',', '.'))
    
    def get_value_as_str(self):
        self.validator.rectify(self.text_input)
        return self.text_input.value
    
    def set_value(self, value):     
        if value is None:
            self.text_input.value = ''
        elif isinstance(value, str):
            self.text_input.value = value
        elif isinstance(value, float):
            self.text_input.value = format(value, '.2f').replace('.', ',')
        elif isinstance(value, int):
            self.text_input.value = format(float(value), '.2f').replace('.', ',')

        self.validator.rectify(self.text_input)
    

class LabeledIntInput(LabeledTextInput):
    """Create a box with a label and a text input for integers."""

    def __init__(self, label_text, **kwargs):
        super().__init__(label_text, validator='int', **kwargs)

    def get_value(self):
        self.validator.rectify(self.text_input)
        return 0 if not self.text_input.value else int(self.text_input.value)
    
    def get_value_as_str(self):
        self.validator.rectify(self.text_input)
        return self.text_input.value
    
    def set_value(self, value):
        if value is None:
            self.text_input.value = ''
        elif isinstance(value, str):
            self.text_input.value = value
        elif isinstance(value, int):
            self.text_input.value = str(value)

        self.validator.rectify(self.text_input)


class LabeledPercentInput(LabeledTextInput):
    """Create a box with a label and a text input for percentages."""

    def __init__(self, label_text, **kwargs):
        super().__init__(label_text, validator='percent', **kwargs)

    def get_value(self):
        self.validator.rectify(self.text_input)
        return 0 if not self.text_input.value else int(self.text_input.value)
    
    def get_value_as_str(self):
        self.validator.rectify(self.text_input)
        return self.text_input.value
    
    def set_value(self, value):
        if value is None:
            self.text_input.value = ''
        elif isinstance(value, str):
            self.text_input.value = value
        elif isinstance(value, int):
            self.text_input.value = str(value)

        self.validator.rectify(self.text_input)


class LabeledPostalInput(LabeledTextInput):
    """Create a box with a label and a text input for postal codes."""

    def __init__(self, label_text, **kwargs):
        super().__init__(label_text, validator='postal', **kwargs)


class LabeledPhoneInput(LabeledTextInput):
    """Create a box with a label and a text input for phone numbers."""

    def __init__(self, label_text, **kwargs):
        super().__init__(label_text, validator='phone', **kwargs)


class LabeledEmailInput(LabeledTextInput):
    """Create a box with a label and a text input for email addresses."""

    def __init__(self, label_text, **kwargs):
        super().__init__(label_text, validator='email', **kwargs)


class LabeledWebsiteInput(LabeledTextInput):
    """Create a box with a label and a text input for website addresses."""

    def __init__(self, label_text, **kwargs):
        super().__init__(label_text, placeholder='www.', validator='website', **kwargs)


class LabeledMultilineTextInput(toga.Box):
    """Create a box with a label and a multiline text input."""

    def __init__(self, label_text, **kwargs):
        self.label = toga.Label(label_text, style=style_label_input)
        self.text_input = toga.MultilineTextInput(style=style_input, readonly=kwargs.get('readonly', False))
        
        self.label_box = toga.Box(style=style_flex_box, children=[self.label])
        self.input_box = toga.Box(style=style_flex_box, children=[self.text_input])
        super().__init__(style=style_box_row, children=[self.label_box, self.input_box])

        # Help Button
        if 'helptext' in kwargs and 'window' in kwargs:
            self.label_box.add(HelpButton(**kwargs))

    def show(self):
        self.add(self.label_box)
        self.add(self.input_box)

    def hide(self):
        self.remove(self.label_box)
        self.remove(self.input_box)

    def set_label(self, label_text):
        self.label.text = label_text

    def get_label(self):
        return self.label.text

    def set_value(self, value):
        self.text_input.value = value

    def get_value(self):
        return self.text_input.value


class LabeledSelection(toga.Box):
    """Create a box with a label and a selection."""

    def __init__(self, label_text, data, accessor=None, **kwargs):
        
        self.label = toga.Label(label_text, style=style_label_input)

        self.selection = toga.Selection(
            style=style_selection,
            items=data,
            accessor=accessor,
            on_change=kwargs.get('on_change', None)
        )
        
        self.label_box = toga.Box(style=style_flex_box, children=[self.label])
        self.selection_box = toga.Box(style=style_flex_box, children=[self.selection])
        super().__init__(style=style_box_row, children=[self.label_box, self.selection_box])

        # Help Button
        if 'helptext' in kwargs and 'window' in kwargs:
            self.label_box.add(HelpButton(**kwargs))

    def show(self):
        self.add(self.label_box)
        self.add(self.selection_box)

    def hide(self):
        self.remove(self.label_box)
        self.remove(self.selection_box)

    def set_label(self, label_text):
        self.label.text = label_text

    def get_label(self):
        return self.label.text

    def set_value(self, value):
        self.selection.value = value

    def get_value(self):
        return self.selection.value
    
    def set_items(self, items):
        self.selection.items = items
    
    def set_on_change(self, on_change):
        self.selection.on_change = on_change


class LabeledDoubleSelection(toga.Box):
    """Create a box with a label and two selection fields."""

    def __init__(self, label_text, data, accessors=[None, None], **kwargs):

        self.label = toga.Label(label_text, style=style_label_input)

        self.selections = []

        self.selections.append(toga.Selection(
            style=style_selection,
            items=data[0],
            accessor=accessors[0],
            on_change=kwargs.get('on_change', [None, None])[0]
        ))

        self.selections.append(toga.Selection(
            style=style_selection_flex2,
            items=data[1],
            accessor=accessors[1],
            on_change=kwargs.get('on_change', [None, None])[1]
        ))

        # Boxes
        self.label_box = toga.Box(style=style_flex_box, children=[self.label])
        self.selection_box = toga.Box(style=style_flex_box2, children=self.selections)
        super().__init__(style=style_box_row, children=[self.label_box, self.selection_box])

        # Help Button
        if 'helptext' in kwargs and 'window' in kwargs:
            self.label_box.add(HelpButton(**kwargs))

    def set_label(self, label_text):
        self.label.text = label_text

    def get_label(self):
        return self.label.text

    def set_value(self, value, index=None):
        if index is None:
            self.selections[0].value = value[0]
            self.selections[1].value = value[1]
        else:
            self.selections[index].value = value

    def get_value(self, index=None):
        if index is None:
            return [self.selections[0].value, self.selections[1].value]
        else:
            return self.selections[index].value
    
    def set_items(self, items, index=None):
        if index is None:
            self.selections[0].items = items[0]
            self.selections[1].items = items[1]
        else:
            self.selections[index].items = items
    
    def set_on_change(self, on_change, index=None):
        if index is None:
            self.selections[0].on_change = on_change[0]
            self.selections[1].on_change = on_change[1]
        else:
            self.selections[index].on_change = on_change


class LabeledSwitch(toga.Box):
    """Create a box with a label and a switch."""

    def __init__(self, label_text, **kwargs):
        super().__init__(style=style_box_row)
        self.label_box = toga.Box(style=style_flex_box)
        self.switch_box = toga.Box(style=style_noflex_box)
        self.label = toga.Label(label_text, style=style_label_input_noflex)

        self.switch = toga.Switch(
            '', 
            style=kwargs.get('style', style_switch), 
            on_change=kwargs.get('on_change', None), 
            value=kwargs.get('value', False)
        )

        self.label_box.add(self.label)
        self.switch_box.add(self.switch)
        self.add(self.label_box)
        self.add(self.switch_box)

        if 'helptext' in kwargs and 'window' in kwargs:
            self.label_box.add(HelpButton(**kwargs))

    def set_label(self, label_text):
        self.label.text = label_text

    def get_label(self):
        return self.label.text
    
    def hide(self):
        self.remove(self.label_box)
        self.remove(self.switch_box)

    def show(self):
        self.add(self.label_box)
        self.add(self.switch_box)

    def set_value(self, value):
        self.switch.value = value

    def get_value(self):
        return self.switch.value
    
    def _set_on_change(self, on_change):
        self.switch.on_change = on_change


class ButtonBox(toga.Box):
    """Create a box with up to four buttons."""

    def __init__(self, labels, targets, ids=None, enabled=True, connections=None, **kwargs):
        """Create a box with up to four buttons at the bottom of a window."""
        if not len(labels) == len(targets):
            raise ValueError('Labels and targets must have the same length.')
        
        if ids is not None and not len(labels) == len(ids):
            raise ValueError('There must be either no IDs or as many IDs as labels and targets.')
        
        if ids is None:
            ids = [None] * len(labels)

        if connections is  None:
            connections = [None] * len(labels)
        else:
            if len(connections) != len(labels):
                raise ValueError('The length of connections must be the same as labels (None allowed).')
            

        # enabled should be a list of booleans of the same length than labels and targets
        # if enabled is a boolean, it will be converted to a list of the same length than labels and targets
        # if it is a list of booleans that is shorter than labels and targets, it will be extended to the same length with True
        if isinstance(enabled, bool):
            enabled = [enabled] * len(labels)
        elif isinstance(enabled, list):
            if len(enabled) < len(labels):
                enabled.extend([True] * (len(labels) - len(enabled)))

        self.buttons = []
        for label, target, button_id, status, connection in zip(labels, targets, ids, enabled, connections):
            if isinstance(connection, ListSource):
                self.buttons.append(ConnectedButton(
                    connection, 
                    text=label, 
                    on_press=target, 
                    id=button_id, 
                    style=style_button, 
                    enabled=status
                ))
            else:
                self.buttons.append(toga.Button(label, on_press=target, id=button_id, style=style_button, enabled=status))
            

        if len(self.buttons) < 4:
            super().__init__(style=style_box_row)
            for button in self.buttons:
                self.add(button)
        elif len(self.buttons) == 4:
            super().__init__(style=style_box_column)
            self.box1 = toga.Box(style=style_box_row)
            self.box2 = toga.Box(style=style_box_row)
            for button in self.buttons[:2]:
                self.box1.add(button)
            for button in self.buttons[2:]:
                self.box2.add(button)
            self.add(self.box1)
            self.add(self.box2)

    def set_enabled(self, button_id, status):
        """Enable or disable a button by its ID."""
        for button in self.buttons:
            if button.id == button_id:
                button.enabled = status
                return
        else:
            print("+++ Kontolupe: Button mit ID " + str(button_id) + " nicht gefunden.")


class SubtextDivider(toga.Box):
    """Create a divider with a subtext."""

    def __init__(self, text):
        """Create a divider with a subtext."""
        super().__init__(style=style_box_column)
        self.divider = toga.Divider(style=style_divider_subtext)
        self.label = toga.Label(text, style=style_label_subtext)
        self.add(self.divider)
        self.add(self.label)