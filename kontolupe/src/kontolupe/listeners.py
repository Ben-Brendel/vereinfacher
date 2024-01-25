"""Listener Klassen für die GUI-Objekte."""

from toga.sources import Listener


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


class ButtonListener(Listener):

    def __init__(self, button):
        self.__button = button

    def change(self, item):
        pass

    def clear(self):
        pass

    def insert(self, index, item):  
        pass

    def remove(self, index, item):  
        pass