"""Listener Klassen für die GUI-Objekte."""

from toga.sources import Listener


class SubmitsListener(Listener):

    def __init__(self, list_allowances=None, list_insurances=None):
        self.list_allowances = list_allowances
        self.list_insurances = list_insurances

    def change(self, item):
        if self.list_allowances:
            if item in self.list_allowances and item.beihilfe_id is not None:
                self.list_allowances.remove(item)
            elif item.beihilfe_id is None:
                self.list_allowances.append(item)

        if self.list_insurances:
            if item in self.list_insurances and item.pkv_id is not None:
                self.list_insurances.remove(item)
            elif item.pkv_id is None:
                self.list_insurances.append(item)

    def clear(self):
        if self.list_allowances:
            self.list_allowances.clear()
        if self.list_insurances:
            self.list_insurances.clear()

    def insert(self, index, item):
        if self.list_allowances and item.beihilfe_id == None:
            self.list_allowances.append(item)
        if self.list_insurances and item.pkv_id == None:
            self.list_insurances.append(item)

    def remove(self, index, item):  
        if self.list_allowances and item.beihilfe_id == None:
            self.list_allowances.remove(item)
        if self.list_insurances and item.pkv_id == None:
            self.list_insurances.remove(item)
        

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