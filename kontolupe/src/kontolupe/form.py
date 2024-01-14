import toga
from kontolupe.layout import *
from kontolupe.validator import *

class TopBox:
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


class LabeledTextInput:
    def __init__(self, parent, label_text, placeholder=None, validator=None, readonly=False):
        self.validator = Validator(validator)
        self.box = toga.Box(style=style_box_row)
        self.label = toga.Label(label_text, style=style_label_input)
        self.text_input = toga.TextInput(
            style=style_input, 
            placeholder=placeholder, 
            on_lose_focus=self.validator.rectify, 
            readonly=readonly
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

    def set_value(self, value):
        self.text_input.value = value

    def get_value(self):
        return self.text_input.value
    
    def _set_on_lose_focus(self, on_lose_focus):
        self.text_input.on_lose_focus = on_lose_focus

    def is_empty(self):
        return self.text_input.value == ''
    
    def is_valid(self):
        return self.validator.is_valid(self.text_input)
    

class LabeledDateInput(LabeledTextInput):
    def __init__(self, parent, label_text, readonly=False):
        super().__init__(parent, label_text, 'TT.MM.JJJJ', 'date', readonly)

    def get_value(self):
        return None if not self.text_input.value else datetime.strptime(self.text_input.value, '%d.%m.%Y').date()

    def get_value_as_str(self):
        return self.text_input.value
        
    def set_value(self, value):
        if value is None:
            self.text_input.value = ''
        elif isinstance(value, str):
            self.text_input.value = value
        elif isinstance(value, datetime):
            self.text_input.value = value.strftime('%d.%m.%Y')


class LabeledFloatInput(LabeledTextInput):
    def __init__(self, parent, label_text, readonly=False):
        super().__init__(parent, label_text, '', 'float', readonly)

    def get_value_as_date(self):
        return 0.0 if not self.text_input.value else float(self.text_input.value.replace(',', '.'))
    
    def set_value(self, value):     
        if value is None:
            self.text_input.value = ''
        elif isinstance(value, str):
            self.text_input.value = value
        elif isinstance(value, float):
            self.text_input.value = format(value, '.2f').replace('.', ',')
    

class LabeledIntInput(LabeledTextInput):
    def __init__(self, parent, label_text, readonly=False):
        super().__init__(parent, label_text, '', 'int', readonly)

    def get_value(self):
        return 0 if not self.text_input.value else int(self.text_input.value)
    
    def get_value_as_str(self):
        return self.text_input.value
    
    def set_value(self, value):
        if value is None:
            self.text_input.value = ''
        elif isinstance(value, str):
            self.text_input.value = value
        elif isinstance(value, int):
            self.text_input.value = str(value)


class LabeledPercentInput(LabeledTextInput):
    def __init__(self, parent, label_text, readonly=False):
        super().__init__(parent, label_text, '', 'percent', readonly)

    def get_value(self):
        return 0 if not self.text_input.value else int(self.text_input.value)
    
    def get_value_as_str(self):
        return self.text_input.value
    
    def set_value(self, value):
        if value is None:
            self.text_input.value = ''
        elif isinstance(value, str):
            self.text_input.value = value
        elif isinstance(value, int):
            self.text_input.value = str(value)


class LabeledPostalInput(LabeledTextInput):
    def __init__(self, parent, label_text, readonly=False):
        super().__init__(parent, label_text, '', 'postal', readonly)


class LabeledPhoneInput(LabeledTextInput):
    def __init__(self, parent, label_text, readonly=False):
        super().__init__(parent, label_text, '', 'phone', readonly)


class LabeledEmailInput(LabeledTextInput):
    def __init__(self, parent, label_text, readonly=False):
        super().__init__(parent, label_text, '', 'email', readonly)


class LabeledWebsiteInput(LabeledTextInput):
    def __init__(self, parent, label_text, readonly=False):
        super().__init__(parent, label_text, 'https://...', 'website', readonly)


class LabeledMultilineTextInput:
    def __init__(self, parent, label_text, readonly=False):
        self.box = toga.Box(style=style_box_row)
        self.label = toga.Label(label_text, style=style_label_input)
        self.text_input = toga.MultilineTextInput(style=style_input, readonly=readonly)
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
    
    def _set_on_lose_focus(self, on_lose_focus):
        self.text_input.on_lose_focus = on_lose_focus


class LabeledSelection:
    def __init__(self, parent, label_text, data, accessor, on_change=None):
        self.box = toga.Box(style=style_box_row)
        self.label = toga.Label(label_text, style=style_label_input)
        self.selection = toga.Selection(
            style=style_input,
            items=data,
            accessor=accessor,
            on_select=on_change
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
    
    def _set_on_change(self, on_change):
        self.selection.on_change = on_change


class LabeledSwitch:
    def __init__(self, parent, label_text, on_change=None):
        self.box = toga.Box(style=style_box_row)
        self.switch = toga.Switch(label_text, style=style_switch, on_change=on_change)
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


class BottomBox:
    def __init__(self, parent, labels, targets):
        if not len(labels) == len(targets):
            raise ValueError('Labels and targets must have the same length.')
        
        self.buttons = []
        for label, target in zip(labels, targets):
            self.buttons.append(toga.Button(label, on_press=target, style=style_button))

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
        parent.add(self.box)

    def _set_on_press(self, button_id, target):
        if button_id < 0 or button_id >= len(self.buttons):
            raise ValueError('Button ID must be between 0 and {}'.format(len(self.buttons) - 1))
        self.buttons[button_id].on_press = target