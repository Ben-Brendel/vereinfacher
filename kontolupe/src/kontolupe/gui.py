import toga
from kontolupe.layout import *

class TopBox:
    def __init__(self, label_text, style_box, target_back):
        self.box = toga.Box(style=style_box)
        self.button = toga.Button('Zurück', on_press=target_back, style=style_button)
        self.label = toga.Label(label_text, style=style_label_h1_hell)
        self.box.add(self.button)
        self.box.add(self.label)

    def add_to_parent(self, parent):
        parent.add(self.box)

    def set_label(self, label_text):
        self.label.text = label_text

    def set_on_press(self, target_back):
        self.button.on_press = target_back


class LabeledTextInput:
    def __init__(self, label_text, placeholder=None, on_lose_focus=None, readonly=False):
        self.box = toga.Box(style=style_box_row)
        self.label = toga.Label(label_text, style=style_label_input)
        self.text_input = toga.TextInput(style=style_input, placeholder=placeholder, on_lose_focus=on_lose_focus, readonly=readonly)
        self.box.add(self.label)
        self.box.add(self.text_input)

    def add_to_parent(self, parent):
        parent.add(self.box)

    def set_label(self, label_text):
        self.label.text = label_text

    def get_label(self):
        return self.label.text

    def set_value(self, value):
        self.text_input.value = value

    def get_value(self):
        return self.text_input.value
    
    def set_on_lose_focus(self, on_lose_focus):
        self.text_input.on_lose_focus = on_lose_focus


class LabeledMultilineTextInput:
    def __init__(self, label_text, readonly=False):
        self.box = toga.Box(style=style_box_row)
        self.label = toga.Label(label_text, style=style_label_input)
        self.text_input = toga.MultilineTextInput(style=style_input, readonly=readonly)
        self.box.add(self.label)
        self.box.add(self.text_input)

    def add_to_parent(self, parent):
        parent.add(self.box)

    def set_label(self, label_text):
        self.label.text = label_text

    def get_label(self):
        return self.label.text

    def set_value(self, value):
        self.text_input.value = value

    def get_value(self):
        return self.text_input.value
    
    def set_on_lose_focus(self, on_lose_focus):
        self.text_input.on_lose_focus = on_lose_focus


class LabeledSelection:
    def __init__(self, label_text, data, accessor, on_change=None):
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

    def add_to_parent(self, parent):
        parent.add(self.box)

    def set_label(self, label_text):
        self.label.text = label_text

    def get_label(self):
        return self.label.text

    def set_value(self, value):
        self.selection.value = value

    def get_value(self):
        return self.selection.value
    
    def set_on_change(self, on_change):
        self.selection.on_change = on_change


class LabeledSwitch:
    def __init__(self, label_text, on_change=None):
        self.box = toga.Box(style=style_box_row)
        self.switch = toga.Switch(label_text, style=style_switch, on_change=on_change)
        self.box.add(self.switch)

    def add_to_parent(self, parent):
        parent.add(self.box)

    def set_label(self, label_text):
        self.label.text = label_text

    def get_label(self):
        return self.label.text

    def set_value(self, value):
        self.switch.value = value

    def get_value(self):
        return self.switch.value
    
    def set_on_change(self, on_change):
        self.switch.on_change = on_change


class BottomBox:
    def __init__(self, labels, targets):
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

    def add_to_parent(self, parent):
        parent.add(self.box)

    def set_on_press(self, button_id, target):
        if button_id < 0 or button_id >= len(self.buttons):
            raise ValueError('Button ID must be between 0 and {}'.format(len(self.buttons) - 1))
        self.buttons[button_id].on_press = target