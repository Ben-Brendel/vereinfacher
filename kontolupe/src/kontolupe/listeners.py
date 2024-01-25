"""Listener Klassen für die GUI-Objekte."""

from toga.sources import Listener


class TableListener(Listener):

    def __init__(self, table):
        self.__table = table

    def change(self, item):
        self.__table.update()

    def clear(self):
        self.__table.update()

    def insert(self, index, item):
        self.__table.update()

    def remove(self, index, item):  
        self.__table.update()


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