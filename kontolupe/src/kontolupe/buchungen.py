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
        self.tables = {
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

        # Datenbank erstellen
        self.create_db()

    def __add_column_if_not_exists(cursor, table_name, new_column, column_type):
        cursor.execute(f"PRAGMA table_info({table_name})")
        if not any(row[1] == new_column for row in cursor.fetchall()):
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {new_column} {column_type}")

    def create_db(self):
        """Erstellen und Update der Datenbank."""
        
        # Datenbankverbindung herstellen
        connection = sql.connect(self.db_path)
        cursor = connection.cursor()

        # create tables if they don't exist
        for table_name, columns in self.tables.items():
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join([f'{column[0]} {column[1]}' for column in columns])})")

        # add columns if they don't exist
        for table_name, columns in self.tables.items():
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
        # for table_name, columns in self.tables.items():
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

    def neue_rechnung(self, rechnung):
        """Einfügen einer neuen Arztrechnung in die Datenbank."""
        # Datenbankverbindung herstellen
        connection = sql.connect(self.db_path)
        cursor = connection.cursor()

        # Get the table columns from self.tables
        columns = self.tables['arztrechnungen']

        # Extract the column names
        column_names = [column[0] for column in columns]

        # drop the column 'id' from the list and do not assume that it is the first column
        column_names.remove('id')

        # Build the SQL query dynamically
        query = f"""INSERT INTO arztrechnungen ({', '.join(column_names)}) VALUES ({', '.join(['?' for _ in column_names])})"""

        # Build the values tuple dynamically
        values = tuple(getattr(rechnung, column_name) for column_name in column_names)

        # Daten einfügen
        cursor.execute(query, values)

        # id der neuen Buchung abfragen
        db_id = cursor.lastrowid

        # Datenbankverbindung schließen
        connection.commit()
        connection.close()

        return db_id
    
    def neues_beihilfepaket(self, beihilfepaket):
        """Einfügen eines neuen Beihilfepakets in die Datenbank."""
        # Datenbankverbindung herstellen
        connection = sql.connect(self.db_path)
        cursor = connection.cursor()

        # Daten einfügen
        cursor.execute("""INSERT INTO beihilfepakete (
            betrag,
            datum,
            aktiv,
            erhalten
        ) VALUES (?, ?, ?, ?)""", (
            beihilfepaket.betrag,
            beihilfepaket.datum,
            beihilfepaket.aktiv,
            beihilfepaket.erhalten
        ))

        # id der neuen Buchung abfragen
        db_id = cursor.lastrowid

        # Datenbankverbindung schließen
        connection.commit()
        connection.close()

        return db_id
    
    def neues_pkvpaket(self, pkvpaket):
        """Einfügen eines neuen PKV-Pakets in die Datenbank."""
        # Datenbankverbindung herstellen
        connection = sql.connect(self.db_path)
        cursor = connection.cursor()

        # Daten einfügen
        cursor.execute("""INSERT INTO pkvpakete (
            betrag,
            datum,
            aktiv,
            erhalten
        ) VALUES (?, ?, ?, ?)""", (
            pkvpaket.betrag,
            pkvpaket.datum,
            pkvpaket.aktiv,
            pkvpaket.erhalten
        ))

        # id der neuen Buchung abfragen
        db_id = cursor.lastrowid

        # Datenbankverbindung schließen
        connection.commit()
        connection.close()

        return db_id
    
    def neuer_arzt(self, arzt):
        """Einfügen eines neuen Arztes in die Datenbank."""
        # Datenbankverbindung herstellen
        connection = sql.connect(self.db_path)
        cursor = connection.cursor()

        # Daten einfügen
        cursor.execute("""INSERT INTO aerzte (
            name
        ) VALUES (?)""", (
            arzt.name,
        ))

        # id der neuen Buchung abfragen
        db_id = cursor.lastrowid

        # Datenbankverbindung schließen
        connection.commit()
        connection.close()

        return db_id
    
    def aendere_rechnung(self, rechnung):
        """Ändern einer Arztrechnung in der Datenbank."""
        # Datenbankverbindung herstellen
        connection = sql.connect(self.db_path)
        cursor = connection.cursor()

        # Daten ändern
        cursor.execute("""UPDATE arztrechnungen SET
            betrag = ?,
            arzt = ?,
            rechnungsdatum = ?,
            notiz = ?,
            beihilfesatz = ?,
            buchungsdatum = ?,
            aktiv = ?,
            bezahlt = ?,
            beihilfe_id = ?,
            pkv_id = ?
        WHERE id = ?""", (
            rechnung.betrag,
            rechnung.arzt_id,
            rechnung.rechnungsdatum,
            rechnung.notiz,
            rechnung.beihilfesatz,
            rechnung.buchungsdatum,
            rechnung.aktiv,
            rechnung.bezahlt,
            rechnung.beihilfe_id,
            rechnung.pkv_id,
            rechnung.db_id
        ))

        # Datenbankverbindung schließen
        connection.commit()
        connection.close() 

    def aendere_beihilfepaket(self, beihilfepaket):
        """Ändern eines Beihilfepakets in der Datenbank."""
        # Datenbankverbindung herstellen
        connection = sql.connect(self.db_path)
        cursor = connection.cursor()

        # Daten ändern
        cursor.execute("""UPDATE beihilfepakete SET
            betrag = ?,
            datum = ?,
            aktiv = ?,
            erhalten = ?
        WHERE id = ?""", (
            beihilfepaket.betrag,
            beihilfepaket.datum,
            beihilfepaket.aktiv,
            beihilfepaket.erhalten,
            beihilfepaket.db_id
        ))

        # Datenbankverbindung schließen
        connection.commit()
        connection.close()

    def aendere_pkvpaket(self, pkvpaket):
        """Ändern eines PKV-Pakets in der Datenbank."""
        # Datenbankverbindung herstellen
        connection = sql.connect(self.db_path)
        cursor = connection.cursor()

        # Daten ändern
        cursor.execute("""UPDATE pkvpakete SET
            betrag = ?,
            datum = ?,
            aktiv = ?,
            erhalten = ?
        WHERE id = ?""", (
            pkvpaket.betrag,
            pkvpaket.datum,
            pkvpaket.aktiv,
            pkvpaket.erhalten,
            pkvpaket.db_id
        ))

        # Datenbankverbindung schließen
        connection.commit()
        connection.close()

    def aendere_arzt(self, arzt):
        """Ändern eines Arztes in der Datenbank."""
        # Datenbankverbindung herstellen
        connection = sql.connect(self.db_path)
        cursor = connection.cursor()

        # Daten ändern
        cursor.execute("""UPDATE aerzte SET
            name = ?
        WHERE id = ?""", (
            arzt.name,
            arzt.db_id
        ))

        # Datenbankverbindung schließen
        connection.commit()
        connection.close()

    def loesche_rechnung(self, rechnung):
        """Löschen einer Arztrechnung aus der Datenbank."""
        # Datenbankverbindung herstellen
        connection = sql.connect(self.db_path)
        cursor = connection.cursor()

        # Daten löschen
        cursor.execute("""DELETE FROM arztrechnungen WHERE id = ?""", (
            rechnung.db_id,
        ))

        # Datenbankverbindung schließen
        connection.commit()
        connection.close()

    def loesche_beihilfepaket(self, beihilfepaket):
        """Löschen eines Beihilfepakets aus der Datenbank."""
        # Datenbankverbindung herstellen
        connection = sql.connect(self.db_path)
        cursor = connection.cursor()

        # Daten löschen
        cursor.execute("""DELETE FROM beihilfepakete WHERE id = ?""", (
            beihilfepaket.db_id,
        ))

        # Datenbankverbindung schließen
        connection.commit()
        connection.close()

    def loesche_pkvpaket(self, pkvpaket):
        """Löschen eines PKV-Pakets aus der Datenbank."""
        # Datenbankverbindung herstellen
        connection = sql.connect(self.db_path)
        cursor = connection.cursor()

        # Daten löschen
        cursor.execute("""DELETE FROM pkvpakete WHERE id = ?""", (
            pkvpaket.db_id,
        ))

        # Datenbankverbindung schließen
        connection.commit()
        connection.close()

    def loesche_arzt(self, arzt):
        """Löschen eines Arztes aus der Datenbank."""
        # Datenbankverbindung herstellen
        connection = sql.connect(self.db_path)
        cursor = connection.cursor()

        # Daten löschen
        cursor.execute("""DELETE FROM aerzte WHERE id = ?""", (
            arzt.db_id,
        ))

        # Datenbankverbindung schließen
        connection.commit()
        connection.close()

    def lade_rechnungen(self):
        """Laden der Arztrechnungen aus der Datenbank."""
        # Datenbankverbindung herstellen
        connection = sql.connect(self.db_path)
        cursor = connection.cursor()

        # Daten abfragen
        cursor.execute("""SELECT * FROM arztrechnungen WHERE aktiv = 1""")
        db_result = cursor.fetchall()

        # Speichere die Daten in einem Dictionary
        ergebnis = [dict(zip([column[0] for column in cursor.description], row)) for row in db_result]

        rechnungen = []
        for row in ergebnis:
            rechnung = Arztrechnung()
            rechnung.db_id = row['id']
            rechnung.betrag = row['betrag']
            rechnung.arzt_id = row['arzt_id']
            rechnung.rechnungsdatum = row['rechnungsdatum']
            rechnung.notiz = row['notiz']
            rechnung.beihilfesatz = row['beihilfesatz']
            rechnung.buchungsdatum = row['buchungsdatum']
            rechnung.aktiv = row['aktiv']
            rechnung.bezahlt = row['bezahlt']
            rechnung.beihilfe_id = row['beihilfe_id']
            rechnung.pkv_id = row['pkv_id']
            rechnungen.append(rechnung)

        # Datenbankverbindung schließen
        connection.close()

        return rechnungen
    
    def lade_beihilfepakete(self):
        """Laden der Beihilfepakete aus der Datenbank."""
        # Datenbankverbindung herstellen
        connection = sql.connect(self.db_path)
        cursor = connection.cursor()

        # Daten abfragen
        cursor.execute("""SELECT * FROM beihilfepakete WHERE aktiv = 1""")
        db_result = cursor.fetchall()

        # Speichere die Daten in einem Dictionary
        ergebnis = [dict(zip([column[0] for column in cursor.description], row)) for row in db_result]

        # beihilfepakete in BeihilfePaket-Objekte umwandeln
        beihilfepakete = []
        for row in ergebnis:
            beihilfepaket = BeihilfePaket()
            beihilfepaket.db_id = row['id']
            beihilfepaket.betrag = row['betrag']
            beihilfepaket.datum = row['datum']
            beihilfepaket.aktiv = row['aktiv']
            beihilfepaket.erhalten = row['erhalten']
            beihilfepakete.append(beihilfepaket)

        # Datenbankverbindung schließen
        connection.close()

        return beihilfepakete
    
    def lade_pkvpakete(self):
        """Laden der PKV-Pakete aus der Datenbank."""
        # Datenbankverbindung herstellen
        connection = sql.connect(self.db_path)
        cursor = connection.cursor()

        # Daten abfragen
        cursor.execute("""SELECT * FROM pkvpakete WHERE aktiv = 1""")
        db_result = cursor.fetchall()

        # Speichere die Daten in einem Dictionary
        ergebnis = [dict(zip([column[0] for column in cursor.description], row)) for row in db_result]

        # pkvpakete in PKVPaket-Objekte umwandeln
        pkvpakete = []
        for row in ergebnis:
            pkvpaket = PKVPaket()
            pkvpaket.db_id = row['id']
            pkvpaket.betrag = row['betrag']
            pkvpaket.datum = row['datum']
            pkvpaket.aktiv = row['aktiv']
            pkvpaket.erhalten = row['erhalten']
            pkvpakete.append(pkvpaket)

        # Datenbankverbindung schließen
        connection.close()

        return pkvpakete
    
    def lade_aerzte(self):
        """Laden der Ärzte aus der Datenbank."""
        # Datenbankverbindung herstellen
        connection = sql.connect(self.db_path)
        cursor = connection.cursor()

        # Daten abfragen
        cursor.execute("""SELECT * FROM aerzte""")
        db_result = cursor.fetchall()

        # Speichere die Daten in einem Dictionary
        ergebnis = [dict(zip([column[0] for column in cursor.description], row)) for row in db_result]

        # aerzte in Arzt-Objekte umwandeln
        aerzte = []
        for row in ergebnis:
            arzt = Arzt()
            arzt.db_id = row['id']
            arzt.name = row['name']
            aerzte.append(arzt)

        # Datenbankverbindung schließen
        connection.close()

        return aerzte


class Arztrechnung:
    """Klasse zur Erfassung einer Arztrechnung."""
    
    def __init__(self):
        """Initialisierung der Arztrechnung."""
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
        """Neue Arztrechnung erstellen."""
        self.db_id = db.neue_rechnung(self)

    def speichern(self, db):
        """Speichern der Arztrechnung in der Datenbank."""
        db.aendere_rechnung(self)

    def loeschen(self, db):
        """Löschen der Arztrechnung aus der Datenbank."""
        db.loesche_rechnung(self)

    def __str__(self):
        """Ausgabe der Arztrechnung."""
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