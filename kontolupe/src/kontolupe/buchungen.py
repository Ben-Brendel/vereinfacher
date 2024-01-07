"""Definition der Klassen der verschiedenen Buchungsarten."""

from pathlib import Path
import sqlite3 as sql
import shutil
from datetime import datetime


class Datenbank:
    """Klasse zur Verwaltung der Datenbank."""

    def __init__(self):
        """Initialisierung der Datenbank."""
        self.db_dir = Path('/data/data/net.biberwerk.kontolupe')
        #self.db_dir = Path('C:/Users/Ben/code/vereinfacher/kontolupe/src/kontolupe')
        
        self.db_path = self.db_dir / 'kontolupe.db'

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
                ('beihilfesatz', 'REAL'),
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
                ('name', 'TEXT')
            ]
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
        # Die Tabellen werden schrittweise von einer alten Tabellenversion auf die neueste Tabellenversion migriert.
        self.__tables_rename = [
            ('arztrechnungen', 'rechnungen'),
            ('aerzte', 'einrichtungen')
        ]

        # Datenbank-Datei initialisieren
        self.__create_db()

    def __get_column_type(self, table_name, column_name):
        for column in self.__tables[table_name]:
            if column[0] == column_name:
                return column[1]
        return None  # return None if the column is not found

    def __new_table_name(self, old_table):
        """returns the new table name for the old_table"""
        new_table = self.__new_table_name_iter(old_table)
        while new_table != old_table:
            next_table = self.__new_table_name_iter(new_table)
            if next_table == new_table:
                break
            new_table = next_table
        return new_table
    
    def __new_table_name_iter(self, old_table):
        """returns the new table name for the old_table"""
        for table in self.__tables_rename:
            if table[0] == old_table:
                return table[1]
        return old_table

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
            if not any(row[1] == new_column for row in result):
                cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {new_column} {self.__get_column_type(self.__new_table_name(table_name), new_column)}")

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

        # Backup erstellen
        # check if database exists and is structured correctly
        # if not create a backup
        if self.db_path.exists():
            # Datenbankverbindung herstellen
            connection = sql.connect(self.db_path)
            cursor = connection.cursor()

            # check if database is structured correctly
            is_correct = True
            for table_name, columns in self.__tables.items():
                cursor.execute(f"PRAGMA table_info({table_name})")
                result = cursor.fetchall()
                for column in columns:
                    if not any(row[1] == column[0] for row in result):
                        # database is not structured correctly
                        # create a backup and exit the loop
                        is_correct = False
                        self.__create_backup()
                        break
                if not is_correct:
                    break

            # Datenbankverbindung schließen
            connection.close()
        
        # Datenbankverbindung herstellen
        connection = sql.connect(self.db_path)
        cursor = connection.cursor()

        if not self.db_path.exists() or not is_correct:

            # Update-Routine zur Aktualisierung der Datenbankstruktur
            for table_name, columns in self.__tables.items():
                Datenbank.__create_table_if_not_exists(self, cursor, table_name, columns)
                for column in columns:
                    Datenbank.__add_column_if_not_exists(self, cursor, table_name, column[0], column[1])
            
            # Update-Routine zur Migration der Daten in die neue Datenbankstruktur
            for table_name, columns in self.__table_columns_rename.items():
                for column in columns:
                    Datenbank.__copy_column(self, cursor, table_name, column[0], column[1])

            # Update-Routine zur Umbenennung der Tabellen
            for table in self.__tables_rename:
                Datenbank.__copy_table_and_delete(self, cursor, table[0], self.__new_table_name(table[0]))            

        # Datenbankverbindung schließen
        connection.commit()
        connection.close()

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
                    element = Arztrechnung()
                case 'beihilfepakete':
                    element = BeihilfePaket()
                case 'pkvpakete':
                    element = PKVPaket()
                case 'einrichtungen':
                    element = Arzt()

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
        return self.__load_data('einrichtungen')


class Arztrechnung:
    """Klasse zur Erfassung einer Rechnung."""
    
    def __init__(self):
        """Initialisierung der Rechnung."""
        self.db_id = None
        self.betrag = 0
        self.rechnungsdatum = None
        self.einrichtung_id = None
        self.notiz = None
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
        ausgabe = 'Rechnung vom {}\n'.format(self.rechnungsdatum)
        ausgabe += 'Betrag: {:.2f} €\n'.format(self.betrag).replace('.', ',')
        ausgabe += 'Beihilfesatz: {:.0f} %\n'.format(self.beihilfesatz)
        ausgabe += 'Einrichtung: {}\n'.format(self.arzt_id)
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
            # Beihilfe-Einreichung mit Arztrechnungen verknüpfen
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
            # PKV-Einreichung mit Arztrechnungen verknüpfen
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


class Arzt:
    """Klasse zur Verwaltung der Einrichtungen."""
    
    def __init__(self):
        """Initialisierung der Einrichtung."""
        self.name = None
        self.db_id = None

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
        return (f"ID: {self.db_id}\n"
            f"Arzt: {self.name}")