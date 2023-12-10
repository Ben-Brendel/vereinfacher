"""
Behalte den Überblick über Deine Finanzen.

Kontolupe ist eine einfache Anwendung, mit der Du Deine Finanzen im Blick behalten kannst.
Du kannst Deine Buchungen erfassen und den Kontostand berechnen lassen.
"""

import datetime

import toga
from toga.app import AppStartupMethod, OnExitHandler
from toga.icons import Icon
from toga.style.pack import COLUMN, LEFT, RIGHT, ROW, Pack

import locale
locale.setlocale(locale.LC_ALL, '')

import decimal
from decimal import Decimal


class Kontolupe(toga.App):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        """
        Creating the class variables and initializing them with
        example values.
        """
        # Object variables with initial values
        self.balance = 100
        self.bookings = [
            (datetime.date(2023,12,12), -100, 'Arzt',       0),
            (datetime.date(2023,12,19), +250, 'Kindergeld', 1),
            (datetime.date(2023,12,27), +500, 'Ben',        0),
            (datetime.date(2024, 1, 1), -300, 'PKV',        1),                        
        ]
        self.bookings.sort()

        # Create a list of dates starting from today for the slider
        today = datetime.date.today()
        self.dates = [today + datetime.timedelta(days=i) for i in range(31)]
        self.date_index = 0
        self.date = self.dates[self.date_index]

        """
        Creating the box with the main application content.
        """
        # Container for the main content
        self.main_box = toga.Box(style=Pack(direction=COLUMN))

        # Inputs
        self.input_balance_today = toga.NumberInput(
            readonly=False,
            value=self.balance,
            style=Pack(padding=10),
            step=Decimal('0.01'),
            on_change=self.update_values            
        )
        
        self.input_balance_future = toga.NumberInput(
            readonly=True,
            value=self.balance,
            style=Pack(padding=10),
            step=Decimal('0.01')           
        )

        # self.input_balance_date = toga.TextInput(
        #     readonly=True,
        #     value=self.format_date(self.dates[self.date_index]),
        #     style=Pack(padding=10)
        # )  

        self.input_balance_date = toga.DateInput(
            value=self.date,
            style=Pack(padding=10),
            min=today,
            on_change=self.update_values
        )

        # Slider
        self.slider_balance_date = toga.Slider(
            min=0,
            max=30,
            tick_count=31,
            value=0,
            on_change=self.update_values,
            style=Pack(flex=1, padding=10)
        )

        # table for the bookings
        self.table_bookings = toga.Table(
            headings=['Datum', 'Betrag', 'Notiz', 'Wiederkehrend'],
            data=self.table_data(),
            style=Pack(flex=1, padding=10),
            multiple_select=False
        )

        # Label section
        label_balance_today = toga.Label(
            'Kontostand heute:',
            style=Pack(padding=10)
        )

        label_balance_future = toga.Label(
            'Kontostand:',
            style=Pack(padding=10)
        )

        label_balance_date = toga.Label(
            'am:',
            style=Pack(padding=10)
        )

        # Button section
        button_booking = toga.Button(
            'Neue Buchung erfassen',
            on_press=self.new_booking,
            style=Pack(padding=10)
        )

        # Create the subboxes for the main box        
        balance_today_box = toga.Box(style=Pack(direction=ROW, flex=1, height=50))
        balance_future_box = toga.Box(style=Pack(direction=ROW, flex=1, height=50))
        slider_box = toga.Box(style=Pack(direction=ROW, flex=1, height=50))
        content_box = toga.Box(style=Pack(direction=COLUMN, flex=1))

        # Add the subboxes to the main box
        self.main_box.add(balance_today_box)
        self.main_box.add(balance_future_box)
        self.main_box.add(slider_box) 
        self.main_box.add(content_box)

        # Add the widgets to the boxes
        balance_today_box.add(label_balance_today)
        balance_today_box.add(self.input_balance_today)
        balance_future_box.add(label_balance_future)
        balance_future_box.add(self.input_balance_future)
        balance_future_box.add(label_balance_date)
        balance_future_box.add(self.input_balance_date)
        slider_box.add(self.slider_balance_date)
        content_box.add(self.table_bookings)
        content_box.add(button_booking)
        

        """
        Create the content for the form box.
        It is not yet visible. It will be shown when the user
        clicks the button to add a new booking.
        """
        # Create a new box for the form
        self.form_box = toga.Box(style=Pack(direction=COLUMN))

        # Create a label and text input for each field in the form
        name_label = toga.Label('Name:', style=Pack(padding=(10)))
        name_input = toga.TextInput()

        amount_label = toga.Label('Amount:', style=Pack(padding=(10)))
        amount_input = toga.NumberInput()

        # Add the labels and inputs to the form box
        self.form_box.add(name_label)
        self.form_box.add(name_input)
        self.form_box.add(amount_label)
        self.form_box.add(amount_input)

    def table_data(self):
        # Parse the table data list from the bookings list
        table_data = []
        for booking in self.bookings:
            table_data.append((
                self.format_date(booking[0]), 
                '{:,.2f} €'.format(booking[1]), 
                booking[2], 
                'Ja' if booking[3] else 'Nein'
            ))
        return table_data

    def format_date(self, date):
        return date.strftime('%d.%m.%Y')
    
    def new_booking(self, widget):
        
        # Switch to the form box
        self.main_window.content = self.form_box
        # Refresh the main window to show the new form
        self.main_window.refresh()    

    """
    The most important function to getting the values right.
    """
    def update_values(self, widget):
        # getting the date values right
        if widget == self.slider_balance_date:
            self.date_index = int(widget.value)
            self.date = self.dates[self.date_index]
            self.input_balance_date.value = self.date
            return
        
        elif widget == self.input_balance_date:
            self.date = widget.value
            try:
                self.date_index = self.dates.index(self.date)
            except:
                self.date_index = 30
            self.slider_balance_date.value = self.date_index
        
        elif widget == self.input_balance_today:
            try:
                self.balance = Decimal(self.input_balance_today.value)
            except:
                self.balance = 0

        print('Balance: '+str(self.balance))
        # calculate the future balance
        new_balance = self.balance
        for booking in self.bookings:
            if booking[0] <= self.date:
                print('Buchung: '+str(booking[1]))
                new_balance += booking[1]
        self.input_balance_future.value = new_balance

        # update the table
        self.table_bookings.data = self.table_data()


    """ 
    This method is called when the app starts up and is responsible
    for creating the main window and its contents.
    """
    def startup(self):
        # Create the main window
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = self.main_box
        self.main_window.show()
        
# Main loop
def main():
    return Kontolupe()
