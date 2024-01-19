import toga
from kontolupe.layout import *
from kontolupe.validator import *

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


class LabeledTextInput:
    """Create a box with a label and a text input."""

    def __init__(self, parent, label_text, **kwargs):
        self.validator = Validator(kwargs.get('validator', None))
        self.box = toga.Box(style=style_box_row)
        self.label = toga.Label(label_text, style=style_label_input)
        self.text_input = toga.TextInput(
            style=style_input, 
            placeholder=kwargs.get('placeholder', None), 
            on_lose_focus=self.validator.rectify, 
            readonly=kwargs.get('readonly', False)
        )
        self.box.add(self.label)
        self.box.add(self.text_input)
        self.__add_to_parent(parent)

    def __add_to_parent(self, parent):
        parent.add(self.box)

    def _set_label(self, label_text):
        self.label.text = label_text

    def _get_label(self):
        return self.label.text
    
    def hide(self):
        self.box.remove(self.label)
        self.box.remove(self.text_input)

    def show(self):
        self.box.add(self.label)
        self.box.add(self.text_input)

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
        super().__init__(parent, label_text, placeholder="TT.MM.JJJJ", validator='date', **kwargs)

    def get_value_as_date(self):
        self.validator.rectify(self.text_input)
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

        self.validator.rectify(self.text_input)


class LabeledFloatInput(LabeledTextInput):
    """Create a box with a label and a text input for floats."""

    def __init__(self, parent, label_text, **kwargs):
        super().__init__(parent, label_text, validator='float', **kwargs)

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
        super().__init__(parent, label_text, placeholder='https://...', validator='website', **kwargs)


class LabeledMultilineTextInput:
    """Create a box with a label and a multiline text input."""

    def __init__(self, parent, label_text, **kwargs):
        self.box = toga.Box(style=style_box_row)
        self.label = toga.Label(label_text, style=style_label_input)
        self.text_input = toga.MultilineTextInput(style=style_input, readonly=kwargs.get('readonly', False))
        self.box.add(self.label)
        self.box.add(self.text_input)
        self.__add_to_parent(parent)

    def __add_to_parent(self, parent):
        parent.add(self.box)

    def _set_label(self, label_text):
        self.label.text = label_text

    def _get_label(self):
        return self.label.text

    def set_value(self, value):
        self.text_input.value = value

    def get_value(self):
        return self.text_input.value


class LabeledSelection:
    """Create a box with a label and a selection."""

    def __init__(self, parent, label_text, data, accessor, **kwargs):
        self.box = toga.Box(style=style_box_row)
        self.label = toga.Label(label_text, style=style_label_input)
        self.selection = toga.Selection(
            style=style_selection,
            items=data,
            accessor=accessor,
            on_change=kwargs.get('on_change', None)
        )
        self.box.add(self.label)
        self.box.add(self.selection)
        self.__add_to_parent(parent)

    def __add_to_parent(self, parent):
        parent.add(self.box)

    def _set_label(self, label_text):
        self.label.text = label_text

    def _get_label(self):
        return self.label.text

    def set_value(self, value):
        self.selection.value = value

    def get_value(self):
        return self.selection.value
    
    def set_items(self, items):
        self.selection.items = items
    
    def _set_on_change(self, on_change):
        self.selection.on_change = on_change


class LabeledSwitch:
    """Create a box with a label and a switch."""

    def __init__(self, parent, label_text, **kwargs):
        self.box = toga.Box(style=style_box_row)
        self.switch = toga.Switch(label_text, style=kwargs.get('style', style_switch), on_change=kwargs.get('on_change', None))
        self.box.add(self.switch)
        self.__add_to_parent(parent)

    def __add_to_parent(self, parent):
        parent.add(self.box)

    def _set_label(self, label_text):
        self.label.text = label_text

    def _get_label(self):
        return self.label.text

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