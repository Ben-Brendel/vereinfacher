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
from toga.paths import Paths
from decimal import Decimal
from pathlib import Path

import os

# set localization 
import locale
locale.setlocale(locale.LC_ALL, '')


class Kontolupe(toga.App):

    # initialize the app
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        """
        Creating the class variables and initializing them with
        example values.
        """

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
        self.selected_expected_index = 0
        
        # flags
        self.appstart = 1
        self.edit_mode = 0
        self.edit_mode_expected = 0
        self.far_future = 0

        # Variable for saving the balance
        self.balance = 0

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

        # TODO: add expected bookings that have no fixed date yet
        # self.bookings = [
        #     (datetime.date(2023,12,18), -100, 'Arzt',       0),
        #     (datetime.date(2023,12,19), +250, 'Kindergeld', 1),
        #     (datetime.date(2023,12,27), +500, 'Beihilfe',   0),
        #     (datetime.date(2024, 1, 1), -300, 'Test',        0),                        
        #     (datetime.date(2024, 1, 2), -250, 'Test',        0),
        #     (datetime.date(2024, 1, 3), +150, 'Test',        0),
        #     (datetime.date(2024, 1, 4), -800, 'Test',        0),
        #     (datetime.date(2024, 1, 5), +2500, 'Gehalt',     0),
        #     (datetime.date(2024, 1, 6), -300, 'Test',        0),
        #     (datetime.date(2024, 1, 7), +200, 'Test',        0),
        #     (datetime.date(2024, 1, 8), -550, 'Test',        0),
        # ]
        self.bookings = []

        # self.expected = [
        #     ('Kindergeld', 250),
        #     ('Beihilfe', 500),
        #     ('Gehalt', 2500),
        #     ('Beihilfe', 300),
        #     ('Beihilfe', 200),
        #     ('PKV', 300),
        #     ('PKV', 200),
        # ]        
        self.expected = []

        # create the path name to the data file
        # and create the file if it does not exist
        # then load the saved data
        self.data_file = Path(os.path.dirname(os.path.abspath(__file__))) / Path('data.txt')
        # print(self.data_file)
        if not self.data_file.exists():
            self.data_file.touch()
        self.load_data()
        self.bookings.sort()
        self.expected.sort()

        # create the content boxes
        # first box to be shown will be the main box
        # HAS TO BE AT THE END OF THE INIT FUNCTION!!!
        self.create_main_box()      
        self.create_form_box()         
        self.create_expected_box()


    """
    Creating the box with the main application content.
    """
    def create_main_box(self):

        # Inputs
        self.input_balance_today = toga.NumberInput(
            readonly=False,
            value=self.balance,
            style=Pack(padding=5, padding_bottom=20, padding_top=20),
            step=Decimal('0.01'),
            on_change=self.update_values            
        )
        
        self.input_balance_future = toga.NumberInput(
            readonly=True,
            value=self.balance,
            style=Pack(padding=5, padding_top=20, font_weight='bold'),
            step=Decimal('0.01')           
        )

        self.input_balance_future_with_expected = toga.NumberInput(
            readonly=True,
            value=self.balance,
            style=Pack(padding=5, padding_bottom=20, font_weight='bold'),
            step=Decimal('0.01')           
        )

        self.input_balance_date = toga.DateInput(
            value=self.date,
            style=Pack(padding=5),
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
            style=Pack(flex=1, padding=20)
        )

        # tables
        self.table_bookings = toga.Table(
            accessors=['Datum', 'Betrag', 'Notiz', 'Intervall'],
            data=self.table_data(),
            style=Pack(flex=1, padding=5, height=200),
            multiple_select=False,
            on_activate=self.edit_booking
        )

        self.table_expected = toga.Table(
            accessors=['Notiz', 'Betrag'],
            data=self.table_expected_data(),
            style=Pack(flex=1, padding=5, height=200),
            multiple_select=False,
            on_activate=self.edit_expected
        )

        # Label section
        label_balance_today = toga.Label(
            'Kontostand heute:',
            style=Pack(padding=5, padding_left=10)
        )

        label_balance_future = toga.Label(
            'Kontostand:',
            style=Pack(padding=5, padding_left=10, font_weight='bold')
        )

        label_balance_future_with_expected = toga.Label(
            'Kontostand:',
            style=Pack(padding=5, padding_left=10, font_weight='bold')
        )

        label_balance_date = toga.Label(
            'am:',
            style=Pack(padding=0, flex=1)
        )
        
        label_balance_future_with_expected_explanation = toga.Label(
            'inklusive offener Buchungen',
            style=Pack(padding=0, flex=1)
        )

        label_bookings_area = toga.Label(
            'Terminierte Buchungen:',
            style=Pack(
                padding=10,
                font_weight='bold',
            )
        )

        self.label_expected_area = toga.Label(
            'Offene Buchungen:',
            style=Pack(
                padding=10,
                font_weight='bold',
            )
        )

        # Button section
        button_new_booking = toga.Button(
            'Neu',
            on_press=self.new_booking,
            style=Pack(padding=5, flex=1)
        )

        button_delete_booking = toga.Button(
            'Löschen',
            on_press=self.confirm_delete_booking,
            style=Pack(padding=5, flex=1)
        )

        button_edit_booking = toga.Button(
            'Bearbeiten',
            on_press=self.edit_booking,
            style=Pack(padding=5, flex=1)
        )

        button_expected_new = toga.Button(
            'Neu',
            on_press=self.new_expected,
            style=Pack(padding=5, flex=1)
        )

        button_expected_edit = toga.Button(
            'Bearbeiten',
            on_press=self.edit_expected,
            style=Pack(padding=5, flex=1)
        )

        button_expected_delete = toga.Button(
            'Löschen',
            on_press=self.confirm_delete_expected,
            style=Pack(padding=5, flex=1)
        )

        # button_expected_confirm = toga.Button(
        #     'Bestätigen',
        #     on_press=self.confirm_expected,
        #     style=Pack(padding=5, flex=1)
        # )

        # Container for the main content
        self.main_box = toga.Box(style=Pack(direction=COLUMN))

        # ScrollContainer
        self.main_container = toga.ScrollContainer(
            content=self.main_box,
            vertical=True,
            horizontal=False
        )

        # Create the subboxes for the main box        
        balance_today_box = toga.Box(style=Pack(direction=ROW, alignment=CENTER))
        balance_future_box = toga.Box(style=Pack(direction=ROW, alignment=CENTER, background_color='#368BA9'))
        balance_future_with_expected_box = toga.Box(style=Pack(direction=ROW, alignment=CENTER, background_color='#368BA9'))
        slider_box = toga.Box(style=Pack(direction=ROW, alignment=CENTER))
        content_bookings_box = toga.Box(style=Pack(direction=COLUMN, flex=3))
        button_bookings_box = toga.Box(style=Pack(direction=ROW, alignment=CENTER))
        content_expected_box = toga.Box(style=Pack(direction=COLUMN, flex=2))
        button_expected_box = toga.Box(style=Pack(direction=ROW, alignment=CENTER))  

        # Add the subboxes to the main box
        self.main_box.add(balance_today_box)
        self.main_box.add(balance_future_box)
        self.main_box.add(balance_future_with_expected_box)
        self.main_box.add(slider_box) 
        self.main_box.add(content_expected_box)
        self.main_box.add(content_bookings_box)

        # Add the widgets to the boxes
        balance_today_box.add(label_balance_today)
        balance_today_box.add(self.input_balance_today)
        balance_future_box.add(label_balance_future)
        balance_future_box.add(self.input_balance_future)
        balance_future_box.add(label_balance_date)
        balance_future_box.add(self.input_balance_date)
        balance_future_with_expected_box.add(label_balance_future_with_expected)
        balance_future_with_expected_box.add(self.input_balance_future_with_expected)
        balance_future_with_expected_box.add(label_balance_future_with_expected_explanation)
        slider_box.add(self.slider_balance_date)
        
        # bookings area
        content_bookings_box.add(toga.Divider(style=Pack(padding=5)))
        button_bookings_box.add(button_new_booking)
        button_bookings_box.add(button_edit_booking)
        button_bookings_box.add(button_delete_booking)
        content_bookings_box.add(label_bookings_area)
        content_bookings_box.add(self.table_bookings)
        content_bookings_box.add(button_bookings_box)

        # expected area
        content_expected_box.add(toga.Divider(style=Pack(padding=5)))
        button_expected_box.add(button_expected_new)
        button_expected_box.add(button_expected_edit)
        button_expected_box.add(button_expected_delete)
        #button_expected_box.add(button_expected_confirm)
        content_expected_box.add(self.label_expected_area)
        content_expected_box.add(self.table_expected)
        content_expected_box.add(button_expected_box)

    """
    Create the content for the form box for a new scheduled booking.
    It is not yet visible. It will be shown when the user
    clicks the button to add a new booking.
    """
    def create_form_box(self):
        
        # Create a new box for the form
        self.form_box = toga.Box(style=Pack(direction=COLUMN))

        # ScrollContainer
        self.form_container = toga.ScrollContainer(
            content=self.form_box,
            vertical=True,
            horizontal=False
        )

        # header
        self.form_box_header_label = toga.Label('Neue Buchung', style=Pack(padding=10, font_weight='bold'))
        self.form_box.add(self.form_box_header_label)

        # date input
        form_box_date = toga.Box(style=Pack(direction=ROW, flex=1, height=50, alignment=CENTER))
        label_date = toga.Label('Datum:', style=Pack(padding=10))
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
        label_amount = toga.Label('Betrag:', style=Pack(padding=10))
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
        label_note = toga.Label('Notiz:', style=Pack(padding=10))
        self.form_box_input_note = toga.TextInput(value='', style=Pack(padding=10, flex=1))
        form_box_note.add(label_note)
        form_box_note.add(self.form_box_input_note)
        self.form_box.add(form_box_note)

        # interval input
        form_box_interval = toga.Box(style=Pack(direction=ROW, flex=1, height=50, alignment=CENTER))
        label_interval = toga.Label('Intervall:', style=Pack(padding=10))

        self.form_box_input_interval = toga.Selection(
            items=[item['note'] for item in self.interval_items],
            style=Pack(padding=10, flex=1)
        )
        self.form_box_input_interval.value = self.interval_items[0]['note']
        
        form_box_interval.add(label_interval)
        form_box_interval.add(self.form_box_input_interval)
        self.form_box.add(form_box_interval)

        # button box
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
    Create the content for the form box for a new expected booking.
    """
    def create_expected_box(self):
        
        # Create a new box for the form
        self.expected_box = toga.Box(style=Pack(direction=COLUMN))

        # ScrollContainer
        self.expected_container = toga.ScrollContainer(
            content=self.expected_box,
            vertical=True,
            horizontal=False
        )

        # header
        self.expected_box_header_label = toga.Label('Neue offene Buchung', style=Pack(padding=10, font_weight='bold'))
        self.expected_box.add(self.expected_box_header_label)

        # note input
        expected_box_note = toga.Box(style=Pack(direction=ROW, flex=1, height=50, alignment=CENTER))
        label_note = toga.Label('Notiz:', style=Pack(padding=(10)))
        self.expected_box_input_note = toga.TextInput(value='', style=Pack(padding=10, flex=1))
        expected_box_note.add(label_note)
        expected_box_note.add(self.expected_box_input_note)
        self.expected_box.add(expected_box_note)

        # amount input
        expected_box_amount = toga.Box(style=Pack(direction=ROW, flex=1, height=50, alignment=CENTER))
        label_amount = toga.Label('Betrag:', style=Pack(padding=(10)))
        self.expected_box_input_amount = toga.NumberInput(
            value=0,
            style=Pack(padding=10, flex=1),
            step=Decimal('0.01')
        )
        expected_box_amount.add(label_amount)
        expected_box_amount.add(self.expected_box_input_amount)
        self.expected_box.add(expected_box_amount)

        # button box
        expected_box_buttons = toga.Box(style=Pack(direction=COLUMN, flex=1))
        
        button_cancel = toga.Button(
            'Abbrechen',
            on_press=self.cancel_expected,
            style=Pack(padding=10, flex=1)
        )
        expected_box_buttons.add(button_cancel)

        self.button_expected_save = toga.Button(
            'Speichern',
            on_press=self.save_expected,
            style=Pack(padding=10, flex=1)
        )
        expected_box_buttons.add(self.button_expected_save)

        button_save_and_new = toga.Button(
            'Speichern und neue Buchung',
            on_press=self.save_expected,
            style=Pack(padding=10, flex=1)
        )
        expected_box_buttons.add(button_save_and_new)

        self.expected_box.add(expected_box_buttons)


    """
    Functions to handle the scheduled booking section.
    Buttons on the main box.
    """

    def new_booking(self, widget):
        # Switch to the form box
        self.main_window.content = self.form_container

    def edit_booking(self, widget):

        if not self.table_bookings.selection:
            return

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
        self.main_window.content = self.form_container

    def confirm_delete_booking(self, widget):
        if self.table_bookings.selection:
            self.main_window.confirm_dialog(
                'Buchung löschen', 
                'Soll die ausgewählte Buchung wirklich gelöscht werden?',
                on_result=self.delete_booking
            )

    def delete_booking(self, widget, result):
        # Delete the selected booking from the bookings list
        if self.table_bookings.selection and result:
            index = self.table_bookings.data.index(self.table_bookings.selection)
            self.bookings.pop(index)
            self.update_values(widget)
            self.save_data()


    """
    Functions to handle the scheduled booking section.
    Buttons on the form box.
    """

    def cancel_booking(self, widget):
        self.main_window.content = self.main_container
        self.clear_form_box()

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
        self.update_values(widget)

        # save data
        self.save_data()

        # Clear the form inputs
        self.clear_form_box()

        # if save button was pressed, return to main box
        if widget == self.button_save:
            self.main_window.content = self.main_container

    def clear_form_box(self):
        # Clear the form box
        self.form_box_header_label.text = 'Neue Buchung'
        self.form_box_input_date.value = datetime.date.today()
        self.form_box_input_amount.value = 0
        self.form_box_input_note.value = ''
        self.form_box_input_interval.value = self.interval_items[0]['note']

    """
    Functions to handle the expected booking section.
    Buttons on the main box.
    """    

    def new_expected(self, widget):
        self.main_window.content = self.expected_container

    def edit_expected(self, widget):
        if not self.table_expected.selection:
            return

        # Set the edit mode flag
        self.edit_mode_expected = 1

        # Find the selected booking
        self.selected_expected_index = self.table_expected.data.index(self.table_expected.selection)
        selected_booking = self.expected[self.selected_expected_index]

        # Fill the form inputs with the values of the selected booking
        self.expected_box_header_label.text = 'Offene Buchung bearbeiten'
        self.expected_box_input_amount.value = selected_booking[1]
        self.expected_box_input_note.value = selected_booking[0]

        # Switch to the form box
        self.main_window.content = self.expected_container

    def confirm_delete_expected(self, widget):
        if self.table_expected.selection:
            self.main_window.confirm_dialog(
                'Buchung löschen', 
                'Soll die ausgewählte Buchung wirklich gelöscht werden?',
                on_result=self.delete_expected
            )
    
    def delete_expected(self, widget, result):
        # Delete the selected booking from the bookings list
        if self.table_expected.selection and result:
            index = self.table_expected.data.index(self.table_expected.selection)
            self.expected.pop(index)
            self.update_values(widget)
            self.save_data()

    """
    Functions to handle the expected booking section.
    Buttons on the form box.
    """

    def cancel_expected(self, widget):
        self.main_window.content = self.main_container
        self.clear_expected_box()

    # take the values from the inputs and save the expected booking
    def save_expected(self, widget):
        # If edit mode is active, delete the old booking
        if self.edit_mode_expected == 1:
            self.expected.pop(self.selected_expected_index)
            self.edit_mode_expected = 0      

        # Create the new booking
        new_booking = (
            self.expected_box_input_note.value,
            Decimal(self.expected_box_input_amount.value)
        )

        # Add the new booking to the bookings list and sort the list
        self.expected.append(new_booking)
        self.expected.sort()

        # Update the table data
        self.update_values(widget)

        # save data
        self.save_data()

        # Clear the form inputs
        self.clear_expected_box()

        # if save button was pressed, return to main box
        if widget == self.button_expected_save:
            self.main_window.content = self.main_container

    def clear_expected_box(self):
        # Clear the expected box
        self.expected_box_header_label.text = 'Neue offene Buchung'
        self.expected_box_input_amount.value = 0
        self.expected_box_input_note.value = ''


    """
    Functions to handle the table data.
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
    
    def table_expected_data(self):
        table_data = []
        for booking in self.expected:
            table_data.append((
                booking[0], 
                '{:,.2f} €'.format(booking[1])
            ))
        return table_data

    def format_date(self, date):
        return date.strftime('%d.%m.%Y')     

    """
    Functions for saving and loading the data to the data file
    """
    def save_data(self):
        # print('######### SAVING DATA #########')
        with self.data_file.open('w') as f:
            f.write(str(self.balance) + '\n')
            # print(str(self.balance))
            for booking in self.bookings:
                f.write(str(booking[0]) + '\n')
                # print(str(booking[0]))
                f.write(str(booking[1]) + '\n')
                # print(str(booking[1]))
                f.write(str(booking[2]) + '\n')
                # print(str(booking[2]))
                f.write(str(booking[3]) + '\n')
                # print(str(booking[3]))
            f.write('---\n')
            # print('---')
            for booking in self.expected:
                f.write(str(booking[0]) + '\n')
                # print(str(booking[0]))
                f.write(str(booking[1]) + '\n')
                # print(str(booking[1]))

    def load_data(self):
        # print('######### LOADING DATA #########')
        with self.data_file.open('r') as f:
            try:
                balance = f.readline()
                if not balance:
                    print("No data in file")
                    return
                # print(balance.strip())
                self.balance = Decimal(balance.strip())
                self.bookings = []
                self.expected = []
                while True:
                    date = f.readline()
                    # print(date.strip())
                    if not date or date == '---\n':
                        break
                    amount = f.readline()
                    # print(amount.strip())
                    note = f.readline()
                    # print(note.strip())
                    interval = f.readline()
                    # print(interval.strip())
                    self.bookings.append((datetime.date.fromisoformat(date.strip()), Decimal(amount.strip()), note.strip(), int(interval.strip())))
                while True:
                    note = f.readline()
                    # print(note.strip())
                    if not note:
                        break
                    amount = f.readline()
                    # print(amount.strip())
                    self.expected.append((note.strip(), Decimal(amount.strip())))
            except Exception as e:
                print('Error while loading data from file:', e)
                pass


    """
    Updating the values of the widgets.
    This function should be called every time a value changes.
    """
    def update_values(self, widget):
        # getting the date values right
        # TODO: clean up!
        if widget == self.slider_balance_date:
            if not self.far_future:
                self.date_index = int(widget.value)
                self.date = self.dates[self.date_index]
                self.far_future = 1
                self.input_balance_date.value = self.date
            else:
                self.far_future = 0
            return
        
        elif widget == self.input_balance_date:
            if not self.far_future:
                self.date = widget.value
                try:
                    self.date_index = self.dates.index(self.date)
                except:
                    self.date_index = 30
                self.far_future = 1
                self.slider_balance_date.value = self.date_index
            else:
                self.far_future = 0
        
        elif widget == self.input_balance_today:
            try:
                self.balance = Decimal(self.input_balance_today.value)
            except:
                self.balance = 0
            if self.appstart:
                self.appstart = 0
            else:
                self.save_data()

        # calculate the future balance
        new_balance = self.balance
        for booking in self.bookings:
            if booking[0] <= self.date:
                new_balance += booking[1]
        self.input_balance_future.value = new_balance

        # calculate the sum of the expected bookings
        expected_sum = 0
        for booking in self.expected:
            expected_sum += booking[1]
        
        # calculate the future balance including the expected bookings
        new_balance_with_expected = new_balance + expected_sum
        self.input_balance_future_with_expected.value = new_balance_with_expected

        # update the expected label
        self.label_expected_area.text = 'Offene Buchungen: {:,.2f} €'.format(expected_sum)

        # update the tables
        self.table_bookings.data = self.table_data()
        self.table_expected.data = self.table_expected_data()


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
        # self.main_window.content = self.main_box
        self.main_window.content = self.main_container
        # update the display
        self.update_values(self.input_balance_today)
        # show the main window
        self.main_window.show()
        
# Main loop
def main():
    return Kontolupe()
