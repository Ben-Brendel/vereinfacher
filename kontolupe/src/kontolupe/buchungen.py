"""Definition der Klassen der verschiedenen Buchungsarten."""

from pathlib import Path
import sqlite3 as sql
import os


class Datenbank:
    """Klasse zur Verwaltung der Datenbank."""

    def __init__(self):
        """Initialisierung der Datenbank."""
        self.db_path = Path('/data/data/net.biberwerk.kontolupe/kontolupe.db')
        #self.db_path = Path('C:/Users/Ben/code/vereinfacher/kontolupe/src/kontolupe/kontolupe.db')

        # lösche die Datei der Datenbank
        #self.db_path.unlink()

        # Dictionary mit den Tabellen und Spalten der Datenbank erstellen
        self.__tables = {
            'arztrechnungen': [
                ('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
                ('betrag', 'REAL'),
                ('arzt_id', 'INTEGER'),
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
            'aerzte': [
                ('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
                ('name', 'TEXT')
            ]
        }

        # Datenbank-Datei initialisieren
        self.__create_db()

    def __add_column_if_not_exists(cursor, table_name, new_column, column_type):
        cursor.execute(f"PRAGMA table_info({table_name})")
        if not any(row[1] == new_column for row in cursor.fetchall()):
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {new_column} {column_type}")

    def __create_db(self):
        """Erstellen und Update der Datenbank."""
        
        # Datenbankverbindung herstellen
        connection = sql.connect(self.db_path)
        cursor = connection.cursor()

        # create tables if they don't exist
        for table_name, columns in self.__tables.items():
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join([f'{column[0]} {column[1]}' for column in columns])})")

        # add columns if they don't exist
        for table_name, columns in self.__tables.items():
            for column in columns:
                Datenbank.__add_column_if_not_exists(cursor, table_name, column[0], column[1])
        
        # update the column 'arzt' to 'arzt_id' in the table 'arztrechnungen' if it exists
        # copy the values from the column 'arzt' to the column 'arzt_id' and drop it afterwards
        cursor.execute(f"PRAGMA table_info(arztrechnungen)")
        if any(row[1] == 'arzt' for row in cursor.fetchall()):
            cursor.execute(f"SELECT id, arzt FROM arztrechnungen")
            db_result = cursor.fetchall()
            for row in db_result:
                cursor.execute(f"UPDATE arztrechnungen SET arzt_id = ? WHERE id = ?", (row[1], row[0]))
            cursor.execute(f"ALTER TABLE arztrechnungen DROP COLUMN arzt")

        # validate all datum entries in the tables
        # check if they are in the format YYYY-MM-DD
        # and change them from the format YYYY-MM-DD to DD.MM.YYYY
        # for table_name, columns in self.__tables.items():
        #     for column in columns:
        #         if 'datum' in column[0]:
        #             cursor.execute(f"SELECT id, {column[0]} FROM {table_name}")
        #             db_result = cursor.fetchall()
        #             for row in db_result:
        #                 if row[1] is not None:
        #                     if len(row[1].split('-')) == 3:
        #                         datum = f"{row[1].split('-')[2]}.{row[1].split('-')[1]}.{row[1].split('-')[0]}"
        #                         cursor.execute(f"UPDATE {table_name} SET {column[0]} = ? WHERE id = ?", (datum, row[0]))

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
                case 'arztrechnungen':
                    element = Arztrechnung()
                case 'beihilfepakete':
                    element = BeihilfePaket()
                case 'pkvpakete':
                    element = PKVPaket()
                case 'aerzte':
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
        """Einfügen einer neuen Arztrechnung in die Datenbank."""
        return self.__new_element('arztrechnungen', rechnung)
    
    def neues_beihilfepaket(self, beihilfepaket):
        """Einfügen eines neuen Beihilfepakets in die Datenbank."""
        return self.__new_element('beihilfepakete', beihilfepaket)
    
    def neues_pkvpaket(self, pkvpaket):
        """Einfügen eines neuen PKV-Pakets in die Datenbank."""
        return self.__new_element('pkvpakete', pkvpaket)
    
    def neuer_arzt(self, arzt):
        """Einfügen eines neuen Arztes in die Datenbank."""
        return self.__new_element('aerzte', arzt)
    
    def aendere_rechnung(self, rechnung):
        """Ändern einer Arztrechnung in der Datenbank."""
        self.__change_element('arztrechnungen', rechnung)

    def aendere_beihilfepaket(self, beihilfepaket):
        """Ändern eines Beihilfepakets in der Datenbank."""
        self.__change_element('beihilfepakete', beihilfepaket)

    def aendere_pkvpaket(self, pkvpaket):
        """Ändern eines PKV-Pakets in der Datenbank."""
        self.__change_element('pkvpakete', pkvpaket)

    def aendere_arzt(self, arzt):
        """Ändern eines Arztes in der Datenbank."""
        self.__change_element('aerzte', arzt)

    def loesche_rechnung(self, rechnung):
        """Löschen einer Arztrechnung aus der Datenbank."""
        self.__delete_element('arztrechnungen', rechnung)

    def loesche_beihilfepaket(self, beihilfepaket):
        """Löschen eines Beihilfepakets aus der Datenbank."""
        self.__delete_element('beihilfepakete', beihilfepaket)

    def loesche_pkvpaket(self, pkvpaket):
        """Löschen eines PKV-Pakets aus der Datenbank."""
        self.__delete_element('pkvpakete', pkvpaket)

    def loesche_arzt(self, arzt):
        """Löschen eines Arztes aus der Datenbank."""
        self.__delete_element('aerzte', arzt)

    def lade_rechnungen(self):
        """Laden der Rechnungen aus der Datenbank."""
        return self.__load_data('arztrechnungen', only_active=True)
    
    def lade_beihilfepakete(self):
        """Laden der Beihilfepakete aus der Datenbank."""
        return self.__load_data('beihilfepakete', only_active=True)
    
    def lade_pkvpakete(self):
        """Laden der PKV-Pakete aus der Datenbank."""
        return self.__load_data('pkvpakete', only_active=True)
    
    def lade_aerzte(self):
        """Laden der Ärzte aus der Datenbank."""
        return self.__load_data('aerzte')


class Arztrechnung:
    """Klasse zur Erfassung einer Rechnung."""
    
    def __init__(self):
        """Initialisierung der Rechnung."""
        self.db_id = None
        self.betrag = 0
        self.rechnungsdatum = None
        self.arzt_id = None
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
    """Klasse zur Verwaltung der Ärzte."""
    
    def __init__(self):
        """Initialisierung des Arztes."""
        self.name = None
        self.db_id = None

    def neu(self, db):
        """Neuen Arzt erstellen."""
        self.db_id = db.neuer_arzt(self)

    def speichern(self, db):
        """Speichern des Arztes in der Datenbank."""
        db.aendere_arzt(self)

    def loeschen(self, db):
        """Löschen des Arztes aus der Datenbank."""
        db.loesche_arzt(self)

    def __str__(self):
        """Ausgabe des Arztes."""
        return (f"ID: {self.db_id}\n"
            f"Arzt: {self.name}")