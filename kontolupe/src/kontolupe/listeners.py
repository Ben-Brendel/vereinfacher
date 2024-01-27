"""Listener Klassen für die GUI-Objekte."""

from toga.sources import Listener


class ListListener(Listener):

    def __init__(self, interface, list_source):
        self.interface = interface
        self.list_source = list_source

    def change(self, item):
        self.interface.update(self.list_source)

    def clear(self):
        self.list_source.clear()

    def insert(self, index, item):
        self.interface.update(self.list_source)

    def remove(self, index, item):  
        self.interface.update(self.list_source)

class TableListener(Listener):

    def __init__(self, table):
        self.table = table

    def change(self, item):
        self.table.change_row(item)

    def clear(self):
        self.table.clear()

    def insert(self, index, item):
        self.table.insert_row(index, item)

    def remove(self, index, item):  
        self.table.remove(index, item)


class SectionListener(Listener):

    def __init__(self, section):
        self.section = section

    def change(self, item):
        self.section.update_info(item)

    def clear(self):
        self.section.update_info()

    def insert(self, index, item):
        self.section.update_info(index, item)

    def remove(self, index, item):  
        self.section.update_info(index, item)


class ButtonListener(Listener):

    def __init__(self, button):
        self.button = button

    def change(self, item):
        self.button.update_status(item)

    def clear(self):
        self.button.update_status()

    def insert(self, index, item):  
        self.button.update_status(index, item)

    def remove(self, index, item):  
        self.button.update_status(index, item)