"""
Behalte den Überblick über Deine Finanzen.

Kontolupe ist eine einfache Anwendung, mit der Du Deine Finanzen im Blick behalten kannst.
Du kannst Deine Buchungen erfassen und den Kontostand berechnen lassen.
"""

import datetime

import toga
from toga.app import AppStartupMethod, OnExitHandler
from toga.icons import Icon
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

import locale
locale.setlocale(locale.LC_ALL, '')

import decimal
from decimal import Decimal


class Kontolupe(toga.App):

    def startup(self):

        # Initial variables
        
        balance = 100
        bookings = [
            (datetime.date(2023,12,12), -100, 'Arzt', 0),
            (datetime.date(2023,12,19), +250, 'Kindergeld', 1),
            (datetime.date(2023,12,27), +500, 'Ben', 0),
            (datetime.date(2024, 1, 1), -300, 'PKV', 1),                        
        ]
        bookings.sort()

        today = datetime.date.today()
        dates = [today + datetime.timedelta(days=i) for i in range(31)]
        
        def format_date(date):
            return date.strftime('%d.%m.%Y')
        
        def changed_balance_date(widget):
            # display the date in the input field
            input_balance_date.value = format_date(dates[int(widget.value)])
            
            # calculate the balance
            try:
                balance = Decimal(input_balance_today.value)
            except:
                balance = 0

            for booking in bookings:
                if booking[0] <= dates[int(widget.value)]:
                    balance += booking[1]
            input_balance_future.value = balance

        def changed_balance(widget):
            changed_balance_date(slider_balance_date)

        def new_booking(widget):
            print(input_balance_today.value)

        # Create the input area for the actual balance
        label_balance_today = toga.Label(
            'Kontostand heute:',
            style=Pack(padding=10)
        )
        
        input_balance_today = toga.NumberInput(
            readonly=False,
            value=balance,
            style=Pack(padding=10),
            step=Decimal('0.01'),
            on_change=changed_balance            
        )

        # Create the display area of the future calculated balance
        label_balance_future = toga.Label(
            'Kontostand:',
            style=Pack(padding=10)
        )
        input_balance_future = toga.NumberInput(
            readonly=True,
            value=balance,
            style=Pack(padding=10),
            step=Decimal('0.01')           
        )

        # Create a date slider that starts at today
        # and goes forward 30 days. The chosen date
        # will be displayed in a separate input field.
        slider_balance_date = toga.Slider(
            min=0,
            max=30,
            tick_count=31,
            value=0,
            on_change=changed_balance_date,
            style=Pack(flex=1, padding=10)
        )

        label_balance_date = toga.Label(
            'am:',
            style=Pack(padding=10)
        )
                
        input_balance_date = toga.TextInput(
            readonly=True,
            value=format_date(dates[0]),
            style=Pack(padding=10)
        )        

        button_booking = toga.Button(
            'Neue Buchung erfassen',
            on_press=new_booking,
            style=Pack(padding=10)
        )

        # Create a table with the bookings by taking the data
        # from the bookings list and formatting the date
        # and the amount as a currency value with two decimals
        # and the currency € behind the value
        # the fourth columns boolean value is transformed to a string
        # where 0 is displayed as 'Nein' and 1 as 'Ja'.
        
        # The table is displayed in a scrollable area.
        data = []
        for booking in bookings:
            data.append((
                format_date(booking[0]), 
                '{:,.2f} €'.format(booking[1]), 
                booking[2], 
                'Ja' if booking[3] else 'Nein'
            ))

        table_bookings = toga.Table(
            headings=['Datum', 'Betrag', 'Notiz', 'Wiederkehrend'],
            data=data,
            style=Pack(flex=1, padding=10),
            multiple_select=False
        )

        # Set up the main window
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
        balance_today_box.add(input_balance_today)
        balance_future_box.add(label_balance_future)
        balance_future_box.add(input_balance_future)
        balance_future_box.add(label_balance_date)
        balance_future_box.add(input_balance_date)
        slider_box.add(slider_balance_date)
        content_box.add(button_booking)
        content_box.add(table_bookings)

        # Create the main window
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()
        

def main():
    return Kontolupe()
