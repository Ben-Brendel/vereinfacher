"""Contains the database and data-interface classes."""

import sqlite3 as sql
import shutil
from pathlib import Path
from datetime import datetime
from toga.sources import ListSource, ValueSource, Row
from kontolupe.listeners import *
from kontolupe.general import *


class Database:
    """Class that manages the database."""

    def __init__(self, data_path=None):
        """Initializes the database."""
        
        # use the provided data path that should be the toga specific path to the data directory
        # if data-path is None and it is an android device use the provided android path
        # otherwise use the provided windows path
        if data_path:
            data_path.mkdir(parents=True, exist_ok=True)
            self.db_dir = data_path
            print(f'### Database: Using data path {self.db_dir} from toga.app')
        elif Path('/data/data/net.biberwerk.kontolupe').exists():
            self.db_dir = Path('/data/data/net.biberwerk.kontolupe')
        elif Path('C:/Users/Ben/code/vereinfacher/kontolupe/src/kontolupe').exists():
            self.db_dir = Path('C:/Users/Ben/code/vereinfacher/kontolupe/src/kontolupe')
        
        self.db_path = self.db_dir / 'kontolupe.db'
        self.init_file = self.db_dir / 'init.txt'

        # Dictionary mit den Tabellen und Spalten der Datenbank erstellen
        self.__tables = {}
        self.__tables['rechnungen'] = []
        for attribute in BILLS_ATTRIBUTES:
            if attribute['name_db'] is not None:
                self.__tables['rechnungen'].append((attribute['name_db'], attribute['type_db']))
        
        self.__tables['beihilfepakete'] = []
        for attribute in ALLOWANCE_ATTRIBUTES:
            if attribute['name_db'] is not None:
                self.__tables['beihilfepakete'].append((attribute['name_db'], attribute['type_db']))
        
        self.__tables['pkvpakete'] = []
        for attribute in INSURANCE_ATTRIBUTES:
            if attribute['name_db'] is not None:
                self.__tables['pkvpakete'].append((attribute['name_db'], attribute['type_db']))
        
        self.__tables['einrichtungen'] = []
        for attribute in INSTITUTION_ATTRIBUTES:
            if attribute['name_db'] is not None:
                self.__tables['einrichtungen'].append((attribute['name_db'], attribute['type_db']))
        
        self.__tables['personen'] = []
        for attribute in PERSON_ATTRIBUTES:
            if attribute['name_db'] is not None:
                self.__tables['personen'].append((attribute['name_db'], attribute['type_db']))

        # Dictionary, welches die umzubenennenden Spalten enthält.
        # Die Spalten werden von einer alten Tabellenversion auf die neueste Tabellenversion migriert.
        self.__table_columns_rename = {
            'arztrechnungen': [
                ('arzt', 'einrichtung_id', 'INTEGER'),
                ('arzt_id', 'einrichtung_id', 'INTEGER')
            ],
            'rechnungen': [
                ('arzt_id', 'einrichtung_id', 'INTEGER')
            ]
        }

        # Liste, welche die umzubenennden Tabellen enthält.
        # Die Tabellen werden direkt auf die neueste Bezeichnung migriert.
        # Bei einer Umbenennung muss auch geprüft werden, ob ältere Einträge angepasst werden müssen.
        self.__tables_rename = {
            'arztrechnungen': 'rechnungen',
            'aerzte': 'einrichtungen'
        }

        self.__tables_predecessors = {new: old for old, new in self.__tables_rename.items()}

        # Speicherorte überprüfen und aktualisieren
        self.__check_paths()

        # Datenbank-Datei initialisieren und ggf. aktualisieren
        self.__create_db()

        # Aktualisiere die init-Datei
        self.__update_init()

    def __update_init(self):
        """Checks and updates the init file."""
        
        # check if the init file exists
        if not self.init_file.exists():
            # check if database exists and has any data
            if self.db_path.exists():
                # load the data
                rechnungen = self.load(BILL_OBJECT, only_active=False)
                beihilfepakete = self.load(ALLOWANCE_OBJECT, only_active=False)
                pkvpakete = self.load(INSURANCE_OBJECT, only_active=False)
                einrichtungen = self.load(INSTITUTION_OBJECT, only_active=False)
                personen = self.load(PERSON_OBJECT, only_active=False)

                # update from the version before the init file was introduced
                if rechnungen or beihilfepakete or pkvpakete or einrichtungen or personen:
                    print(f'### Database: __update_init: Init file {self.init_file} does not exist and database has data. Create initialized init file.')
                    self.save_init_file(version=DATABASE_VERSION, initialized=True, beihilfe=True)
                    return
                else:
                    print(f'### Database: __update_init: Init file {self.init_file} does not exist and database is empty. Create not initialized init file.')
                    self.save_init_file()
                    return
            else:
                print(f'### Database: __update_init: Init file {self.init_file} does not exist and database does not exist. Do not create init file.')
                return

        # load the init file when it exists
        init_file = self.load_init_file()

        # check if the version is in the init file
        if 'version' not in init_file:
            print(f'### Database: __update_init: Version not found in init file {self.init_file}.')
            return

        # check if the version is the latest version
        if init_file['version'] == DATABASE_VERSION:
            print(f"### Database: __update_init: Version {init_file['version']} in init file {self.init_file} is up to date.")
            return
        else:
            print(f"### Database: __update_init: Version {init_file['version']} in init file {self.init_file} is not up to date. Updating it to version {DATABASE_VERSION}.")
            # placeholder for future updates
            return

    def is_first_start(self):
        """Returns if the app is started for the first time."""

        if not self.init_file.exists():
            print(f'### Database.is_first_start: Init file {self.init_file} does not exist. First start.')
            self.save_init_file()
            return True
        init_file = self.load_init_file()
        if 'initialized' not in init_file:
            print(f'### Database.is_first_start: Initialized not found in init file {self.init_file}. First start.')
            return True
        print(f'### Database.is_first_start: Init file {self.init_file} and Initialized exists. Return Initialized.')
        return not init_file['initialized']
    
    def save_init_file(self, **kwargs):
        """Saves the init file."""

        # if the value is a boolean, it should be converted to True or False
        content = ''

        # default values for the first start of the app
        if 'version' not in kwargs:
            kwargs['version'] = DATABASE_VERSION
        if 'initialized' not in kwargs:
            kwargs['initialized'] = False

        for key, value in kwargs.items():
            if isinstance(value, bool):
                value = str(value).lower()
            content += f'{key}={value}\n'

        self.init_file.write_text(content)
        print(f'### Database.save_init_file: Saved init file {self.init_file}')

    def load_init_file(self):
        """Loads the init file."""
        
        # the value should be converted to the correct type
        # return the variables as a dictionary
        result = {}
        if self.init_file.exists(): 
            # read the init file line by line
            for line in self.init_file.read_text().splitlines():
                # check if there is an equal sign in the line
                if '=' not in line:
                    continue
                key, value = line.split('=')
                if value == 'true':
                    value = True
                elif value == 'false':
                    value = False
                elif value.isnumeric():
                    value = int(value)
                result[key] = value

        # check if the version is in the init file and add it if it is not
        if 'version' not in result:
            result['version'] = DATABASE_VERSION

        if 'initialized' not in result:
            result['initialized'] = False

        print(f'### Database.load_init_file: Loaded init file {self.init_file}')
        return result

    def reset(self):
        """Reset all data."""

        # create a backup of the database
        self.__delete_backups()
        self.__create_backup()

        # delete the database
        if self.db_path.exists():
            self.db_path.unlink()
            print(f'### Database: Deleted database {self.db_path}')

        # delete the init file
        if self.init_file.exists():
            self.init_file.unlink()
            print(f'### Database: Deleted init file {self.init_file}')

        # Speicherorte überprüfen und aktualisieren
        self.__check_paths()

        # Datenbank-Datei initialisieren und ggf. aktualisieren
        self.__create_db()

        # Aktualisiere die init-Datei
        self.__update_init()

    def __check_paths(self):
        """Checks if the data is saved at the correct path and moves it if necessary."""

        if not self.db_path.exists():
            if Path('/data/data/net.biberwerk.kontolupe/kontolupe.db').exists():
                # move the database to the correct location
                shutil.move(Path('/data/data/net.biberwerk.kontolupe/kontolupe.db'), self.db_path)
                print(f'### Database.__check_paths: Moved database to {self.db_path}')
            elif Path('C:/Users/Ben/code/vereinfacher/kontolupe/src/kontolupe/kontolupe.db').exists():
                # move the database to the correct location
                shutil.move(Path('C:/Users/Ben/code/vereinfacher/kontolupe/src/kontolupe/kontolupe.db'), self.db_path)
                print(f'### Database.__check_paths: Moved database to {self.db_path}')

        if not self.init_file.exists():
            if Path('/data/data/net.biberwerk.kontolupe/init.txt').exists():
                # move the init file to the correct location
                shutil.move(Path('/data/data/net.biberwerk.kontolupe/init.txt'), self.init_file)
                print(f'### Database.__check_paths: Moved init file to {self.init_file}')
            elif Path('C:/Users/Ben/code/vereinfacher/kontolupe/src/kontolupe/init.txt').exists():
                # move the init file to the correct location
                shutil.move(Path('C:/Users/Ben/code/vereinfacher/kontolupe/src/kontolupe/init.txt'), self.init_file)
                print(f'### Database.__check_paths: Moved init file to {self.init_file}')

    def __get_column_type(self, table_name, column_name):
        """Get the type of a column from the self.__tables dictionary."""

        for column in self.__tables[table_name]:
            if column[0] == column_name:
                print(f'### Database.__get_column_type: Column type for column {column_name} in table {table_name} is {column[1]}')
                return column[1]
        print(f'### Database.__get_column_type: Column {column_name} not found in table {table_name}')
        return None  # return None if the column is not found

    def __create_backup(self):
        """Create a backup of the database."""

        # Get the current date and time, formatted as a string
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create the backup path with the timestamp
        backup_path = self.db_dir / Path(f'kontolupe_{timestamp}.db.backup')
        
        if self.db_path.exists():
            if backup_path.exists():
                backup_path.unlink()
            shutil.copy(self.db_path, backup_path)
            print(f'### Database.__create_backup: Created backup {backup_path}')
        else:
            print(f'### Database.__create_backup: Database {self.db_path} does not exist. No backup created.')

    def __delete_backups(self):
        """Delete all backups of the database."""

        for file in self.db_dir.glob('kontolupe_*.db.backup'):
            print(f'### Database: Deleting backup {file}')
            file.unlink()

    def __create_table_if_not_exists(self, cursor, table_name, columns):
        """Create a table if it does not exist."""

        cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join([f'{column[0]} {column[1]}' for column in columns])})")

    def __add_column_if_not_exists(self, cursor, table_name, new_column, column_type):
        """Add a column to a table if it does not exist."""

        cursor.execute(f"PRAGMA table_info({table_name})")
        if not any(row[1] == new_column for row in cursor.fetchall()):
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {new_column} {column_type}")
            print(f'### Database.__add_column_if_not_exists: Added column {new_column} to table {table_name}')
            if new_column == 'aktiv':
                cursor.execute(f"UPDATE {table_name} SET aktiv = 1")

    def __copy_column(self, cursor, table_name, old_column, new_column):
        """Copy a column within a table (renaming a column)."""

        # Check if table_name exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if not cursor.fetchone():
            print(f'### Database.__copy_column: Table {table_name} does not exist')
            return  # table_name doesn't exist, so return early

        # Check if old_column exists
        cursor.execute(f"PRAGMA table_info({table_name})")
        result = cursor.fetchall()
        if any(row[1] == old_column for row in result):
            # check if new_column exists if not create it
            # look up the type of the new column in the self.__tables dictionary 
            # using the new table name
            self.__add_column_if_not_exists(cursor, table_name, new_column, self.__get_column_type(self.__tables_rename[table_name], new_column))
            
            # copy the data from old_column to new_column
            cursor.execute(f"SELECT id, {old_column} FROM {table_name}")
            db_result = cursor.fetchall()
            for row in db_result:
                cursor.execute(f"UPDATE {table_name} SET {new_column} = ? WHERE id = ?", (row[1], row[0]))
            print(f'### Database.__copy_column: Copied column {old_column} to {new_column} in table {table_name}')
        else:
            print(f'### Database.__copy_column: Column {old_column} does not exist in table {table_name}')

    def __copy_table_and_delete(self, cursor, old_table, new_table):
        """Copy a table to a new table and delete the old table."""

        # Check if old_table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (old_table,))
        if not cursor.fetchone():
            print(f'### Database.__copy_table_and_delete: Table {old_table} does not exist')
            return  # old_table doesn't exist, so return early

        # Get the schema of old_table
        cursor.execute(f"PRAGMA table_info({old_table})")
        columns_info = cursor.fetchall()
        column_names = [column[1] for column in columns_info]  # Get the column names

        # Remove the columns from column_names that are not in the new table
        for column in columns_info:
            if not any(column[1] == column_name for column_name in [column[0] for column in self.__tables[new_table]]):
                column_names.remove(column[1])

        # Copy rows from old_table to new_table
        # select only the columns that are in the new table
        cursor.execute(f"SELECT {', '.join(column_names)} FROM {old_table}")
        db_result = cursor.fetchall()
        for row in db_result:
            # Create a dictionary where keys are column names and values are row values
            row_dict = dict(zip(column_names, row))
            # Create a string of column names and a string of corresponding placeholders
            columns_str = ', '.join(column_names)
            placeholders_str = ', '.join(['?' for _ in column_names])
            # Insert the row into the new table
            cursor.execute(f"INSERT INTO {new_table} ({columns_str}) VALUES ({placeholders_str})", list(row_dict.values()))
        print(f'### Database.__copy_table_and_delete: Copied table {old_table} to {new_table}')

        # Drop old_table
        cursor.execute(f"DROP TABLE {old_table}")
        print(f'### Database.__copy_table_and_delete: Dropped table {old_table}')

    def __create_db(self):
        """Create the database if it does not exist and update it if the structure has changed."""

        # Check if database exists and is structured correctly
        # If not, create a backup and rebuild the database
        if self.__db_exists_and_is_correct():
            return

        # Backup and rebuild the database
        self.__create_backup()
        self.__rebuild_db()

    def __db_exists_and_is_correct(self):
        """Check if the database exists and is structured correctly."""

        if not self.db_path.exists():
            print('### Database.__db_exists_and_is_correct: Database does not exist.')
            return False

        with sql.connect(self.db_path) as connection:
            cursor = connection.cursor()
            for table_name, columns in self.__tables.items():
                if not self.__table_is_correct(cursor, table_name, columns):
                    print(f'### Database.__db_exists_and_is_correct: Database exists but is not structured correctly. Table {table_name} is not correct.')
                    return False

        print('### Database.__db_exists_and_is_correct: Database exists and is structured correctly.')
        return True

    def __table_is_correct(self, cursor, table_name, columns):
        """Check if a table is structured correctly."""

        cursor.execute(f"PRAGMA table_info({table_name})")
        result = cursor.fetchall()
        for column in columns:
            if not any(row[1] == column[0] for row in result):
                return False

        return True

    def __rebuild_db(self):
        """Rebuild the database."""

        with sql.connect(self.db_path) as connection:
            cursor = connection.cursor()

            # Update the database structure
            self.__update_db_structure(cursor)

            # Migrate the data to the new database structure
            self.__migrate_data(cursor)

            # Rename the tables
            self.__rename_tables(cursor)

    def __update_db_structure(self, cursor):
        """Update the database structure."""

        for table_name, columns in self.__tables.items():
            self.__create_table_if_not_exists(cursor, table_name, columns)
            for column in columns:
                self.__add_column_if_not_exists(cursor, table_name, column[0], column[1])

            # look for a predecessor table and update its structure if it exists
            old_table = self.__tables_predecessors.get(table_name)
            if old_table is not None:
                # now check if the old table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (old_table,))
                if cursor.fetchone():
                    # the old table exists, so update its structure
                    for column in self.__tables[table_name]:
                        self.__add_column_if_not_exists(cursor, old_table, column[0], column[1])
                    print(f'### Database.__update_db_structure: Updated table {old_table} to the latest structure.')
            
    def __migrate_data(self, cursor):
        """Migrate the data to the new database structure."""

        for table_name, columns in self.__table_columns_rename.items():
            for column in columns:
                self.__copy_column(cursor, table_name, column[0], column[1])

    def __rename_tables(self, cursor):
        """Rename the tables."""

        for old_table, new_table in self.__tables_rename.items():
            self.__copy_table_and_delete(cursor, old_table, new_table)
            print(f'### Database.__rename_tables: Migrated data from {old_table} to {new_table} and deleted {old_table}')

    def __new_element(self, table, element):
        """Insert a new element into the database."""

        # Datenbankverbindung herstellen
        connection = sql.connect(self.db_path)
        cursor = connection.cursor()

        # Get the columns for the query
        column_names = [column[0] for column in self.__tables[table]]
        column_names.remove('id')

        attributes = get_attributes(table)
        attribute_names = []
        for column in column_names:
            attribute_names.append([attribute['name_object'] for attribute in attributes if attribute['name_db'] == column][0])

        # Build the SQL query and values tuple dynamically
        query = f"""INSERT INTO {table} ({', '.join(column_names)}) VALUES ({', '.join(['?' for _ in column_names])})"""
        # get the values to insert
        if isinstance(element, dict):
            values = tuple(element[attribute] for attribute in attribute_names)
        else:
            values = tuple(getattr(element, attribute) for attribute in attribute_names)

        # Daten einfügen
        cursor.execute(query, values)
        db_id = cursor.lastrowid

        # Datenbankverbindung schließen
        connection.commit()
        connection.close()

        return db_id
    
    def __change_element(self, table, element):
        """Change an element in the database."""

        # Datenbankverbindung herstellen
        connection = sql.connect(self.db_path)
        cursor = connection.cursor()

        # Get the columns for the query
        column_names = [column[0] for column in self.__tables[table]]
        column_names.remove('id')

        attributes = get_attributes(table)
        attribute_names = []
        for column in column_names:
            attribute_names.append([attribute['name_object'] for attribute in attributes if attribute['name_db'] == column][0])

        # Build the SQL query and values tuple dynamically
        query = f"""UPDATE {table} SET {', '.join([f'{column_name} = ?' for column_name in column_names])} WHERE id = ?"""
        if isinstance(element, dict):
            values = tuple(element[attribute] for attribute in attribute_names)
            values += (element['db_id'],)
        else:
            values = tuple(getattr(element, attribute) for attribute in attribute_names)
            values += (element.db_id,)

        # Daten ändern
        cursor.execute(query, values)

        # Datenbankverbindung schließen
        connection.commit()
        connection.close()

    def __delete_element(self, table, element):
        """Delete an element from the database."""

        # Datenbankverbindung herstellen
        connection = sql.connect(self.db_path)
        cursor = connection.cursor()

        # Daten löschen
        if isinstance(element, dict):
            db_id = element['db_id']
        else:
            db_id = element.db_id
        cursor.execute(f"""DELETE FROM {table} WHERE id = ?""", (db_id,))

        # Datenbankverbindung schließen
        connection.commit()
        connection.close()

    def __load_data(self, table, only_active=False):
        """Load data from a table."""

        # Datenbankverbindung herstellen
        connection = sql.connect(self.db_path)
        cursor = connection.cursor()

        # Daten abfragen
        query = f"""SELECT * FROM {table}"""
        if only_active:
            query += f""" WHERE aktiv = 1"""
            print(f'### Database.__load_data: Only active elements will be loaded from table {table}')
        else:
            print(f'### Database.__load_data: All elements will be loaded from table {table}')
        cursor.execute(query)
        db_result = cursor.fetchall()

        # Speichere die Daten in einem Dictionary
        ergebnis = [dict(zip([column[0] for column in cursor.description], row)) for row in db_result]

        # Datenbankverbindung schließen
        connection.close()

        result = []
        for row in ergebnis:
            # Create the data dictionary for the list source
            data = {}
            for attribute in get_attributes(table):
                data[attribute['name_object']] = row.get(attribute['name_db'], attribute['default_value'])  
            result.append(data)

        return result 

    def new(self, object_type, element):
        """Database frontend: insert a new element into the database."""

        db_table = OBJECT_TYPE_TO_DB_TABLE.get(object_type)
        if db_table:
            return self.__new_element(db_table, element)
        else:
            raise ValueError(f'### Database.new: Element {element} not found')

    def save(self, object_type, element):
        """Database frontend: change an element in the database."""

        db_table = OBJECT_TYPE_TO_DB_TABLE.get(object_type)
        if db_table:
            self.__change_element(db_table, element)
        else:
            raise ValueError(f'### Database.save: Element {element} not found')

    def delete(self, object_type, element):
        """Database frontend: delete an element from the database."""

        db_table = OBJECT_TYPE_TO_DB_TABLE.get(object_type)
        if db_table:
            self.__delete_element(db_table, element)
        else:
            raise ValueError(f'### Database.delete: Element {element} not found')

    def load(self, object_type, only_active=True):
        """Database frontend: load data from the database."""

        db_table = OBJECT_TYPE_TO_DB_TABLE.get(object_type)
        if db_table:
            print(f'### Database: Loading {db_table} from database')
            return self.__load_data(db_table, only_active)
        else:
            raise ValueError(f'### Database.load: Invalid object type {object_type}')
    

class DataInterface:
    """Data-interface for the application."""

    def __init__(self, data_path=None):
        """Initializes the data-interface."""
        
        # Datenbank initialisieren
        self.data_path = data_path
        self.db = Database(data_path)
        
        self.accessors_open_bookings = [
                'db_id',                        # Datenbank-Id des jeweiligen Elements
                'typ',                          # Typ des Elements (Rechnung, Beihilfe, PKV)
                'betrag_euro',                  # Betrag der Buchung in Euro
                'datum',                        # Rechnungsdatum oder Einreichungsdatum der Beihilfe/PKV
                'buchungsdatum',                # Buchungsdatum der Rechnung
                'info'                          # Info-Text der Buchung
            ]
        
        self.accessors_archivables = [
                'rechnung',
                'beihilfe',
                'pkv'
            ]
        
        self.bills = ListSource(accessors = get_accessors(BILL_OBJECT))
        self.allowances = ListSource(accessors = get_accessors(ALLOWANCE_OBJECT))
        self.insurances = ListSource(accessors = get_accessors(INSURANCE_OBJECT))
        self.institutions = ListSource(accessors = get_accessors(INSTITUTION_OBJECT))
        self.persons = ListSource(accessors = get_accessors(PERSON_OBJECT))

        self.lists_accessor = {
            BILL_OBJECT: self.bills,
            ALLOWANCE_OBJECT: self.allowances,
            INSURANCE_OBJECT: self.insurances,
            INSTITUTION_OBJECT: self.institutions,
            PERSON_OBJECT: self.persons
        }

        self.allowances_bills = ListSource(accessors = get_accessors(BILL_OBJECT))
        self.insurances_bills = ListSource(accessors = get_accessors(BILL_OBJECT))
        self.open_bookings = ListSource(accessors = self.accessors_open_bookings)
        self.archivables = ListSource(accessors = self.accessors_archivables)

        self.open_sum = ValueSource()

        self.__init_data()

        # Listeners
        self.submits_listener = SubmitsListener(self.allowances_bills, self.insurances_bills)
        self.bills.add_listener(self.submits_listener)

    def __init_data(self):
        """Initial loading of the data after reset or first start."""

        # Init-Dictionary laden
        self.init = self.db.load_init_file()

        # Aktive Einträge aus der Datenbank laden
        object_types = [
            (PERSON_OBJECT, self.persons),
            (INSTITUTION_OBJECT, self.institutions),
            (ALLOWANCE_OBJECT, self.allowances),
            (INSURANCE_OBJECT, self.insurances),
            (BILL_OBJECT, self.bills)
        ]

        for object_type, object_list in object_types:
            sort_key = SORT_KEYS.get(object_type)
            list_objects = self.db.load(object_type)
            if sort_key and 'datum' in sort_key:
                list_objects.sort(key=lambda obj: "".join(reversed(obj[sort_key].split('.'))), reverse=True)
            elif sort_key and 'name' in sort_key:
                list_objects.sort(key=lambda obj: obj[sort_key], reverse=False)
        
            for row in list_objects:
                object_list.append(self.update_object(object_type, **row))

        # Listen initialisieren
        self.update_bills()
        self.update_allowances_bills()
        self.update_insurances_bills()
        self.update_open_bookings()
        self.update_archivables()
        self.update_open_sum()

    def update_object(self, object_type, row=None, **data):
        """Updates the additional, non db-values of an object."""

        def format_euro(value):
            return '{:.2f} €'.format(value).replace('.', ',')

        def format_percent(value):
            return '{:.0f} %'.format(value)

        def get_value(name, default):
            return data.get(name) or (getattr(row, name) if isinstance(row, Row) else 0) or default

        init_data = {}
        for attribute in get_attributes(object_type):
            if attribute['name_object']:
                value = get_value(attribute['name_object'], attribute['default_value'])
                match attribute['name_object']:
                    case 'betrag_euro' | 'abzug_beihilfe_euro' | 'abzug_pkv_euro':
                        value = format_euro(get_value(attribute['name_object'].replace('_euro', ''), 0))
                    case 'beihilfesatz_prozent':
                        value = format_percent(get_value('beihilfesatz', 0))
                    case 'bezahlt_text' | 'erhalten_text':
                        value = 'Ja' if get_value(attribute['name_object'].replace('_text', ''), False) else 'Nein'
                    case 'beihilfe_eingereicht' | 'pkv_eingereicht':
                        value = 'Ja' if get_value(attribute['name_object'].replace('_eingereicht', '_id'), None) else 'Nein'
                    case 'plz_ort':
                        value = (data.get('plz', '') or '') + (' ' if data.get('plz', '') else '') + (data.get('ort', '') or '')
                    case 'rechnungsdatum_kurz':
                        value = get_value('rechnungsdatum', '')[:6] + get_value('rechnungsdatum', '')[8:]      
                    case 'buchungsdatum_kurz':
                        value = get_value('buchungsdatum', '')[:6] + get_value('buchungsdatum', '')[8:]
                    case 'datum_kurz':
                        value = get_value('datum', '')[:6] + get_value('datum', '')[8:]
                    case 'einrichtung_name':
                        try:
                            value = self.institutions.find({'db_id': get_value('einrichtung_id', None)}).name or ''
                        except ValueError:
                            value = ''
                    case 'person_name':
                        try:
                            value = self.persons.find({'db_id': get_value('person_id', None)}).name or ''
                        except ValueError:
                            value = ''
                    case 'info':
                        try:
                            name = self.persons.find({'db_id': get_value('person_id', None)}).name
                        except ValueError:
                            name = ''
                        if name:
                            name += ', '
                        try:
                            einrichtung = self.institutions.find({'db_id': get_value('einrichtung_id', None)}).name
                        except ValueError:
                            einrichtung = ''
                        value = name + einrichtung
                init_data[attribute['name_object']] = value

        return init_data

    def is_first_start(self):
        """Returns if the app is started for the first time."""

        return self.db.is_first_start()

    def initialized(self):
        """Returns if the app is initialized. Default is False."""

        return self.init.get('initialized', False)
    
    def allowance_active(self):
        """Returns if the allowance functionality is active."""

        return self.init.get('beihilfe', True)

    def reset(self):
        """Resets all data and the database."""

        print(f'### DatenInterface.reset: resetting all data')

        # reset database
        self.db.reset()

        # remove listeners
        self.bills.remove_listener(self.submits_listener)

        # reset lists
        self.bills.clear()
        self.allowances.clear()
        self.insurances.clear()
        self.institutions.clear()
        self.persons.clear()
        self.allowances_bills.clear()
        self.insurances_bills.clear()
        self.open_bookings.clear()
        self.archivables.clear()
        self.open_sum.value = 0

        # Daten initialisieren
        self.__init_data()

        # add listeners
        self.bills.add_listener(self.submits_listener)

    def save_init_file(self):
        """Saves the init file."""

        self.db.save_init_file(**self.init)
        print(self.init)

    def load_init_file(self):
        """Loads the init file."""

        self.init = self.db.load_init_file()

    def archive(self):
        """Archives all archivable bookings (set them to inactive)."""

        if not self.archivables:
            print(f'### DatenInterface.archive: No archivables found')
            return

        for index in self.archivables[0].rechnung:
            self.deactivate(BILL_OBJECT, self.bills[index])

        for index in self.archivables[0].beihilfe:
            self.deactivate(ALLOWANCE_OBJECT, self.allowances[index])
            
        for index in self.archivables[0].pkv:
            self.deactivate(INSURANCE_OBJECT, self.insurances[index])

        self.archivables.clear()

    def get_element_by_dbid(self, list_source, db_id):
        """Gets an element of a list source by its database id."""

        try:
            return list_source.find({'db_id': db_id})
        except ValueError:
            print(f'### DatenInterface.get_element_by_dbid: No element found with id {db_id}')
            return None

    def get_allowance_by_name(self, name):
        """Gets the allowance percentage for a person by its name."""

        try:
            person = self.persons.find({'name': name})
            print(f'### DatenInterface.get_allowance_by_name: Found allowance percentage for person {name}')
            return person.beihilfesatz
        except ValueError:
            return None
        
    def get_element_index_by_dbid(self, list_source, db_id):
        """Gets the index of an element of a list source by its database id."""

        try:
            row = list_source.find({'db_id': db_id})
            return list_source.index(row)
        except ValueError:
            print(f'### DatenInterface.get_list_element_by_dbid: No element found with id {db_id}')
            return None

    def new(self, object_type, data, **kwargs):
        """Creates a new element and returns its database id."""

        if object_type in BILL_TYPES:
            # update the bill data and add it to the list source to create the row object
            bill = self.update_object(object_type, **data)
            bill['db_id'] = self.db.new(object_type, bill)            
            index = get_index_new_element(object_type, self.bills, bill)
            self.bills.insert(index, bill)
            
            # update connected values
            if bill['bezahlt'] == False:
                self.open_sum.value -= (bill['abzug_beihilfe'] + bill['abzug_pkv'])
                self.update_open_bookings()
            else:
                self.open_sum.value += (bill['betrag'] - bill['abzug_beihilfe'] - bill['abzug_pkv'])
            
            return bill['db_id']

        elif object_type in ALLOWANCE_TYPES:
            
            # update the allowance data and add it to the list source to create the row object
            allowance = self.update_object(object_type, **data)
            allowance['db_id'] = self.db.new(object_type, allowance)
            index = get_index_new_element(object_type, self.allowances, allowance)
            self.allowances.insert(index, allowance)
            
            for bill_db_id in kwargs.get('bill_db_ids', []):
                bill = dict_from_row(BILL_OBJECT, self.bills.find({'db_id': bill_db_id}))
                print(f'### DatenInterface.new_element: Adding beihilfe to bill with dbid {bill_db_id}')
                bill['beihilfe_id'] = allowance['db_id']
                print(f'### DatenInterface.new_element: Saving bill with beihilfe_id {bill_db_id}')
                self.save(BILL_OBJECT, bill, update=False)

            # update connected values
            if allowance['erhalten'] == False:
                self.update_open_bookings()
            else:
                self.open_sum.value -= allowance['betrag']
                self.update_archivables()

            return allowance['db_id']

        elif object_type in INSURANCE_TYPES:

            # update the insurance data and add it to the list source to create the row object
            insurance = self.update_object(object_type, **data)
            insurance['db_id'] = self.db.new(object_type, insurance)
            index = get_index_new_element(object_type, self.insurances, insurance)
            self.insurances.insert(index, insurance)
            
            for bill_db_id in kwargs.get('bill_db_ids', []):
                bill = dict_from_row(BILL_OBJECT, self.bills.find({'db_id': bill_db_id}))
                bill['pkv_id'] = insurance['db_id']
                self.save(BILL_OBJECT, bill, update=False)

            # update connected values
            if insurance['erhalten'] == False:
                self.update_open_bookings()
            else:
                self.open_sum.value -= insurance['betrag']
                self.update_archivables()

            return insurance['db_id']
        
        elif object_type in INSTITUTION_TYPES:
            institution = self.update_object(object_type, **data)
            institution['db_id'] = self.db.new(object_type, institution)
            index = get_index_new_element(object_type, self.institutions, institution)
            self.institutions.insert(index, institution)
            return institution['db_id']
        
        elif object_type in PERSON_TYPES:
            person = self.update_object(object_type, **data)
            person['db_id'] = self.db.new(object_type, person)
            index = get_index_new_element(object_type, self.persons, person)
            self.persons.insert(index, person)
            return person['db_id']
        
        else:
            raise ValueError(f'### DataInterface.new_element: element type not known')     

    def save(self, object_type, element, update=True, **kwargs):
        """Saves an element and updates the connected values."""

        if isinstance(element, dict):
            old_dict = element
            updated_dict = self.update_object(object_type, **element)
        else:
            old_dict = dict_from_row(object_type, element)
            updated_dict = self.update_object(object_type, **old_dict)

        if object_type in self.lists_accessor:
            current_list = self.lists_accessor[object_type]
            current_index = current_list.index(current_list.find({'db_id': old_dict['db_id']}))
            new_index = get_index_new_element(object_type, current_list, updated_dict)
            if current_index == new_index:
                current_list[current_index] = updated_dict
            else:
                current_list.remove(current_list.find({'db_id': old_dict['db_id']}))
                current_list.insert(new_index, updated_dict)

        self.db.save(object_type, element)

        if update and object_type in BILL_TYPES or object_type in ALLOWANCE_TYPES or object_type in INSURANCE_TYPES:
            self.update_open_bookings()
            self.update_archivables()
            self.update_open_sum()
        elif update and object_type in INSTITUTION_TYPES or object_type in PERSON_TYPES:
            self.update_bills()
            self.update_open_bookings()
        elif update:
            raise ValueError(f'### DataInterface.save_element: element type not known')
            
    def delete(self, object_type, element):
        """Deletes an element and updates the connected values."""

        if object_type in BILL_TYPES:
            if isinstance(element, dict):
                element = self.bills.find({'db_id': element['db_id']})

            index = self.bills.index(element)
            self.db.delete(object_type, element)
            self.bills.remove(element)
            if element.bezahlt == False:
                self.update_open_bookings()
            elif index in self.archivables[0].rechnung:
                self.update_archivables()
            self.update_open_sum()
            return True

        elif object_type in ALLOWANCE_TYPES:
            if isinstance(element, dict):
                element = self.allowances.find({'db_id': element['db_id']})

            index = self.allowances.index(element)
            self.db.delete(object_type, element)
            self.allowances.remove(element)

            for bill in self.bills:
                if bill.beihilfe_id == element.db_id:
                    bill_dict = dict_from_row(BILL_OBJECT, bill)
                    bill_dict['beihilfe_id'] = None
                    print(f'### DatenInterface.delete_element: Deleting beihilfe from bill with dbid {bill.db_id}')
                    self.save(BILL_OBJECT, bill_dict, update=False)

            if element.erhalten == False:
                self.update_open_bookings()
            elif index in self.archivables[0].beihilfe:
                self.update_archivables()
            self.update_open_sum()
            return True

        elif object_type in INSURANCE_TYPES:
            if isinstance(element, dict):
                element = self.insurances.find({'db_id': element['db_id']})

            index = self.insurances.index(element)
            self.db.delete(object_type, element)
            self.insurances.remove(element)

            for bill in self.bills:
                if bill.pkv_id == element.db_id:
                    bill.pkv_id = None
                    self.save(BILL_OBJECT, bill, update=False)
            
            if element.erhalten == False:
                self.update_open_bookings()
            elif index in self.archivables[0].pkv:
                self.update_archivables()
            self.update_open_sum()
            return True
        
        elif object_type in INSTITUTION_TYPES:
            if isinstance(element, dict):
                element = self.institutions.find({'db_id': element['db_id']})

            if not self.__check_institution_used(element):
                self.db.delete(object_type, element)
                self.institutions.remove(element)
                return True
            else:
                return False
        
        elif object_type in PERSON_TYPES:
            if isinstance(element, dict):
                element = self.persons.find({'db_id': element['db_id']})

            if not self.__check_person_used(element):
                self.db.delete(object_type, element)
                self.persons.remove(element)
                return True
            else:
                return False

        else:
            raise ValueError(f'### DataInterface.delete_element: element type not known')
            
    def deactivate(self, object_type, element):
        """Deactivates an element and updates the connected values."""
        
        if object_type in BILL_TYPES:
            if isinstance(element, dict):
                element = self.bills.find({'db_id': element['db_id']})

            index = self.bills.index(element)

            element.aktiv = False
            self.db.save(object_type, element)
            self.bills.remove(element)
            if element.bezahlt == False:
                self.update_open_bookings()
            elif index in self.archivables[0].rechnung:
                self.update_archivables()
            self.update_open_sum()
            return True

        elif object_type in ALLOWANCE_TYPES:
            if isinstance(element, dict):
                element = self.allowances.find({'db_id': element['db_id']})

            index = self.allowances.index(element)

            element.aktiv = False
            self.db.save(object_type, element)
            self.allowances.remove(element)

            if element.erhalten == False:
                self.update_open_bookings()
            elif index in self.archivables[0].beihilfe:
                self.update_archivables()
            self.update_open_sum()
            return True

        elif object_type in INSURANCE_TYPES:
            if isinstance(element, dict):
                element = self.insurances.find({'db_id': element['db_id']})

            index = self.insurances.index(element)

            element.aktiv = False
            self.db.save(object_type, element)
            self.insurances.remove(element)

            if element.erhalten == False:
                self.update_open_bookings()
            elif index in self.archivables[0].pkv:
                self.update_archivables()
            self.update_open_sum()
            return True

        elif object_type in INSTITUTION_TYPES:
            if isinstance(element, dict):
                element = self.institutions.find({'db_id': element['db_id']})

            if not self.__check_institution_used(element):
                element.aktiv = False
                self.db.save(object_type, element)
                self.institutions.remove(element)
                return True
            else:
                return False

        elif object_type in PERSON_TYPES:
            if isinstance(element, dict):
                element = self.persons.find({'db_id': element['db_id']})

            if not self.__check_person_used(element):
                element.aktiv = False
                self.db.save(object_type, element)
                self.persons.remove(element)
                return True
            else:
                return False

        else:
            raise ValueError(f'### DataInterface.deactivate_element: element type not known')
            
    def pay_receive(self, object_type, element, date=None):
        """Marks a bill as paid or an allowance/insurance as received and updates the connected values."""

        if object_type in BILL_TYPES:
            element.bezahlt = True
            if date is not None:
                element.buchungsdatum = date
            elif not element.buchungsdatum:
                element.buchungsdatum = datetime.now().strftime('%d.%m.%Y')
            self.save(object_type, element)

        elif object_type in ALLOWANCE_TYPES or object_type in INSURANCE_TYPES:
            element.erhalten = True
            self.save(object_type, element)

    def __check_person_used(self, person):
        """Returns if a person is used in a bill."""

        try:
            bill = self.bills.find({'person_id': person.db_id})
            print(f'### DatenInterface.__check_person_used: Person with id {person.db_id} is used in bill with id {bill.db_id}')
            return True
        except ValueError:
            return False
        
    def __check_institution_used(self, institution):
        """Returns if an institution is used in a bill."""

        try:
            bill = self.bills.find({'einrichtung_id': institution.db_id})
            print(f'### DatenInterface.__check_institution_used: Institution with id {institution.db_id} is used in bill with id {bill.db_id}')
            return True
        except ValueError:
            return False

    def update_submit_amount(self, object_type, element):
        """Updates the amount of an allowance or insurance and saves it in the database."""

        if not (object_type in ALLOWANCE_TYPES or object_type in INSURANCE_TYPES):
            raise ValueError(f'### DatenInterface.update_submit_amount: Object type {object_type} is not an allowance or insurance')

        amount = 0
        content = False
        for bill in self.bills:
            if object_type in ALLOWANCE_TYPES and bill.beihilfe_id == element.db_id:
                content = True
                amount += (bill.betrag - bill.abzug_beihilfe) * (bill.beihilfesatz / 100)
            
            if object_type in INSURANCE_TYPES and bill.pkv_id == element.db_id:
                content = True
                if self.allowance_active():
                    amount += (bill.betrag - bill.abzug_pkv) * (1 - (bill.beihilfesatz / 100))
                else:
                    amount += bill.betrag - bill.abzug_pkv

        if content:
            element.betrag = amount
            self.save(object_type, element)
        else:
            self.delete(object_type, element)

    def update_bills(self):
        """Updates the bills and checks if the connected values are still valid."""

        for index, bill in enumerate(self.bills):

            dict = dict_from_row(BILL_OBJECT, bill)
            changed = False

            # Aktualisiere die Beihilfe
            if bill.beihilfe_id:
                # If the allowance does not exist, reset the allowance id
                if not any(allowance.db_id == bill.beihilfe_id for allowance in self.allowances):
                    print(f'### DatenInterface.__update_rechnungen: Beihilfepaket with id {bill.beihilfe_id} not found, reset beihilfe in rechnung with id {bill.db_id}')
                    dict['beihilfe_id'] = None
                    changed = True

            # Aktualisiere die PKV
            if bill.pkv_id:
                # If the insurance does not exist, reset the insurance id
                if not any(insurance.db_id == bill.pkv_id for insurance in self.insurances):
                    print(f'### DatenInterface.__update_rechnungen: PKV-Paket with id {bill.pkv_id} not found, reset pkv in rechnung with id {bill.db_id}')
                    dict['pkv_id'] = None
                    changed = True

            # Aktualisiere die Einrichtung
            if bill.einrichtung_id:
                # If the institution does not exist, reset the institution id
                if not any(institution.db_id == bill.einrichtung_id for institution in self.institutions):
                    print(f'### DatenInterface.__update_rechnungen: Institution with id {bill.einrichtung_id} not found, reset einrichtung in rechnung with id {bill.db_id}')
                    dict['einrichtung_id'] = None
                    changed = True

            # Aktualisiere die Person
            if bill.person_id:
                # If the person does not exist, reset the person id
                if not any(person.db_id == bill.person_id for person in self.persons):
                    print(f'### DatenInterface.__update_rechnungen: Person with id {bill.person_id} not found, reset person in rechnung with id {bill.db_id}')
                    dict['person_id'] = None
                    changed = True

            # Aktualisierte Rechnung speichern
            
            self.bills[index] = self.update_object(BILL_OBJECT, **dict)
            if changed:
                self.db.save(BILL_OBJECT, self.bills[index])
        
    def update_open_bookings(self):
        """Updates the list of open bookings."""

        self.open_bookings.clear()
        
        for bill in self.bills:
            if not bill.bezahlt:
                self.open_bookings.append({
                    'db_id': bill.db_id,
                    'typ': 'Rechnung',
                    'betrag_euro': '-{:.2f} €'.format(bill.betrag).replace('.', ',') if bill.betrag else '0,00 €',
                    'datum': bill.rechnungsdatum or '',
                    'buchungsdatum': bill.buchungsdatum or '',
                    'info': bill.info
                })
    
        if self.allowance_active():
            for allowance in self.allowances:
                if not allowance.erhalten:
                    self.open_bookings.append({
                        'db_id': allowance.db_id,
                        'typ': 'Beihilfe',
                        'betrag_euro': '+{:.2f} €'.format(allowance.betrag).replace('.', ',') if allowance.betrag else '0,00 €',
                        'datum': allowance.datum or '',
                        'buchungsdatum': '',
                        'info': 'Beihilfe-Einreichung'
                    })

        for insurance in self.insurances:
            if not insurance.erhalten:
                self.open_bookings.append({
                    'db_id': insurance.db_id,
                    'typ': 'PKV',
                    'betrag_euro': '+{:.2f} €'.format(insurance.betrag).replace('.', ',') if insurance.betrag else '0,00 €',
                    'datum': insurance.datum or '',
                    'buchungsdatum': '',
                    'info': 'PKV-Einreichung'
                })

    def update_allowances_bills(self):
        """Updates the list of not yet submitted bills for the allowance."""

        self.allowances_bills.clear()
        for bill in self.bills:
            if not bill.beihilfe_id:
                dict = dict_from_row(BILL_OBJECT, bill)
                self.allowances_bills.append(dict)

    def update_insurances_bills(self):
        """Updates the list of not yet submitted bills for the insurance."""

        self.insurances_bills.clear()
        for bill in self.bills:
            if not bill.pkv_id:
                dict = dict_from_row(BILL_OBJECT, bill)
                self.insurances_bills.append(dict)
    
    def update_open_sum(self):
        """Updates the sum of all open bookings."""

        sum = 0.00
        
        if self.bills is not None:
            for bill in self.bills:
                if bill.bezahlt == False:
                    sum -= bill.betrag
                if self.allowance_active() and bill.beihilfe_id == None:
                    sum += (bill.betrag - bill.abzug_beihilfe) * (bill.beihilfesatz / 100)
                if bill.pkv_id == None:
                    if self.allowance_active():
                        sum += (bill.betrag - bill.abzug_pkv) * (1 - (bill.beihilfesatz / 100))
                    else:
                        sum += bill.betrag - bill.abzug_pkv
        
        if self.allowance_active() and self.allowances is not None:
            for submit in self.allowances:
                if submit.erhalten == False:
                    sum += submit.betrag

        if self.insurances is not None:
            for submit in self.insurances:
                if submit.erhalten == False:
                    sum += submit.betrag

        self.open_sum.value = sum

    def update_archivables(self):
        """Updates the list of archivable bookings."""

        temp = {
            'rechnung' : [],
            'beihilfe' : set(),
            'pkv' : set()
        }

        def all_bills_paid_and_submitted(bill, checked_bills=None):
            """Recursively check if all bills associated with the given bill's allowance and insurance are paid and submitted."""
            if checked_bills is None:
                checked_bills = set()

            if bill in checked_bills:
                return True

            checked_bills.add(bill)

            associated_bills = [ar for ar in self.bills if (self.allowance_active() and ar.beihilfe_id == bill.beihilfe_id) or ar.pkv_id == bill.pkv_id]
            for associated_bill in associated_bills:
                if not associated_bill.bezahlt:
                    return False

                try:
                    allowance = self.allowances.find({ 'db_id' : associated_bill.beihilfe_id})
                except ValueError:
                    allowance = None
                
                try:
                    insurance = self.insurances.find({ 'db_id' : associated_bill.pkv_id})
                except ValueError:
                    insurance = None

                if ((allowance and allowance.erhalten) or not self.allowance_active()) and insurance and insurance.erhalten:
                    if not all_bills_paid_and_submitted(associated_bill, checked_bills):
                        return False
                else:
                    return False
            return True

        for i, bill in enumerate(self.bills):
            if bill.bezahlt and (bill.beihilfe_id or not self.allowance_active()) and bill.pkv_id:
                try:
                    allowance = self.allowances.find({ 'db_id' : bill.beihilfe_id})
                except ValueError:
                    allowance = None
                
                try:
                    insurance = self.insurances.find({ 'db_id' : bill.pkv_id})
                except ValueError:
                    insurance = None

                if ((allowance and allowance.erhalten) or not self.allowance_active()) and insurance and insurance.erhalten:
                    # Check if all other rechnungen associated with the beihilfepaket and pkvpaket are paid and submitted
                    if all_bills_paid_and_submitted(bill):
                        temp['rechnung'].append(i)
                        if self.allowance_active():
                            temp['beihilfe'].add(self.allowances.index(allowance))
                        temp['pkv'].add(self.insurances.index(insurance))

        # Convert sets back to lists
        temp['beihilfe'] = list(temp['beihilfe'])
        temp['pkv'] = list(temp['pkv'])

        # sort the lists in reverse order
        temp['rechnung'].sort(reverse=True)
        temp['beihilfe'].sort(reverse=True)
        temp['pkv'].sort(reverse=True)

        # convert to listSource
        self.archivables.clear()
        self.archivables.append(temp)

        print(f'### DatenInterface.__update_archivables: Archivables updated: {temp}')
