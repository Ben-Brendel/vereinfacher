"""Enthält die Klassen für die Datenbank und das Daten-Interface."""

import sqlite3 as sql
import shutil
from pathlib import Path
from datetime import datetime
from toga.sources import ListSource

DATABASE_VERSION = 1

class Datenbank:
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
        print(f'### Database: {self.db_path}')

        self.init_file = self.db_dir / 'init.txt'
        print(f'### Database: {self.init_file}')

        # delete database
        #if self.db_path.exists(): 
        #    self.db_path.unlink()

        # Dictionary mit den Tabellen und Spalten der Datenbank erstellen
        self.__tables = {
            'rechnungen': [
                ('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
                ('betrag', 'REAL'),
                ('einrichtung_id', 'INTEGER'),
                ('rechnungsdatum', 'TEXT'),
                ('notiz', 'TEXT'),
                ('person_id', 'INTEGER'),
                ('beihilfesatz', 'INTEGER'),
                ('buchungsdatum', 'TEXT'),
                ('aktiv', 'INTEGER'),
                ('bezahlt', 'INTEGER'),
                ('beihilfe_id', 'INTEGER'),
                ('pkv_id', 'INTEGER')
            ],
            'beihilfepakete': [
                ('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
                ('betrag', 'REAL'),
                ('datum', 'TEXT'),
                ('aktiv', 'INTEGER'),
                ('erhalten', 'INTEGER')
            ],
            'pkvpakete': [
                ('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
                ('betrag', 'REAL'),
                ('datum', 'TEXT'),
                ('aktiv', 'INTEGER'),
                ('erhalten', 'INTEGER')
            ],
            'einrichtungen': [
                ('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
                ('name', 'TEXT'),
                ('strasse', 'TEXT'),
                ('plz', 'TEXT'),
                ('ort', 'TEXT'),
                ('telefon', 'TEXT'),
                ('email', 'TEXT'),
                ('webseite', 'TEXT'),
                ('notiz', 'TEXT'),
                ('aktiv', 'INTEGER')
            ],
            'personen': [
                ('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
                ('name', 'TEXT'),
                ('beihilfesatz', 'INTEGER'),
                ('aktiv', 'INTEGER')
            ],
        }

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

                # check if there is any data
                if rechnungen or beihilfepakete or pkvpakete or einrichtungen or personen:
                    print(f'### Database: __update_init: Init file {self.init_file} does not exist and database has data. Create init file.')
                    self.save_init_file(version=DATABASE_VERSION, beihilfe=True)
                    return
                else:
                    print(f'### Database: __update_init: Init file {self.init_file} does not exist and database is empty. Do not create init file.')
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
        return not self.init_file.exists()
    
    def save_init_file(self, **kwargs):
        """Speichern der init.txt Datei."""
        # create the init file
        # write the variables to the init file
        # if the value is a boolean, it should be converted to True or False
        content = ''
        for key, value in kwargs.items():
            if isinstance(value, bool):
                value = str(value).lower()
            content += f'{key}={value}\n'

        self.init_file.write_text(content)
        print(f'### Database: save_init_file: Saved init file {self.init_file}')

    def load_init_file(self):
        """Laden der init.txt Datei und Rückgabe als Dictionary."""
        # load the init file
        # the value should be converted to the correct type
        # return the variables as a dictionary
        result = {}
        for line in self.init_file.read_text().splitlines():
            # check if there is an equal sign in the line
            if '=' not in line:
                print(f'### Database: load_init_file: Line {line} does not contain an equal sign. Skipping it.')
                continue
            key, value = line.split('=')
            if value == 'true':
                value = True
            elif value == 'false':
                value = False
            elif value.isnumeric():
                value = int(value)
            result[key] = value
        print(f'### Database: load_init_file: Loaded init file {self.init_file}')
        return result

    def reset_data(self):
        """Setzt alle Daten zurück."""
        # create a backup of the database
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
        print(f'### Database: Get column type for column {column_name} in table {table_name}')
        for column in self.__tables[table_name]:
            if column[0] == column_name:
                print(f'### Database: Column type for column {column_name} in table {table_name} is {column[1]}')
                return column[1]
        print(f'### Database: Column {column_name} not found in table {table_name}')
        return None  # return None if the column is not found

    def __create_backup(self):
        """Erstellen eines Backups der Datenbank."""
        # Get the current date and time, formatted as a string
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        print(f'### Database: Timestamp is {timestamp}')

        # Create the backup path with the timestamp
        backup_path = self.db_dir / Path(f'kontolupe_{timestamp}.db.backup')
        print(f'### Database: Backup path is {backup_path}')
        
        if self.db_path.exists():
            if backup_path.exists():
                print(f'### Database: Backup {backup_path} already exists. Deleting it.')
                backup_path.unlink()
            shutil.copy2(self.db_path, backup_path)
            print(f'### Database: Created backup {backup_path}')
        else:
            print(f'### Database: Database {self.db_path} does not exist. No backup created.')

    def __delete_backups(self):
        """Löschen aller Backups der Datenbank."""
        for file in self.db_dir.glob('kontolupe_*.db.backup'):
            print(f'### Database: Deleting backup {file}')
            file.unlink()

    def __create_table_if_not_exists(self, cursor, table_name, columns):
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join([f'{column[0]} {column[1]}' for column in columns])})")
        print(f'### Database: Created table {table_name}')

    def __add_column_if_not_exists(self, cursor, table_name, new_column, column_type):
        cursor.execute(f"PRAGMA table_info({table_name})")
        if not any(row[1] == new_column for row in cursor.fetchall()):
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {new_column} {column_type}")
            print(f'### Database: Added column {new_column} to table {table_name}')
            if new_column == 'aktiv':
                cursor.execute(f"UPDATE {table_name} SET aktiv = 1")

    def __copy_column(self, cursor, table_name, old_column, new_column):
        # Check if table_name exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if not cursor.fetchone():
            print(f'### Database: Copy Column: Table {table_name} does not exist')
            return  # table_name doesn't exist, so return early
        else:
            print(f'### Database: Copy Column: Table {table_name} exists')

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
            print(f'### Database: Copied column {old_column} to {new_column} in table {table_name}')
        else:
            print(f'### Database: Column {old_column} does not exist in table {table_name}')

    def __copy_table_and_delete(self, cursor, old_table, new_table):
        # Check if old_table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (old_table,))
        if not cursor.fetchone():
            print(f'### Database: Copy Table and Delete: Table {old_table} does not exist')
            return  # old_table doesn't exist, so return early
        else:
            print(f'### Database: Copy Table and Delete: Table {old_table} exists')

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
        print(f'### Database: Copied table {old_table} to {new_table}')

        # Drop old_table
        cursor.execute(f"DROP TABLE {old_table}")
        print(f'### Database: Dropped table {old_table}')

    def __create_db(self):
        """Erstellen und Update der Datenbank."""

        # Check if database exists and is structured correctly
        # If not, create a backup and rebuild the database
        if self.__db_exists_and_is_correct():
            print('### Database: Database exists and is structured correctly.')
            return
        print('### Database: Database does not exist or is not structured correctly.')

        # Backup and rebuild the database
        self.__create_backup()
        self.__rebuild_db()

    def __db_exists_and_is_correct(self):
        """Check if the database exists and is structured correctly."""

        if not self.db_path.exists():
            print('### Database: Database does not exist.')
            return False
        else:
            print('### Database: Database exists.')

        with sql.connect(self.db_path) as connection:
            cursor = connection.cursor()
            for table_name, columns in self.__tables.items():
                if not self.__table_is_correct(cursor, table_name, columns):
                    print(f'### Database: Table {table_name} is not structured correctly.')
                    return False
                else:
                    print(f'### Database: Table {table_name} is structured correctly.')

        print('### Database: Database exists and is structured correctly.')

        return True

    def __table_is_correct(self, cursor, table_name, columns):
        """Check if a table is structured correctly."""

        cursor.execute(f"PRAGMA table_info({table_name})")
        result = cursor.fetchall()
        for column in columns:
            if not any(row[1] == column[0] for row in result):
                print(f'### Database: Column {column[0]} does not exist in table {table_name}.')
                return False
            else:
                print(f'### Database: Column {column[0]} exists in table {table_name}.')

        print(f'### Database: Table {table_name} is structured correctly.')

        return True

    def __rebuild_db(self):
        """Rebuild the database."""

        print('### Database: Rebuilding database.')

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

        print('### Database: Updating database structure.')

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
                    print(f'### Database: Updated table {old_table} to the latest structure.')
            

    def __migrate_data(self, cursor):
        """Migrate the data to the new database structure."""

        for table_name, columns in self.__table_columns_rename.items():
            for column in columns:
                Datenbank.__copy_column(self, cursor, table_name, column[0], column[1])
                print(f'### Database: Migrated data in table {table_name} from column {column[0]} to column {column[1]}')

    def __rename_tables(self, cursor):
        """Rename the tables."""

        for old_table, new_table in self.__tables_rename.items():
            Datenbank.__copy_table_and_delete(self, cursor, old_table, new_table)
            print(f'### Database: Migrated data from {old_table} to {new_table} and deleted {old_table}')


    def __new_element(self, table, element):
        """Einfügen eines neuen Elements in die Datenbank."""
        # Datenbankverbindung herstellen
        connection = sql.connect(self.db_path)
        cursor = connection.cursor()

        # Get the columns for the query
        column_names = [column[0] for column in self.__tables[table]]
        column_names.remove('id')

        # Build the SQL query and values tuple dynamically
        query = f"""INSERT INTO {table} ({', '.join(column_names)}) VALUES ({', '.join(['?' for _ in column_names])})"""
        values = tuple(getattr(element, column_name) for column_name in column_names)

        # Daten einfügen
        cursor.execute(query, values)
        db_id = cursor.lastrowid

        # Datenbankverbindung schließen
        connection.commit()
        connection.close()
        print(f'### Database: Inserted element with id {db_id} into table {table}')

        return db_id
    
    def __change_element(self, table, element):
        """Ändern eines Elements in der Datenbank."""
        # Datenbankverbindung herstellen
        connection = sql.connect(self.db_path)
        cursor = connection.cursor()

        # Get the columns for the query
        column_names = [column[0] for column in self.__tables[table]]
        column_names.remove('id')

        # Build the SQL query and values tuple dynamically
        query = f"""UPDATE {table} SET {', '.join([f'{column_name} = ?' for column_name in column_names])} WHERE id = ?"""
        values = tuple(getattr(element, column_name) for column_name in column_names)
        values += (element.db_id,)

        # Daten ändern
        cursor.execute(query, values)

        # Datenbankverbindung schließen
        connection.commit()
        connection.close()
        print(f'### Database: Changed element with id {element.db_id} in table {table}')

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
        print(f'### Database: Deleted element with id {element.db_id} from table {table}')

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

        result = []
        for row in ergebnis:
            match table:
                case 'rechnungen':
                    element = Rechnung()
                case 'beihilfepakete':
                    element = BeihilfePaket()
                case 'pkvpakete':
                    element = PKVPaket()
                case 'einrichtungen':
                    element = Einrichtung()
                case 'personen':
                    element = Person()
                case _:
                    raise ValueError(f'### Database.__load_data: Table {table} not found')

            # Setze die Attribute des Elements
            for column in self.__tables[table]:
                if column[0] in row:
                    if column[0] == 'id':
                        setattr(element, 'db_id', row[column[0]])
                    else:
                        setattr(element, column[0], row[column[0]])

            result.append(element)
            print(f'### Database.__load_data: Loaded element with id {element.db_id} and type {type(element)} from table {table}')

        # Datenbankverbindung schließen
        connection.close()
        print(f'### Database.__load_data: Loaded data from table {table}')

        return result

    def neue_rechnung(self, rechnung):
        """Einfügen einer neuen Rechnung in die Datenbank."""
        print(f'### Database: Inserting new Rechnung into database')
        return self.__new_element('rechnungen', rechnung)
    
    def neues_beihilfepaket(self, beihilfepaket):
        """Einfügen eines neuen Beihilfepakets in die Datenbank."""
        print(f'### Database: Inserting new Beihilfepaket into database')
        return self.__new_element('beihilfepakete', beihilfepaket)
    
    def neues_pkvpaket(self, pkvpaket):
        """Einfügen eines neuen PKV-Pakets in die Datenbank."""
        print(f'### Database: Inserting new PKVPaket into database')
        return self.__new_element('pkvpakete', pkvpaket)
    
    def neue_einrichtung(self, einrichtung):
        """Einfügen einer neuen Einrichtung in die Datenbank."""
        print(f'### Database: Inserting new Einrichtung into database')
        return self.__new_element('einrichtungen', einrichtung)
    
    def neue_person(self, person):
        """Einfügen einer neuen Person in die Datenbank."""
        print(f'### Database: Inserting new Person into database')
        return self.__new_element('personen', person)
    
    def aendere_rechnung(self, rechnung):
        """Ändern einer Rechnung in der Datenbank."""
        print(f'### Database: Changing Rechnung with id {rechnung.db_id} in database')
        self.__change_element('rechnungen', rechnung)

    def aendere_beihilfepaket(self, beihilfepaket):
        """Ändern eines Beihilfepakets in der Datenbank."""
        print(f'### Database: Changing Beihilfepaket with id {beihilfepaket.db_id} in database')
        self.__change_element('beihilfepakete', beihilfepaket)

    def aendere_pkvpaket(self, pkvpaket):
        """Ändern eines PKV-Pakets in der Datenbank."""
        print(f'### Database: Changing PKVPaket with id {pkvpaket.db_id} in database')
        self.__change_element('pkvpakete', pkvpaket)

    def aendere_einrichtung(self, einrichtung):
        """Ändern einer Einrichtung in der Datenbank."""
        print(f'### Database: Changing Einrichtung with id {einrichtung.db_id} in database')
        self.__change_element('einrichtungen', einrichtung)

    def aendere_person(self, person):
        """Ändern einer Person in der Datenbank."""
        print(f'### Database: Changing Person with id {person.db_id} in database')
        self.__change_element('personen', person)

    def loesche_rechnung(self, rechnung):
        """Löschen einer Rechnung aus der Datenbank."""
        print(f'### Database: Deleting Rechnung with id {rechnung.db_id} from database')
        self.__delete_element('rechnungen', rechnung)

    def loesche_beihilfepaket(self, beihilfepaket):
        """Löschen eines Beihilfepakets aus der Datenbank."""
        print(f'### Database: Deleting Beihilfepaket with id {beihilfepaket.db_id} from database')
        self.__delete_element('beihilfepakete', beihilfepaket)

    def loesche_pkvpaket(self, pkvpaket):
        """Löschen eines PKV-Pakets aus der Datenbank."""
        print(f'### Database: Deleting PKVPaket with id {pkvpaket.db_id} from database')
        self.__delete_element('pkvpakete', pkvpaket)

    def loesche_einrichtung(self, einrichtung):
        """Löschen einer Einrichtung aus der Datenbank."""
        print(f'### Database: Deleting Einrichtung with id {einrichtung.db_id} from database')
        self.__delete_element('einrichtungen', einrichtung)

    def loesche_person(self, person):
        """Löschen einer Person aus der Datenbank."""
        print(f'### Database: Deleting Person with id {person.db_id} from database')
        self.__delete_element('personen', person)

    def lade_rechnungen(self, only_active=True):
        """Laden der Rechnungen aus der Datenbank."""
        print(f'### Database: Loading Rechnungen from database')
        return self.__load_data('rechnungen', only_active)
    
    def lade_beihilfepakete(self, only_active=True):
        """Laden der Beihilfepakete aus der Datenbank."""
        print(f'### Database: Loading Beihilfepakete from database')
        return self.__load_data('beihilfepakete', only_active)
    
    def lade_pkvpakete(self, only_active=True):
        """Laden der PKV-Pakete aus der Datenbank."""
        print(f'### Database: Loading PKVPakete from database')
        return self.__load_data('pkvpakete', only_active)
    
    def lade_einrichtungen(self, only_active=True):
        """Laden der Einrichtungen aus der Datenbank."""
        print(f'### Database: Loading Einrichtungen from database')
        return self.__load_data('einrichtungen', only_active)
    
    def lade_personen(self, only_active=True):
        """Laden der Personen aus der Datenbank."""
        print(f'### Database: Loading Personen from database')
        return self.__load_data('personen', only_active)


class Rechnung:
    """Klasse zur Erfassung einer Rechnung."""
    
    def __init__(self):
        """Initialisierung der Rechnung."""
        self.db_id = None
        self.betrag = 0
        self.rechnungsdatum = None
        self.einrichtung_id = None
        self.notiz = None
        self.person_id = None
        self.beihilfesatz = None
        self.buchungsdatum = None
        self.bezahlt = False
        self.beihilfe_id = None
        self.pkv_id = None
        self.aktiv = True

    def neu(self, db):
        """Neue Rechnung erstellen."""
        self.db_id = db.neue_rechnung(self)

    def speichern(self, db):
        """Speichern der Rechnung in der Datenbank."""
        db.aendere_rechnung(self)

    def loeschen(self, db):
        """Löschen der Rechnung aus der Datenbank."""
        db.loesche_rechnung(self)

    def __str__(self):
        """Ausgabe der Rechnung."""
        ausgabe = 'ID: {}\n'.format(self.db_id)
        ausgabe += 'Rechnung vom {}\n'.format(self.rechnungsdatum)
        ausgabe += 'Betrag: {:.2f} €\n'.format(self.betrag).replace('.', ',')
        ausgabe += 'Person: {}\n'.format(self.person_id)
        ausgabe += 'Beihilfesatz: {:.0f} %\n'.format(self.beihilfesatz)
        ausgabe += 'Einrichtung: {}\n'.format(self.einrichtung_id)
        ausgabe += 'Notiz: {}\n'.format(self.notiz)
        if self.buchungsdatum is not None:
            ausgabe += 'Buchungsdatum: {}\n'.format(self.buchungsdatum)
        else:
            ausgabe += 'Buchungsdatum: -\n'
        if self.bezahlt:
            ausgabe += 'Bezahlt: Ja'
        else:
            ausgabe += 'Bezahlt: Nein'

        return ausgabe
    

class BeihilfePaket:
    """Klasse zur Darstellung einer Beihilfe-Einreichung."""
    
    def __init__(self):
        """Initialisierung der Beihilfe-Einreichung."""

        # Betrag der Beihilfe-Einreichung berechnen
        self.db_id = None
        self.betrag = 0        
        self.datum = None
        self.aktiv = True
        self.erhalten = False

    def neu(self, db, rechnungen=None):
        """Neue Beihilfe-Einreichung erstellen."""
        # Betrag der Beihilfe-Einreichung berechnen

        if rechnungen is not None:
            self.betrag = 0
            for rechnung in rechnungen:
                self.betrag += rechnung.betrag * rechnung.beihilfesatz / 100

        # Beihilfepaket speichern
        self.db_id = db.neues_beihilfepaket(self)

        if rechnungen is not None:
            # Beihilfe-Einreichung mit Rechnungen verknüpfen
            for rechnung in rechnungen:
                rechnung.beihilfe_id = self.db_id
                rechnung.speichern(db)

    def speichern(self, db):
        """Speichern der Beihilfe-Einreichung in der Datenbank."""
        db.aendere_beihilfepaket(self)

    def loeschen(self, db):
        """Löschen der Beihilfe-Einreichung aus der Datenbank."""
        db.loesche_beihilfepaket(self)

    def __str__(self):
        """Ausgabe der Beihilfe-Einreichung."""
        return (f"Beihilfe-Einreichung: {self.db_id}\n"
            f"Datum: {self.datum}\n"
            f"Betrag: {self.betrag} €\n"
            f"Erstattet: {self.erhalten}")
        

class PKVPaket:
    """Klasse zur Darstellung einer PKV-Einreichung."""
    
    def __init__(self):
        """Initialisierung der PKV-Einreichung."""
        self.betrag = 0
        self.datum = None
        self.aktiv = True
        self.erhalten = False
        self.db_id = None

    def neu(self, db, rechnungen=None):
        """Neue PKV-Einreichung erstellen."""

        # Betrag der PKV-Einreichung berechnen
        if rechnungen is not None:
            self.betrag = 0
            for rechnung in rechnungen:
                self.betrag += rechnung.betrag * (100 - rechnung.beihilfesatz) / 100

        # PKV-Einreichung speichern
        self.db_id = db.neues_pkvpaket(self)

        if rechnungen is not None:
            # PKV-Einreichung mit Rechnungen verknüpfen
            for rechnung in rechnungen:
                rechnung.pkv_id = self.db_id
                rechnung.speichern(db)

    def speichern(self, db):
        """Speichern der PKV-Einreichung in der Datenbank."""
        db.aendere_pkvpaket(self)

    def loeschen(self, db):
        """Löschen der PKV-Einreichung aus der Datenbank."""
        db.loesche_pkvpaket(self)

    def __str__(self):
        """Ausgabe der PKV-Einreichung."""
        return (f"PKV-Einreichung: {self.db_id}\n"
            f"Datum: {self.datum}\n"
            f"Betrag: {self.betrag} €\n"
            f"Erstattet: {self.erhalten}")


class Einrichtung:
    """Klasse zur Verwaltung der Einrichtungen."""
    
    def __init__(self):
        """Initialisierung der Einrichtung."""
        self.name = None
        self.db_id = None
        self.strasse = None
        self.plz = None
        self.ort = None
        self.telefon = None
        self.email = None
        self.webseite = None
        self.notiz = None
        self.aktiv = True

    def neu(self, db):
        """Neue Einrichtung erstellen."""
        self.db_id = db.neue_einrichtung(self)

    def speichern(self, db):
        """Speichern der Einrichtung in der Datenbank."""
        db.aendere_einrichtung(self)

    def loeschen(self, db):
        """Löschen der Einrichtung aus der Datenbank."""
        db.loesche_einrichtung(self)

    def __str__(self):
        """Ausgabe der Einrichtung."""
        return (f'ID: {self.db_id}\n'
            f'Einrichtung: {self.name}'
            f'\nStraße: {self.strasse}'
            f'\nPLZ, Ort: {self.plz, self.ort}'
            f'\nTelefon: {self.telefon}'
            f'\nE-Mail: {self.email}'
            f'\nWebseite: {self.webseite}'
            f'\nNotiz: {self.notiz}')
    

class Person:
    """Klasse zur Verwaltung der Personen."""
    
    def __init__(self):
        """Initialisierung der Person."""
        self.name = None
        self.beihilfesatz = None
        self.aktiv = True
        self.db_id = None

    def neu(self, db):
        """Neue Person erstellen."""
        self.db_id = db.neue_person(self)

    def speichern(self, db):
        """Speichern der Person in der Datenbank."""
        db.aendere_person(self)

    def loeschen(self, db):
        """Löschen der Person aus der Datenbank."""
        db.loesche_person(self)

    def __str__(self):
        """Ausgabe der Person."""
        return (f'ID: {self.db_id}\n'
            f'Name: {self.name}'
            f'\nBeihilfe: {self.beihilfesatz} %')
    

class DatenInterface:
    """Daten-Interface für die GUI."""

    def __init__(self):
        """Initialisierung des Daten-Interfaces."""

        print(f'### DatenInterface: Initialisierung des Daten-Interfaces')
        
        # Datenbank initialisieren
        self.db = Datenbank()

        # Aktive Einträge aus der Datenbank laden
        self.rechnungen = self.db.lade_rechnungen()
        self.beihilfepakete = self.db.lade_beihilfepakete()
        self.pkvpakete = self.db.lade_pkvpakete()
        self.einrichtungen = self.db.lade_einrichtungen()
        self.personen = self.db.lade_personen()

        print(f'### DatenInterface.__init__: {len(self.rechnungen)} Rechnungen loaded')
        print(f'### DatenInterface.__init__: {len(self.beihilfepakete)} Beihilfepakete loaded')
        print(f'### DatenInterface.__init__: {len(self.pkvpakete)} PKV-Pakete loaded')
        print(f'### DatenInterface.__init__: {len(self.einrichtungen)} Einrichtungen loaded')
        print(f'### DatenInterface.__init__: {len(self.personen)} Personen loaded')

        # ListSources für die GUI erstellen
        # Diese enthalten alle Felder der Datenbank und zusätzliche Felder für die GUI
        self.list_rechnungen = ListSource(
            accessors = [
                'db_id', 
                'betrag', 
                'betrag_euro',
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
        )

        self.list_rg_beihilfe = ListSource(
            accessors = [
                'db_id', 
                'betrag', 
                'betrag_euro',
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
        )

        self.list_rg_pkv = ListSource(
            accessors = [
                'db_id', 
                'betrag', 
                'betrag_euro',
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
        )

        self.list_einrichtungen = ListSource(
            accessors = [
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
        )

        self.list_personen = ListSource(
            accessors = [
                'db_id',
                'name',
                'beihilfesatz',
                'beihilfesatz_prozent',
            ]
        )

        self.list_beihilfepakete = ListSource(
            accessors = [
                'db_id',
                'betrag',
                'betrag_euro',
                'datum',
                'erhalten',
                'erhalten_text'
            ]
        )

        self.list_pkvpakete = ListSource(
            accessors = [
                'db_id',
                'betrag',
                'betrag_euro',
                'datum',
                'erhalten',
                'erhalten_text'
            ]
        )

        self.list_open_bookings = ListSource(
            accessors = [
                'db_id',                        # Datenbank-Id des jeweiligen Elements
                'typ',                          # Typ des Elements (Rechnung, Beihilfe, PKV)
                'betrag_euro',                  # Betrag der Buchung in Euro
                'datum',                        # Datum der Buchung (Plandatum der Rechnung oder Einreichungsdatum der Beihilfe/PKV)
                'info'                          # Info-Text der Buchung
            ]
        )

        for rechnung in self.rechnungen:            
            self.__list_rechnungen_append(rechnung)
        
        print(f'### DatenInterface.__init__: {len(self.list_rechnungen)} Rechnungen loaded to ListSource')

        for einrichtung in self.einrichtungen:            
            self.__list_einrichtungen_append(einrichtung)

        print(f'### DatenInterface.__init__: {len(self.list_einrichtungen)} Einrichtungen loaded to ListSource')

        for person in self.personen:            
            self.__list_personen_append(person)

        print(f'### DatenInterface.__init__: {len(self.list_personen)} Personen loaded to ListSource')

        for beihilfepaket in self.beihilfepakete:            
            self.__list_beihilfepakete_append(beihilfepaket)

        print(f'### DatenInterface.__init__: {len(self.list_beihilfepakete)} Beihilfepakete loaded to ListSource')

        for pkvpaket in self.pkvpakete:            
            self.__list_pkvpakete_append(pkvpaket)

        print(f'### DatenInterface.__init__: {len(self.list_pkvpakete)} PKV-Pakete loaded to ListSource')

        self.__update_list_open_bookings()
        self.__update_list_rg_beihilfe()
        self.__update_list_rg_pkv()
        self.__update_archivables()

    def is_first_start(self):
        """Prüft, ob das Programm zum ersten Mal gestartet wird."""
        return self.db.is_first_start()

    def save_init_file(self, **kwargs):
        """Speichert die Initialisierungsdatei."""
        self.db.save_init_file(**kwargs)

    def load_init_file(self):
        """Lädt die Initialisierungsdatei und gibt ihren Inhalt als Dictionary zurück."""
        return self.db.load_init_file()

    def __update_archivables(self):
        """Ermittelt die archivierbaren Elemente des Daten-Interfaces."""

        print(f'### DatenInterface.__update_archivables: Updating archivables')

        self.archivables = {
            'Rechnung' : [],
            'Beihilfe' : set(),
            'PKV' : set()
        }

        # Create dictionaries for quick lookup of beihilfepakete and pkvpakete by db_id
        beihilfepakete_dict = {paket.db_id: paket for paket in self.beihilfepakete}
        pkvpakete_dict = {paket.db_id: paket for paket in self.pkvpakete}

        for i, rechnung in enumerate(self.rechnungen):
            if rechnung.bezahlt and rechnung.beihilfe_id and rechnung.pkv_id:
                beihilfepaket = beihilfepakete_dict.get(rechnung.beihilfe_id)
                pkvpaket = pkvpakete_dict.get(rechnung.pkv_id)
                if beihilfepaket and beihilfepaket.erhalten and pkvpaket and pkvpaket.erhalten:
                    # Check if all other rechnungen associated with the beihilfepaket and pkvpaket are paid
                    other_rechnungen = [ar for ar in self.rechnungen if ar.beihilfe_id == beihilfepaket.db_id or ar.pkv_id == pkvpaket.db_id]
                    if all(ar.bezahlt for ar in other_rechnungen):
                        self.archivables['Rechnung'].append(i)
                        self.archivables['Beihilfe'].add(self.beihilfepakete.index(beihilfepaket))
                        self.archivables['PKV'].add(self.pkvpakete.index(pkvpaket))

        # Convert sets back to lists
        self.archivables['Beihilfe'] = list(self.archivables['Beihilfe'])
        self.archivables['PKV'] = list(self.archivables['PKV'])

        # sort the lists in reverse order
        self.archivables['Rechnung'].sort(reverse=True)
        self.archivables['Beihilfe'].sort(reverse=True)
        self.archivables['PKV'].sort(reverse=True)

        print(f'### DatenInterface.__update_archivables: Archivables updated: {self.archivables}')


    def archive(self):
        """Archiviert alle archivierbaren Buchungen."""

        print(f'### DatenInterface: archive: Archiving process started')

        for i in self.archivables['Rechnung']:
            self.__deactivate_rechnung(i)

        for i in self.archivables['Beihilfe']:
            self.__deactivate_beihilfepaket(i)
            
        for i in self.archivables['PKV']:
            self.__deactivate_pkvpaket(i)

        print(f'### DatenInterface.archive: Archiving process finished')
        self.__update_archivables()


    def get_open_sum(self, *args, **kwargs):
        """Berechnet die Summe der offenen Buchungen."""
        
        sum = 0

        if kwargs.get('rechnungen', True):
            for rechnung in self.rechnungen:
                if rechnung.bezahlt == False:
                    sum -= rechnung.betrag
                if rechnung.beihilfe_id == None:
                    sum += rechnung.betrag * (rechnung.beihilfesatz / 100)
                if rechnung.pkv_id == None:
                    sum += rechnung.betrag * (1 - (rechnung.beihilfesatz / 100))
        
        if kwargs.get('beihilfe', True):
            for beihilfepaket in self.beihilfepakete:
                if beihilfepaket.erhalten == False:
                    sum += beihilfepaket.betrag

        if kwargs.get('pkv', True):
            for pkvpaket in self.pkvpakete:
                if pkvpaket.erhalten == False:
                    sum += pkvpaket.betrag

        print(f'### DatenInterface.get_open_sum: Open sum: {sum} €')

        return round(sum, 2)
    

    def get_number_rechnungen_not_paid(self):
        """Ermittelt die Anzahl der noch nicht bezahlten Rechnungen."""
        count = 0
        for rechnung in self.rechnungen:
            if rechnung.bezahlt == False:
                count += 1
        print(f'### DatenInterface.get_number_rechnungen_not_paid: Number rechnungen not paid: {count}')
        return count
    

    def get_number_rechnungen_not_submitted_beihilfe(self):
        """Ermittelt die Anzahl der noch nicht bei der Beihilfe eingereichten Rechnungen."""
        count = 0
        for rechnung in self.rechnungen:
            if rechnung.beihilfe_id == None:
                count += 1
        print(f'### DatenInterface.get_number_rechnungen_not_submitted_beihilfe: Number rechnungen not submitted to Beihilfe: {count}')
        return count
    

    def get_number_rechnungen_not_submitted_pkv(self):
        """Ermittelt die Anzahl der noch nicht bei der PKV eingereichten Rechnungen."""
        count = 0
        for rechnung in self.rechnungen:
            if rechnung.pkv_id == None:
                count += 1
        print(f'### DatenInterface.get_number_rechnungen_not_submitted_pkv: Number rechnungen not submitted to PKV: {count}')
        return count


    def get_number_archivables(self):   
        """Ermittelt die Anzahl der archivierbaren Elemente in self.archivables."""
        count = sum(len(self.archivables[key]) for key in self.archivables)
        print(f'### DatenInterface.get_number_archivables: Number archivables: {count}')
        return count
        

    def get_rechnung_by_dbid(self, id, objekt=False):
        """Gibt eine Rechnung anhand der ID zurück."""
        rechnungen = self.rechnungen if objekt else self.list_rechnungen

        for rechnung in rechnungen:
            if rechnung['db_id'] == id:
                print(f'### DatenInterface.get_rechnung_by_dbid: Found rechnung with id {id}')
                return rechnung
        print(f'### DatenInterface.get_rechnung_by_dbid: No rechnung found with id {id}')

        return None
    

    def get_beihilfepaket_by_dbid(self, id, objekt=False):
        """Gibt ein Beihilfepaket anhand der ID zurück."""
        beihilfepakete = self.beihilfepakete if objekt else self.list_beihilfepakete

        for beihilfepaket in beihilfepakete:
            if beihilfepaket.db_id == id:
                print(f'### DatenInterface.get_beihilfepaket_by_dbid: Found beihilfepaket with id {id}')
                return beihilfepaket
        print(f'### DatenInterface.get_beihilfepaket_by_dbid: No beihilfepaket found with id {id}')
            
        return None
    

    def get_pkvpaket_by_dbid(self, id, objekt=False):
        """Gibt ein PKV-Paket anhand der ID zurück."""
        pkvpakete = self.pkvpakete if objekt else self.list_pkvpakete

        for pkvpaket in pkvpakete:
            if pkvpaket.db_id == id:
                print(f'### DatenInterface.get_pkvpaket_by_dbid: Found pkvpaket with id {id}')
                return pkvpaket
        print(f'### DatenInterface.get_pkvpaket_by_dbid: No pkvpaket found with id {id}')
            
        return None
    

    def get_einrichtung_by_dbid(self, id, objekt=False):
        """Gibt eine Einrichtung anhand der ID zurück."""
        einrichtungen = self.einrichtungen if objekt else self.list_einrichtungen

        for einrichtung in einrichtungen:
            if einrichtung.db_id == id:
                print(f'### DatenInterface.get_einrichtung_by_dbid: Found einrichtung with id {id}')
                return einrichtung
        print(f'### DatenInterface.get_einrichtung_by_dbid: No einrichtung found with id {id}')
            
        return None
    

    def get_person_by_dbid(self, id, objekt=False):
        """Gibt eine Person anhand der ID zurück."""
        personen = self.personen if objekt else self.list_personen

        for person in personen:
            if person.db_id == id:
                print(f'### DatenInterface.get_person_by_dbid: Found person with id {id}')
                return person
        print(f'### DatenInterface.get_person_by_dbid: No person found with id {id}')
            
        return None
    

    def get_rechnung_by_index(self, index, objekt=False):
        """Gibt eine Rechnung als Row-Objekt oder als Rechnung-Objekt anhand des Index zurück."""
        rechnungen = self.rechnungen if objekt else self.list_rechnungen

        if index < 0 or index >= len(rechnungen):
            print(f'### DatenInterface.get_rechnung_by_index: No rechnung with index {index}')
            return None
        
        print(f'### DatenInterface.get_rechnung_by_index: Return rechnung with index {index}')

        return rechnungen[index]
    

    def get_beihilfepaket_by_index(self, index, objekt=False):
        """Gibt ein Beihilfepaket als Row-Objekt oder als BeihilfePaket-Objekt anhand des Index zurück."""
        beihilfepakete = self.beihilfepakete if objekt else self.list_beihilfepakete

        if index < 0 or index >= len(beihilfepakete):
            print(f'### DatenInterface.get_beihilfepaket_by_index: No beihilfepaket with index {index}')
            return None
        
        print(f'### DatenInterface.get_beihilfepaket_by_index: Return beihilfepaket with index {index}')

        return beihilfepakete[index]
    

    def get_pkvpaket_by_index(self, index, objekt=False):
        """Gibt ein PKV-Paket als Row-Objekt oder als PKVPaket-Objekt anhand des Index zurück."""
        pkvpakete = self.pkvpakete if objekt else self.list_pkvpakete

        if index < 0 or index >= len(pkvpakete):
            print(f'### DatenInterface.get_pkvpaket_by_index: No pkvpaket with index {index}')
            return None
        
        print(f'### DatenInterface.get_pkvpaket_by_index: Return pkvpaket with index {index}')

        return pkvpakete[index]
    

    def get_einrichtung_by_index(self, index, objekt=False):
        """Gibt eine Einrichtung als Row-Objekt oder als Einrichtung-Objekt anhand des Index zurück."""
        einrichtungen = self.einrichtungen if objekt else self.list_einrichtungen

        if index < 0 or index >= len(einrichtungen):
            print(f'### DatenInterface.get_einrichtung_by_index: No einrichtung with index {index}')
            return None
        
        print(f'### DatenInterface.get_einrichtung_by_index: Return einrichtung with index {index}')

        return einrichtungen[index]
    

    def get_person_by_index(self, index, objekt=False):
        """Gibt eine Person als Row-Objekt oder als Person-Objekt anhand des Index zurück."""
        personen = self.personen if objekt else self.list_personen

        if index < 0 or index >= len(personen):
            print(f'### DatenInterface.get_person_by_index: No person with index {index}')
            return None
        
        print(f'### DatenInterface.get_person_by_index: Return person with index {index}')

        return personen[index]
    

    def get_beihilfesatz_by_name(self, name):
        """Gibt den Beihilfesatz einer Person anhand des Namens zurück."""
        for person in self.personen:
            if person.name == name:
                print(f'### DatenInterface.get_beihilfesatz_by_name: Found beihilfesatz for person {name}')
                return person.beihilfesatz
            
        print(f'### DatenInterface.get_beihilfesatz_by_name: No beihilfesatz found for person {name}')
        
        return None
    

    def get_rechnung_index_by_dbid(self, db_id):
        """Gibt den Index einer Rechnung anhand der ID zurück."""
        index = self.__get_list_index_by_dbid(self.list_rechnungen, db_id)
        if index is None:
            print(f'### DatenInterface.get_rechnung_index_by_dbid: No rechnung found with db_id {db_id}')
        else:
            print(f'### DatenInterface.get_rechnung_index_by_dbid: Return rechnung index {index} with id {db_id}') 
        return index
    

    def get_einrichtung_index_by_dbid(self, db_id):
        """Gibt den Index einer Einrichtung anhand der ID zurück."""
        index = self.__get_list_index_by_dbid(self.list_einrichtungen, db_id)
        if index is None:
            print(f'### DatenInterface.get_einrichtung_index_by_dbid: No einrichtung found with id {db_id}')
        else:
            print(f'### DatenInterface.get_einrichtung_index_by_dbid: Return einrichtung index {index} with id {db_id}') 
        return index
    

    def get_person_index_by_dbid(self, db_id):
        """Gibt den Index einer Person anhand der ID zurück."""
        index = self.__get_list_index_by_dbid(self.list_personen, db_id)
        if index is None:
            print(f'### DatenInterface.get_person_index_by_dbid: No person found with id {db_id}')
        else:
            print(f'### DatenInterface.get_person_index_by_dbid: Return person index {index} with id {db_id}') 
        return index
    

    def new_rechnung(self, rechnung):
        """Neue Rechnung erstellen."""
        print(f'### DatenInterface.new_rechnung: New rechnung')
        rechnung.neu(self.db)
        self.rechnungen.append(rechnung)
        self.__list_rechnungen_append(rechnung)
        self.__update_list_open_bookings()
        self.__update_list_rg_beihilfe()
        self.__update_list_rg_pkv()
        self.__update_archivables()


    def edit_rechnung(self, rechnung, rg_id):
        """Rechnung ändern."""
        print(f'### DatenInterface.edit_rechnung: Edit rechnung with list id {rg_id}')
        self.rechnungen[rg_id] = rechnung
        self.rechnungen[rg_id].speichern(self.db)
        self.__update_list_rechnungen_id(rechnung, rg_id)
        self.__update_list_open_bookings()
        self.__update_list_rg_beihilfe()
        self.__update_list_rg_pkv()
        self.__update_archivables()


    def delete_rechnung(self, rg_id):
        """Rechnung löschen."""
        print(f'### DatenInterface.delete_rechnung: Delete rechnung with list id {rg_id}')
        self.rechnungen[rg_id].loeschen(self.db)
        self.rechnungen.pop(rg_id)
        del self.list_rechnungen[rg_id]
        self.__update_list_open_bookings()
        self.__update_list_rg_beihilfe()
        self.__update_list_rg_pkv()
        self.__update_archivables()


    def __deactivate_rechnung(self, rg_id):
        """Rechnung deaktivieren."""
        print(f'### DatenInterface.deactivate_rechnung: Deactivate rechnung with list id {rg_id}')
        self.rechnungen[rg_id].aktiv = False
        self.rechnungen[rg_id].speichern(self.db)
        self.rechnungen.pop(rg_id)
        del self.list_rechnungen[rg_id]


    def pay_rechnung(self, db_id):
        """Rechnung bezahlen."""
        print(f'### DatenInterface.pay_rechnung: Pay rechnung with db_id {db_id}')
        index = self.__get_list_index_by_dbid(self.list_rechnungen, db_id)
        self.rechnungen[index].bezahlt = True
        self.rechnungen[index].buchungsdatum = datetime.now().strftime('%d.%m.%Y')
        self.rechnungen[index].speichern(self.db)
        self.__update_list_rechnungen_id(self.rechnungen[index], index)
        self.__update_list_open_bookings()
        self.__update_archivables()


    def receive_beihilfe(self, db_id):
        """Beihilfe erhalten."""
        print(f'### DatenInterface.receive_beihilfe: Receive beihilfe with db_id {db_id}')
        index = self.__get_list_index_by_dbid(self.list_beihilfepakete, db_id)
        self.beihilfepakete[index].erhalten = True
        self.beihilfepakete[index].speichern(self.db)
        self.__update_list_beihilfepakete_id(self.beihilfepakete[index], index)
        self.__update_list_open_bookings()
        self.__update_archivables()


    def receive_pkv(self, db_id):
        """PKV erhalten."""
        print(f'### DatenInterface.receive_pkv: Receive pkv with db_id {db_id}')
        index = self.__get_list_index_by_dbid(self.list_pkvpakete, db_id)
        self.pkvpakete[index].erhalten = True
        self.pkvpakete[index].speichern(self.db)
        self.__update_list_pkvpakete_id(self.pkvpakete[index], index)
        self.__update_list_open_bookings()
        self.__update_archivables()


    def new_beihilfepaket(self, beihilfepaket, rechnungen_db_ids):
        """Neues Beihilfepaket erstellen."""
        print(f'### DatenInterface.new_beihilfepaket: New beihilfepaket')
        beihilfepaket.neu(self.db)
        self.beihilfepakete.append(beihilfepaket)
        self.__list_beihilfepakete_append(beihilfepaket)

        # Beihilfepaket mit Rechnungen verknüpfen
        for rechnung_db_id in rechnungen_db_ids:
            index = self.__get_list_index_by_dbid(self.list_rechnungen, rechnung_db_id)
            self.rechnungen[index].beihilfe_id = beihilfepaket.db_id
            print(f'### DatenInterface.new_beihilfepaket: rechnung type: {type(self.rechnungen[index])}')
            self.rechnungen[index].speichern(self.db)
            self.__update_list_rechnungen_id(self.rechnungen[index], index)
            print(f'### DatenInterface.new_beihilfepaket: Rechnung with id {rechnung_db_id} linked to beihilfepaket with id {beihilfepaket.db_id}')

        self.__update_list_open_bookings()
        self.__update_list_rg_beihilfe()
        self.__update_list_rg_pkv()
        self.__update_archivables()


    def delete_beihilfepaket(self, beihilfepaket_id):
        """Beihilfepaket löschen."""
        print(f'### DatenInterface.delete_beihilfepaket: Delete beihilfepaket with id {beihilfepaket_id}')
        self.beihilfepakete[beihilfepaket_id].loeschen(self.db)
        self.beihilfepakete.pop(beihilfepaket_id)
        del self.list_beihilfepakete[beihilfepaket_id]
        self.__update_rechnungen()
        self.__update_list_open_bookings()
        self.__update_list_rg_beihilfe()
        self.__update_list_rg_pkv()
        self.__update_archivables()


    def __deactivate_beihilfepaket(self, beihilfepaket_id):
        """Beihilfepaket deaktivieren."""
        print(f'### DatenInterface.deactivate_beihilfepaket: Deactivate beihilfepaket with id {beihilfepaket_id}')
        self.beihilfepakete[beihilfepaket_id].aktiv = False
        self.beihilfepakete[beihilfepaket_id].speichern(self.db)
        self.beihilfepakete.pop(beihilfepaket_id)
        del self.list_beihilfepakete[beihilfepaket_id]


    def new_pkvpaket(self, pkvpaket, rechnungen_db_ids):
        """Neues PKV-Paket erstellen."""
        print(f'### DatenInterface.new_pkvpaket: New pkvpaket')
        pkvpaket.neu(self.db)
        self.pkvpakete.append(pkvpaket)
        self.__list_pkvpakete_append(pkvpaket)

        # PKV-Paket mit Rechnungen verknüpfen
        for rechnung_db_id in rechnungen_db_ids:
            index = self.__get_list_index_by_dbid(self.list_rechnungen, rechnung_db_id)
            self.rechnungen[index].pkv_id = pkvpaket.db_id
            print(f'### DatenInterface.new_pkvpaket: rechnung type: {type(self.rechnungen[index])}')
            self.rechnungen[index].speichern(self.db)
            self.__update_list_rechnungen_id(self.rechnungen[index], index)
            print(f'### DatenInterface.new_pkvpaket: Rechnung with id {rechnung_db_id} linked to pkvpaket with id {pkvpaket.db_id}')

        self.__update_list_open_bookings()
        self.__update_list_rg_beihilfe()
        self.__update_list_rg_pkv()
        self.__update_archivables()


    def delete_pkvpaket(self, pkvpaket_id):
        """PKV-Paket löschen."""
        print(f'### DatenInterface.delete_pkvpaket: Delete pkvpaket with id {pkvpaket_id}')
        self.pkvpakete[pkvpaket_id].loeschen(self.db)
        self.pkvpakete.pop(pkvpaket_id)
        del self.list_pkvpakete[pkvpaket_id]
        self.__update_rechnungen()
        self.__update_list_open_bookings()
        self.__update_list_rg_beihilfe()
        self.__update_list_rg_pkv()
        self.__update_archivables()


    def __deactivate_pkvpaket(self, pkvpaket_id):
        """PKV-Paket deaktivieren."""
        print(f'### DatenInterface.deactivate_pkvpaket: Deactivate pkvpaket with id {pkvpaket_id}')
        self.pkvpakete[pkvpaket_id].aktiv = False
        self.pkvpakete[pkvpaket_id].speichern(self.db)
        self.pkvpakete.pop(pkvpaket_id)
        del self.list_pkvpakete[pkvpaket_id]


    def new_einrichtung(self, einrichtung):
        """Neue Einrichtung erstellen."""
        print(f'### DatenInterface.new_einrichtung: New einrichtung')
        einrichtung.neu(self.db)
        self.einrichtungen.append(einrichtung)
        self.__list_einrichtungen_append(einrichtung)


    def edit_einrichtung(self, einrichtung, einrichtung_id):
        """Einrichtung ändern."""
        print(f'### DatenInterface.edit_einrichtung: Edit einrichtung with id {einrichtung_id}')
        self.einrichtungen[einrichtung_id] = einrichtung
        self.einrichtungen[einrichtung_id].speichern(self.db)
        self.__update_list_einrichtungen_id(einrichtung, einrichtung_id)
        self.__update_rechnungen()
        self.__update_list_open_bookings()


    def delete_einrichtung(self, einrichtung_id):
        """Einrichtung löschen."""
        print(f'### DatenInterface.delete_einrichtung: Delete einrichtung with id {einrichtung_id}')
        if self.__check_einrichtung_used(einrichtung_id):
            return False
        self.einrichtungen[einrichtung_id].loeschen(self.db)
        self.einrichtungen.pop(einrichtung_id)
        del self.list_einrichtungen[einrichtung_id]
        return True


    def deactivate_einrichtung(self, einrichtung_id):
        """Einrichtung deaktivieren."""
        print(f'### DatenInterface.deactivate_einrichtung: Deactivate einrichtung with id {einrichtung_id}')
        if self.__check_einrichtung_used(einrichtung_id):
            return False
        self.einrichtungen[einrichtung_id].aktiv = False
        self.einrichtungen[einrichtung_id].speichern(self.db)
        self.einrichtungen.pop(einrichtung_id)
        del self.list_einrichtungen[einrichtung_id]
        return True


    def __check_einrichtung_used(self, einrichtung_id):
        """Prüft, ob eine Einrichtung verwendet wird."""
        for rechnung in self.rechnungen:
            if rechnung.einrichtung_id == einrichtung_id:
                print(f'### DatenInterface.__check_einrichtung_used: Einrichtung with id {einrichtung_id} is used in rechnung with id {rechnung.db_id}')
                return True
        print(f'### DatenInterface.__check_einrichtung_used: Einrichtung with id {einrichtung_id} is not used')
        return False


    def new_person(self, person):
        """Neue Person erstellen."""
        print(f'### DatenInterface.new_person: New person')
        person.neu(self.db)
        self.personen.append(person)
        self.__list_personen_append(person)


    def edit_person(self, person, person_id):
        """Person ändern."""
        print(f'### DatenInterface.edit_person: Edit person with id {person_id}')
        self.personen[person_id] = person
        self.personen[person_id].speichern(self.db)
        self.__update_list_personen_id(person, person_id)
        self.__update_rechnungen()
        self.__update_list_open_bookings()


    def delete_person(self, person_id):
        """Person löschen."""
        print(f'### DatenInterface.delete_person: Delete person with id {person_id}')
        if self.__check_person_used(person_id):
            return False
        self.personen[person_id].loeschen(self.db)
        self.personen.pop(person_id)
        del self.list_personen[person_id]
        return True


    def deactivate_person(self, person_id):
        """Person deaktivieren."""
        print(f'### DatenInterface.deactivate_person: Deactivate person with id {person_id}')
        if self.__check_person_used(person_id):
            return False
        self.personen[person_id].aktiv = False
        self.personen[person_id].speichern(self.db)
        self.personen.pop(person_id)
        del self.list_personen[person_id]
        return True


    def __check_person_used(self, person_id):
        """Prüft, ob eine Person verwendet wird."""
        for rechnung in self.rechnungen:
            if rechnung.person_id == person_id:
                print(f'### DatenInterface.__check_person_used: Person with id {person_id} is used in rechnung with id {rechnung.db_id}')
                return True
        print(f'### DatenInterface.__check_person_used: Person with id {person_id} is not used')
        return False


    def update_beihilfepaket_betrag(self, db_id):
        """Aktualisiert eine Beihilfe-Einreichung"""
        print(f'### DatenInterface.update_beihilfepaket_betrag: Update beihilfepaket with id {db_id}')
        # Finde die Beihilfe-Einreichung
        for beihilfepaket in self.beihilfepakete:
            if beihilfepaket.db_id == db_id:
                print(f'### DatenInterface.update_beihilfepaket_betrag: Found beihilfepaket with id {db_id}')
                # Alle Rechnungen durchlaufen und den Betrag aktualisieren
                beihilfepaket.betrag = 0
                print(f'### DatenInterface.update_beihilfepaket_betrag: Beihilfepaket Betrag: {beihilfepaket.betrag}')
                inhalt = False
                for rechnung in self.rechnungen:
                    if rechnung.beihilfe_id == db_id:
                        print(f'### DatenInterface.update_beihilfepaket_betrag: Found rechnung with id {rechnung.db_id}')
                        inhalt = True
                        beihilfepaket.betrag += rechnung.betrag * (rechnung.beihilfesatz / 100)
                        print(f'### DatenInterface.update_beihilfepaket_betrag: Beihilfepaket Betrag: {beihilfepaket.betrag}')
                # Die Beihilfe-Einreichung speichern
                if inhalt:
                    print(f'### DatenInterface.update_beihilfepaket_betrag: Beihilfepaket with id {db_id} has content and is saved')
                    beihilfepaket.speichern(self.db)
                    self.__update_list_beihilfepakete_id(beihilfepaket, self.beihilfepakete.index(beihilfepaket))
                else:
                    print(f'### DatenInterface.update_beihilfepaket_betrag: Beihilfepaket with id {db_id} has no content and is deleted')
                    self.delete_beihilfepaket(self.beihilfepakete.index(beihilfepaket))
                self.__update_list_open_bookings()
                break
            

    def update_pkvpaket_betrag(self, db_id):
        """Aktualisiert eine PKV-Einreichung einer Rechnung."""
        print(f'### DatenInterface.update_pkvpaket_betrag: Update pkvpaket with id {db_id}')
        for pkvpaket in self.pkvpakete:
            if pkvpaket.db_id == db_id:
                print(f'### DatenInterface.update_pkvpaket_betrag: Found pkvpaket with id {db_id}')
                pkvpaket.betrag = 0
                print(f'### DatenInterface.update_pkvpaket_betrag: PKV-Paket Betrag: {pkvpaket.betrag}')
                inhalt = False
                for rechnung in self.rechnungen:
                    if rechnung.pkv_id == db_id:
                        print(f'### DatenInterface.update_pkvpaket_betrag: Found rechnung with id {rechnung.db_id}')
                        inhalt = True
                        pkvpaket.betrag += rechnung.betrag * (1 - (rechnung.beihilfesatz / 100))
                        print(f'### DatenInterface.update_pkvpaket_betrag: PKV-Paket Betrag: {pkvpaket.betrag}')
                if inhalt:
                    print(f'### DatenInterface.update_pkvpaket_betrag: PKV-Paket with id {db_id} has content and is saved')
                    pkvpaket.speichern(self.db)
                    self.__update_list_pkvpakete_id(pkvpaket, self.pkvpakete.index(pkvpaket))
                else:
                    print(f'### DatenInterface.update_pkvpaket_betrag: PKV-Paket with id {db_id} has no content and is deleted')
                    self.delete_pkvpaket(self.pkvpakete.index(pkvpaket))
                self.__update_list_open_bookings()
                break
    

    def __get_list_index_by_dbid(self, liste, db_id):
        """Ermittelt den Index eines Elements einer Liste anhand der ID."""
        for i, element in enumerate(liste):
            if element.db_id == db_id:
                print(f'### DatenInterface.__get_list_index_by_dbid: Found element with id {db_id} at index {i} in {liste}')
                return i
        else:
            print(f'### DatenInterface.__get_list_index_by_dbid: No element found with id {db_id}')
            return None


    def __person_name(self, person_id):
        """Gibt den Namen einer Person zurück."""
        for person in self.personen:
            if person.db_id == person_id:
                print(f'### DatenInterface.__person_name: Found person {person.name} with id {person_id}')
                return person.name
        print(f'### DatenInterface.__person_name: No person found with id {person_id}')
        return ''
    

    def __einrichtung_name(self, einrichtung_id):
        """Gibt den Namen einer Einrichtung zurück."""
        for einrichtung in self.einrichtungen:
            if einrichtung.db_id == einrichtung_id:
                print(f'### DatenInterface.__einrichtung_name: Found einrichtung {einrichtung.name} with id {einrichtung_id}')
                return einrichtung.name
        print(f'### DatenInterface.__einrichtung_name: No einrichtung found with id {einrichtung_id}')
        return ''
    

    def __row_from_rechnung(self, rechnung):
        """Erzeugt ein Row-Objekt aus einer Rechnung."""
        print(f'### DatenInterface.__row_from_rechnung: Create row from rechnung with id {rechnung.db_id}')
        return {
            'db_id': rechnung.db_id,
            'betrag': rechnung.betrag,
            'betrag_euro': '{:.2f} €'.format(rechnung.betrag).replace('.', ','),
            'rechnungsdatum': rechnung.rechnungsdatum,
            'einrichtung_id': rechnung.einrichtung_id,
            'notiz': rechnung.notiz,
            'person_id': rechnung.person_id,
            'person_name': self.__person_name(rechnung.person_id),
            'einrichtung_name': self.__einrichtung_name(rechnung.einrichtung_id),
            'info': (self.__person_name(rechnung.person_id) + ', ' if self.__person_name(rechnung.person_id) else '') + self.__einrichtung_name(rechnung.einrichtung_id),
            'beihilfesatz': rechnung.beihilfesatz,
            'beihilfesatz_prozent': '{:.0f} %'.format(rechnung.beihilfesatz),
            'buchungsdatum': rechnung.buchungsdatum,
            'bezahlt': rechnung.bezahlt,
            'bezahlt_text': 'Ja' if rechnung.bezahlt else 'Nein',
            'beihilfe_id': rechnung.beihilfe_id,
            'beihilfe_eingereicht': 'Ja' if rechnung.beihilfe_id else 'Nein',
            'pkv_id': rechnung.pkv_id,
            'pkv_eingereicht': 'Ja' if rechnung.pkv_id else 'Nein'
        }


    def __list_rechnungen_append(self, rechnung):
        """Fügt der Liste der Rechnungen eine neue Rechnung hinzu."""
        print(f'### DatenInterface.__list_rechnungen_append: Append rechnung with id {rechnung.db_id}')
        self.list_rechnungen.append(self.__row_from_rechnung(rechnung))
        

    def __update_list_rechnungen_id(self, rechnung, rg_id):
        """Ändert ein Element der Liste der Rechnungen."""
        print(f'### DatenInterface.__update_list_rechnungen_id: Update rechnung with id {rechnung.db_id} at index {rg_id}')
        self.list_rechnungen[rg_id] = self.__row_from_rechnung(rechnung)
        

    def __update_rechnungen(self):
        """Aktualisiert die referenzierten Werte in den Rechnungen und speichert sie in der Datenbank."""
        print(f'### DatenInterface.__update_rechnungen: Update referenced values in rechnungen')

        for i, rechnung in enumerate(self.rechnungen):

            # Aktualisiere die Beihilfe
            if rechnung.beihilfe_id:
                print(f'### DatenInterface.__update_rechnungen: Check beihilfe with id {rechnung.beihilfe_id} in rechnung with id {rechnung.db_id}')
                # Überprüfe ob die Beihilfe noch existiert
                beihilfepaket_vorhanden = False
                for beihilfepaket in self.beihilfepakete:
                    if beihilfepaket.db_id == rechnung.beihilfe_id:
                        print(f'### DatenInterface.__update_rechnungen: Found beihilfepaket with id {rechnung.beihilfe_id}')
                        beihilfepaket_vorhanden = True
                        break
                
                # Wenn die Beihilfe nicht mehr existiert, setze die Beihilfe zurück
                if not beihilfepaket_vorhanden:
                    print(f'### DatenInterface.__update_rechnungen: Beihilfepaket with id {rechnung.beihilfe_id} not found, reset beihilfe in rechnung with id {rechnung.db_id}')
                    rechnung.beihilfe_id = None

            # Aktualisiere die PKV
            if rechnung.pkv_id:
                print(f'### DatenInterface.__update_rechnungen: Check pkv with id {rechnung.pkv_id} in rechnung with id {rechnung.db_id}')
                # Überprüfe ob die PKV noch existiert
                pkvpaket_vorhanden = False
                for pkvpaket in self.pkvpakete:
                    if pkvpaket.db_id == rechnung.pkv_id:
                        print(f'### DatenInterface.__update_rechnungen: Found pkvpaket with id {rechnung.pkv_id}')
                        pkvpaket_vorhanden = True
                        break
                
                # Wenn die PKV nicht mehr existiert, setze die PKV zurück
                if not pkvpaket_vorhanden:
                    print(f'### DatenInterface.__update_rechnungen: PKV-Paket with id {rechnung.pkv_id} not found, reset pkv in rechnung with id {rechnung.db_id}')
                    rechnung.pkv_id = None

            # Aktualisiere die Einrichtung
            if rechnung.einrichtung_id:
                print(f'### DatenInterface.__update_rechnungen: Check einrichtung with id {rechnung.einrichtung_id} in rechnung with id {rechnung.db_id}')
                # Überprüfe ob die Einrichtung noch existiert
                einrichtung_vorhanden = False
                for einrichtung in self.einrichtungen:
                    if einrichtung.db_id == rechnung.einrichtung_id:
                        print(f'### DatenInterface.__update_rechnungen: Found einrichtung with id {rechnung.einrichtung_id}')
                        einrichtung_vorhanden = True
                        break
                
                # Wenn die Einrichtung nicht mehr existiert, setze die Einrichtung zurück
                if not einrichtung_vorhanden:
                    print(f'### DatenInterface.__update_rechnungen: Einrichtung with id {rechnung.einrichtung_id} not found, reset einrichtung in rechnung with id {rechnung.db_id}')
                    rechnung.einrichtung_id = None

            # Aktualisiere die Person
            if rechnung.person_id:
                print(f'### DatenInterface.__update_rechnungen: Check person with id {rechnung.person_id} in rechnung with id {rechnung.db_id}')
                # Überprüfe ob die Person noch existiert
                person_vorhanden = False
                for person in self.personen:
                    if person.db_id == rechnung.person_id:
                        print(f'### DatenInterface.__update_rechnungen: Found person with id {rechnung.person_id}')
                        person_vorhanden = True
                        break
                
                # Wenn die Person nicht mehr existiert, setze die Person zurück
                if not person_vorhanden:
                    print(f'### DatenInterface.__update_rechnungen: Person with id {rechnung.person_id} not found, reset person in rechnung with id {rechnung.db_id}')
                    rechnung.person_id = None
            
            # Aktualisierte Rechnung speichern
            print(f'### DatenInterface.__update_rechnungen: Save rechnung with id {rechnung.db_id}')
            rechnung.speichern(self.db)
            self.__update_list_rechnungen_id(rechnung, i)


    def __row_from_einrichtung(self, einrichtung):
        """Erzeugt ein Row-Objekt aus einer Einrichtung."""
        print(f'### DatenInterface.__row_from_einrichtung: Create row from einrichtung with id {einrichtung.db_id}')
        return {
            'db_id': einrichtung.db_id,
            'name': einrichtung.name or '',
            'strasse': einrichtung.strasse or '',
            'plz': einrichtung.plz or '',
            'ort': einrichtung.ort or '',
            'plz_ort': (einrichtung.plz or '') + (' ' if einrichtung.plz else '') + (einrichtung.ort or ''),
            'telefon': einrichtung.telefon or '',
            'email': einrichtung.email or '',
            'webseite': einrichtung.webseite or '',
            'notiz': einrichtung.notiz or ''
        }


    def __list_einrichtungen_append(self, einrichtung):
        """Fügt der Liste der Einrichtungen eine neue Einrichtung hinzu."""
        print(f'### DatenInterface.__list_einrichtungen_append: Append einrichtung with id {einrichtung.db_id}')
        self.list_einrichtungen.append(self.__row_from_einrichtung(einrichtung))
        

    def __update_list_einrichtungen_id(self, einrichtung, einrichtung_id):
        """Ändert ein Element der Liste der Einrichtungen."""
        print(f'### DatenInterface.__update_list_einrichtungen_id: Update einrichtung with id {einrichtung.db_id} at index {einrichtung_id}')
        self.list_einrichtungen[einrichtung_id] = self.__row_from_einrichtung(einrichtung)


    def __row_from_person(self, person):
        """Erzeugt ein Row-Objekt aus einer Person."""
        print(f'### DatenInterface.__row_from_person: Create row from person with id {person.db_id}')
        return {
            'db_id': person.db_id,
            'name': person.name or '',
            'beihilfesatz': person.beihilfesatz or '',
            'beihilfesatz_prozent': '{:.0f} %'.format(person.beihilfesatz) if person.beihilfesatz else '0 %'
        }

    
    def __list_personen_append(self, person):
        """Fügt der Liste der Personen eine neue Person hinzu."""
        print(f'### DatenInterface.__list_personen_append: Append person with id {person.db_id}')
        self.list_personen.append(self.__row_from_person(person))
        

    def __update_list_personen_id(self, person, person_id):    
        """Ändert ein Element der Liste der Personen."""
        print(f'### DatenInterface.__update_list_personen_id: Update person with id {person.db_id} at index {person_id}')
        self.list_personen[person_id] = self.__row_from_person(person)

    
    def __update_list_beihilfepakete(self):
        """Aktualisiert die Liste der Beihilfepakete."""
        print(f'### DatenInterface.__update_list_beihilfepakete: Update list beihilfepakete')
        for beihilfepaket_id in range(len(self.list_beihilfepakete)):
            self.__update_list_beihilfepakete_id(self.beihilfepakete[beihilfepaket_id], beihilfepaket_id)


    def __row_from_beihilfepaket(self, beihilfepaket):
        """Erzeugt ein Row-Objekt aus einem Beihilfepaket."""
        print(f'### DatenInterface.__row_from_beihilfepaket: Create row from beihilfepaket with id {beihilfepaket.db_id}')
        return {
            'db_id': beihilfepaket.db_id,
            'betrag': beihilfepaket.betrag,
            'betrag_euro': '{:.2f} €'.format(beihilfepaket.betrag).replace('.', ','),
            'datum': beihilfepaket.datum,
            'erhalten': beihilfepaket.erhalten,
            'erhalten_text': 'Ja' if beihilfepaket.erhalten else 'Nein'
        }


    def __list_beihilfepakete_append(self, beihilfepaket):
        print(f'### DatenInterface.__list_beihilfepakete_append: Append beihilfepaket with id {beihilfepaket.db_id}')
        """Fügt der Liste der Beihilfepakete ein neues Beihilfepaket hinzu."""
        self.list_beihilfepakete.append(self.__row_from_beihilfepaket(beihilfepaket))

    
    def __update_list_beihilfepakete_id(self, beihilfepaket, beihilfepaket_id):
        """Ändert ein Element der Liste der Beihilfepakete."""
        print(f'### DatenInterface.__update_list_beihilfepakete_id: Update beihilfepaket with id {beihilfepaket.db_id} at index {beihilfepaket_id}')
        self.list_beihilfepakete[beihilfepaket_id] = self.__row_from_beihilfepaket(beihilfepaket)
        

    def __update_list_pkvpakete(self):
        """Aktualisiert die Liste der PKV-Pakete."""
        print(f'### DatenInterface.__update_list_pkvpakete: Update list pkvpakete')
        for pkvpaket_id in range(len(self.list_pkvpakete)):
            self.__update_list_pkvpakete_id(self.pkvpakete[pkvpaket_id], pkvpaket_id)


    def __row_from_pkvpaket(self, pkvpaket):
        """Erzeugt ein Row-Objekt aus einem PKV-Paket."""
        print(f'### DatenInterface.__row_from_pkvpaket: Create row from pkvpaket with id {pkvpaket.db_id}')
        return {
            'db_id': pkvpaket.db_id,
            'betrag': pkvpaket.betrag,
            'betrag_euro': '{:.2f} €'.format(pkvpaket.betrag).replace('.', ','),
            'datum': pkvpaket.datum,
            'erhalten': pkvpaket.erhalten,
            'erhalten_text': 'Ja' if pkvpaket.erhalten else 'Nein'
        }
        

    def __list_pkvpakete_append(self, pkvpaket):
        """Fügt der Liste der PKV-Pakete ein neues PKV-Paket hinzu."""
        print(f'### DatenInterface.__list_pkvpakete_append: Append pkvpaket with id {pkvpaket.db_id}')
        self.list_pkvpakete.append(self.__row_from_pkvpaket(pkvpaket))
        

    def __update_list_pkvpakete_id(self, pkvpaket, pkvpaket_id):
        """Ändert ein Element der Liste der PKV-Pakete."""
        print(f'### DatenInterface.__update_list_pkvpakete_id: Update pkvpaket with id {pkvpaket.db_id} at index {pkvpaket_id}')
        self.list_pkvpakete[pkvpaket_id] = self.__row_from_pkvpaket(pkvpaket)
        

    def __update_list_open_bookings(self):
        """Aktualisiert die Liste der offenen Buchungen."""
        print(f'### DatenInterface.__update_list_open_bookings: Update list open bookings')

        self.list_open_bookings.clear()
        print(f'### DatenInterface.__update_list_open_bookings: Cleared list open bookings')
        for b in self.list_open_bookings:
            print(f'### DatenInterface.__update_list_open_bookings: element: {b}')

        for rechnung in self.list_rechnungen:
            if not rechnung.bezahlt:
                self.list_open_bookings.append({
                    'db_id': rechnung.db_id,
                    'typ': 'Rechnung',
                    'betrag_euro': '-{:.2f} €'.format(rechnung.betrag).replace('.', ','),
                    'datum': rechnung.buchungsdatum,
                    'info': rechnung.info
                })
                print(f'### DatenInterface.__update_list_open_bookings: Added rechnung with id {rechnung.db_id} to list open bookings')
    
        for beihilfepaket in self.beihilfepakete:
            if not beihilfepaket.erhalten:
                self.list_open_bookings.append({
                    'db_id': beihilfepaket.db_id,
                    'typ': 'Beihilfe',
                    'betrag_euro': '+{:.2f} €'.format(beihilfepaket.betrag).replace('.', ','),
                    'datum': beihilfepaket.datum,
                    'info': 'Beihilfe-Einreichung'
                })
                print(f'### DatenInterface.__update_list_open_bookings: Added beihilfepaket with id {beihilfepaket.db_id} to list open bookings')

        for pkvpaket in self.pkvpakete:
            if not pkvpaket.erhalten:
                self.list_open_bookings.append({
                    'db_id': pkvpaket.db_id,
                    'typ': 'PKV',
                    'betrag_euro': '+{:.2f} €'.format(pkvpaket.betrag).replace('.', ','),
                    'datum': pkvpaket.datum,
                    'info': 'PKV-Einreichung'
                })
                print(f'### DatenInterface.__update_list_open_bookings: Added pkvpaket with id {pkvpaket.db_id} to list open bookings')


    def __update_list_rg_beihilfe(self):
        """Aktualisiert die Liste der noch nicht eingereichten Rechnungen für die Beihilfe."""
        print(f'### DatenInterface.__update_list_rg_beihilfe: Update list rg beihilfe')

        self.list_rg_beihilfe.clear()
        print(f'### DatenInterface.__update_list_rg_beihilfe: Cleared list rg beihilfe')
        for b in self.list_rg_beihilfe:
            print(f'### DatenInterface.__update_list_rg_beihilfe: element: {b}')

        for rechnung in self.rechnungen:
            if not rechnung.beihilfe_id:
                self.list_rg_beihilfe.append(self.__row_from_rechnung(rechnung))
                print(f'### DatenInterface.__update_list_rg_beihilfe: Added rechnung with id {rechnung.db_id} to list rg beihilfe')


    def __update_list_rg_pkv(self):
        """Aktualisiert die Liste der noch nicht eingereichten Rechnungen für die PKV."""
        print(f'### DatenInterface.__update_list_rg_pkv: Update list rg pkv')

        self.list_rg_pkv.clear()
        print(f'### DatenInterface.__update_list_rg_pkv: Cleared list rg pkv')
        for b in self.list_rg_pkv:
            print(f'### DatenInterface.__update_list_rg_pkv: element: {b}')

        for rechnung in self.rechnungen:
            if not rechnung.pkv_id:
                self.list_rg_pkv.append(self.__row_from_rechnung(rechnung))
                print(f'### DatenInterface.__update_list_rg_pkv: Added rechnung with id {rechnung.db_id} to list rg pkv')
