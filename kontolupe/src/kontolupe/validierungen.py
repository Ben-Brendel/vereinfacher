from datetime import datetime

def pruefe_zahl(widget):
    """Prüft, ob die Eingabe eine Zahl ist und korrigiert sie entsprechend."""

    # Entferne alle Zeichen, die keine Zahl von 0 bis 9 oder ein , sind.
    eingabe = ''.join(c for c in widget.value if c in '0123456789,')
    
    # entferne alle , außer dem letzten
    if eingabe.count(',') > 1:
        eingabe = eingabe.replace(',', '', eingabe.count(',') - 1)

    widget.value = eingabe

    # replace , with .
    eingabe = eingabe.replace(',', '.')

    try:
        float(eingabe)
        return True
    except ValueError:
        #widget.value = ''
        #self.main_window.error_dialog('Fehler', 'Kein gültiger Betrag eingegeben.')
        return False


def pruefe_prozent(widget):
    """Prüft, ob die Eingabe eine ganze Zahl zwischen 0 und 100 ist und korrigiert sie entsprechend."""

    # Entferne alle Zeichen, die keine Zahl von 0 bis 9 oder ein , sind.
    eingabe = ''.join(c for c in widget.value if c in '0123456789')
    widget.value = eingabe

    try:
        zahl = int(eingabe)
        if zahl > 100:
            widget.value = '100'
        if zahl not in range(0, 101, 5):
            #self.main_window.info_dialog('Bitte überprüfen', 'Der Beihilfesatz ist üblicherweise ein Vielfaches von 5 und nicht 0 oder 100.')
            return False
        return True
    except ValueError:
        widget.value = ''
        #self.main_window.error_dialog('Fehler', 'Kein gültiger Prozentsatz eingegeben.')
        return False


def pruefe_datum(widget):
    """ Prüft, ob die Eingabe ein gültiges Datum ist und korrigiert die Eingabe."""

    eingabe = ''.join(c for c in widget.value if c in '0123456789.')
    widget.value = eingabe

    if widget.value == '':
        return True

    error = False            
    # check if there are 3 parts
    if widget.value.count('.') != 2:
        # check if the entry is numeric
        if not widget.value.isnumeric():
            error = True
        # check if the entry is 6 digits long and insert 20 after the first four digits
        elif len(widget.value) == 6:
            widget.value = widget.value[:4] + '20' + widget.value[4:]
        elif len(widget.value) != 8:
            error = True
    
        if not error:
            # add a . after the first two digits and after the second two digits
            widget.value = widget.value[:2] + '.' + widget.value[2:4] + '.' + widget.value[4:]
        
        # check if the date is valid
        try:
            datetime.strptime(widget.value, '%d.%m.%Y')
        except ValueError:
            error = True

    else:
        # check if all parts are numbers
        parts = widget.value.split('.')
        for part in parts:
            if not part.isnumeric():
                error = True
                break
        
        # first and second part must be two digits long, if not add a leading 0
        if not error and len(parts[0]) != 2:
            parts[0] = '0' + parts[0]
        if not error and len(parts[1]) != 2:
            parts[1] = '0' + parts[1]
        # third part must be 4 or 2 digits long. if 2 digits long, add 20 to the beginning
        if not error and len(parts[2]) == 2:
            parts[2] = '20' + parts[2]
        elif not error and len(parts[2]) != 4:
            error = True

        # put the parts back together
        if not error:
            widget.value = '.'.join(parts)
        
        # check if the date is valid
        try:
            datetime.strptime(widget.value, '%d.%m.%Y')
        except ValueError:
            error = True

    # if error:
    #     widget.value = ''

    return not error


def pruefe_plz(widget):
    """Prüft, ob die Eingabe eine gültige Postleitzahl ist und korrigiert sie entsprechend."""

    # Entferne alle Zeichen, die keine Zahl von 0 bis 9 sind.
    eingabe = ''.join(c for c in widget.value if c in '0123456789')
    widget.value = eingabe

    if widget.value == '':
        return True

    if len(widget.value) != 5:
        return False
    
    return True
    

def pruefe_telefon(widget):
    """Prüft, ob die Eingabe eine gültige Telefonnummer ist und korrigiert sie entsprechend."""

    # Entferne alle Zeichen, die keine Zahl von 0 bis 9 sind.
    eingabe = ''.join(c for c in widget.value if c in '0123456789 -/()+*#')
    widget.value = eingabe

    if widget.value == '':
        return True

    return True


def pruefe_email(widget):
    """Prüft, ob die Eingabe eine gültige E-Mail-Adresse ist und korrigiert sie entsprechend."""

    # Entferne alle Zeichen, die nicht in einer E-Mail-Adresse vorkommen dürfen
    eingabe = ''.join(c for c in widget.value if c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@.-_')
    widget.value = eingabe

    if widget.value == '':
        return True

    # Überprüfe ob die Struktur der Mail-Adresse korrekt ist
    if eingabe.count('@') != 1:
        return False
    if eingabe.count('.') < 1:
        return False
    if eingabe.count('.') > 2:
        return False
    if eingabe[0] == '@':
        return False   
    if eingabe[-1] == '@':
        return False
    if eingabe[0] == '.': 
        return False
    if eingabe[-1] == '.':
        return False
    if eingabe[-1] == '-':
        return False
    if eingabe[-1] == '_':
        return False
    
    return True


def pruefe_webseite(widget):
    """Prüft, ob die Eingabe eine gültige Webseite ist und korrigiert sie entsprechend."""

    # Entferne alle Zeichen, die nicht in einer Webadresse vorkommen dürfen
    eingabe = ''.join(c for c in widget.value if c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@.-_/:?%=#&')
    widget.value = eingabe

    if widget.value == '':
        return True

    # Überprüfe ob die Struktur der Webadresse korrekt ist
    if eingabe.count('.') < 1:
        return False
    if eingabe[0] == '.':
        return False
    if eingabe[-1] == '.':
        return False
    
    # Überprüfe ob die Webadresse mit http:// oder https:// beginnt
    # Und ersetze http:// durch https:// oder füge https:// hinzu
    if eingabe[:7] != 'http://' and eingabe[:8] != 'https://':
        eingabe = 'https://' + eingabe
        widget.value = eingabe
    elif eingabe[:7] == 'http://':
        eingabe = 'https://' + eingabe[7:]
        widget.value = eingabe
    
    return True