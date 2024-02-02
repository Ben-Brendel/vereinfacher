"""Listener-Objekte für die GUI-Elemente."""

from toga.sources import Listener
from kontolupe.handlers import *

class SubmitsListener(Listener):

    def __init__(self, list_allowances=None, list_insurances=None):
        self.list_allowances = list_allowances
        self.list_insurances = list_insurances

    def change(self, item):
        print(f'### SubmitsListener.change')
        if self.list_allowances:
            try:
                list_item = self.list_allowances.find({'db_id': item.db_id})
                if item.beihilfe_id is not None:
                    self.list_allowances.remove(list_item)
                    print(f'### SubmitsListener.change: removed item with dbid {item.db_id} and beihilfe_id {item.beihilfe_id} from list_allowances')
            except ValueError:    
                if item.beihilfe_id is None:
                    self.list_allowances.append(dict_from_row(BILL_OBJECT, item))
                    print(f'### SubmitsListener.change: appended item with dbid {item.db_id} and beihilfe_id {item.beihilfe_id} to list_allowances')

        if self.list_insurances:
            try:
                list_item = self.list_insurances.find({'db_id': item.db_id})
                if item.pkv_id is not None:
                    self.list_insurances.remove(list_item)
            except ValueError:
                if item.pkv_id is None:
                    self.list_insurances.append(dict_from_row(BILL_OBJECT, item))


    def clear(self):
        print(f'### SubmitsListener.clear')
        if self.list_allowances:
            self.list_allowances.clear()
        if self.list_insurances:
            self.list_insurances.clear()


    def insert(self, index, item):
        print(f'### SubmitsListener.insert')
        if self.list_allowances:
            if item.beihilfe_id == None:
                try:
                    self.list_allowances.find({'db_id': item.db_id})
                except ValueError:
                    self.list_allowances.append(dict_from_row(BILL_OBJECT, item))
                    print(f'### SubmitsListener.insert: appended item with dbid {item.db_id} and beihilfe_id {item.beihilfe_id} to list_allowances')
            else:
                try:
                    self.list_allowances.remove(self.list_allowances.find({'db_id': item.db_id}))
                    print(f'### SubmitsListener.insert: removed item with dbid {item.db_id} and beihilfe_id {item.beihilfe_id} from list_allowances')
                except ValueError:
                    pass

        if self.list_insurances:
            if item.pkv_id == None:
                try:
                    self.list_insurances.find({'db_id': item.db_id})
                except ValueError:
                    self.list_insurances.append(dict_from_row(BILL_OBJECT, item))
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
                print(f'### SubmitsListener.remove: removed item with dbid {item.db_id} and beihilfe_id {item.beihilfe_id} from list_allowances')
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