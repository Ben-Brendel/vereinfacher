"""GUI-Objekte für die Kontolupe-App."""

import toga
from kontolupe.layout import *
from kontolupe.validator import *
from kontolupe.listeners import *
from datetime import datetime

def table_index_selection(widget):
    """Ermittelt den Index des ausgewählten Elements einer Tabelle."""
    if type(widget) == toga.Table and widget.selection is not None:
        zeile = widget.selection
        for i, z in enumerate(widget.data):
            if str(z) == str(zeile):
                return i
        else:
            print("+++ Kontolupe: Ausgewählte Zeile konnte nicht gefunden werden.")
            return None
    else:
        print("+++ Kontolupe: Keine Zeile ausgewählt.")
        return None
    

def add_newlines(input_string, max_line_length):
    lines = input_string.split(' ')
    result_lines = []
    current_line = ''
    for line in lines:
        if len(current_line) + len(line) + 1 > max_line_length:  # +1 for the comma
            result_lines.append(current_line.rstrip(' '))
            current_line = line + ' '
        else:
            current_line += line + ' '
    result_lines.append(current_line.rstrip(' '))
    return '\n'.join(result_lines)


class Section:
    """Create a section on the mainpage."""

    def __init__(self, parent, title, type=None, on_press_show=None, on_press_new=None, new_enabled=True):

        match type:
            case 'rechnungen':
                style = style_section_rechnungen
            case 'beihilfe':
                style = style_section_beihilfe
            case 'pkv':
                style = style_section_pkv
            case 'daten':
                style = style_section_daten
            case _:
                style = style_section_daten

        self.section_box = toga.Box(style=style)
        self.button_box = toga.Box(style=style_box_buttons_start)
        self.title = toga.Label(title, style=style_label_h2_start)
        self.info = toga.Label('', style=style_label_section)
        self.button_show = toga.Button('Anzeigen', on_press=on_press_show, style=style_button)
        self.button_new = toga.Button('Neu', on_press=on_press_new, style=style_button, enabled=new_enabled)
        self.button_box.add(self.button_show)
        self.button_box.add(self.button_new)
        self.section_box.add(self.title)
        self.section_box.add(self.info)
        self.section_box.add(self.button_box)
        self.__add_to_parent(parent)

    def __add_to_parent(self, parent):
        parent.add(self.section_box)

    def hide(self):
        self.section_box.remove(self.title)
        self.section_box.remove(self.info)
        self.section_box.remove(self.button_box)

    def show(self):
        self.section_box.add(self.title)
        self.section_box.add(self.info)
        self.section_box.add(self.button_box)

    def set_info(self, info_text):
        self.info.text = info_text

    def set_enabled_new(self, status):
        self.button_new.enabled = status


class TopBox:
    """Create a box with a label and a button at the top of a window."""

    def __init__(self, parent, label_text, style_box, target_back):
        self.box = toga.Box(style=style_box)
        self.button = toga.Button('Zurück', on_press=target_back, style=style_button)
        self.label = toga.Label(label_text, style=style_label_h1_hell)
        self.box.add(self.button)
        self.box.add(self.label)
        self.__add_to_parent(parent)

    def __add_to_parent(self, parent):
        parent.add(self.box)

    def set_label(self, label_text):
        self.label.text = label_text

    def _set_on_press(self, target_back):
        self.button.on_press = target_back


class InfoLabel:
    """Create two labels in a row with a title and a value."""

    def __init__(self, parent, title, value=''):
        self.box = toga.Box(style=style_box_row)
        self.label_title = toga.Label(title, style=style_label_info)
        self.label_value = toga.Label(value, style=style_label_detail)
        self.box.add(self.label_title)
        self.box.add(self.label_value)
        self.__add_to_parent(parent)

    def __add_to_parent(self, parent):
        parent.add(self.box)

    def set_value(self, value):
        self.label_value.text = value


class InfoLink:
    """"Create a button with a hyperlink."""

    def __init__(self, parent, text, on_press=None):
        self.box = toga.Box(style=style_box_row)
        self.button = toga.Button(text, on_press=on_press, style=style_button_link)
        self.box.add(self.button)
        self.__add_to_parent(parent)

    def __add_to_parent(self, parent):
        parent.add(self.box)

    def hide_button(self):
        self.box.remove(self.button)

    def show_button(self):
        self.box.add(self.button)

    def set_text(self, text):
        self.button.text = text


class HelpButton(toga.Button):
    """Create a button with a help text."""

    def __init__(self, parent, **kwargs):
        super().__init__(
            '?', 
            on_press=lambda widget: kwargs.get('window', None).info_dialog(kwargs.get('helptitle', 'Hilfe'), kwargs.get('helptext', 'Keine Hilfe verfügbar.')), 
            style=style_button_help
        )
        self.__add_to_parent(parent)

    def __add_to_parent(self, parent):
        parent.add(self)


class TableEntry:
    """Erstellt eine Zeile der app-eigenen Tabellenklasse."""

    def __init__(
            self, 
            parent, 
            even = False, 
            texts = ['', '', ''],
            buttons = {'text': [''], 'button_id': [None], 'style': [None], 'on_press': [None]}, 
            **kwargs
        ):

        # create the row style depending on even
        if even:
            style_box = style_table_box_even
        else:
            style_box = style_table_box_odd

        # create the elements        
        self.box = toga.Box(style=style_box)
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

        self.box.add(self.label_box)
        self.box.add(self.button_box)

        self.__add_to_parent(parent)

    def __add_to_parent(self, parent):
        parent.add(self.box)

    def show(self):
        self.box.add(self.label_box)
        self.box.add(self.button_box)

    def hide(self):
        self.box.remove(self.label_box)
        self.box.remove(self.button_box)

    def delete(self):
        self.box.remove(self.label_box)
        self.box.remove(self.button_box)
    
        self.label_top = None
        self.label_bottom = None
        self.label_inner_box = None
        self.label_box = None
        
        while self.button_box.children:
            self.button_box.remove(self.button_box.children[0])

        self.button_box = None
        self.box = None


class Table:
    """Grundklasse für eine app-eigene Tabelle."""

    def __init__(self, parent, list_source, **kwargs):
        self.entries = []
        self.parent = parent
        self.list_source = list_source
        self.listener = TableListener(self)
        self.list_source.add_listener(self.listener)
        self.create()

    def create(self):
        for index in range(len(self.list_source)):
            row = self.convert(index)
            self.entries.append(TableEntry(
                parent          = self.parent, 
                texts           = row[0],
                even            = (index % 2 == 0),
                buttons         = row[1]
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

    def delete(self):
        for entry in self.entries:
            entry.delete()
        self.entries = []

    def update(self):
        self.delete()
        self.create()


class TableOpenBookings(Table):
    """Erstellt die Tabelle zur Anzeige der offenen Buchungen."""

    def __init__(self, parent, list_bookings, on_press_pay, on_press_info, **kwargs):
        self.on_press_pay = on_press_pay
        self.on_press_info = on_press_info
        super().__init__(parent, list_bookings, **kwargs)
    
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


class LabeledTextInput:
    """Create a box with a label and a text input."""

    def __init__(self, parent, label_text, **kwargs):
        self.validator = Validator(kwargs.get('validator', None))
        self.box = toga.Box(style=style_box_row)
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

        self.box.add(self.label_box)
        self.box.add(self.input_box)

        if 'helptext' in kwargs and 'window' in kwargs:
            HelpButton(self.label_box, **kwargs), 

        self.__add_to_parent(parent)

    def __add_to_parent(self, parent):
        parent.add(self.box)

    def _set_label(self, label_text):
        self.label.text = label_text

    def _get_label(self):
        return self.label.text
    
    def hide(self):
        self.box.remove(self.label_box)
        self.box.remove(self.input_box)

    def show(self):
        self.box.add(self.label_box)
        self.box.add(self.input_box)

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

    def __init__(self, parent, label_text, **kwargs):
        super().__init__(
            parent, 
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

    def __init__(self, parent, label_text, suffix=None, **kwargs):
        super().__init__(parent, label_text, suffix=suffix, validator='float', **kwargs)

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

    def __init__(self, parent, label_text, **kwargs):
        super().__init__(parent, label_text, validator='int', **kwargs)

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

    def __init__(self, parent, label_text, **kwargs):
        super().__init__(parent, label_text, validator='percent', **kwargs)

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

    def __init__(self, parent, label_text, **kwargs):
        super().__init__(parent, label_text, validator='postal', **kwargs)


class LabeledPhoneInput(LabeledTextInput):
    """Create a box with a label and a text input for phone numbers."""

    def __init__(self, parent, label_text, **kwargs):
        super().__init__(parent, label_text, validator='phone', **kwargs)


class LabeledEmailInput(LabeledTextInput):
    """Create a box with a label and a text input for email addresses."""

    def __init__(self, parent, label_text, **kwargs):
        super().__init__(parent, label_text, validator='email', **kwargs)


class LabeledWebsiteInput(LabeledTextInput):
    """Create a box with a label and a text input for website addresses."""

    def __init__(self, parent, label_text, **kwargs):
        super().__init__(parent, label_text, placeholder='www.', validator='website', **kwargs)


class LabeledMultilineTextInput:
    """Create a box with a label and a multiline text input."""

    def __init__(self, parent, label_text, **kwargs):
        self.label = toga.Label(label_text, style=style_label_input)
        self.text_input = toga.MultilineTextInput(style=style_input, readonly=kwargs.get('readonly', False))
        
        self.label_box = toga.Box(style=style_flex_box, children=[self.label])
        self.input_box = toga.Box(style=style_flex_box, children=[self.text_input])
        self.box = toga.Box(style=style_box_row, children=[self.label_box, self.input_box])

        # Help Button
        if 'helptext' in kwargs and 'window' in kwargs:
            HelpButton(self.label_box, **kwargs)

        self.__add_to_parent(parent)

    def __add_to_parent(self, parent):
        parent.add(self.box)

    def show(self):
        self.box.add(self.label_box)
        self.box.add(self.input_box)

    def hide(self):
        self.box.remove(self.label_box)
        self.box.remove(self.input_box)

    def set_label(self, label_text):
        self.label.text = label_text

    def get_label(self):
        return self.label.text

    def set_value(self, value):
        self.text_input.value = value

    def get_value(self):
        return self.text_input.value


class LabeledSelection:
    """Create a box with a label and a selection."""

    def __init__(self, parent, label_text, data, accessor=None, **kwargs):
        
        self.label = toga.Label(label_text, style=style_label_input)

        self.selection = toga.Selection(
            style=style_selection,
            items=data,
            accessor=accessor,
            on_change=kwargs.get('on_change', None)
        )
        
        self.label_box = toga.Box(style=style_flex_box, children=[self.label])
        self.selection_box = toga.Box(style=style_flex_box, children=[self.selection])
        self.box = toga.Box(style=style_box_row, children=[self.label_box, self.selection_box])

        # Help Button
        if 'helptext' in kwargs and 'window' in kwargs:
            HelpButton(self.label_box, **kwargs)
        
        self.__add_to_parent(parent)

    def __add_to_parent(self, parent):
        parent.add(self.box)

    def show(self):
        self.box.add(self.label_box)
        self.box.add(self.selection_box)

    def hide(self):
        self.box.remove(self.label_box)
        self.box.remove(self.selection_box)

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


class LabeledDoubleSelection:
    """Create a box with a label and two selection fields."""

    def __init__(self, parent, label_text, data, accessors=[None, None], **kwargs):

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
        self.box = toga.Box(style=style_box_row, children=[self.label_box, self.selection_box])

        # Help Button
        if 'helptext' in kwargs and 'window' in kwargs:
            HelpButton(self.label_box, **kwargs)

        self.__add_to_parent(parent)

    def __add_to_parent(self, parent):
        parent.add(self.box)

    def set_label(self, label_text):
        self.label.text = label_text

    def get_label(self):
        return self.label.text

    def set_value(self, index, value):
        self.selections[index].value = value

    def get_value(self, index):
        return self.selections[index].value
    
    def set_items(self, index, items):
        self.selections[index].items = items
    
    def set_on_change(self, index, on_change):
        self.selections[index].on_change = on_change


class LabeledSwitch:
    """Create a box with a label and a switch."""

    def __init__(self, parent, label_text, **kwargs):
        self.box = toga.Box(style=style_box_row)
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
        self.box.add(self.label_box)
        self.box.add(self.switch_box)

        if 'helptext' in kwargs and 'window' in kwargs:
            HelpButton(self.label_box, **kwargs)

        self.__add_to_parent(parent)

    def __add_to_parent(self, parent):
        parent.add(self.box)

    def set_label(self, label_text):
        self.label.text = label_text

    def get_label(self):
        return self.label.text
    
    def hide(self):
        self.box.remove(self.label_box)
        self.box.remove(self.switch_box)

    def show(self):
        self.box.add(self.label_box)
        self.box.add(self.switch_box)

    def set_value(self, value):
        self.switch.value = value

    def get_value(self):
        return self.switch.value
    
    def _set_on_change(self, on_change):
        self.switch.on_change = on_change


class ButtonBox:
    """Create a box with up to four buttons."""

    def __init__(self, parent, labels, targets, ids=None, enabled=True):
        """Create a box with up to four buttons at the bottom of a window."""
        if not len(labels) == len(targets):
            raise ValueError('Labels and targets must have the same length.')
        
        if ids is not None and not len(labels) == len(ids):
            raise ValueError('There must be either no IDs or as many IDs as labels and targets.')
        
        if ids is None:
            ids = [None] * len(labels)

        # enabled should be a list of booleans of the same length than labels and targets
        # if enabled is a boolean, it will be converted to a list of the same length than labels and targets
        # if it is a list of booleans that is shorter than labels and targets, it will be extended to the same length with True
        if isinstance(enabled, bool):
            enabled = [enabled] * len(labels)
        elif isinstance(enabled, list):
            if len(enabled) < len(labels):
                enabled.extend([True] * (len(labels) - len(enabled)))

        self.buttons = []
        for label, target, button_id, status in zip(labels, targets, ids, enabled):
            self.buttons.append(toga.Button(label, on_press=target, id=button_id, style=style_button, enabled=status))
            

        if len(self.buttons) < 4:
            self.box = toga.Box(style=style_box_row)
            for button in self.buttons:
                self.box.add(button)
        elif len(self.buttons) == 4:
            self.box = toga.Box(style=style_box_column)
            self.box1 = toga.Box(style=style_box_row)
            self.box2 = toga.Box(style=style_box_row)
            for button in self.buttons[:2]:
                self.box1.add(button)
            for button in self.buttons[2:]:
                self.box2.add(button)
            self.box.add(self.box1)
            self.box.add(self.box2)

        self.__add_to_parent(parent)

    def __add_to_parent(self, parent):
        """Add the box to the parent."""
        parent.add(self.box)

    def set_enabled(self, button_id, status):
        """Enable or disable a button by its ID."""
        for button in self.buttons:
            if button.id == button_id:
                button.enabled = status
                return
        else:
            print("+++ Kontolupe: Button mit ID " + str(button_id) + " nicht gefunden.")


class SubtextDivider:
    def __init__(self, parent, text):
        """Create a divider with a subtext."""
        self.box = toga.Box(style=style_box_column)
        self.divider = toga.Divider(style=style_divider_subtext)
        self.label = toga.Label(text, style=style_label_subtext)
        self.box.add(self.divider)
        self.box.add(self.label)
        self.__add_to_parent(parent)

    def __add_to_parent(self, parent):
        """Add the box to the parent."""
        parent.add(self.box)