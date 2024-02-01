"""Enthält die Klassen für die Datenbank und das Daten-Interface."""

import sqlite3 as sql
import shutil
from pathlib import Path
from datetime import datetime
from toga.sources import ListSource, ValueSource, Row
from kontolupe.listeners import *

DATABASE_VERSION = 1

BILL_OBJECT = 'bill'
ALLOWANCE_OBJECT = 'allowance'
INSURANCE_OBJECT = 'insurance'
INSTITUTION_OBJECT = 'institution'
PERSON_OBJECT = 'person'

BILL_TYPES = ('bill', 'bills', 'rechnung', 'rechnungen', 'Rechnung', 'Rechnungen')
ALLOWANCE_TYPES = ('allowance', 'allowances', 'beihilfe', 'beihilfepakete', 'Beihilfe', 'Beihilfepakete')
INSURANCE_TYPES = ('insurance', 'insurances', 'pkv', 'pkvpakete', 'PKV', 'PKVpakete')
INSTITUTION_TYPES = ('institution', 'institutions', 'einrichtung', 'einrichtungen', 'Einrichtung', 'Einrichtungen')
PERSON_TYPES = ('person', 'persons', 'personen', 'Person', 'Personen')

OBJECT_TYPE_TO_DB_TABLE = {
    **dict.fromkeys(BILL_TYPES, 'rechnungen'),
    **dict.fromkeys(ALLOWANCE_TYPES, 'beihilfepakete'),
    **dict.fromkeys(INSURANCE_TYPES, 'pkvpakete'),
    **dict.fromkeys(INSTITUTION_TYPES, 'einrichtungen'),
    **dict.fromkeys(PERSON_TYPES, 'personen')
}

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
        'name_db': None,
        'type_db': None,
        'name_object': 'betrag_euro',
        'default_value': '0,00 €',
    },
    {
        'name_db': 'abzug_beihilfe',
        'type_db': 'REAL',
        'name_object': 'abzug_beihilfe',
        'default_value': 0.0,
    },
    {
        'name_db': None,
        'type_db': None,
        'name_object': 'abzug_beihilfe_euro',
        'default_value': '0,00 €',
    },
    {
        'name_db': 'abzug_pkv',
        'type_db': 'REAL',
        'name_object': 'abzug_pkv',
        'default_value': 0.0,
    },
    {
        'name_db': None,
        'type_db': None,
        'name_object': 'abzug_pkv_euro',
        'default_value': '0,00 €',
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
        'name_db': None,
        'type_db': None,
        'name_object': 'einrichtung_name',
        'default_value': '',
    },
    {
        'name_db': 'notiz',
        'type_db': 'TEXT',
        'name_object': 'notiz',
        'default_value': None,
    },
    {
        'name_db': None,
        'type_db': None,
        'name_object': 'info',
        'default_value': '',
    },
    {
        'name_db': 'person_id',
        'type_db': 'INTEGER',
        'name_object': 'person_id',
        'default_value': None,
    },
    {
        'name_db': None,
        'type_db': None,
        'name_object': 'person_name',
        'default_value': '',
    },
    {
        'name_db': 'beihilfesatz',
        'type_db': 'INTEGER',
        'name_object': 'beihilfesatz',
        'default_value': None,
    },
    {
        'name_db': None,
        'type_db': None,
        'name_object': 'beihilfesatz_prozent',
        'default_value': '0 %',
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
        'name_db': None,
        'type_db': None,
        'name_object': 'bezahlt_text',
        'default_value': 'Nein',
    },
    {
        'name_db': 'beihilfe_id',
        'type_db': 'INTEGER',
        'name_object': 'beihilfe_id',
        'default_value': None,
    },
    {
        'name_db': None,
        'type_db': None,
        'name_object': 'beihilfe_eingereicht',
        'default_value': 'Nein',
    },
    {
        'name_db': 'pkv_id',
        'type_db': 'INTEGER',
        'name_object': 'pkv_id',
        'default_value': None,
    },
    {
        'name_db': None,
        'type_db': None,
        'name_object': 'pkv_eingereicht',
        'default_value': 'Nein',
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
        'name_db': None,
        'type_db': None,
        'name_object': 'betrag_euro',
        'default_value': '0,00 €',
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
    {
        'name_db': None,
        'type_db': None,
        'name_object': 'erhalten_text',
        'default_value': 'Nein',
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
        'name_db': None,
        'type_db': None,
        'name_object': 'betrag_euro',
        'default_value': '0,00 €',
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
    {
        'name_db': None,
        'type_db': None,
        'name_object': 'erhalten_text',
        'default_value': 'Nein',
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
        'name_db': None,
        'type_db': None,
        'name_object': 'plz_ort',
        'default_value': '',
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
        'name_db': None,
        'type_db': None,
        'name_object': 'beihilfesatz_prozent',
        'default_value': '0 %',
    },
    {
        'name_db': 'aktiv',
        'type_db': 'INTEGER',
        'name_object': 'aktiv',
        'default_value': True,
    },
]

def get_attributes(object_type):
    """Gibt die zur Tabelle gehörende Liste der Attribute zurück."""
    attributes = []
    if object_type in BILL_TYPES:
        attributes = BILLS_ATTRIBUTES
    elif object_type in ALLOWANCE_TYPES:
        attributes = ALLOWANCE_ATTRIBUTES
    elif object_type in INSURANCE_TYPES:
        attributes = INSURANCE_ATTRIBUTES
    elif object_type in INSTITUTION_TYPES:
        attributes = INSTITUTION_ATTRIBUTES
    elif object_type in PERSON_TYPES:
        attributes = PERSON_ATTRIBUTES
    return attributes

def get_accessors(object_type):
    """Extract 'name_object' from attributes based on object_type."""
    attributes = get_attributes(object_type)
    return [attribute['name_object'] for attribute in attributes if attribute['name_object']]

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

        # Datenbank-Datei initialisieren und ggf. aktualisieren
        self.__create_db()

        # Aktualisiere die init-Datei
        self.__update_init()

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
        """Einfügen eines neuen Elements in die Datenbank."""
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

        attributes = get_attributes(table)
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

        accessors = get_accessors(table)
        result = ListSource(accessors=accessors)
        for row in ergebnis:
            # Create the data dictionary for the list source
            data = {}
            for attribute in get_attributes(table):
                data[attribute['name_object']] = row.get(attribute['name_db'], attribute['default_value'])  
            result.append(data)

        return result 

    def new(self, object_type, element):
        """Einfügen eines neuen Elements in die Datenbank."""
        db_table = OBJECT_TYPE_TO_DB_TABLE.get(object_type)
        if db_table:
            return self.__new_element(db_table, element)
        else:
            raise ValueError(f'### Database.new: Element {element} not found')

    def save(self, object_type, element):
        """Ändern eines Elements in der Datenbank."""
        db_table = OBJECT_TYPE_TO_DB_TABLE.get(object_type)
        if db_table:
            self.__change_element(db_table, element)
        else:
            raise ValueError(f'### Database.save: Element {element} not found')

    def delete(self, object_type, element):
        """Löschen eines Elements aus der Datenbank."""
        db_table = OBJECT_TYPE_TO_DB_TABLE.get(object_type)
        if db_table:
            self.__delete_element(db_table, element)
        else:
            raise ValueError(f'### Database.delete: Element {element} not found')

    def load(self, object_type, only_active=True):
        """Load the elements of a certain type from the database."""
        db_table = OBJECT_TYPE_TO_DB_TABLE.get(object_type)
        if db_table:
            print(f'### Database: Loading {db_table} from database')
            return self.__load_data(db_table, only_active)
        else:
            raise ValueError(f'### Database.load: Invalid object type {object_type}')
    

class DataInterface:
    """Daten-Interface für die GUI."""

    def __init__(self):
        """Initialisierung des Daten-Interfaces."""
        
        # Datenbank initialisieren
        self.db = Database()

        # Init-Dictionary laden
        self.init = self.db.load_init_file()
        
        self.accessors_open_bookings = [
                'db_id',                        # Datenbank-Id des jeweiligen Elements
                'typ',                          # Typ des Elements (Rechnung, Beihilfe, PKV)
                'betrag_euro',                  # Betrag der Buchung in Euro
                'datum',                        # Rechnungsdatum oder Einreichungsdatum der Beihilfe/PKV
                'buchungsdatum',                # Buchungsdatum der Rechnung
                'info'                          # Info-Text der Buchung
            ]
        
        self.accessors_archivables = [
                'Rechnung',
                'Beihilfe',
                'PKV'
            ]
        
        self.allowances_bills = ListSource(accessors = get_accessors('bill'))
        self.insurances_bills = ListSource(accessors = get_accessors('bill'))
        self.open_bookings = ListSource(accessors = self.accessors_open_bookings)
        self.archivables = ListSource(accessors = self.accessors_archivables)

        self.open_sum = ValueSource()

        # Aktive Einträge aus der Datenbank laden
        # TODO: the data is only mapped onto the first accessor!
        self.bills = self.db.load(BILL_OBJECT)
        self.allowances = self.db.load(ALLOWANCE_OBJECT)
        self.insurances = self.db.load(INSURANCE_OBJECT)
        self.institutions = self.db.load(INSTITUTION_OBJECT)
        self.persons = self.db.load(PERSON_OBJECT)

        # Listen initialisieren
        self.update_bills()
        self.update_allowances_bills()
        self.update_insurances_bills()
        self.update_open_bookings()
        self.update_archivables()
        self.update_open_sum()

        # Listeners
        self.bills.add_listener(SubmitsListener(self.allowances_bills, self.insurances_bills))
        # self.bills.add_listener(ListListener(self, self.open_bookings))
        # self.bills.add_listener(ListListener(self, self.archivables))
        # self.allowances.add_listener(ListListener(self, self.open_bookings))
        # self.allowances.add_listener(ListListener(self, self.archivables))
        # self.insurances.add_listener(ListListener(self, self.open_bookings))
        # self.insurances.add_listener(ListListener(self, self.archivables))

    def update_object(self, object_type, row=None, **data):
        """Update an object."""

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
                    case 'einrichtung_name':
                        value = self.institutions.find({'db_id': get_value('einrichtung_id', None)}).name or ''
                    case 'person_name':
                        value = self.persons.find({'db_id': get_value('person_id', None)}).name or ''
                    case 'info':
                        value = (self.persons.find({'db_id': get_value('person_id', None)}).name + ', ' or '') + (self.institutions.find({'db_id': get_value('einrichtung_id', None)}).name or '')
                if isinstance(row, Row):
                    setattr(row, attribute['name_object'], value)
                else:
                    init_data[attribute['name_object']] = value

        if not isinstance(row, Row):
            return init_data

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

    def archive(self):
        """Archiviert alle archivierbaren Buchungen."""

        for index in self.archivables['Rechnung']:
            self.deactivate(BILL_OBJECT, self.bills[index])

        for index in self.archivables['Beihilfe']:
            self.deactivate(ALLOWANCE_OBJECT, self.allowances[index])
            
        for index in self.archivables['PKV']:
            self.deactivate(INSURANCE_OBJECT, self.insurances[index])

        self.archivables.clear()

    def get_element_by_dbid(self, list_source, db_id):
        """Gibt ein Element einer Liste anhand der ID zurück."""
        try:
            return list_source.find({'db_id': db_id})
        except ValueError:
            print(f'### DatenInterface.get_element_by_dbid: No element found with id {db_id}')
            return None

    def get_allowance_by_name(self, name):
        """Gibt den Beihilfesatz einer Person anhand des Namens zurück."""
        try:
            person = self.persons.find({'name': name})
            print(f'### DatenInterface.get_allowance_by_name: Found allowance percentage for person {name}')
            return person.beihilfesatz
        except ValueError:
            return None
        
    def get_element_index_by_dbid(self, list_source, db_id):
        """Ermittelt den Index eines Elements einer Liste anhand der ID."""
        try:
            row = list_source.find({'db_id': db_id})
            return list_source.index(row)
        except ValueError:
            print(f'### DatenInterface.get_list_element_by_dbid: No element found with id {db_id}')
            return None
        
    def new(self, object_type, data, **kwargs):
        """Erstellt ein neues Element."""

        if object_type in BILL_TYPES:
            # update the bill data and add it to the list source to create the row object
            self.bills.append(self.update_object(object_type, **data))

            # save the new bill to the database
            bill = self.bills[-1]
            bill.db_id = self.db.new(object_type, bill)            
            
            # update connected values
            if bill.bezahlt == False:
                self.open_sum -= (bill.abzug_beihilfe + bill.abzug_pkv)
                self.update_open_bookings()
            else:
                self.open_sum += (bill.betrag - bill.abzug_beihilfe - bill.abzug_pkv)
            
            return bill.db_id

        elif object_type in ALLOWANCE_TYPES:
            # get the amount of the allowance
            amount = 0
            for bill_db_id in kwargs.get('bill_db_ids', []):
                bill = self.bills.find({'db_id': bill_db_id})
                amount += (bill.betrag - bill.abzug_beihilfe) * (bill.beihilfesatz / 100)
            data['betrag'] = amount                    
            
            # update the allowance data and add it to the list source to create the row object
            self.allowances.append(self.update_object(object_type, **data))

            # save the new allowance to the database
            allowance = self.allowances[-1]
            allowance.db_id = self.db.new(object_type, allowance)            
            
            # update connected values
            if allowance.erhalten == False:
                self.update_open_bookings()
            else:
                self.open_sum -= allowance.betrag
                self.update_archivables()
            
            for bill_db_id in kwargs.get('bill_db_ids', []):
                bill = self.bills.find({'db_id': bill_db_id})
                bill.beihilfe_id = allowance.db_id
                self.save(object_type, bill)

            return allowance.db_id

        elif object_type in INSURANCE_TYPES:
            # get the amount of the insurance
            amount = 0
            for bill_db_id in kwargs.get('bill_db_ids', []):
                bill = self.bills.find({'db_id': bill_db_id})
                amount += (bill.betrag - bill.abzug_pkv) * (1 - (bill.beihilfesatz / 100))
            data['betrag'] = amount

            # update the insurance data and add it to the list source to create the row object
            self.insurances.append(self.update_object(object_type, **data))

            # save the new insurance to the database
            insurance = self.insurances[-1]
            insurance.db_id = self.db.new(object_type, insurance)
            
            # update connected values
            if insurance.erhalten == False:
                self.update_open_bookings()
            else:
                self.open_sum -= insurance.betrag
                self.update_archivables()
            
            for bill_db_id in kwargs.get('bill_db_ids', []):
                bill = self.bills.find({'db_id': bill_db_id})
                bill.pkv_id = insurance.db_id
                self.save(object_type, bill)

            return insurance.db_id
        
        elif object_type in INSTITUTION_TYPES:
            self.institutions.append(self.update_object(object_type, **data))
            institution = self.institutions[-1]
            institution.db_id = self.db.new(object_type, institution)
            return institution.db_id
        
        elif object_type in PERSON_TYPES:
            self.persons.append(self.update_object(object_type, **data))
            person = self.persons[-1]
            person.db_id = self.db.new(object_type, person)
            return person.db_id
        
        else:
            raise ValueError(f'### DataInterface.new_element: element type not known')     

    def save(self, object_type, element):
        """Speichert ein Element."""

        self.db.save(object_type, element)
        if object_type in BILL_TYPES or object_type in ALLOWANCE_TYPES or object_type in INSURANCE_TYPES:
            if object_type in BILL_TYPES:
                self.update_object(BILL_OBJECT, element)
            self.update_open_bookings()
            self.update_archivables()
            self.update_open_sum()
        elif object_type in INSTITUTION_TYPES or object_type in PERSON_TYPES:
            self.update_bills()
            self.update_open_bookings()
        
        else:
            raise ValueError(f'### DataInterface.save_element: element type not known')
            
    def delete(self, object_type, element):
        """Löscht ein Element und gibt zurück ob es erfolgreich war."""

        if object_type in BILL_TYPES:
            self.db.delete(object_type, element)
            self.bills.remove(element)
            if element.bezahlt == False:
                self.update_open_bookings()
            elif element.db_id in self.archivables['Rechnung']:
                self.update_archivables()
            self.update_open_sum()
            return True

        elif object_type in ALLOWANCE_TYPES:
            self.db.delete(object_type, element)
            self.allowances.remove(element)

            while self.bills.find({'beihilfe_id': element.db_id}):
                bill = self.bills.find({'beihilfe_id': element.db_id})
                bill.beihilfe_id = None
                self.save(bill)
            
            if element.erhalten == False:
                self.update_open_bookings()
            elif element.db_id in self.archivables['Beihilfe']:
                self.update_archivables()
            self.update_open_sum()
            return True

        elif object_type in INSURANCE_TYPES:
            self.db.delete(object_type, element)
            self.insurances.remove(element)
            
            while self.bills.find({'pkv_id': element.db_id}): 
                bill = self.bills.find({'pkv_id': element.db_id})
                bill.pkv_id = None
                self.save(bill)
            
            if element.erhalten == False:
                self.update_open_bookings()
            elif element.db_id in self.archivables['PKV']:
                self.update_archivables()
            self.update_open_sum()
            return True
        
        elif object_type in INSTITUTION_TYPES:
            if not self.__check_institution_used(element):
                self.db.delete(element)
                self.institutions.remove(element)
                return True
            else:
                return False
        
        elif object_type in PERSON_TYPES:
            if not self.__check_person_used(element):
                self.db.delete(element)
                self.persons.remove(element)
                return True
            else:
                return False

        else:
            raise ValueError(f'### DataInterface.delete_element: element type not known')
            
    def deactivate(self, object_type, element):
        """Deaktiviert ein Element und gibt zurück, ob es erfolgreich war."""
        
        if object_type in BILL_TYPES:
            element.aktiv = False
            self.db.save(object_type, element)
            self.bills.remove(element)
            if element.bezahlt == False:
                self.update_open_bookings()
            elif element.db_id in self.archivables['Rechnung']:
                self.update_archivables()
            self.update_open_sum()
            return True

        elif object_type in ALLOWANCE_TYPES:
            element.aktiv = False
            self.db.save(object_type, element)
            self.allowances.remove(element)

            if element.erhalten == False:
                self.update_open_bookings()
            elif element.db_id in self.archivables['Beihilfe']:
                self.update_archivables()
            self.update_open_sum()
            return True

        elif object_type in INSURANCE_TYPES:
            element.aktiv = False
            self.db.save(object_type, element)
            self.insurances.remove(element)

            if element.erhalten == False:
                self.update_open_bookings()
            elif element.db_id in self.archivables['PKV']:
                self.update_archivables()
            self.update_open_sum()
            return True

        elif object_type in INSTITUTION_TYPES:
            if not self.__check_institution_used(element):
                element.aktiv = False
                self.db.save(object_type, element)
                self.institutions.remove(element)
                return True
            else:
                return False

        elif object_type in PERSON_TYPES:
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
        """Rechnung bezahlen oder Beihilfe/PKV erhalten."""

        if object_type in BILL_TYPES:
            element.bezahlt = True
            if date is not None:
                element.buchungsdatum = date
            elif not element.buchungsdatum:
                element.buchungsdatum = datetime.now().strftime('%d.%m.%Y')
            self.save(object_type, element)
            self.open_bookings.remove(self.open_bookings.find({'db_id': element.db_id, 'typ': 'Rechnung'}))
            self.open_sum += (element.betrag - element.abzug_beihilfe - element.abzug_pkv)

        elif object_type in ALLOWANCE_TYPES:
            element.erhalten = True
            self.save(object_type, element)
            self.open_bookings.remove(self.open_bookings.find({'db_id': element.db_id, 'typ': 'Beihilfe'}))
            self.open_sum -= element.betrag

        elif object_type in INSURANCE_TYPES:
            element.erhalten = True
            self.save(object_type, element)
            self.open_bookings.remove(self.open_bookings.find({'db_id': element.db_id, 'typ': 'PKV'}))
            self.open_sum -= element.betrag

        self.update_archivables()

    def __check_person_used(self, person):
        """Prüft, ob eine Person verwendet wird."""
        try:
            bill = self.bills.find({'person_id': person.db_id})
            print(f'### DatenInterface.__check_person_used: Person with id {person.db_id} is used in bill with id {bill.db_id}')
            return True
        except ValueError:
            return False
        
    def __check_institution_used(self, institution):
        """Prüft, ob eine Einrichtung verwendet wird."""
        try:
            bill = self.bills.find({'einrichtung_id': institution.db_id})
            print(f'### DatenInterface.__check_institution_used: Institution with id {institution.db_id} is used in bill with id {bill.db_id}')
            return True
        except ValueError:
            return False

    def update_submit_amount(self, object_type, element):
        """Aktualisiert eine Beihilfe-Einreichung"""

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
            self.db.save(object_type, element)
        else:
            self.delete(object_type, element)

    def update_bills(self):
        """Aktualisiert die referenzierten Werte in den Rechnungen und speichert sie in der Datenbank."""

        for bill in self.bills:

            changed = False

            # Aktualisiere die Beihilfe
            if bill.beihilfe_id:
                # If the allowance does not exist, reset the allowance id
                if not any(allowance.db_id == bill.beihilfe_id for allowance in self.allowances):
                    print(f'### DatenInterface.__update_rechnungen: Beihilfepaket with id {bill.beihilfe_id} not found, reset beihilfe in rechnung with id {bill.db_id}')
                    bill.beihilfe_id = None
                    changed = True

            # Aktualisiere die PKV
            if bill.pkv_id:
                # If the insurance does not exist, reset the insurance id
                if not any(insurance.db_id == bill.pkv_id for insurance in self.insurances):
                    print(f'### DatenInterface.__update_rechnungen: PKV-Paket with id {bill.pkv_id} not found, reset pkv in rechnung with id {bill.db_id}')
                    bill.pkv_id = None
                    changed = True

            # Aktualisiere die Einrichtung
            if bill.einrichtung_id:
                # If the institution does not exist, reset the institution id
                if not any(institution.db_id == bill.einrichtung_id for institution in self.institutions):
                    print(f'### DatenInterface.__update_rechnungen: Institution with id {bill.einrichtung_id} not found, reset einrichtung in rechnung with id {bill.db_id}')
                    bill.einrichtung_id = None
                    bill.einrichtung_name = ''
                    changed = True
                else:
                    bill.einrichtung_name = self.institutions.find({ 'db_id' : bill.einrichtung_id }).name

            # Aktualisiere die Person
            if bill.person_id:
                # If the person does not exist, reset the person id
                if not any(person.db_id == bill.person_id for person in self.persons):
                    print(f'### DatenInterface.__update_rechnungen: Person with id {bill.person_id} not found, reset person in rechnung with id {bill.db_id}')
                    bill.person_id = None
                    bill.person_name = ''
                    changed = True
                else:
                    bill.person_name = self.persons.find({ 'db_id' : bill.person_id }).name
            
            # Info-Texte aktualisieren
            self.update_object(BILL_OBJECT, bill)           
            # Aktualisierte Rechnung speichern
            if changed:
                self.db.save(BILL_OBJECT, bill)
        
    def update_open_bookings(self):
        """Aktualisiert die Liste der offenen Buchungen."""
        new_list = ListSource(accessors = self.accessors_open_bookings)
        
        for bill in self.bills:
            if not bill.bezahlt:
                new_list.append({
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
                    new_list.append({
                        'db_id': allowance.db_id,
                        'typ': 'Beihilfe',
                        'betrag_euro': '+{:.2f} €'.format(allowance.betrag).replace('.', ',') if allowance.betrag else '0,00 €',
                        'datum': allowance.datum or '',
                        'buchungsdatum': '',
                        'info': 'Beihilfe-Einreichung'
                    })

        for insurance in self.insurances:
            if not insurance.erhalten:
                new_list.append({
                    'db_id': insurance.db_id,
                    'typ': 'PKV',
                    'betrag_euro': '+{:.2f} €'.format(insurance.betrag).replace('.', ',') if insurance.betrag else '0,00 €',
                    'datum': insurance.datum or '',
                    'buchungsdatum': '',
                    'info': 'PKV-Einreichung'
                })

        self.open_bookings = new_list

    def update_allowances_bills(self):
        """Aktualisiert die Liste der noch nicht eingereichten Rechnungen für die Beihilfe."""
        self.allowances_bills.clear()
        for bill in self.bills:
            if not bill.beihilfe_id:
                self.allowances_bills.append(bill)

    def update_insurances_bills(self):
        """Aktualisiert die Liste der noch nicht eingereichten Rechnungen für die PKV."""
        self.insurances_bills.clear()
        for bill in self.bills:
            if not bill.pkv_id:
                self.insurances_bills.append(bill)
    
    def update_open_sum(self):
        """Aktualisiert die Summe der offenen Buchungen."""
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
        """Ermittelt die archivierbaren Elemente des Daten-Interfaces."""

        temp = {
            'Rechnung' : [],
            'Beihilfe' : set(),
            'PKV' : set()
        }

        for i, bill in enumerate(self.bills):
            if bill.bezahlt and (bill.beihilfe_id or not self.allowance_active()) and bill.pkv_id:
                allowance = self.allowances.find({ 'db_id' : bill.beihilfe_id})
                insurance = self.insurances.find({ 'db_id' : bill.pkv_id})
                if ((allowance and allowance.erhalten) or not self.allowance_active()) and insurance and insurance.erhalten:
                    # Check if all other rechnungen associated with the beihilfepaket and pkvpaket are paid
                    other_bills = [ar for ar in self.bill if (self.allowance_active() and ar.beihilfe_id == allowance.db_id) or ar.pkv_id == insurance.db_id]
                    if all(ar.bezahlt for ar in other_bills):
                        temp['Rechnung'].append(i)
                        if self.allowance_active():
                            temp['Beihilfe'].add(self.beihilfepakete.index(allowance))
                        temp['PKV'].add(self.pkvpakete.index(insurance))

        # Convert sets back to lists
        temp['Beihilfe'] = list(temp['Beihilfe'])
        temp['PKV'] = list(temp['PKV'])

        # sort the lists in reverse order
        temp['Rechnung'].sort(reverse=True)
        temp['Beihilfe'].sort(reverse=True)
        temp['PKV'].sort(reverse=True)

        # convert to listSource
        self.archivables.clear()
        self.archivables.append(temp)

        print(f'### DatenInterface.__update_archivables: Archivables updated: {self.archivables}')