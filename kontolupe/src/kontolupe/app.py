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

        # Input section
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

        self.input_balance_date = toga.TextInput(
            readonly=True,
            value=self.format_date(self.dates[self.date_index]),
            style=Pack(padding=10)
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

        # Create a table with the bookings by taking the data
        # from the bookings list and formatting the date
        # and the amount as a currency value with two decimals
        # and the currency € behind the value
        # the fourth columns boolean value is transformed to a string
        # where 0 is displayed as 'Nein' and 1 as 'Ja'.
        self.table_bookings = toga.Table(
            headings=['Datum', 'Betrag', 'Notiz', 'Wiederkehrend'],
            data=self.table_data(),
            style=Pack(flex=1, padding=10),
            multiple_select=False
        )

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
    
    def update_values(self, widget):
        # retrieve the current values
        try:
            self.balance = Decimal(self.input_balance_today.value)
        except:
            self.balance = 0
        
        self.date_index = int(self.slider_balance_date.value)

        # show the chosen date
        self.input_balance_date.value = self.format_date(self.dates[self.date_index])

        # calculate the future balance
        for booking in self.bookings:
            if booking[0] <= self.dates[self.date_index]:
                self.balance += booking[1]
        self.input_balance_future.value = self.balance

    def new_booking(self, widget):
        print(self.input_balance_today.value)


    """ 
    This method is called when the app starts up and is responsible
    for creating the main window and its contents.
    """
    def startup(self):

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

        # Create the boxes for the main window
        main_box = toga.Box(style=Pack(direction=COLUMN))
        balance_today_box = toga.Box(style=Pack(direction=ROW, flex=1, height=50))
        balance_future_box = toga.Box(style=Pack(direction=ROW, flex=1, height=50))
        slider_box = toga.Box(style=Pack(direction=ROW, flex=1, height=50))
        content_box = toga.Box(style=Pack(direction=COLUMN, flex=1))

        # Add the subboxes to the main box
        main_box.add(balance_today_box)
        main_box.add(balance_future_box)
        main_box.add(slider_box) 
        main_box.add(content_box)

        # Add the widgets to the boxes
        balance_today_box.add(label_balance_today)
        balance_today_box.add(self.input_balance_today)
        balance_future_box.add(label_balance_future)
        balance_future_box.add(self.input_balance_future)
        balance_future_box.add(label_balance_date)
        balance_future_box.add(self.input_balance_date)
        slider_box.add(self.slider_balance_date)
        content_box.add(button_booking)
        content_box.add(self.table_bookings)

        # Create the main window
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()
        
# Main loop
def main():
    return Kontolupe()
