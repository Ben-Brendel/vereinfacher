"""
Behalte den Überblick über Deine Finanzen.

Kontolupe ist eine einfache Anwendung, mit der Du Deine Finanzen im Blick behalten kannst.
Du kannst Deine Buchungen erfassen und den Kontostand berechnen lassen.
"""

import datetime

import toga
from toga.app import AppStartupMethod, OnExitHandler
from toga.icons import Icon
from toga.style.pack import COLUMN, LEFT, RIGHT, ROW, TOP, BOTTOM, CENTER, Pack

# set localization 
import locale
locale.setlocale(locale.LC_ALL, '')

import decimal
from decimal import Decimal


class Kontolupe(toga.App):

    # initialize the app
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        """
        Creating the class variables and initializing them with
        example values.
        """
        # Object variables with initial values
        self.balance = 100

        # Create a list of dates starting from today for the slider
        today = datetime.date.today()
        self.dates = [today + datetime.timedelta(days=i) for i in range(31)]
        self.date_index = 0
        self.date = self.dates[self.date_index]

        # Timespan for the creation of the recurring bookings
        # TODO: make this configurable
        self.timespan = 365

        # Create the list of interval items
        self.interval_items=[
            {'id': 0, 'note': 'einmalig'},
            {'id': 1, 'note': 'wöchentlich'},
            {'id': 2, 'note': '14-tägig'},
            {'id': 3, 'note': 'monatlich'},
            {'id': 4, 'note': 'quartalsweise'},
            {'id': 5, 'note': 'halbjährlich'},
            {'id': 6, 'note': 'jährlich'}
        ]

        # store the index of a selected booking
        self.selected_booking_index = 0
        
        # flags
        self.edit_mode = 0
        self.far_future = 0

        """
        Array of tuples with the following structure:
        (date, amount, note, interval) or in German:
        (Datum, Betrag, Notiz, Intervall)
        date:    datetime.date object
        amount:  Decimal object
        note:    string
        interval boolean: 
            0 = single booking
            1 = recurring every 7 days
            2 = recurring every 14 days
            3 = recurring every month
            4 = recurring every 3 months
            5 = recurring every 6 months
            6 = recurring every year
        """
        # TODO: figure out how to store and read the bookings
        # TODO: add expected bookings that have no fixed date yet
        self.bookings = [
            (datetime.date(2023,12,12), -100, 'Arzt',       0),
            (datetime.date(2023,12,19), +250, 'Kindergeld', 1),
            (datetime.date(2023,12,27), +500, 'Beihilfe',   0),
            (datetime.date(2024, 1, 1), -300, 'PKV',        1),                        
        ]
        self.bookings.sort()

        # create the content boxes
        # first box to be shown will be the main box
        self.create_main_box()      
        self.create_form_box()         


    """
    Creating the box with the main application content.
    """
    def create_main_box(self):
        # Container for the main content
        self.main_box = toga.Box(style=Pack(direction=COLUMN))

        # TODO: styling
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

        self.input_balance_date = toga.DateInput(
            value=self.date,
            style=Pack(padding=10),
            min=datetime.date.today(),
            on_change=self.update_values
        )

        # Slider
        self.slider_balance_date = toga.Slider(
            min=0,
            max=30,
            tick_count=31,
            value=0,
            on_change=self.update_values,
            style=Pack(flex=1, padding=10, padding_top=25)
        )

        # table for the bookings
        self.table_bookings = toga.Table(
            headings=['Datum', 'Betrag', 'Notiz', 'Intervall'],
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
        button_new_booking = toga.Button(
            'Neue Buchung erfassen',
            on_press=self.new_booking,
            style=Pack(padding=10)
        )

        button_delete_booking = toga.Button(
            'Ausgewählte Buchung löschen',
            on_press=self.delete_booking,
            style=Pack(padding=10)
        )

        button_edit_booking = toga.Button(
            'Ausgewählte Buchung bearbeiten',
            on_press=self.edit_booking,
            style=Pack(padding=10)
        )

        # Create the subboxes for the main box        
        balance_today_box = toga.Box(style=Pack(direction=ROW, flex=1, height=50, alignment=CENTER))
        balance_future_box = toga.Box(style=Pack(direction=ROW, flex=1, height=50, alignment=CENTER))
        slider_box = toga.Box(style=Pack(direction=ROW, flex=1, height=50, alignment=CENTER))
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
        content_box.add(button_new_booking)
        content_box.add(button_delete_booking)
        content_box.add(button_edit_booking)


    """
    Create the content for the form box.
    It is not yet visible. It will be shown when the user
    clicks the button to add a new booking.
    """
    def create_form_box(self):
        
        # Create a new box for the form
        self.form_box = toga.Box(style=Pack(direction=COLUMN))

        # header
        self.form_box_header_label = toga.Label('Neue Buchung', style=Pack(padding=(10)))
        self.form_box.add(self.form_box_header_label)

        # date input
        form_box_date = toga.Box(style=Pack(direction=ROW, flex=1, height=50, alignment=CENTER))
        label_date = toga.Label('Datum:', style=Pack(padding=(10)))
        self.form_box_input_date = toga.DateInput(
            value=datetime.date.today(), 
            style=Pack(padding=10, flex=1),
            min=datetime.date.today()
        )
        form_box_date.add(label_date)
        form_box_date.add(self.form_box_input_date)
        self.form_box.add(form_box_date)

        # amount input
        form_box_amount = toga.Box(style=Pack(direction=ROW, flex=1, height=50, alignment=CENTER))
        label_amount = toga.Label('Betrag:', style=Pack(padding=(10)))
        self.form_box_input_amount = toga.NumberInput(
            readonly=False,
            value=0,
            style=Pack(padding=10, flex=1),
            step=Decimal('0.01')
        )
        form_box_amount.add(label_amount)
        form_box_amount.add(self.form_box_input_amount)
        self.form_box.add(form_box_amount)

        # note input
        form_box_note = toga.Box(style=Pack(direction=ROW, flex=1, height=50, alignment=CENTER))
        label_note = toga.Label('Notiz:', style=Pack(padding=(10)))
        self.form_box_input_note = toga.TextInput(value='', style=Pack(padding=10, flex=1))
        form_box_note.add(label_note)
        form_box_note.add(self.form_box_input_note)
        self.form_box.add(form_box_note)

        # interval input
        form_box_interval = toga.Box(style=Pack(direction=ROW, flex=1, height=50, alignment=CENTER))
        label_interval = toga.Label('Intervall:', style=Pack(padding=(10)))

        self.form_box_input_interval = toga.Selection(
            items=[item['note'] for item in self.interval_items],
            style=Pack(padding=10, flex=1)
        )
        self.form_box_input_interval.value = self.interval_items[0]['note']
        
        form_box_interval.add(label_interval)
        form_box_interval.add(self.form_box_input_interval)
        self.form_box.add(form_box_interval)

        # button box
        # TODO: add functionality to the buttons
        form_box_buttons = toga.Box(style=Pack(direction=COLUMN, flex=1))
        
        button_cancel = toga.Button(
            'Abbrechen',
            on_press=self.cancel_booking,
            style=Pack(padding=10, flex=1)
        )
        form_box_buttons.add(button_cancel)

        self.button_save = toga.Button(
            'Speichern',
            on_press=self.save_booking,
            style=Pack(padding=10, flex=1)
        )
        form_box_buttons.add(self.button_save)

        button_save_and_new = toga.Button(
            'Speichern und neue Buchung',
            on_press=self.save_booking,
            style=Pack(padding=10, flex=1)
        )
        form_box_buttons.add(button_save_and_new)

        self.form_box.add(form_box_buttons)


    """
    Delete the selected booking if there is a selection.
    """
    def delete_booking(self, widget):
        # Delete the selected booking from the bookings list
        if self.table_bookings.selection:
            index = self.table_bookings.data.index(self.table_bookings.selection)
            self.bookings.pop(index)
            self.update_values(widget)

    """
    Cancel the booking form.
    """
    def cancel_booking(self, widget):
        self.main_window.content = self.main_box
        self.clear_form_box()

    """
    Save the booking.
    """
    def save_booking(self, widget):
        # Find the selected interval item
        selected_interval_note = self.form_box_input_interval.value
        selected_interval_item = next(item for item in self.interval_items if item['note'] == selected_interval_note)

        # Get the id of the selected interval item
        selected_interval_id = selected_interval_item['id']

        # If edit mode is active, delete the old booking
        if self.edit_mode == 1:
            self.bookings.pop(self.selected_booking_index)
            self.edit_mode = 0        

        # Create the new booking
        new_booking = (
            self.form_box_input_date.value,
            Decimal(self.form_box_input_amount.value),
            self.form_box_input_note.value,
            selected_interval_id
        )

        # Add the new booking to the bookings list and sort the list
        self.bookings.append(new_booking)
        self.bookings.sort()

        # Update the table data
        #self.table_bookings.data = self.table_data()
        self.update_values(widget)

        # Clear the form inputs
        self.clear_form_box()

        # if save button was pressed, return to main box
        if widget == self.button_save:
            self.main_window.content = self.main_box

    """
    Edit the selected booking.
    """
    def edit_booking(self, widget):
        # Set the edit mode flag
        self.edit_mode = 1

        # Find the selected booking
        self.selected_booking_index = self.table_bookings.data.index(self.table_bookings.selection)
        selected_booking = self.bookings[self.selected_booking_index]

        # Fill the form inputs with the values of the selected booking
        self.form_box_header_label.text = 'Buchung bearbeiten'
        self.form_box_input_date.value = selected_booking[0]
        self.form_box_input_amount.value = selected_booking[1]
        self.form_box_input_note.value = selected_booking[2]

        # Find the interval item with the id equal to booking[3]
        interval_item = next(item for item in self.interval_items if item['id'] == selected_booking[3])
        self.form_box_input_interval.value = interval_item['note']

        # Switch to the form box
        self.main_window.content = self.form_box


    """
    Event handlers.
    """
    def new_booking(self, widget):
        # Switch to the form box
        self.main_window.content = self.form_box 


    """
    Helper functions.
    """
    def table_data(self):
        # Parse the table data list from the bookings list
        table_data = []
        for booking in self.bookings:
            # Find the interval item with the id equal to booking[3]
            interval_item = next(item for item in self.interval_items if item['id'] == booking[3])

            table_data.append((
                self.format_date(booking[0]), 
                '{:,.2f} €'.format(booking[1]), 
                booking[2], 
                interval_item['note']  # Display the note of the chosen interval
            ))
        return table_data


    def format_date(self, date):
        return date.strftime('%d.%m.%Y') 
    

    def clear_form_box(self):
        # Clear the form box
        self.form_box_header_label.text = 'Neue Buchung'
        self.form_box_input_date.value = datetime.date.today()
        self.form_box_input_amount.value = 0
        self.form_box_input_note.value = ''
        self.form_box_input_interval.value = self.interval_items[0]['note']


    """
    The most important function for getting the values right.
    """
    def update_values(self, widget):
        # getting the date values right
        # TODO: clean up!
        if widget == self.slider_balance_date:
            if not self.far_future:
                self.date_index = int(widget.value)
                self.date = self.dates[self.date_index]
                self.input_balance_date.value = self.date
            else:
                self.far_future = 0
            """
            important to interrupt the function here
            because changing the value of input_balance_date
            will trigger the function again which would lead
            to a miscalculation of the future balance
            """
            return
        
        elif widget == self.input_balance_date:
            self.date = widget.value
            try:
                self.date_index = self.dates.index(self.date)
            except:
                self.date_index = 30
                self.far_future = 1
            self.slider_balance_date.value = self.date_index
        
        elif widget == self.input_balance_today:
            try:
                self.balance = Decimal(self.input_balance_today.value)
            except:
                self.balance = 0

        # calculate the future balance
        new_balance = self.balance
        for booking in self.bookings:
            if booking[0] <= self.date:
                new_balance += booking[1]
        self.input_balance_future.value = new_balance

        # update the table
        self.table_bookings.data = self.table_data()


    """ 
    This method is called when the app starts up and is responsible
    for creating the main window and its contents.
    """
    # TODO: add a refresh functionality when the app has been
    #       started on another day
    def startup(self):
        # create the main window
        self.main_window = toga.MainWindow(title=self.formal_name)

        # show the main box
        self.main_window.content = self.main_box
        self.main_window.show()
        
# Main loop
def main():
    return Kontolupe()
