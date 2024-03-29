"""Constants and functions used throughout the application."""

import toga

DATAPROTECTION_URL = 'https://kontolupe.biberwerk.net/datenschutz.html'

DATABASE_VERSION = 1

# constants to use for data functions and listeners
BILL_OBJECT = 'bill'
ALLOWANCE_OBJECT = 'allowance'
INSURANCE_OBJECT = 'insurance'
INSTITUTION_OBJECT = 'institution'
PERSON_OBJECT = 'person'

# lists of object types for the database
BILL_TYPES = ('bill', 'bills', 'rechnung', 'rechnungen', 'Rechnung', 'Rechnungen')
ALLOWANCE_TYPES = ('allowance', 'allowances', 'beihilfe', 'beihilfepakete', 'Beihilfe', 'Beihilfepakete')
INSURANCE_TYPES = ('insurance', 'insurances', 'pkv', 'pkvpakete', 'PKV', 'PKVpakete')
INSTITUTION_TYPES = ('institution', 'institutions', 'einrichtung', 'einrichtungen', 'Einrichtung', 'Einrichtungen')
PERSON_TYPES = ('person', 'persons', 'personen', 'Person', 'Personen')

# dictionary to map object types to database table names
OBJECT_TYPE_TO_DB_TABLE = {
    **dict.fromkeys(BILL_TYPES, 'rechnungen'),
    **dict.fromkeys(ALLOWANCE_TYPES, 'beihilfepakete'),
    **dict.fromkeys(INSURANCE_TYPES, 'pkvpakete'),
    **dict.fromkeys(INSTITUTION_TYPES, 'einrichtungen'),
    **dict.fromkeys(PERSON_TYPES, 'personen')
}

# sort keys
SORT_KEYS = {
    BILL_OBJECT: 'rechnungsdatum',
    ALLOWANCE_OBJECT: 'datum',
    INSURANCE_OBJECT: 'datum',
    INSTITUTION_OBJECT: 'name',
    PERSON_OBJECT: 'name',
}

# definitions of the attributes for each object type
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
        'name_db': None,
        'type_db': None,
        'name_object': 'rechnungsdatum_kurz',
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
        'name_db': None,
        'type_db': None,
        'name_object': 'buchungsdatum_kurz',
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
        'name_db': None,
        'type_db': None,
        'name_object': 'datum_kurz',
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
        'name_db': None,
        'type_db': None,
        'name_object': 'datum_kurz',
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
    """Return the attributes dictionary corresponding to object_type."""

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

def dict_from_row(object_type, row):
        """Convert a Row object to a dictionary."""
        
        return {attribute['name_object']: getattr(row, attribute['name_object']) for attribute in get_attributes(object_type)}

def get_index_new_element(object_type, list_source, element):
        """Gets the index position of a new or changed element in a list source."""
        
        if isinstance(element, dict):
            data = element
        else:
            data = dict_from_row(object_type, element)

        sort_key = SORT_KEYS.get(object_type)

        # check if the element is already in the list (element changed)
        try:
            list_item = list_source.find({'db_id': data['db_id']})
            list_index = list_source.index(list_item)
            if getattr(list_source[list_index], sort_key) == data[sort_key]:
                return list_index
            element_changed = True
        except ValueError:
            element_changed = False

        new_index = 0        
        for row in list_source:
            if 'datum' in sort_key:
                if "".join(reversed(data[sort_key].split('.'))) < "".join(reversed(getattr(row, sort_key).split('.'))):
                    new_index += 1
                else:
                    break
            else:
                if data[sort_key] > getattr(row, sort_key):
                    new_index += 1
                else:
                    break

        if element_changed and new_index > list_index:
            new_index -= 1

        return new_index

def table_index_selection(widget):
    """Return the index of the selected row in a Table widget."""
    
    if isinstance(widget, toga.Table) and widget.selection is not None:
        return widget.data.index(widget.selection) 
    return None
    
def add_newlines(input_string, max_line_length):
    """Insert newlines into input_string to limit line length to max_line_length."""

    if input_string is None:
        return ''
    lines = input_string.split(' ')
    result_lines = []
    current_line = ''
    for line in lines:
        if len(current_line) + len(line) + 1 > max_line_length:  # +1 for the comma
            result_lines.append(current_line.rstrip(' '))
            current_line = line + ' '
        else:
            current_line += line + ' '
    result_lines.append(current_line.rstrip(' '))
    return '\n'.join(result_lines)