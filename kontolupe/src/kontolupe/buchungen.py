"""Definition der Klassen der verschiedenen Buchungsarten."""

from pathlib import Path
import datetime
import sqlite3 as sql


class Datenbank:
    """Klasse zur Verwaltung der Datenbank."""

    def __init__(self):
        """Initialisierung der Datenbank."""
        self.db_path = Path('/data/data/net.biberwerk.kontolupe/kontolupe.db')
        #self.db_path = Path('kontolupe.db')

        # lösche die Datei der Datenbank
        #self.db_path.unlink()

        # Datenbank erstellen
        self.create_db()

    def create_db(self):
        """Erstellen der Datenbank."""
        
        # Datenbankverbindung herstellen
        connection = sql.connect(self.db_path)
        cursor = connection.cursor()

        # Tabellen erstellen
        cursor.execute("""CREATE TABLE IF NOT EXISTS arztrechnungen (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            betrag REAL,
            arzt INTEGER REFERENCES aerzte(id),
            rechnungsdatum TEXT,
            notiz TEXT,
            beihilfesatz REAL,
            aktiv INTEGER,
            bezahlt INTEGER,
            beihilfe_id INTEGER REFERENCES beihilfepakete(id),
            pkv_id INTEGER REFERENCES pkvpakete(id)
        )""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS beihilfepakete (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            betrag REAL,
            datum TEXT,
            aktiv INTEGER,
            erhalten INTEGER
        )""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS pkvpakete (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            betrag REAL,
            datum TEXT,
            aktiv INTEGER,
            erhalten INTEGER
        )""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS aerzte (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT
        )""")

        # Datenbankverbindung schließen
        connection.commit()
        connection.close()

    def neue_arztrechnung(self, arztrechnung):
        """Einfügen einer neuen Arztrechnung in die Datenbank."""
        # Datenbankverbindung herstellen
        connection = sql.connect(self.db_path)
        cursor = connection.cursor()

        # Daten einfügen
        cursor.execute("""INSERT INTO arztrechnungen (
            betrag,
            arzt,
            rechnungsdatum,
            notiz,
            beihilfesatz,
            aktiv,
            bezahlt,
            beihilfe_id,
            pkv_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", (
            arztrechnung.betrag,
            arztrechnung.arzt_id,
            arztrechnung.rechnungsdatum,
            arztrechnung.notiz,
            arztrechnung.beihilfesatz,
            arztrechnung.aktiv,
            arztrechnung.bezahlt,
            arztrechnung.beihilfe_id,
            arztrechnung.pkv_id
        ))

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
    
    def aendere_arztrechnung(self, arztrechnung):
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
            aktiv = ?,
            bezahlt = ?,
            beihilfe_id = ?,
            pkv_id = ?
        WHERE id = ?""", (
            arztrechnung.betrag,
            arztrechnung.arzt_id,
            arztrechnung.rechnungsdatum,
            arztrechnung.notiz,
            arztrechnung.beihilfesatz,
            arztrechnung.aktiv,
            arztrechnung.bezahlt,
            arztrechnung.beihilfe_id,
            arztrechnung.pkv_id,
            arztrechnung.db_id
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

    def loesche_arztrechnung(self, arztrechnung):
        """Löschen einer Arztrechnung aus der Datenbank."""
        # Datenbankverbindung herstellen
        connection = sql.connect(self.db_path)
        cursor = connection.cursor()

        # Daten löschen
        cursor.execute("""DELETE FROM arztrechnungen WHERE id = ?""", (
            arztrechnung.db_id,
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

    def lade_arztrechnungen(self):
        """Laden der Arztrechnungen aus der Datenbank."""
        # Datenbankverbindung herstellen
        connection = sql.connect(self.db_path)
        cursor = connection.cursor()

        # Daten abfragen
        cursor.execute("""SELECT * FROM arztrechnungen WHERE aktiv = 1""")
        db_result = cursor.fetchall()

        # arztrechnungen in Arztrechnung-Objekte umwandeln
        arztrechnungen = [Arztrechnung() for r in db_result]
        for i, arztrechnung in enumerate(arztrechnungen):
            arztrechnung.db_id = db_result[i][0]
            arztrechnung.betrag = db_result[i][1]
            arztrechnung.arzt_id = db_result[i][2]
            arztrechnung.rechnungsdatum = db_result[i][3]
            arztrechnung.notiz = db_result[i][4]
            arztrechnung.beihilfesatz = db_result[i][5]
            arztrechnung.aktiv = db_result[i][6]
            arztrechnung.bezahlt = db_result[i][7]
            arztrechnung.beihilfe_id = db_result[i][8]
            arztrechnung.pkv_id = db_result[i][9]

        # Datenbankverbindung schließen
        connection.close()

        return arztrechnungen
    
    def lade_beihilfepakete(self):
        """Laden der Beihilfepakete aus der Datenbank."""
        # Datenbankverbindung herstellen
        connection = sql.connect(self.db_path)
        cursor = connection.cursor()

        # Daten abfragen
        cursor.execute("""SELECT * FROM beihilfepakete WHERE aktiv = 1""")
        db_result = cursor.fetchall()

        # beihilfepakete in BeihilfePaket-Objekte umwandeln
        beihilfepakete = [BeihilfePaket() for r in db_result]
        for i, beihilfepaket in enumerate(beihilfepakete):
            beihilfepaket.db_id = db_result[i][0]
            beihilfepaket.betrag = db_result[i][1]
            beihilfepaket.datum = db_result[i][2]
            beihilfepaket.aktiv = db_result[i][3]
            beihilfepaket.erhalten = db_result[i][4]

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

        # pkvpakete in PKVPaket-Objekte umwandeln
        pkvpakete = [PKVPaket() for r in db_result]
        for i, pkvpaket in enumerate(pkvpakete):
            pkvpaket.db_id = db_result[i][0]
            pkvpaket.betrag = db_result[i][1]
            pkvpaket.datum = db_result[i][2]
            pkvpaket.aktiv = db_result[i][3]
            pkvpaket.erhalten = db_result[i][4]

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

        # aerzte in Arzt-Objekte umwandeln
        aerzte = [Arzt() for r in db_result]
        for i, arzt in enumerate(aerzte):
            arzt.db_id = db_result[i][0]
            arzt.name = db_result[i][1]

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
        self.db_id = db.neue_arztrechnung(self)

    def speichern(self, db):
        """Speichern der Arztrechnung in der Datenbank."""
        db.aendere_arztrechnung(self)

    def loeschen(self, db):
        """Löschen der Arztrechnung aus der Datenbank."""
        db.loesche_arztrechnung(self)

    def __str__(self):
        """Ausgabe der Arztrechnung."""
        return f"Arztrechnung: {self.db_id}\nArzt: {self.arzt_id}\nBetrag: {self.betrag} €\nRechnungsdatum: {self.rechnungsdatum}\nNotiz: {self.notiz}\nBeihilfesatz: {self.beihilfesatz} %\nBezahlt: {self.bezahlt}"
    

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
        return f"Beihilfe-Einreichung: {self.db_id}\nDatum: {self.datum}\nBetrag: {self.betrag} €\nErhalten: {self.erhalten}"
        

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
        return f"PKV-Einreichung: {self.db_id}\nDatum: {self.datum}\nBetrag: {self.betrag} €\nErhalten: {self.erhalten}"


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
        return f"ID: {self.db_id}\nArzt: {self.name}"

