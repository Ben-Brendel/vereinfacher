"""Listener-Objekte für die GUI-Elemente."""

from toga.sources import Listener
from kontolupe.general import *


class CommandListener(Listener):

    def __init__(self, command, list_source):
        self.command = command
        self.list_source = list_source
        self.update()

    def change(self, item):
        self.update(item)

    def clear(self):
        self.command.enabled = False

    def insert(self, index, item):
        self.update(index, item)

    def remove(self, index, item):
        self.update(index, item)

    def update(self, *args, **kwargs):
        if self.list_source:
            self.command.enabled = True
        else:
            self.command.enabled = False


class ArchiveCommandListener(CommandListener):

    def update(self, *args, **kwargs):
        if self.list_source and len(self.list_source[0].rechnung) + len(self.list_source[0].beihilfe) + len(self.list_source[0].pkv) > 0:
            print(f'### ArchiveCommandListener.update: enabled')
            self.command.enabled = True
        else:
            self.command.enabled = False

class SubmitsListener(Listener):

    def __init__(self, list_allowances=None, list_insurances=None):
        self.list_allowances = list_allowances
        self.list_insurances = list_insurances

    def change(self, item):
        print(f'### SubmitsListener.change')
        if self.list_allowances != None:
            try:
                list_item = self.list_allowances.find({'db_id': item.db_id})
                index = self.list_allowances.index(list_item)
                if item.beihilfe_id is not None:
                    self.list_allowances.remove(list_item)
                else:
                    self.list_allowances[index] = dict_from_row(BILL_OBJECT, item)
            except ValueError:    
                if item.beihilfe_id is None:
                    index = get_index_new_element(BILL_OBJECT, self.list_allowances, item)
                    self.list_allowances.insert(index, dict_from_row(BILL_OBJECT, item))

        if self.list_insurances != None:
            try:
                list_item = self.list_insurances.find({'db_id': item.db_id})
                index = self.list_insurances.index(list_item)
                if item.pkv_id is not None:
                    self.list_insurances.remove(list_item)
                else:
                    self.list_insurances[index] = dict_from_row(BILL_OBJECT, item)
            except ValueError:
                if item.pkv_id is None:
                    index = get_index_new_element(BILL_OBJECT, self.list_insurances, item)
                    self.list_insurances.insert(index, dict_from_row(BILL_OBJECT, item))


    def clear(self):
        print(f'### SubmitsListener.clear')
        if self.list_allowances:
            self.list_allowances.clear()
        if self.list_insurances:
            self.list_insurances.clear()


    def insert(self, index, item):
        print(f'### SubmitsListener.insert')
        if self.list_allowances != None:
            if item.beihilfe_id == None:
                try:
                    list_item = self.list_allowances.find({'db_id': item.db_id})
                    list_index = self.list_allowances.index(list_item)
                    self.list_allowances[list_index] = dict_from_row(BILL_OBJECT, item)
                except ValueError:
                    index = get_index_new_element(BILL_OBJECT, self.list_allowances, item)
                    self.list_allowances.insert(index, dict_from_row(BILL_OBJECT, item))
            else:
                try:
                    self.list_allowances.remove(self.list_allowances.find({'db_id': item.db_id}))
                except ValueError:
                    pass

        if self.list_insurances != None:
            if item.pkv_id == None:
                try:
                    list_item = self.list_insurances.find({'db_id': item.db_id})
                    list_index = self.list_insurances.index(list_item)
                    self.list_insurances[list_index] = dict_from_row(BILL_OBJECT, item)
                except ValueError:
                    index = get_index_new_element(BILL_OBJECT, self.list_insurances, item)
                    self.list_insurances.insert(index, dict_from_row(BILL_OBJECT, item))
            else:
                try:
                    self.list_insurances.remove(self.list_insurances.find({'db_id': item.db_id}))
                except ValueError:
                    pass


    def remove(self, index, item):  
        print(f'### SubmitsListener.remove')
        if self.list_allowances and item.beihilfe_id == None:
            try:
                self.list_allowances.remove(self.list_allowances.find({'db_id': item.db_id}))
            except ValueError:
                pass

        if self.list_insurances and item.pkv_id == None:
            try:
                self.list_insurances.remove(self.list_insurances.find({'db_id': item.db_id}))
            except ValueError:
                pass
        

class TableListener(Listener):

    def __init__(self, table):
        self.table = table

    def change(self, item):
        #self.table.change_row(item)
        self.table.update()

    def clear(self):
        self.table.clear()

    def insert(self, index, item):
        #self.table.insert_row(index, item)
        self.table.update()

    def remove(self, index, item):  
        #self.table.remove_row(index, item)
        self.table.update()


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