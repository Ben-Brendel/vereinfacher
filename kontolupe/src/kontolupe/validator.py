from datetime import datetime

class Validator:
    """Klasse, die die Validierungsfunktionen für die Eingabefelder enthält."""

    def __init__(self, validator=None):

        # Ordne den übergebenen Validator der Instanz zu
        match validator:
            case None:
                self.rectify = self.__pass
                self.is_valid = self.__pass
            case 'float':  
                self.rectify = self.__rect_float
                self.is_valid = self.__is_float
            case 'int':
                self.rectify = self.__rect_int
                self.is_valid = self.__is_int
            case 'percent':
                self.rectify = self.__rect_percent
                self.is_valid = self.__is_percent
            case 'date':
                self.rectify = self.__rect_date
                self.is_valid = self.__is_date
            case 'postal':
                self.rectify = self.__rect_postal
                self.is_valid = self.__is_postal
            case 'phone':
                self.rectify = self.__rect_phone
                self.is_valid = self.__is_phone
            case 'email':
                self.rectify = self.__rect_email
                self.is_valid = self.__is_email
            case 'website':
                self.rectify = self.__rect_website
                self.is_valid = self.__is_website
            case _:
                self.rectify = None
                self.is_valid = None
                raise ValueError('Ungültiger Validator')
            

    def __pass(self, widget):
        """Funktion, die nichts tut."""
        pass


    def __rect_float(self, widget):
        """Korrigiert die Eingabe, sodass nur noch Zahlen von 0 bis 9 und ein , enthalten sind."""

        # Entferne alle Zeichen, die keine Zahl von 0 bis 9 oder ein , sind.
        eingabe = ''.join(c for c in widget.value if c in '0123456789,')
        
        # Entferne alle , außer dem letzten
        if eingabe.count(',') > 1:
            eingabe = eingabe.replace(',', '', eingabe.count(',') - 1)

        # Setze den Wert des Widgets auf die korrigierte Eingabe
        widget.value = eingabe


    def __is_float(self, widget):
        """Prüft, ob die Eingabe eine Zahl ist und gibt True oder False zurück."""

        # Eingabe anpassen
        self.__rect_float(widget)

        try:
            float(widget.value.replace(',', '.'))
            return True
        except ValueError:
            return False


    def __rect_int(self, widget):
        """Korrigiert die Eingabe, sodass nur noch Zahlen von 0 bis 9 enthalten sind."""

        # Entferne alle Zeichen, die keine Zahl von 0 bis 9 sind.
        eingabe = ''.join(c for c in widget.value if c in '0123456789')

        # Setze den Wert des Widgets auf die korrigierte Eingabe
        widget.value = eingabe


    def __is_int(self, widget):
        """Prüft, ob die Eingabe eine ganze Zahl ist und gibt True oder False zurück."""

        # Eingabe anpassen
        self.__rect_int(widget)

        try:
            int(widget.value)
            return True
        except ValueError:
            return False


    def __rect_percent(self, widget):
        """Prüft, ob nur Zahlen von 0 bis 9 enthalten sind und korrigiert die Eingabe entsprechend."""

        # Entferne alle Zeichen, die keine Zahl von 0 bis 9 oder ein , sind.
        eingabe = ''.join(c for c in widget.value if c in '0123456789')
        widget.value = eingabe


    def __is_percent(self, widget):
        """Prüft, ob die Eingabe eine ganze Zahl zwischen 0 und 100 ist und gibt True oder False zurück."""

        # Eingabe anpassen
        self.__rect_percent(widget)

        try:
            zahl = int(widget.value)
            if zahl > 100:
                return False
            if zahl not in range(0, 101, 1):
                return False
            return True
        except ValueError:
            return False


    def __rect_date(self, widget):
        """Korrigiert die Eingabe, sodass nur noch ein gültiges Datum enthalten sein kann."""

        # Entferne alle Zeichen, die keine Zahl von 0 bis 9 oder ein . sind.
        eingabe = ''.join(c for c in widget.value if c in '0123456789.')
        widget.value = eingabe

        if widget.value == '':
            return

        # Überprüfe ob das Datum nur als Folge von Zahlen ohne . eingegeben wurde
        if widget.value.count('.') == 0:
            if len(widget.value) == 6:
                widget.value = widget.value[:4] + '20' + widget.value[4:]
            if len(widget.value) == 8:
                widget.value = widget.value[:2] + '.' + widget.value[2:4] + '.' + widget.value[4:]
            
        # Überprüfe ob das Datum als Folge von Zahlen mit . eingegeben wurde
        elif widget.value.count('.') == 2:
            parts = widget.value.split('.')
            # Führende 0 hinzufügen, wenn die ersten beiden Teile nur eine Ziffer haben
            if len(parts[0]) != 2:
                parts[0] = '0' + parts[0]
            if len(parts[1]) != 2:
                parts[1] = '0' + parts[1]
            # 20 hinzufügen, wenn der letzte Teil nur zwei Ziffern hat
            if len(parts[2]) == 2:
                parts[2] = '20' + parts[2]

                widget.value = '.'.join(parts)
    

    def __is_date(self, widget):
        """ Prüft, ob die Eingabe ein gültiges Datum ist und gibt True oder False zurück."""

        # Eingabe anpassen
        self.__rect_date(widget)    
        
        try:
            datetime.strptime(widget.value, '%d.%m.%Y')
            return True
        except ValueError:
            return False


    def __rect_postal(self, widget):
        """Prüft, ob nur Zahlen von 0 bis 9 enthalten sind und korrigiert die Eingabe entsprechend."""

        # Entferne alle Zeichen, die keine Zahl von 0 bis 9 sind.
        eingabe = ''.join(c for c in widget.value if c in '0123456789')
        widget.value = eingabe


    def __is_postal(self, widget):
        """Prüft, ob die Eingabe eine gültige Postleitzahl ist und gibt True oder False zurück."""

        # Eingabe anpassen
        self.__rect_postal(widget)

        if widget.value == '' or len(widget.value) != 5:
            return False
        
        return True
    

    def __rect_phone(self, widget):
        """Prüft, ob nur Zahlen von 0 bis 9 enthalten sind und korrigiert die Eingabe entsprechend."""

        # Entferne alle Zeichen, die keine Zahl von 0 bis 9 sind.
        eingabe = ''.join(c for c in widget.value if c in '0123456789')
        widget.value = eingabe

    
    def __is_phone(self, widget):
        """Prüft, ob die Eingabe eine gültige Telefonnummer ist und gibt True oder False zurück."""

        # Eingabe anpassen
        self.__rect_phone(widget)

        if widget.value == '':
            return False
        
        return True
    

    def __rect_email(self, widget):
        """Prüft, ob nur Zeichen enthalten sind, die in einer E-Mail-Adresse vorkommen dürfen und korrigiert die Eingabe entsprechend."""

        # Entferne alle Zeichen, die nicht in einer E-Mail-Adresse vorkommen dürfen
        eingabe = ''.join(c for c in widget.value if c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@.-_')
        widget.value = eingabe


    def __is_email(self, widget):
        """Prüft, ob die Eingabe eine gültige E-Mail-Adresse ist und gibt True oder False zurück."""

        # Eingabe anpassen
        self.__rect_email(widget)

        if widget.value == '':
            return False

        # Überprüfe ob die Struktur der Mail-Adresse korrekt ist
        if widget.value.count('@') != 1:
            return False
        if widget.value.count('.') < 1:
            return False
        if widget.value.count('.') > 2:
            return False
        if widget.value[0] == '@':
            return False   
        if widget.value[-1] == '@':
            return False
        if widget.value[0] == '.': 
            return False
        if widget.value[-1] == '.':
            return False
        if widget.value[-1] == '-':
            return False
        if widget.value[-1] == '_':
            return False
        
        return True
    

    def __rect_website(self, widget):
        """Prüft, ob nur Zeichen enthalten sind, die in einer Webadresse vorkommen dürfen und korrigiert die Eingabe entsprechend."""

        # Entferne alle Zeichen, die nicht in einer Webadresse vorkommen dürfen
        eingabe = ''.join(c for c in widget.value if c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@.-_/:?%=#&')
        widget.value = eingabe


    def __is_website(self, widget):
        """Prüft, ob die Eingabe eine gültige Webseite ist und korrigiert sie entsprechend."""

        # Eingabe anpassen
        self.__rect_website(widget)

        if widget.value == '':
            return False

        # Überprüfe ob die Struktur der Webadresse korrekt ist
        if widget.value.count('.') < 1:
            return False
        if widget.value[0] == '.':
            return False
        if widget.value[-1] == '.':
            return False
        
        # Überprüfe ob die Webadresse mit http:// oder https:// beginnt
        # Und ersetze http:// durch https:// oder füge https:// hinzu
        if widget.value[:7] != 'http://' and widget.value[:8] != 'https://':
            widget.value = 'https://' + widget.value
        elif widget.value[:7] == 'http://':
            widget.value = 'https://' + widget.value[7:]
        
        return True