"""Definition der Klassen der verschiedenen Buchungsarten."""

import sqlite3 as sql
import shutil
from pathlib import Path
from datetime import datetime
from toga.sources import ListSource


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
        print(self.db_path)

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

        # Datenbank-Datei initialisieren
        self.__create_db()

    def __get_column_type(self, table_name, column_name):
        for column in self.__tables[table_name]:
            if column[0] == column_name:
                return column[1]
        return None  # return None if the column is not found

    def __create_backup(self):
        """Erstellen eines Backups der Datenbank."""
        # Get the current date and time, formatted as a string
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create the backup path with the timestamp
        backup_path = self.db_dir / Path(f'kontolupe_{timestamp}.db.backup')
        if backup_path.exists():
            backup_path.unlink()
        if self.db_path.exists():
            shutil.copy2(self.db_path, backup_path)
            print(f'Created backup {backup_path}')

    def __delete_backups(self):
        """Löschen aller Backups der Datenbank."""
        for file in self.db_dir.glob('kontolupe_*.db.backup'):
            print(f'Deleting backup {file}')
            file.unlink()

    def __create_table_if_not_exists(self, cursor, table_name, columns):
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join([f'{column[0]} {column[1]}' for column in columns])})")

    def __add_column_if_not_exists(self, cursor, table_name, new_column, column_type):
        cursor.execute(f"PRAGMA table_info({table_name})")
        if not any(row[1] == new_column for row in cursor.fetchall()):
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {new_column} {column_type}")
        if new_column == 'aktiv':
            cursor.execute(f"UPDATE {table_name} SET aktiv = 1")

    def __copy_column(self, cursor, table_name, old_column, new_column):
        # Check if table_name exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if not cursor.fetchone():
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

    def __copy_table_and_delete(self, cursor, old_table, new_table):
        # Check if old_table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (old_table,))
        if not cursor.fetchone():
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

        # Drop old_table
        cursor.execute(f"DROP TABLE {old_table}")

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
            return False

        with sql.connect(self.db_path) as connection:
            cursor = connection.cursor()
            for table_name, columns in self.__tables.items():
                if not self.__table_is_correct(cursor, table_name, columns):
                    return False

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
            

    def __migrate_data(self, cursor):
        """Migrate the data to the new database structure."""

        for table_name, columns in self.__table_columns_rename.items():
            for column in columns:
                Datenbank.__copy_column(self, cursor, table_name, column[0], column[1])

    def __rename_tables(self, cursor):
        """Rename the tables."""

        for old_table, new_table in self.__tables_rename.items():
            Datenbank.__copy_table_and_delete(self, cursor, old_table, new_table)


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

    def __load_data(self, table, only_active=False):
        """Laden der Elemente einer Tabelle aus der Datenbank."""
        # Datenbankverbindung herstellen
        connection = sql.connect(self.db_path)
        cursor = connection.cursor()

        # Daten abfragen
        query = f"""SELECT * FROM {table}"""
        if only_active:
            query += f""" WHERE aktiv = 1"""
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

            # Setze die Attribute des Elements
            for column in self.__tables[table]:
                if column[0] in row:
                    if column[0] == 'id':
                        setattr(element, 'db_id', row[column[0]])
                    else:
                        setattr(element, column[0], row[column[0]])

            result.append(element)

        # Datenbankverbindung schließen
        connection.close()

        return result

    def neue_rechnung(self, rechnung):
        """Einfügen einer neuen Rechnung in die Datenbank."""
        return self.__new_element('rechnungen', rechnung)
    
    def neues_beihilfepaket(self, beihilfepaket):
        """Einfügen eines neuen Beihilfepakets in die Datenbank."""
        return self.__new_element('beihilfepakete', beihilfepaket)
    
    def neues_pkvpaket(self, pkvpaket):
        """Einfügen eines neuen PKV-Pakets in die Datenbank."""
        return self.__new_element('pkvpakete', pkvpaket)
    
    def neue_einrichtung(self, einrichtung):
        """Einfügen einer neuen Einrichtung in die Datenbank."""
        return self.__new_element('einrichtungen', einrichtung)
    
    def neue_person(self, person):
        """Einfügen einer neuen Person in die Datenbank."""
        return self.__new_element('personen', person)
    
    def aendere_rechnung(self, rechnung):
        """Ändern einer Rechnung in der Datenbank."""
        self.__change_element('rechnungen', rechnung)

    def aendere_beihilfepaket(self, beihilfepaket):
        """Ändern eines Beihilfepakets in der Datenbank."""
        self.__change_element('beihilfepakete', beihilfepaket)

    def aendere_pkvpaket(self, pkvpaket):
        """Ändern eines PKV-Pakets in der Datenbank."""
        self.__change_element('pkvpakete', pkvpaket)

    def aendere_einrichtung(self, einrichtung):
        """Ändern einer Einrichtung in der Datenbank."""
        self.__change_element('einrichtungen', einrichtung)

    def aendere_person(self, person):
        """Ändern einer Person in der Datenbank."""
        self.__change_element('personen', person)

    def loesche_rechnung(self, rechnung):
        """Löschen einer Rechnung aus der Datenbank."""
        self.__delete_element('rechnungen', rechnung)

    def loesche_beihilfepaket(self, beihilfepaket):
        """Löschen eines Beihilfepakets aus der Datenbank."""
        self.__delete_element('beihilfepakete', beihilfepaket)

    def loesche_pkvpaket(self, pkvpaket):
        """Löschen eines PKV-Pakets aus der Datenbank."""
        self.__delete_element('pkvpakete', pkvpaket)

    def loesche_einrichtung(self, einrichtung):
        """Löschen einer Einrichtung aus der Datenbank."""
        self.__delete_element('einrichtungen', einrichtung)

    def loesche_person(self, person):
        """Löschen einer Person aus der Datenbank."""
        self.__delete_element('personen', person)

    def lade_rechnungen(self):
        """Laden der Rechnungen aus der Datenbank."""
        return self.__load_data('rechnungen', only_active=True)
    
    def lade_beihilfepakete(self):
        """Laden der Beihilfepakete aus der Datenbank."""
        return self.__load_data('beihilfepakete', only_active=True)
    
    def lade_pkvpakete(self):
        """Laden der PKV-Pakete aus der Datenbank."""
        return self.__load_data('pkvpakete', only_active=True)
    
    def lade_einrichtungen(self):
        """Laden der Einrichtungen aus der Datenbank."""
        return self.__load_data('einrichtungen', only_active=True)
    
    def lade_personen(self):
        """Laden der Personen aus der Datenbank."""
        return self.__load_data('personen', only_active=True)


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
        
        # Datenbank initialisieren
        self.db = Datenbank()

        # Aktive Einträge aus der Datenbank laden
        self.rechnungen = self.db.lade_rechnungen()
        self.beihilfepakete = self.db.lade_beihilfepakete()
        self.pkvpakete = self.db.lade_pkvpakete()
        self.einrichtungen = self.db.lade_einrichtungen()
        self.personen = self.db.lade_personen()

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

        for einrichtung in self.einrichtungen:            
            self.__list_einrichtungen_append(einrichtung)

        for person in self.personen:            
            self.__list_personen_append(person)

        for beihilfepaket in self.beihilfepakete:            
            self.__list_beihilfepakete_append(beihilfepaket)

        for pkvpaket in self.pkvpakete:            
            self.__list_pkvpakete_append(pkvpaket)

        self.__list_open_bookings_update()


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

        return sum
    

    def get_rechnung_by_dbid(self, id, objekt=False):
        """Gibt eine Rechnung anhand der ID zurück."""
        rechnungen = self.rechnungen if objekt else self.list_rechnungen

        for rechnung in rechnungen:
            if rechnung['db_id'] == id:
                return rechnung

        return None
    

    def get_beihilfepaket_by_dbid(self, id, objekt=False):
        """Gibt ein Beihilfepaket anhand der ID zurück."""
        beihilfepakete = self.beihilfepakete if objekt else self.list_beihilfepakete

        for beihilfepaket in beihilfepakete:
            if beihilfepaket.db_id == id:
                return beihilfepaket
            
        return None
    

    def get_pkvpaket_by_dbid(self, id, objekt=False):
        """Gibt ein PKV-Paket anhand der ID zurück."""
        pkvpakete = self.pkvpakete if objekt else self.list_pkvpakete

        for pkvpaket in pkvpakete:
            if pkvpaket.db_id == id:
                return pkvpaket
            
        return None
    

    def get_einrichtung_by_dbid(self, id, objekt=False):
        """Gibt eine Einrichtung anhand der ID zurück."""
        einrichtungen = self.einrichtungen if objekt else self.list_einrichtungen

        for einrichtung in einrichtungen:
            if einrichtung.db_id == id:
                return einrichtung
            
        return None
    

    def get_person_by_dbid(self, id, objekt=False):
        """Gibt eine Person anhand der ID zurück."""
        personen = self.personen if objekt else self.list_personen

        for person in personen:
            if person.db_id == id:
                return person
            
        return None
    

    def get_rechnung_by_index(self, index, objekt=False):
        """Gibt eine Rechnung anhand des Index zurück."""
        rechnungen = self.rechnungen if objekt else self.list_rechnungen

        return rechnungen[index]
    

    def get_beihilfepaket_by_index(self, index, objekt=False):
        """Gibt ein Beihilfepaket anhand des Index zurück."""
        beihilfepakete = self.beihilfepakete if objekt else self.list_beihilfepakete

        return beihilfepakete[index]
    

    def get_pkvpaket_by_index(self, index, objekt=False):
        """Gibt ein PKV-Paket anhand des Index zurück."""
        pkvpakete = self.pkvpakete if objekt else self.list_pkvpakete

        return pkvpakete[index]
    

    def get_einrichtung_by_index(self, index, objekt=False):
        """Gibt eine Einrichtung anhand des Index zurück."""
        einrichtungen = self.einrichtungen if objekt else self.list_einrichtungen

        return einrichtungen[index]
    

    def get_person_by_index(self, index, objekt=False):
        """Gibt eine Person anhand des Index zurück."""
        personen = self.personen if objekt else self.list_personen

        return personen[index]
    

    def get_beihilfesatz_by_name(self, name):
        """Gibt den Beihilfesatz einer Person anhand des Namens zurück."""
        for person in self.personen:
            if person.name == name:
                return person.beihilfesatz
        
        return None
    

    def get_rechnung_index_by_dbid(self, dbid):
        """Gibt den Index einer Rechnung anhand der ID zurück."""
        return self.__get_list_index_by_dbid(self.list_rechnungen, dbid)
    

    def get_einrichtung_index_by_dbid(self, dbid):
        """Gibt den Index einer Einrichtung anhand der ID zurück."""
        return self.__get_list_index_by_dbid(self.list_einrichtungen, dbid)
    

    def get_person_index_by_dbid(self, dbid):
        """Gibt den Index einer Person anhand der ID zurück."""
        return self.__get_list_index_by_dbid(self.list_personen, dbid)
    

    def new_rechnung(self, rechnung):
        """Neue Rechnung erstellen."""
        rechnung.neu(self.db)
        self.rechnungen.append(rechnung)
        self.__list_rechnungen_append(rechnung)
        self.__list_open_bookings_update()


    def edit_rechnung(self, rechnung, rg_id):
        """Rechnung ändern."""
        self.rechnungen[rg_id] = rechnung
        self.__list_rechnungen_update_id(rechnung, rg_id)
        self.__list_open_bookings_update()

    def beihilfepaket_aktualisieren(self, widget, result):
        """Aktualisiert die Beihilfe-Einreichung einer Rechnung."""
        if result:
            # Finde die Beihilfe-Einreichung
            for beihilfepaket in self.beihilfepakete:
                if beihilfepaket.db_id == self.rechnungen[self.edit_bill_id].beihilfe_id:
                    # Alle Rechnungen durchlaufen und den Betrag aktualisieren
                    beihilfepaket.betrag = 0
                    for rechnung in self.rechnungen:
                        if rechnung.beihilfe_id == beihilfepaket.db_id:
                            beihilfepaket.betrag += rechnung.betrag * (rechnung.beihilfesatz / 100)
                    # Die Beihilfe-Einreichung speichern
                    beihilfepaket.speichern(self.db)
                    self.beihilfepakete_liste_aendern(beihilfepaket, self.beihilfepakete.index(beihilfepaket))
                    break
            

    def pkvpaket_aktualisieren(self, widget, result):
        """Aktualisiert die PKV-Einreichung einer Rechnung."""
        if result:
            # Finde die PKV-Einreichung
            for pkvpaket in self.pkvpakete:
                if pkvpaket.db_id == self.rechnungen[self.edit_bill_id].pkv_id:
                    # ALle Rechnungen durchlaufen und den Betrag aktualisieren
                    pkvpaket.betrag = 0
                    for rechnung in self.rechnungen:
                        if rechnung.pkv_id == pkvpaket.db_id:
                            pkvpaket.betrag += rechnung.betrag * (1 - (rechnung.beihilfesatz / 100))
                    # Die PKV-Einreichung speichern
                    pkvpaket.speichern(self.db)
                    self.pkvpakete_liste_aendern(pkvpaket, self.pkvpakete.index(pkvpaket))
                    break
    

    def __get_list_index_by_dbid(self, liste, dbid):
        """Ermittelt den Index eines Elements einer Liste anhand der ID."""
        for i, element in enumerate(liste):
            if element.db_id == dbid:
                return i
        else:
            print("Element mit der ID {} konnte nicht gefunden werden.".format(id))
            return None


    def __person_name(self, person_id):
        """Gibt den Namen einer Person zurück."""
        for person in self.personen:
            if person.db_id == person_id:
                return person.name
        return None
    

    def __einrichtung_name(self, einrichtung_id):
        """Gibt den Namen einer Einrichtung zurück."""
        for einrichtung in self.einrichtungen:
            if einrichtung.db_id == einrichtung_id:
                return einrichtung.name
        return None


    def __list_rechnungen_append(self, rechnung):
        """Fügt der Liste der Rechnungen eine neue Rechnung hinzu."""
        self.list_rechnungen.append({
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
            })
        

    def __list_rechnungen_update_id(self, rechnung, rg_id):
        """Ändert ein Element der Liste der Rechnungen."""
        self.list_rechnungen[rg_id] = {
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
        

    def __update_rechnungen(self):
        """Aktualisiert die referenzierten Werte in den Rechnungen und speichert sie in der Datenbank."""

        for rechnung in self.rechnungen:

            # Aktualisiere die Beihilfe
            if rechnung.beihilfe_id:
                # Überprüfe ob die Beihilfe noch existiert
                beihilfepaket_vorhanden = False
                for beihilfepaket in self.beihilfepakete:
                    if beihilfepaket.db_id == rechnung.beihilfe_id:
                        beihilfepaket_vorhanden = True
                        break
                
                # Wenn die Beihilfe nicht mehr existiert, setze die Beihilfe zurück
                if not beihilfepaket_vorhanden:
                    rechnung.beihilfe_id = None

            # Aktualisiere die PKV
            if rechnung.pkv_id:
                # Überprüfe ob die PKV noch existiert
                pkvpaket_vorhanden = False
                for pkvpaket in self.pkvpakete:
                    if pkvpaket.db_id == rechnung.pkv_id:
                        pkvpaket_vorhanden = True
                        break
                
                # Wenn die PKV nicht mehr existiert, setze die PKV zurück
                if not pkvpaket_vorhanden:
                    rechnung.pkv_id = None

            # Aktualisiere die Einrichtung
            if rechnung.einrichtung_id:
                # Überprüfe ob die Einrichtung noch existiert
                einrichtung_vorhanden = False
                for einrichtung in self.einrichtungen:
                    if einrichtung.db_id == rechnung.einrichtung_id:
                        einrichtung_vorhanden = True
                        break
                
                # Wenn die Einrichtung nicht mehr existiert, setze die Einrichtung zurück
                if not einrichtung_vorhanden:
                    rechnung.einrichtung_id = None

            # Aktualisiere die Person
            if rechnung.person_id:
                # Überprüfe ob die Person noch existiert
                person_vorhanden = False
                for person in self.personen:
                    if person.db_id == rechnung.person_id:
                        person_vorhanden = True
                        break
                
                # Wenn die Person nicht mehr existiert, setze die Person zurück
                if not person_vorhanden:
                    rechnung.person_id = None
            
            # Aktualisierte Rechnung speichern
            rechnung.speichern(self.db)

        # Aktualisiere die Liste der Rechnungen
        self.__list_rechnungen_update()


    def __list_rechnungen_update(self):
        """Aktualisiert die referenzierten Werte in der Liste der Rechnungen."""
        for rg_id in range(len(self.list_rechnungen)):
            self.__list_rechnungen_update_id(self.rechnungen[rg_id], rg_id)


    def __list_einrichtungen_append(self, einrichtung):
        """Fügt der Liste der Einrichtungen eine neue Einrichtung hinzu."""
        self.einrichtungen_liste.append({
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
            })
        

    def __list_einrichtungen_update_id(self, einrichtung, einrichtung_id):
        """Ändert ein Element der Liste der Einrichtungen."""
        self.einrichtungen_liste[einrichtung_id] = {
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

    
    def __list_personen_append(self, person):
        """Fügt der Liste der Personen eine neue Person hinzu."""
        self.personen_liste.append({
                'db_id': person.db_id,
                'name': person.name or '',
                'beihilfesatz': person.beihilfesatz or '',
                'beihilfesatz_prozent': '{:.0f} %'.format(person.beihilfesatz) if person.beihilfesatz else '0 %'
            })
        

    def __list_personen_update_id(self, person, person_id):    
        """Ändert ein Element der Liste der Personen."""
        self.personen_liste[person_id] = {
                'db_id': person.db_id,
                'name': person.name or '',
                'beihilfesatz': person.beihilfesatz or None,
                'beihilfesatz_prozent': '{:.0f} %'.format(person.beihilfesatz) if person.beihilfesatz else '0 %'
            }

    
    def __list_beihilfepakete_update(self):
        """Aktualisiert die Liste der Beihilfepakete."""
        for beihilfepaket_id in range(len(self.list_beihilfepakete)):
            self.__list_beihilfepakete_update_id(self.beihilfepakete[beihilfepaket_id], beihilfepaket_id)


    def __list_beihilfepakete_append(self, beihilfepaket):
        """Fügt der Liste der Beihilfepakete ein neues Beihilfepaket hinzu."""
        self.list_beihilfepakete.append({
                'db_id': beihilfepaket.db_id,
                'betrag': beihilfepaket.betrag,
                'betrag_euro': '{:.2f} €'.format(beihilfepaket.betrag).replace('.', ','),
                'datum': beihilfepaket.datum,
                'erhalten': beihilfepaket.erhalten,
                'erhalten_text': 'Ja' if beihilfepaket.erhalten else 'Nein'
            })

    
    def __list_beihilfepakete_update_id(self, beihilfepaket, beihilfepaket_id):
        """Ändert ein Element der Liste der Beihilfepakete."""
        self.list_beihilfepakete[beihilfepaket_id] = {
                'db_id': beihilfepaket.db_id,
                'betrag': beihilfepaket.betrag,
                'betrag_euro': '{:.2f} €'.format(beihilfepaket.betrag).replace('.', ','),
                'datum': beihilfepaket.datum,
                'erhalten': beihilfepaket.erhalten,
                'erhalten_text': 'Ja' if beihilfepaket.erhalten else 'Nein'
            }
        

    def __list_pkvpakete_update(self):
        """Aktualisiert die Liste der PKV-Pakete."""
        for pkvpaket_id in range(len(self.list_pkvpakete)):
            self.__list_pkvpakete_update_id(self.pkvpakete[pkvpaket_id], pkvpaket_id)
        

    def __list_pkvpakete_append(self, pkvpaket):
        """Fügt der Liste der PKV-Pakete ein neues PKV-Paket hinzu."""
        self.list_pkvpakete.append({
                'db_id': pkvpaket.db_id,
                'betrag': pkvpaket.betrag,
                'betrag_euro': '{:.2f} €'.format(pkvpaket.betrag).replace('.', ','),
                'datum': pkvpaket.datum,
                'erhalten': pkvpaket.erhalten,
                'erhalten_text': 'Ja' if pkvpaket.erhalten else 'Nein'
            })
        

    def __list_pkvpakete_update_id(self, pkvpaket, pkvpaket_id):
        """Ändert ein Element der Liste der PKV-Pakete."""
        self.list_pkvpakete[pkvpaket_id] = {
                'db_id': pkvpaket.db_id,
                'betrag': pkvpaket.betrag,
                'betrag_euro': '{:.2f} €'.format(pkvpaket.betrag).replace('.', ','),
                'datum': pkvpaket.datum,
                'erhalten': pkvpaket.erhalten,
                'erhalten_text': 'Ja' if pkvpaket.erhalten else 'Nein'
            }
        

    def __list_open_bookings_update(self):
        """Aktualisiert die Liste der offenen Buchungen."""

        self.list_open_bookings.clear()

        for rechnung in self.rechnungen_liste:
            if not rechnung.bezahlt:
                self.list_open_bookings.append({
                    'db_id': rechnung.db_id,
                    'typ': 'Rechnung',
                    'betrag_euro': '-{:.2f} €'.format(rechnung.betrag).replace('.', ','),
                    'datum': rechnung.buchungsdatum,
                    'info': rechnung.info
                })
    
        for beihilfepaket in self.beihilfepakete:
            if not beihilfepaket.erhalten:
                self.list_open_bookings.append({
                    'db_id': beihilfepaket.db_id,
                    'typ': 'Beihilfe',
                    'betrag_euro': '+{:.2f} €'.format(beihilfepaket.betrag).replace('.', ','),
                    'datum': beihilfepaket.datum,
                    'info': 'Beihilfe-Einreichung'
                })

        for pkvpaket in self.pkvpakete:
            if not pkvpaket.erhalten:
                self.list_open_bookings.append({
                    'db_id': pkvpaket.db_id,
                    'typ': 'PKV',
                    'betrag_euro': '+{:.2f} €'.format(pkvpaket.betrag).replace('.', ','),
                    'datum': pkvpaket.datum,
                    'info': 'PKV-Einreichung'
                })