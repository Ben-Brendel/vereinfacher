"""
Behalte den Überblick über Deine Finanzen.

Kontolupe ist eine einfache Anwendung, mit der Du Deine Finanzen im Blick behalten kannst.
Du kannst Deine Buchungen erfassen und den Kontostand berechnen lassen.
"""

import datetime

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW


class Kontolupe(toga.App):

    def startup(self):

        # main variables
        balance = 100

        bookings = [
        ('28.12.2023', -100, 'Arzt'),
        ('01.01.2024', +250, 'Kindergeld'),
        ('05.01.2024', -300, 'PKV'),
        ('18.01.2024', +500, 'Ben')
    ]

        def format_date(date):
            return date.strftime('%d.%m.%Y')
        
        def format_balance(balance):
            return '{:.2f} €'.format(balance)

        def changed_balance_date(widget):
            # print(format_date(dates[int(widget.value)]))
            input_balance_date.value = format_date(dates[int(widget.value)])

        def update_balance(widget):
            # open the new window
            self.balance_window.show()

        def close_balance_window(widget):
            # close the new window
            self.balance_window.hide()
            # return the value of the input field
            balance = self.balance_window.widgets['new_balance'].value
            # update the balance in the main window
            input_balance.value = format_balance(balance)


        # Create the widgets
        label_balance = toga.Label(
            'Kontostand:',
            style=Pack(padding=10)
        )

        # create a readonly text input field for the balance
        # formatted as a currency value with two decimals
        # and the currency € behind the value
        input_balance = toga.TextInput(
            readonly=True,
            value=format_balance(balance),
            style=Pack(padding=10)
        )

        button_balance = toga.Button(
            'Kontostand aktualisieren',
            on_press=update_balance,
            style=Pack(padding=10)
        )

        # Create a date slider that starts at today
        # and goes forward 30 days. The chosen date
        # will be displayed in a separate input field.
        today = datetime.date.today()
        dates = [today + datetime.timedelta(days=i) for i in range(31)]
        slider_balance_date = toga.Slider(
            min=0,
            max=30,
            tick_count=31,
            value=0,
            on_change=changed_balance_date,
            style=Pack(flex=1, padding=10)
        )
                
        input_balance_date = toga.TextInput(
            readonly=True,
            value=format_date(dates[0]),
            style=Pack(padding=10)
        )        

        button_booking = toga.Button(
            'Neue Buchung erfassen',
            #on_press=self.create_booking,
            style=Pack(padding=10)
        )

        table_bookings = toga.Table(
            headings=['Datum', 'Betrag', 'Beschreibung'],
            data=bookings,
            style=Pack(flex=1, padding=10)
        )

        # Set up the main window
        main_box = toga.Box(style=Pack(direction=COLUMN))
        balance_box = toga.Box(style=Pack(direction=ROW, flex=1, height=50))
        slider_box = toga.Box(style=Pack(direction=ROW, flex=1, height=50))
        content_box = toga.Box(style=Pack(direction=COLUMN, flex=1))

        # Add the subboxes to the main box
        main_box.add(balance_box)
        main_box.add(slider_box) 
        main_box.add(content_box)

        # Add the widgets to the boxes
        balance_box.add(label_balance)
        balance_box.add(input_balance)
        balance_box.add(button_balance)
        slider_box.add(slider_balance_date)
        slider_box.add(input_balance_date)
        content_box.add(button_booking)
        content_box.add(table_bookings)

        # Create the main window
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()

        # create a new window with a label called "Aktueller Kontostand:"
        # and a text input field for the new balance and
        # a button to confirm the new balance which then closes the window
        # and updates the balance in the main window
        self.balance_window = toga.Window(
            title='Kontostand aktualisieren',
            closable=False,
            resizable=False,
            minimizable=False,
            size=(200, 100)
        )
        self.balance_window.content = toga.Box(
            children=[
                toga.Label('Aktueller Kontostand:', style=Pack(padding=10)),
                toga.NumberInput(value=balance, step=1, id='new_balance', style=Pack(padding=10)),
                toga.Button('OK', on_press=close_balance_window, style=Pack(padding=10))
            ],
            style=Pack(direction=COLUMN, padding=10),
        )
        

def main():
    return Kontolupe()
