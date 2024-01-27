"""Enthält die Klassen für die Datenbank und das Daten-Interface."""

import sqlite3 as sql
import shutil
from pathlib import Path
from datetime import datetime
from toga.sources import ListSource, Row
from kontolupe.listeners import *

DATABASE_VERSION = 1

BILLS_ATTRIBUTES = [
    {
        'name_db': 'id',
        'type_db': 'INTEGER PRIMARY KEY AUTOINCREMENT',
        'name_object': 'db_id',
        'default_value': None,
    },
    {
        'name_db': 'betrag',
        'type_db': 'REAL',
        'name_object': 'betrag',
        'default_value': 0.0,
    },
    {
        'name_db': 'abzug_beihilfe',
        'type_db': 'REAL',
        'name_object': 'abzug_beihilfe',
        'default_value': 0.0,
    },
    {
        'name_db': 'abzug_pkv',
        'type_db': 'REAL',
        'name_object': 'abzug_pkv',
        'default_value': 0.0,
    },
    {
        'name_db': 'rechnungsdatum',
        'type_db': 'TEXT',
        'name_object': 'rechnungsdatum',
        'default_value': None,
    },
    {
        'name_db': 'einrichtung_id',
        'type_db': 'INTEGER',
        'name_object': 'einrichtung_id',
        'default_value': None,
    },
    {
        'name_db': 'notiz',
        'type_db': 'TEXT',
        'name_object': 'notiz',
        'default_value': None,
    },
    {
        'name_db': 'person_id',
        'type_db': 'INTEGER',
        'name_object': 'person_id',
        'default_value': None,
    },
    {
        'name_db': 'beihilfesatz',
        'type_db': 'INTEGER',
        'name_object': 'beihilfesatz',
        'default_value': None,
    },
    {
        'name_db': 'buchungsdatum',
        'type_db': 'TEXT',
        'name_object': 'buchungsdatum',
        'default_value': None,
    },
    {
        'name_db': 'aktiv',
        'type_db': 'INTEGER',
        'name_object': 'aktiv',
        'default_value': True,
    },
    {
        'name_db': 'bezahlt',
        'type_db': 'INTEGER',
        'name_object': 'bezahlt',
        'default_value': False,
    },
    {
        'name_db': 'beihilfe_id',
        'type_db': 'INTEGER',
        'name_object': 'beihilfe_id',
        'default_value': None,
    },
    {
        'name_db': 'pkv_id',
        'type_db': 'INTEGER',
        'name_object': 'pkv_id',
        'default_value': None,
    },
]

ALLOWANCE_ATTRIBUTES = [
    {
        'name_db': 'id',
        'type_db': 'INTEGER PRIMARY KEY AUTOINCREMENT',
        'name_object': 'db_id',
        'default_value': None,
    },
    {
        'name_db': 'betrag',
        'type_db': 'REAL',
        'name_object': 'betrag',
        'default_value': 0.0,
    },
    {
        'name_db': 'datum',
        'type_db': 'TEXT',
        'name_object': 'datum',
        'default_value': None,
    },
    {
        'name_db': 'aktiv',
        'type_db': 'INTEGER',
        'name_object': 'aktiv',
        'default_value': True,
    },
    {
        'name_db': 'erhalten',
        'type_db': 'INTEGER',
        'name_object': 'erhalten',
        'default_value': False,
    },
]

INSURANCE_ATTRIBUTES = [
    {
        'name_db': 'id',
        'type_db': 'INTEGER PRIMARY KEY AUTOINCREMENT',
        'name_object': 'db_id',
        'default_value': None,
    },
    {
        'name_db': 'betrag',
        'type_db': 'REAL',
        'name_object': 'betrag',
        'default_value': 0.0,
    },
    {
        'name_db': 'datum',
        'type_db': 'TEXT',
        'name_object': 'datum',
        'default_value': None,
    },
    {
        'name_db': 'aktiv',
        'type_db': 'INTEGER',
        'name_object': 'aktiv',
        'default_value': True,
    },
    {
        'name_db': 'erhalten',
        'type_db': 'INTEGER',
        'name_object': 'erhalten',
        'default_value': False,
    },
]

INSTITUTION_ATTRIBUTES = [
    {
        'name_db': 'id',
        'type_db': 'INTEGER PRIMARY KEY AUTOINCREMENT',
        'name_object': 'db_id',
        'default_value': None,
    },
    {
        'name_db': 'name',
        'type_db': 'TEXT',
        'name_object': 'name',
        'default_value': None,
    },
    {
        'name_db': 'strasse',
        'type_db': 'TEXT',
        'name_object': 'strasse',
        'default_value': None,
    },
    {
        'name_db': 'plz',
        'type_db': 'TEXT',
        'name_object': 'plz',
        'default_value': None,
    },
    {
        'name_db': 'ort',
        'type_db': 'TEXT',
        'name_object': 'ort',
        'default_value': None,
    },
    {
        'name_db': 'telefon',
        'type_db': 'TEXT',
        'name_object': 'telefon',
        'default_value': None,
    },
    {
        'name_db': 'email',
        'type_db': 'TEXT',
        'name_object': 'email',
        'default_value': None,
    },
    {
        'name_db': 'webseite',
        'type_db': 'TEXT',
        'name_object': 'webseite',
        'default_value': None,
    },
    {
        'name_db': 'notiz',
        'type_db': 'TEXT',
        'name_object': 'notiz',
        'default_value': None,
    },
    {
        'name_db': 'aktiv',
        'type_db': 'INTEGER',
        'name_object': 'aktiv',
        'default_value': True,
    },
]

PERSON_ATTRIBUTES = [
    {
        'name_db': 'id',
        'type_db': 'INTEGER PRIMARY KEY AUTOINCREMENT',
        'name_object': 'db_id',
        'default_value': None,
    },
    {
        'name_db': 'name',
        'type_db': 'TEXT',
        'name_object': 'name',
        'default_value': None,
    },
    {
        'name_db': 'beihilfesatz',
        'type_db': 'INTEGER',
        'name_object': 'beihilfesatz',
        'default_value': None,
    },
    {
        'name_db': 'aktiv',
        'type_db': 'INTEGER',
        'name_object': 'aktiv',
        'default_value': True,
    },
]

class Database:
    """Klasse zur Verwaltung der Datenbank."""

    def __init__(self):
        """Initialisierung der Datenbank."""
        # if it is an android device use the android path
        # otherwise use the windows path
        if Path('/data/data/net.biberwerk.kontolupe').exists():
            self.db_dir = Path('/data/data/net.biberwerk.kontolupe')
        elif Path('C:/Users/Ben/code/vereinfacher/kontolupe/src/kontolupe').exists():
            self.db_dir = Path('C:/Users/Ben/code/vereinfacher/kontolupe/src/kontolupe')
        
        self.db_path = self.db_dir / 'kontolupe.db'

        self.init_file = self.db_dir / 'init.txt'

        # Dictionary mit den Tabellen und Spalten der Datenbank erstellen
        self.__tables = {}
        self.__tables['rechnungen'] = []
        for attribute in BILLS_ATTRIBUTES:
            self.__tables['rechnungen'].append((attribute['name_db'], attribute['type_db']))
        
        self.__tables['beihilfepakete'] = []
        for attribute in ALLOWANCE_ATTRIBUTES:
            self.__tables['beihilfepakete'].append((attribute['name_db'], attribute['type_db']))
        
        self.__tables['pkvpakete'] = []
        for attribute in INSURANCE_ATTRIBUTES:
            self.__tables['pkvpakete'].append((attribute['name_db'], attribute['type_db']))
        
        self.__tables['einrichtungen'] = []
        for attribute in INSTITUTION_ATTRIBUTES:
            self.__tables['einrichtungen'].append((attribute['name_db'], attribute['type_db']))
        
        self.__tables['personen'] = []
        for attribute in PERSON_ATTRIBUTES:
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

        # Datenbank-Datei initialisieren und ggf. aktualisieren
        self.__create_db()

        # Aktualisiere die init-Datei
        self.__update_init()

    def get_attributes_list(self, table):
        """Gibt die zur Tabelle gehörende Liste der Attribute zurück."""
        attributes = []
        match table:
            case 'rechnungen':
                attributes = BILLS_ATTRIBUTES
            case 'beihilfepakete':
                attributes = ALLOWANCE_ATTRIBUTES
            case 'pkvpakete':
                attributes = INSURANCE_ATTRIBUTES
            case 'einrichtungen':
                attributes = INSTITUTION_ATTRIBUTES
            case 'personen':
                attributes = PERSON_ATTRIBUTES
            case _:
                raise ValueError(f'### Database.__load_data: Table {table} not found')
        return attributes

    def __update_init(self):
        """Überprüfe, ob die init-Datei aktualisiert werden muss."""
        
        # check if the init file exists
        if not self.init_file.exists():
            # check if database exists and has any data
            if self.db_path.exists():
                # load the data
                rechnungen = self.lade_rechnungen(only_active=False)
                beihilfepakete = self.lade_beihilfepakete(only_active=False)
                pkvpakete = self.lade_pkvpakete(only_active=False)
                einrichtungen = self.lade_einrichtungen(only_active=False)
                personen = self.lade_personen(only_active=False)

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
        """Prüfen, ob die App zum ersten Mal gestartet wird."""
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
        """Speichern der init.txt Datei."""
        # create the init file
        # write the variables to the init file
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
        """Laden der init.txt Datei und Rückgabe als Dictionary."""
        # load the init file
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
        """Setzt alle Daten zurück."""
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

    def __get_column_type(self, table_name, column_name):
        """Lade den Typ der Spalte aus dem self.__tables Dictionary."""
        for column in self.__tables[table_name]:
            if column[0] == column_name:
                print(f'### Database.__get_column_type: Column type for column {column_name} in table {table_name} is {column[1]}')
                return column[1]
        print(f'### Database.__get_column_type: Column {column_name} not found in table {table_name}')
        return None  # return None if the column is not found

    def __create_backup(self):
        """Erstellen eines Backups der Datenbank."""
        # Get the current date and time, formatted as a string
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create the backup path with the timestamp
        backup_path = self.db_dir / Path(f'kontolupe_{timestamp}.db.backup')
        
        if self.db_path.exists():
            if backup_path.exists():
                backup_path.unlink()
            shutil.copy2(self.db_path, backup_path)
            print(f'### Database.__create_backup: Created backup {backup_path}')
        else:
            print(f'### Database.__create_backup: Database {self.db_path} does not exist. No backup created.')

    def __delete_backups(self):
        """Löschen aller Backups der Datenbank."""
        for file in self.db_dir.glob('kontolupe_*.db.backup'):
            print(f'### Database: Deleting backup {file}')
            file.unlink()

    def __create_table_if_not_exists(self, cursor, table_name, columns):
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join([f'{column[0]} {column[1]}' for column in columns])})")

    def __add_column_if_not_exists(self, cursor, table_name, new_column, column_type):
        cursor.execute(f"PRAGMA table_info({table_name})")
        if not any(row[1] == new_column for row in cursor.fetchall()):
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {new_column} {column_type}")
            print(f'### Database.__add_column_if_not_exists: Added column {new_column} to table {table_name}')
            if new_column == 'aktiv':
                cursor.execute(f"UPDATE {table_name} SET aktiv = 1")

    def __copy_column(self, cursor, table_name, old_column, new_column):
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
        """Erstellen und Update der Datenbank."""

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
            Datenbank.__create_table_if_not_exists(self, cursor, table_name, columns)
            for column in columns:
                Datenbank.__add_column_if_not_exists(self, cursor, table_name, column[0], column[1])

            # look for a predecessor table and update its structure if it exists
            old_table = self.__tables_predecessors.get(table_name)
            if old_table is not None:
                # now check if the old table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (old_table,))
                if cursor.fetchone():
                    # the old table exists, so update its structure
                    for column in self.__tables[table_name]:
                        Datenbank.__add_column_if_not_exists(self, cursor, old_table, column[0], column[1])
                    print(f'### Database.__update_db_structure: Updated table {old_table} to the latest structure.')
            

    def __migrate_data(self, cursor):
        """Migrate the data to the new database structure."""

        for table_name, columns in self.__table_columns_rename.items():
            for column in columns:
                Datenbank.__copy_column(self, cursor, table_name, column[0], column[1])

    def __rename_tables(self, cursor):
        """Rename the tables."""

        for old_table, new_table in self.__tables_rename.items():
            Datenbank.__copy_table_and_delete(self, cursor, old_table, new_table)
            print(f'### Database.__rename_tables: Migrated data from {old_table} to {new_table} and deleted {old_table}')


    def __new_element(self, table, element):
        """Einfügen eines neuen Elements in die Datenbank."""
        # Datenbankverbindung herstellen
        connection = sql.connect(self.db_path)
        cursor = connection.cursor()

        # Get the columns for the query
        column_names = [column[0] for column in self.__tables[table]]
        column_names.remove('id')

        attributes = self.get_attributes_list(table)
        attribute_names = []
        for column in column_names:
            attribute_names.append([attribute['name_object'] for attribute in attributes if attribute['name_db'] == column][0])

        # Build the SQL query and values tuple dynamically
        query = f"""INSERT INTO {table} ({', '.join(column_names)}) VALUES ({', '.join(['?' for _ in column_names])})"""
        # get the values to insert
        values = tuple(getattr(element, attribute) for attribute in attribute_names)

        # Daten einfügen
        cursor.execute(query, values)
        db_id = cursor.lastrowid

        # Datenbankverbindung schließen
        connection.commit()
        connection.close()
        print(f'### Database.__new_element: Inserted element with id {db_id} into table {table}')

        return db_id
    
    def __change_element(self, table, element):
        """Ändern eines Elements in der Datenbank."""
        # Datenbankverbindung herstellen
        connection = sql.connect(self.db_path)
        cursor = connection.cursor()

        # Get the columns for the query
        column_names = [column[0] for column in self.__tables[table]]
        column_names.remove('id')

        attributes = self.get_attributes_list(table)
        attribute_names = []
        for column in column_names:
            attribute_names.append([attribute['name_object'] for attribute in attributes if attribute['name_db'] == column][0])

        # Build the SQL query and values tuple dynamically
        query = f"""UPDATE {table} SET {', '.join([f'{column_name} = ?' for column_name in column_names])} WHERE id = ?"""
        values = tuple(getattr(element, attribute) for attribute in attribute_names)
        values += (element.db_id,)

        # Daten ändern
        cursor.execute(query, values)

        # Datenbankverbindung schließen
        connection.commit()
        connection.close()
        print(f'### Database.__change_element: Changed element with id {element.db_id} in table {table}')

    def __delete_element(self, table, element):
        """Löschen eines Elements aus der Datenbank."""
        # Datenbankverbindung herstellen
        connection = sql.connect(self.db_path)
        cursor = connection.cursor()

        # Daten löschen
        cursor.execute(f"""DELETE FROM {table} WHERE id = ?""", (element.db_id,))

        # Datenbankverbindung schließen
        connection.commit()
        connection.close()
        print(f'### Database.__delete_element: Deleted element with id {element.db_id} from table {table}')

    def __load_data(self, table, only_active=False):
        """Laden der Elemente einer Tabelle aus der Datenbank."""
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

        result = ListSource()
        for row in ergebnis:
            
            attributes = self.get_attributes_list(table)

            # Create the data dictionary for the list source
            data = {}
            for attribute in attributes:
                data[attribute['name_object']] = row.get(attribute['name_db'], attribute['default_value'])       

            match table:
                case 'rechnungen':
                    element = Bill(**data)
                case 'beihilfepakete':
                    element = Allowance(**data)
                case 'pkvpakete':
                    element = Insurance(**data)
                case 'einrichtungen':
                    element = Institution(**data)
                case 'personen':
                    element = Person(**data)

            result.append(element)

        return result

    def new(self, element):
        """Einfügen eines neuen Elements in die Datenbank."""
        match isinstance(element):
            case Bill():
                return self.__new_element('rechnungen', element)
            case Allowance():
                return self.__new_element('beihilfepakete', element)
            case Insurance():
                return self.__new_element('pkvpakete', element)
            case Institution():
                return self.__new_element('einrichtungen', element)
            case Person():
                return self.__new_element('personen', element)
            case _:
                raise ValueError(f'### Database.new: Element {element} not found')
            
    def save(self, element):
        """Ändern eines Elements in der Datenbank."""
        match isinstance(element):
            case Bill():
                self.__change_element('rechnungen', element)
            case Allowance():
                self.__change_element('beihilfepakete', element)
            case Insurance():
                self.__change_element('pkvpakete', element)
            case Institution():
                self.__change_element('einrichtungen', element)
            case Person():
                self.__change_element('personen', element)
            case _:
                raise ValueError(f'### Database.change: Element {element} not found')
            
    def delete(self, element):
        """Löschen eines Elements aus der Datenbank."""
        match isinstance(element):
            case Bill():
                self.__delete_element('rechnungen', element)
            case Allowance():
                self.__delete_element('beihilfepakete', element)
            case Insurance():
                self.__delete_element('pkvpakete', element)
            case Institution():
                self.__delete_element('einrichtungen', element)
            case Person():
                self.__delete_element('personen', element)
            case _:
                raise ValueError(f'### Database.delete: Element {element} not found')

    def load_bills(self, only_active=True):
        """Laden der Rechnungen aus der Datenbank."""
        print(f'### Database: Loading Rechnungen from database')
        return self.__load_data('rechnungen', only_active)
    
    def load_allowances(self, only_active=True):
        """Laden der Beihilfepakete aus der Datenbank."""
        print(f'### Database: Loading Beihilfepakete from database')
        return self.__load_data('beihilfepakete', only_active)
    
    def load_insurances(self, only_active=True):
        """Laden der PKV-Pakete aus der Datenbank."""
        print(f'### Database: Loading PKVPakete from database')
        return self.__load_data('pkvpakete', only_active)
    
    def load_institutions(self, only_active=True):
        """Laden der Einrichtungen aus der Datenbank."""
        print(f'### Database: Loading Einrichtungen from database')
        return self.__load_data('einrichtungen', only_active)
    
    def load_persons(self, only_active=True):
        """Laden der Personen aus der Datenbank."""
        print(f'### Database: Loading Personen from database')
        return self.__load_data('personen', only_active)


class Bill(Row):
    """Klassen zur Darstellung einer Rechnung."""
    
    def __init__(self, **data):
        """Initialisierung der Rechnung."""
        init_data = {}
        for attribute in BILLS_ATTRIBUTES:
            if attribute['name_object']:
                init_data[attribute['name_object']] = data.get(attribute['name_object'], attribute['default_value'])

        super().__init__(**init_data)
    

class Allowance(Row):
    """Klasse zur Darstellung einer Beihilfe-Einreichung."""
    
    def __init__(self, **data):
        """Initialisierung der Beihilfe-Einreichung."""
        init_data = {}
        for attribute in ALLOWANCE_ATTRIBUTES:
            if attribute['name_object']:
                init_data[attribute['name_object']] = data.get(attribute['name_object'], attribute['default_value'])

        super().__init__(**init_data)

    def neu(self, db, rechnungen=None):
        """Neue Beihilfe-Einreichung erstellen."""
        # Betrag der Beihilfe-Einreichung berechnen

        if rechnungen is not None:
            self.betrag = 0
            for rechnung in rechnungen:
                self.betrag += (rechnung.betrag - rechnung.abzug_beihilfe) * rechnung.beihilfesatz / 100

        # Beihilfepaket speichern
        self.db_id = db.neues_beihilfepaket(self)

        if rechnungen is not None:
            # Beihilfe-Einreichung mit Rechnungen verknüpfen
            for rechnung in rechnungen:
                rechnung.beihilfe_id = self.db_id
                rechnung.speichern(db)
        

class Insurance(Row):
    """Klasse zur Darstellung einer PKV-Einreichung."""
    
    def __init__(self, **data):
        """Initialisierung der PKV-Einreichung."""
        init_data = {}
        for attribute in INSURANCE_ATTRIBUTES:
            if attribute['name_object']:
                init_data[attribute['name_object']] = data.get(attribute['name_object'], attribute['default_value'])
        
        super().__init__(**init_data)

    def neu(self, db, rechnungen=None):
        """Neue PKV-Einreichung erstellen."""

        # Betrag der PKV-Einreichung berechnen
        if rechnungen is not None:
            self.betrag = 0
            for rechnung in rechnungen:
                self.betrag += (rechnung.betrag - rechnung.abzug_pkv) * (100 - rechnung.beihilfesatz) / 100

        # PKV-Einreichung speichern
        self.db_id = db.neues_pkvpaket(self)

        if rechnungen is not None:
            # PKV-Einreichung mit Rechnungen verknüpfen
            for rechnung in rechnungen:
                rechnung.pkv_id = self.db_id
                rechnung.speichern(db)


class Institution(Row):
    """Klasse zur Verwaltung der Einrichtungen."""
    
    def __init__(self, **data):
        """Initialisierung der Einrichtung."""

        # create the dictionary init_data using the BILLS_ATTRIBUTES
        init_data = {}
        for attribute in INSTITUTION_ATTRIBUTES:
            if attribute['name_object']:
                init_data[attribute['name_object']] = data.get(attribute['name_object'], attribute['default_value'])
        
        super().__init__(**init_data)
    

class Person(Row):
    """Klasse zur Verwaltung der Personen."""
    
    def __init__(self, **data):
        """Initialisierung der Person."""
        init_data = {}
        for attribute in PERSON_ATTRIBUTES:
            if attribute['name_object']:
                init_data[attribute['name_object']] = data.get(attribute['name_object'], attribute['default_value'])
        super().__init__(**init_data)
    

class DataInterface:
    """Daten-Interface für die GUI."""

    def __init__(self):
        """Initialisierung des Daten-Interfaces."""
        
        # Datenbank initialisieren
        self.db = Database()

        # Init-Dictionary laden
        self.init = self.db.load_init_file()

        # ListSources für die GUI erstellen
        # Diese enthalten alle Felder der Datenbank und zusätzliche Felder für die GUI
        accessors_bills = [
                'db_id', 
                'betrag', 
                'abzug_beihilfe',
                'abzug_pkv',
                'betrag_euro',
                'abzug_beihilfe_euro',
                'abzug_pkv_euro',
                'rechnungsdatum', 
                'einrichtung_id', 
                'notiz', 
                'einrichtung_name', 
                'info', 
                'person_id',
                'person_name',
                'beihilfesatz', 
                'beihilfesatz_prozent',
                'buchungsdatum', 
                'bezahlt', 
                'bezahlt_text',
                'beihilfe_id', 
                'beihilfe_eingereicht',
                'pkv_id'
                'pkv_eingereicht'
            ]
        
        accessors_allowances = [
                'db_id',
                'betrag',
                'betrag_euro',
                'datum',
                'erhalten',
                'erhalten_text'
            ]
        
        accessors_institutions = [
                'db_id',
                'name',
                'strasse',
                'plz',
                'ort',
                'plz_ort',
                'telefon',
                'email',
                'webseite',
                'notiz'
            ]
        
        accessors_persons = [
                'db_id',
                'name',
                'beihilfesatz',
                'beihilfesatz_prozent',
            ]
        
        accessors_insurances = [
                'db_id',
                'betrag',
                'betrag_euro',
                'datum',
                'erhalten',
                'erhalten_text'
            ]
        
        accessors_open_bookings = [
                'db_id',                        # Datenbank-Id des jeweiligen Elements
                'typ',                          # Typ des Elements (Rechnung, Beihilfe, PKV)
                'betrag_euro',                  # Betrag der Buchung in Euro
                'datum',                        # Rechnungsdatum oder Einreichungsdatum der Beihilfe/PKV
                'buchungsdatum',                # Buchungsdatum der Rechnung
                'info'                          # Info-Text der Buchung
            ]
        
        accessors_archivables = [
                'Rechnung',
                'Beihilfe',
                'PKV'
            ]

        self.bills = ListSource(accessors = accessors_bills)
        self.institutions = ListSource(accessors = accessors_institutions)
        self.persons = ListSource(accessors = accessors_persons)
        self.allowances = ListSource(accessors = accessors_allowances)
        self.insurances = ListSource(accessors = accessors_insurances)
        
        self.allowances_bills = ListSource(accessors = accessors_bills)
        self.insurances_bills = ListSource(accessors = accessors_bills)
        self.open_bookings = ListSource(accessors = accessors_open_bookings)
        self.archivables = ListSource(accessors = accessors_archivables)

        # Aktive Einträge aus der Datenbank laden
        self.bills = self.db.load_bills()
        self.allowances = self.db.load_allowances()
        self.insurances = self.db.load_insurances()
        self.institutions = self.db.load_institutions()
        self.persons = self.db.load_persons()

        # Make initializations and correct the data
        for bill in self.bills:            
            if bill.betrag == None:
                bill.betrag = 0
            if bill.abzug_beihilfe == None:
                bill.abzug_beihilfe = 0
            if bill.abzug_pkv == None:
                bill.abzug_pkv = 0
            if bill.beihilfe_id != None:
                if self.get_allowance_by_dbid(bill.beihilfe_id) == None:
                    bill.beihilfe_id = None
            if bill.pkv_id != None:
                if self.get_insurance_by_dbid(bill.pkv_id) == None:
                    bill.pkv_id = None
            self.extend(bill)

        for institution in self.institutions:            
            self.extend(institution)

        for person in self.persons:            
            if person.beihilfesatz == None:
                person.beihilfesatz = 0
            self.extend(person)

        for allowance in self.allowances:      
            if allowance.betrag == None:
                allowance.betrag = 0      
            self.extend(allowance)

        for insurance in self.insurances: 
            if insurance.betrag == None:
                insurance.betrag = 0           
            self.extend(insurance)

        # Sekundäre Listen initialisieren
        self.update_allowances_bills()
        self.update_insurances_bills()
        self.update_open_bookings()
        self.update_archivables()

        # Listeners
        self.bills.add_listener(ListListener(self, self.allowances_bills))
        self.bills.add_listener(ListListener(self, self.insurances_bills))
        self.bills.add_listener(ListListener(self, self.open_bookings))
        self.bills.add_listener(ListListener(self, self.archivables))
        self.allowances.add_listener(ListListener(self, self.open_bookings))
        self.allowances.add_listener(ListListener(self, self.archivables))
        self.insurances.add_listener(ListListener(self, self.open_bookings))
        self.insurances.add_listener(ListListener(self, self.archivables))

    def initialized(self):
        """Prüft, ob die Anwendung initialisiert wurde. Default ist False."""
        return self.init.get('initialized', False)
    
    def allowance_active(self):
        """Prüft, ob Beihilfe aktiviert ist. Default ist True."""
        return self.init.get('beihilfe', True)

    def reset(self):
        """Zurücksetzen des Daten-Interfaces."""
        print(f'### DatenInterface.reset: resetting all data')

        # delete list sources
        del self.bills
        del self.allowances_bills
        del self.insurances_bills
        del self.institutions
        del self.persons
        del self.allowances
        del self.insurances
        del self.open_bookings
        del self.archivables

        # reset database
        self.db.reset()

        # initialize object again
        self.__init__()

    def is_first_start(self):
        """Prüft, ob das Programm zum ersten Mal gestartet wird."""
        return self.db.is_first_start()

    def save_init_file(self):
        """Speichert die Initialisierungsdatei."""
        self.db.save_init_file(**self.init)

    def load_init_file(self):
        """Lädt die Initialisierungsdatei und speichert sie in der Klassenvariable."""
        self.init = self.db.load_init_file()

    def __update_archivables(self):
        """Ermittelt die archivierbaren Elemente des Daten-Interfaces."""

        self.archivables = {
            'Rechnung' : [],
            'Beihilfe' : set(),
            'PKV' : set()
        }

        # Create dictionaries for quick lookup of beihilfepakete and pkvpakete by db_id
        beihilfepakete_dict = {paket.db_id: paket for paket in self.beihilfepakete}
        pkvpakete_dict = {paket.db_id: paket for paket in self.pkvpakete}

        for i, rechnung in enumerate(self.rechnungen):
            if rechnung.bezahlt and (rechnung.beihilfe_id or not self.beihilfe_aktiv()) and rechnung.pkv_id:
                beihilfepaket = beihilfepakete_dict.get(rechnung.beihilfe_id)
                pkvpaket = pkvpakete_dict.get(rechnung.pkv_id)
                if ((beihilfepaket and beihilfepaket.erhalten) or not self.beihilfe_aktiv()) and pkvpaket and pkvpaket.erhalten:
                    # Check if all other rechnungen associated with the beihilfepaket and pkvpaket are paid
                    other_rechnungen = [ar for ar in self.rechnungen if (self.beihilfe_aktiv() and ar.beihilfe_id == beihilfepaket.db_id) or ar.pkv_id == pkvpaket.db_id]
                    if all(ar.bezahlt for ar in other_rechnungen):
                        self.archivables['Rechnung'].append(i)
                        if self.beihilfe_aktiv():
                            self.archivables['Beihilfe'].add(self.beihilfepakete.index(beihilfepaket))
                        self.archivables['PKV'].add(self.pkvpakete.index(pkvpaket))

        # Convert sets back to lists
        self.archivables['Beihilfe'] = list(self.archivables['Beihilfe'])
        self.archivables['PKV'] = list(self.archivables['PKV'])

        # sort the lists in reverse order
        self.archivables['Rechnung'].sort(reverse=True)
        self.archivables['Beihilfe'].sort(reverse=True)
        self.archivables['PKV'].sort(reverse=True)

        # self.list_archivables should now get the same content as self.archivables
        self.list_archivables.clear()
        self.list_archivables.append(self.archivables)

        print(f'### DatenInterface.__update_archivables: Archivables updated: {self.archivables}')


    def archive(self):
        """Archiviert alle archivierbaren Buchungen."""

        for i in self.archivables['Rechnung']:
            self.__deactivate_bill(i)

        for i in self.archivables['Beihilfe']:
            self.__deactivate_allowance(i)
            
        for i in self.archivables['PKV']:
            self.__deactivate_insurance(i)

        self.__update_archivables()
        

    def get_bill_by_dbid(self, db_id):
        """Gibt eine Rechnung anhand der ID zurück."""
        for bill in self.bills:
            if bill.db_id == db_id:
                return bill
        print(f'### DatenInterface.get_bill_by_dbid: No bill found with id {db_id}')
        return None
    

    def get_beihilfepaket_by_dbid(self, db_id):
        """Gibt ein Beihilfepaket anhand der ID zurück."""
        for allowance in self.allowances:
            if allowance.db_id == db_id:
                return allowance
        print(f'### DatenInterface.get_allowance_by_dbid: No allowance found with id {db_id}')
        return None
    

    def get_pkvpaket_by_dbid(self, db_id):
        """Gibt ein PKV-Paket anhand der ID zurück."""
        for insurance in self.insurances:
            if insurance.db_id == db_id:
                return insurance
        print(f'### DatenInterface.get_insurance_by_dbid: No insurance found with id {db_id}')
        return None
    

    def get_institution_by_dbid(self, db_id):
        """Gibt eine Einrichtung anhand der ID zurück."""
        for institution in self.institutions:
            if institution.db_id == db_id:
                return institution
        print(f'### DatenInterface.get_institution_by_dbid: No institution found with id {db_id}')
        return None
    

    def get_person_by_dbid(self, db_id):
        """Gibt eine Person anhand der ID zurück."""
        for person in self.persons:
            if person.db_id == db_id:
                return person
        print(f'### DatenInterface.get_person_by_dbid: No person found with id {db_id}')
        return None
    

    def get_allowance_by_name(self, name):
        """Gibt den Beihilfesatz einer Person anhand des Namens zurück."""
        for person in self.persons:
            if person.name == name:
                print(f'### DatenInterface.get_allowance_by_name: Found allowance percentage for person {name}')
                return person.beihilfesatz
        return None
    

    def get_bill_index_by_dbid(self, db_id):
        """Gibt den Index einer Rechnung anhand der ID zurück."""
        index = self.__get_list_index_by_dbid(self.bills, db_id)
        if index is None:
            print(f'### DatenInterface.get_bill_index_by_dbid: No rechnung found with db_id {db_id}')
        return index
    

    def get_institutions_index_by_dbid(self, db_id):
        """Gibt den Index einer Einrichtung anhand der ID zurück."""
        index = self.__get_list_index_by_dbid(self.institutions, db_id)
        if index is None:
            print(f'### DatenInterface.get_institutions_index_by_dbid: No einrichtung found with id {db_id}')
        return index
    

    def get_person_index_by_dbid(self, db_id):
        """Gibt den Index einer Person anhand der ID zurück."""
        index = self.__get_list_index_by_dbid(self.persons, db_id)
        if index is None:
            print(f'### DatenInterface.get_person_index_by_dbid: No person found with id {db_id}')
        return index
    

    def new_rechnung(self, rechnung):
        """Neue Rechnung erstellen."""
        rechnung.neu(self.db)
        self.rechnungen.append(rechnung)
        self.__list_rechnungen_append(rechnung)
        self.__update_list_open_bookings()
        self.__update_list_rg_beihilfe()
        self.__update_list_rg_pkv()
        self.__update_archivables()


    def edit_rechnung(self, rechnung, rg_id):
        """Rechnung ändern."""
        self.rechnungen[rg_id] = rechnung
        self.rechnungen[rg_id].speichern(self.db)
        self.__update_list_rechnungen_id(rechnung, rg_id)
        self.__update_list_open_bookings()
        self.__update_list_rg_beihilfe()
        self.__update_list_rg_pkv()
        self.__update_archivables()


    def delete_rechnung(self, rg_id):
        """Rechnung löschen."""
        self.rechnungen[rg_id].loeschen(self.db)
        self.rechnungen.pop(rg_id)
        del self.list_rechnungen[rg_id]
        self.__update_list_open_bookings()
        self.__update_list_rg_beihilfe()
        self.__update_list_rg_pkv()
        self.__update_archivables()


    def __deactivate_bill(self, rg_id):
        """Rechnung deaktivieren."""
        self.rechnungen[rg_id].aktiv = False
        self.rechnungen[rg_id].speichern(self.db)
        self.rechnungen.pop(rg_id)
        del self.list_rechnungen[rg_id]


    def pay_rechnung(self, db_id, date=None):
        """Rechnung bezahlen."""
        index = self.__get_list_index_by_dbid(self.list_rechnungen, db_id)
        self.rechnungen[index].bezahlt = True
        if date is not None:
            self.rechnungen[index].buchungsdatum = date
        elif not self.rechnungen[index].buchungsdatum:
            self.rechnungen[index].buchungsdatum = datetime.now().strftime('%d.%m.%Y')
            
        self.rechnungen[index].speichern(self.db)
        self.__update_list_rechnungen_id(self.rechnungen[index], index)
        self.__update_list_open_bookings()
        self.__update_archivables()


    def receive_beihilfe(self, db_id):
        """Beihilfe erhalten."""
        index = self.__get_list_index_by_dbid(self.list_beihilfepakete, db_id)
        self.beihilfepakete[index].erhalten = True
        self.beihilfepakete[index].speichern(self.db)
        self.__update_list_beihilfepakete_id(self.beihilfepakete[index], index)
        self.__update_list_open_bookings()
        self.__update_archivables()


    def receive_pkv(self, db_id):
        """PKV erhalten."""
        index = self.__get_list_index_by_dbid(self.list_pkvpakete, db_id)
        self.pkvpakete[index].erhalten = True
        self.pkvpakete[index].speichern(self.db)
        self.__update_list_pkvpakete_id(self.pkvpakete[index], index)
        self.__update_list_open_bookings()
        self.__update_archivables()


    def new_beihilfepaket(self, beihilfepaket, rechnungen_db_ids):
        """Neues Beihilfepaket erstellen."""
        beihilfepaket.neu(self.db)
        self.beihilfepakete.append(beihilfepaket)
        self.__list_beihilfepakete_append(beihilfepaket)

        # Beihilfepaket mit Rechnungen verknüpfen
        for rechnung_db_id in rechnungen_db_ids:
            index = self.__get_list_index_by_dbid(self.list_rechnungen, rechnung_db_id)
            self.rechnungen[index].beihilfe_id = beihilfepaket.db_id
            self.rechnungen[index].speichern(self.db)
            self.__update_list_rechnungen_id(self.rechnungen[index], index)

        self.__update_list_open_bookings()
        self.__update_list_rg_beihilfe()
        self.__update_list_rg_pkv()
        self.__update_archivables()


    def delete_beihilfepaket(self, beihilfepaket_id):
        """Beihilfepaket löschen."""
        self.beihilfepakete[beihilfepaket_id].loeschen(self.db)
        self.beihilfepakete.pop(beihilfepaket_id)
        del self.list_beihilfepakete[beihilfepaket_id]
        self.__update_rechnungen()
        self.__update_list_open_bookings()
        self.__update_list_rg_beihilfe()
        self.__update_list_rg_pkv()
        self.__update_archivables()


    def __deactivate_allowance(self, beihilfepaket_id):
        """Beihilfepaket deaktivieren."""
        self.beihilfepakete[beihilfepaket_id].aktiv = False
        self.beihilfepakete[beihilfepaket_id].speichern(self.db)
        self.beihilfepakete.pop(beihilfepaket_id)
        del self.list_beihilfepakete[beihilfepaket_id]


    def new_pkvpaket(self, pkvpaket, rechnungen_db_ids):
        """Neues PKV-Paket erstellen."""
        pkvpaket.neu(self.db)
        self.pkvpakete.append(pkvpaket)
        self.__list_pkvpakete_append(pkvpaket)

        # PKV-Paket mit Rechnungen verknüpfen
        for rechnung_db_id in rechnungen_db_ids:
            index = self.__get_list_index_by_dbid(self.list_rechnungen, rechnung_db_id)
            self.rechnungen[index].pkv_id = pkvpaket.db_id
            self.rechnungen[index].speichern(self.db)
            self.__update_list_rechnungen_id(self.rechnungen[index], index)

        self.__update_list_open_bookings()
        self.__update_list_rg_beihilfe()
        self.__update_list_rg_pkv()
        self.__update_archivables()


    def delete_pkvpaket(self, pkvpaket_id):
        """PKV-Paket löschen."""
        self.pkvpakete[pkvpaket_id].loeschen(self.db)
        self.pkvpakete.pop(pkvpaket_id)
        del self.list_pkvpakete[pkvpaket_id]
        self.__update_rechnungen()
        self.__update_list_open_bookings()
        self.__update_list_rg_beihilfe()
        self.__update_list_rg_pkv()
        self.__update_archivables()


    def __deactivate_insurance(self, pkvpaket_id):
        """PKV-Paket deaktivieren."""
        self.pkvpakete[pkvpaket_id].aktiv = False
        self.pkvpakete[pkvpaket_id].speichern(self.db)
        self.pkvpakete.pop(pkvpaket_id)
        del self.list_pkvpakete[pkvpaket_id]


    def new_einrichtung(self, einrichtung):
        """Neue Einrichtung erstellen."""
        einrichtung.neu(self.db)
        self.einrichtungen.append(einrichtung)
        self.__list_einrichtungen_append(einrichtung)


    def edit_einrichtung(self, einrichtung, einrichtung_id):
        """Einrichtung ändern."""
        self.einrichtungen[einrichtung_id] = einrichtung
        self.einrichtungen[einrichtung_id].speichern(self.db)
        self.__update_list_einrichtungen_id(einrichtung, einrichtung_id)
        self.__update_rechnungen()
        self.__update_list_open_bookings()


    def delete_einrichtung(self, einrichtung_id):
        """Einrichtung löschen."""
        if self.__check_institution_used(self.einrichtungen[einrichtung_id].db_id):
            return False
        self.einrichtungen[einrichtung_id].loeschen(self.db)
        self.einrichtungen.pop(einrichtung_id)
        del self.list_einrichtungen[einrichtung_id]
        return True


    def deactivate_einrichtung(self, einrichtung_id):
        """Einrichtung deaktivieren."""
        if self.__check_institution_used(self.einrichtungen[einrichtung_id].db_id):
            return False
        self.einrichtungen[einrichtung_id].aktiv = False
        self.einrichtungen[einrichtung_id].speichern(self.db)
        self.einrichtungen.pop(einrichtung_id)
        del self.list_einrichtungen[einrichtung_id]
        return True


    def __check_institution_used(self, db_id):
        """Prüft, ob eine Einrichtung verwendet wird."""
        for bill in self.bills:
            if bill.einrichtung_id == db_id:
                print(f'### DatenInterface.__check_institution_used: Institution with id {db_id} is used in bill with id {bill.db_id}')
                return True
        return False


    def new_person(self, person):
        """Neue Person erstellen."""
        person.neu(self.db)
        self.personen.append(person)
        self.__list_personen_append(person)


    def edit_person(self, person, person_id):
        """Person ändern."""
        self.personen[person_id] = person
        self.personen[person_id].speichern(self.db)
        self.__update_list_personen_id(person, person_id)
        self.__update_rechnungen()
        self.__update_list_open_bookings()


    def delete_person(self, person_id):
        """Person löschen."""
        if self.__check_person_used(self.personen[person_id].db_id):
            return False
        self.personen[person_id].loeschen(self.db)
        self.personen.pop(person_id)
        del self.list_personen[person_id]
        return True


    def deactivate_person(self, person_id):
        """Person deaktivieren."""
        if self.__check_person_used(self.personen[person_id].db_id):
            return False
        self.personen[person_id].aktiv = False
        self.personen[person_id].speichern(self.db)
        self.personen.pop(person_id)
        del self.list_personen[person_id]
        return True


    def __check_person_used(self, db_id):
        """Prüft, ob eine Person verwendet wird."""
        for bill in self.bills:
            if bill.person_id == db_id:
                print(f'### DatenInterface.__check_person_used: Person with id {db_id} is used in rechnung with id {bill.db_id}')
                return True
        return False


    def update_allowance_amount(self, db_id):
        """Aktualisiert eine Beihilfe-Einreichung"""
        print(f'### DatenInterface.update_allowance_amount: Update beihilfepaket with id {db_id}')
        # Finde die Beihilfe-Einreichung
        for allowance in self.allowances:
            if allowance.db_id == db_id:
                # Alle Rechnungen durchlaufen und den Betrag aktualisieren
                allowance.betrag = 0
                inhalt = False
                for bill in self.bills:
                    if bill.beihilfe_id == db_id:
                        inhalt = True
                        bill.betrag += (bill.betrag - bill.abzug_beihilfe) * (bill.beihilfesatz / 100)
                # Die Beihilfe-Einreichung speichern
                if inhalt:
                    print(f'### DatenInterface.update_allowance_amount: Allowance with id {db_id} has content and is saved')
                    self.db.save(allowance)
                else:
                    print(f'### DatenInterface.update_allowance_amount: Allowance with id {db_id} has no content and is deleted')
                    self.delete_allowance(self.allowances.index(allowance))
                break
            

    def update_insurance_amount(self, db_id):
        """Aktualisiert eine PKV-Einreichung einer Rechnung."""
        for insurance in self.insurances:
            if insurance.db_id == db_id:
                insurance.betrag = 0
                inhalt = False
                for bill in self.bills:
                    if bill.pkv_id == db_id:
                        inhalt = True
                        if self.allowance_active():
                            insurance.betrag += (bill.betrag - bill.abzug_pkv) * (1 - (bill.beihilfesatz / 100))
                        else:
                            insurance.betrag += bill.betrag - bill.abzug_pkv
                if inhalt:
                    print(f'### DatenInterface.update_insurance_amount: PKV-Paket with id {db_id} has content and is saved')
                    self.db.save(insurance)
                else:
                    print(f'### DatenInterface.update_insurance_amount: PKV-Paket with id {db_id} has no content and is deleted')
                    self.delete_insurance(self.insurances.index(insurance))
                break
    

    def __get_list_index_by_dbid(self, list_source, db_id):
        """Ermittelt den Index eines Elements einer Liste anhand der ID."""
        for i, element in enumerate(list_source):
            if element.db_id == db_id:
                return i
        else:
            print(f'### DatenInterface.__get_list_index_by_dbid: No element found with id {db_id}')
            return None


    def __person_name(self, person_id):
        """Gibt den Namen einer Person zurück."""
        for person in self.personen:
            if person.db_id == person_id:
                return person.name
        print(f'### DatenInterface.__person_name: No person found with id {person_id}')
        return ''
    

    def __institution_name(self, einrichtung_id):
        """Gibt den Namen einer Einrichtung zurück."""
        for einrichtung in self.einrichtungen:
            if einrichtung.db_id == einrichtung_id:
                return einrichtung.name
        print(f'### DatenInterface.__einrichtung_name: No einrichtung found with id {einrichtung_id}')
        return ''
    

    def extend(self, element):
        """Erweitert ein Element um die referenzierten Werte."""
        match isinstance(element):
            case Bill():
                element.betrag_euro = '{:.2f} €'.format(element.betrag).replace('.', ',') if element.betrag else '0,00 €'
                element.abzug_beihilfe_euro = '{:.2f} €'.format(element.abzug_beihilfe).replace('.', ',') if element.abzug_beihilfe else '0,00 €'
                element.abzug_pkv_euro = '{:.2f} €'.format(element.abzug_pkv).replace('.', ',') if element.abzug_pkv else '0,00 €'
                element.person_name = self.__person_name(element.person_id)
                element.institution_name = self.__institution_name(element.institution_id)
                element.info = (element.person_name + ', ' if element.person_name else '') + element.institution_name
                element.beihilfesatz_prozent = '{:.0f} %'.format(element.beihilfesatz) if element.beihilfesatz else '0 %'
                element.bezahlt_text = 'Ja' if element.bezahlt else 'Nein'
                element.beihilfe_eingereicht = 'Ja' if element.beihilfe_id else 'Nein'
                element.pkv_eingereicht = 'Ja' if element.pkv_id else 'Nein'
            case Allowance(): 
                element.betrag_euro = '{:.2f} €'.format(element.betrag).replace('.', ',') if element.betrag else '0,00 €'
                element.erhalten_text = 'Ja' if element.erhalten else 'Nein'
            case Insurance():
                element.betrag_euro = '{:.2f} €'.format(element.betrag).replace('.', ',') if element.betrag else '0,00 €'
                element.erhalten_text = 'Ja' if element.erhalten else 'Nein'
            case Institution():
                element.plz_ort = (element.plz or '') + (' ' if element.plz else '') + (element.ort or '')
            case Person():
                element.beihilfesatz_prozent = '{:.0f} %'.format(element.beihilfesatz) if element.beihilfesatz else '0 %'

    def update_bills(self):
        """Aktualisiert die referenzierten Werte in den Rechnungen und speichert sie in der Datenbank."""

        for bill in self.bills:

            # Aktualisiere die Beihilfe
            if bill.beihilfe_id:
                # If the allowance does not exist, reset the allowance
                if not any(allowance.db_id == bill.beihilfe_id for allowance in self.allowances):
                    print(f'### DatenInterface.__update_rechnungen: Beihilfepaket with id {bill.beihilfe_id} not found, reset beihilfe in rechnung with id {bill.db_id}')
                    bill.beihilfe_id = None

            # Aktualisiere die PKV
            if bill.pkv_id:
                # If the insurance does not exist, reset the insurance
                if not any(insurance.db_id == bill.pkv_id for insurance in self.insurances):
                    print(f'### DatenInterface.__update_rechnungen: PKV-Paket with id {bill.pkv_id} not found, reset pkv in rechnung with id {bill.db_id}')
                    bill.pkv_id = None

            # Aktualisiere die Einrichtung
            if bill.einrichtung_id:
                # If the institution does not exist, reset the institution
                if not any(institution.db_id == bill.einrichtung_id for institution in self.institutions):
                    print(f'### DatenInterface.__update_rechnungen: Institution with id {bill.einrichtung_id} not found, reset einrichtung in rechnung with id {bill.db_id}')
                    bill.einrichtung_id = None

            # Aktualisiere die Person
            if bill.person_id:
                # If the person does not exist, reset the person
                if not any(person.db_id == bill.person_id for person in self.persons):
                    print(f'### DatenInterface.__update_rechnungen: Person with id {bill.person_id} not found, reset person in rechnung with id {bill.db_id}')
                    bill.person_id = None
            
            # Aktualisierte Rechnung speichern
            self.db.save(bill)
        

    def update_open_bookings(self):
        """Aktualisiert die Liste der offenen Buchungen."""

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
        """Aktualisiert die Liste der noch nicht eingereichten Rechnungen für die Beihilfe."""

        self.allowances_bills.clear()

        for bill in self.bills:
            if not bill.beihilfe_id:
                # A copy of the bill should be appended to the list
                # self.bills is a ListSource of Row objects, so we need to create a new Row object
                # with the same data as the bill
                self.allowances_bills.append(Bill(**bill.__dict__))


    def update_insurances_bills(self):
        """Aktualisiert die Liste der noch nicht eingereichten Rechnungen für die PKV."""

        self.insurances_bills.clear()

        for bill in self.bills:
            if not bill.pkv_id:
                # A copy of the bill should be appended to the list
                # self.bills is a ListSource of Row objects, so we need to create a new Row object
                # with the same data as the bill
                self.insurances_bills.append(Bill(**bill.__dict__))