"""GUI-Objekte für die Kontolupe-App."""

import toga
from toga.constants import Baseline
from kontolupe.layout import *
from kontolupe.validator import *
from kontolupe.database import *
from kontolupe.general import *
from datetime import datetime
import math


class StatisticsGraph(toga.Canvas):
    """Erzeugt einen Canvas für die Statistik."""

    def __init__(self, **kwargs):
        super().__init__(
            style = style_canvas,
            on_resize = kwargs.get('on_resize', None)
        )

    def draw(self, width, data_selection, statistic_data, **kwargs):

        def round_up_to_clean_number(n):
            if n == 0:
                return 0
            power = 10 ** (math.floor(math.log10(n)))
            return math.ceil(n / power) * power
        
        def calculate_segments(n):
            if n == 0:
                return 0, 0

            # Calculate the base segment width
            base_segment_width = 5 * (10 ** (math.floor(math.log10(n / 5))))

            # Calculate the number of base segments
            base_segments = n / base_segment_width

            # If the number of base segments is less than 4, halve the segment width and round to nearest multiple of 5
            while base_segments < 4:
                base_segment_width = round(base_segment_width / 2 / 5) * 5
                base_segments = n / base_segment_width

            segment_width = base_segment_width

            # Calculate the number of segments
            segments = math.ceil(n / segment_width)

            return segments, segment_width

        def number_of_segments(data):
            start_month = int(data['from'][0]) + (int(data['from'][1]) - 1) * 12
            end_month = int(data['to'][0]) + (int(data['to'][1]) - 1) * 12

            match data['step']:
                case 'Monat':
                    step = 1
                case 'Quartal':
                    start_month = ((start_month - 1) // 3) * 3 + 1
                    end_month = ((end_month - 1) // 3 + 1) * 3
                    step = 3
                case 'Halbjahr':
                    start_month = ((start_month - 1) // 6) * 6 + 1
                    end_month = ((end_month - 1) // 6 + 1) * 6
                    step = 6
                case 'Jahr':
                    start_month = ((start_month - 1) // 12) * 12 + 1
                    end_month = ((end_month - 1) // 12 + 1) * 12
                    step = 12

            return (end_month - start_month) // step + 1
        
        def date_in_range(date, data):
            day, month, year = map(int, date.split('.'))
            date = [month, year]

            if int(data['from'][1]) > int(data['to'][1]) or (int(data['from'][1]) == int(data['to'][1]) and int(data['from'][0]) > int(data['to'][0])):
                return False
            if int(data['from'][1]) < date[1] < int(data['to'][1]):
                return True
            if int(data['from'][1]) == date[1] and int(data['from'][0]) <= date[0]:
                return True
            if int(data['to'][1]) == date[1] and int(data['to'][0]) >= date[0]:
                return True
            return False
        
        # Daten vorbereiten
        values = {}

        # the person_id in statistic_data['persons'] with the name of data_selection['person']
        if data_selection['person'] == 'Alle':
            person_id = None
        else:
            person_id = [person['db_id'] for person in statistic_data['persons'] if person['name'] == data_selection['person']][0]

        # same for institution
        if data_selection['institution'] == 'Alle':
            institution_id = None
        else:
            institution_id = [institution['db_id'] for institution in statistic_data['institutions'] if institution['name'] == data_selection['institution']][0]

        if data_selection['type'] == 'Rechnungen' or data_selection['type'] == 'Alle':
            for bill in statistic_data['bills']:
                if date_in_range(bill['rechnungsdatum'], data_selection) and (person_id is None or bill['person_id'] == person_id) and (institution_id is None or bill['einrichtung_id'] == institution_id):
                    day, month, year = map(int, bill['rechnungsdatum'].split('.'))
                    values.setdefault('bills', {}).setdefault(year, {}).setdefault(month, 0)
                    values['bills'][year][month] += bill['betrag']
            
        if data_selection['type'] == 'Beihilfe' or data_selection['type'] == 'Alle':
            for allowance in statistic_data['allowances']:
                if date_in_range(allowance['datum'], data_selection):
                    day, month, year = map(int, allowance['datum'].split('.'))
                    values.setdefault('allowances', {}).setdefault(year, {}).setdefault(month, 0)
                    for bill in statistic_data['bills']:
                        if bill['beihilfe_id'] == allowance['db_id'] and (person_id is None or bill['person_id'] == person_id) and (institution_id is None or bill['einrichtung_id'] == institution_id):
                            values['allowances'][year][month] += (bill['betrag'] - bill['abzug_beihilfe']) * bill['beihilfesatz'] / 100

        if data_selection['type'] == 'Private KV' or data_selection['type'] == 'Alle':
            for insurance in statistic_data['insurances']:
                if date_in_range(insurance['datum'], data_selection):
                    day, month, year = map(int, insurance['datum'].split('.'))
                    values.setdefault('insurances', {}).setdefault(year, {}).setdefault(month, 0)
                    for bill in statistic_data['bills']:
                        if bill['pkv_id'] == insurance['db_id'] and (person_id is None or bill['person_id'] == person_id) and (institution_id is None or bill['einrichtung_id'] == institution_id):
                            values['insurances'][year][month] += (bill['betrag'] - bill['abzug_pkv']) * (100 - bill['beihilfesatz']) / 100

        # Print the values for debugging
        print(values)

        # Segmente ermitteln
        segments_number = number_of_segments(data_selection)

        # Determine the step size based on the user's selection
        start_month = int(data_selection['from'][0])
        if data_selection['step'] == 'Monat':
            step = 1
        elif data_selection['step'] == 'Quartal':
            step = 3
            start_month = ((start_month - 1) // 3) * 3 + 1
        elif data_selection['step'] == 'Halbjahr':
            step = 6
            start_month = ((start_month - 1) // 6) * 6 + 1
        elif data_selection['step'] == 'Jahr':
            step = 12
            start_month = 1

        segments = []
        start_year = int(data_selection['from'][1])
        # Initialize month and year
        month = start_month
        year = start_year
        for i in range(segments_number):
            segment = {'bills': 0, 'allowances': 0, 'insurances': 0, 'description': ''}
            for data_type in ['bills', 'allowances', 'insurances']:
                if data_type in values:
                    for j in range(step):
                        month = (start_month - 1 + i * step + j) % 12 + 1
                        year = start_year + (start_month - 1 + i * step + j) // 12
                        if year in values[data_type] and month in values[data_type][year]:
                            segment[data_type] += values[data_type][year][month]
            if step == 1:
                segment['description'] = f"{month:02d}/{year}"
            elif step == 3:
                segment['description'] = f"Q{(month - 1) // 3 + 1}/{year}"
            elif step == 6:
                segment['description'] = f"H{(month - 1) // 6 + 1}/{year}"
            elif step == 12:
                segment['description'] = f"{year}"
            segments.append(segment)

        # print the segments for debugging
        print(segments)

        # stop if all values in segments are 0
        if all([segment['bills'] == 0 and segment['allowances'] == 0 and segment['insurances'] == 0 for segment in segments]):
            self.clear()
            with self.Fill(color=FARBE_DUNKEL) as text_filler:
                    text_filler.write_text(
                        'Keine Daten in der Auswahl vorhanden.', 
                        x = (width - self.measure_text('Keine Daten in der Auswahl vorhanden.')[0]) / 2, 
                        y = 20,
                        baseline = Baseline.TOP
                    )
            return

        # calculate the scaling factor for the y-axis
        # the maximum value of all values in segments excluding 'description'
        max_value = max([max([segment[key] for key in segment.keys() if key != 'description']) for segment in segments])
        
        # calculate the y-axis using max_value
        # the max_value should be increased to the next clean number
        max_value = round_up_to_clean_number(max_value)

        # calculate the number of segments on the y-axis 
        segments_y_axis, segment_value = calculate_segments(max_value)

        # create a list of descriptions for the y-axis
        y_axis_descriptions = [f"{int(i * segment_value)} €" for i in range(segments_y_axis + 1)]

        # calculate the max value of the measurements of the y-axis descriptions
        max_description_length_y = max(self.measure_text(description)[0] for description in y_axis_descriptions)
        max_description_height_y = max(self.measure_text(description)[1] for description in y_axis_descriptions)

        # calculate the max value of the measurements of the description lengths
        max_description_length_x = max(self.measure_text(segment['description'])[0] for segment in segments)
        max_description_height_x = max(self.measure_text(segment['description'])[1] for segment in segments)

        # The measurements for the graph
        graph_legend_height = 50
        graph_legend_bar_width = 30
        graph_legend_bar_height = 10
        graph_legend_space = 5
        graph_legend_section_space = 20
        graph_offset = 10
        graph_description_line = 5
        offset_description = 5
        graph_height = STATISTIK_HOEHE - 2 * graph_offset - graph_description_line - max_description_length_x - graph_legend_height
        graph_offset_x = graph_offset + max_description_length_y + offset_description + graph_description_line
        graph_offset_y = graph_offset + graph_legend_height
        graph_width = width - graph_offset - graph_offset_x
        segment_width = graph_width / segments_number
        bar_width = (segment_width * 0.75) / 3

        # measure the length of the legend containing of Rechnungen, Beihilfe, Private KV
        # it is the sum of the length of the descriptions and the length of the bars and the space between them
        graph_legend_width = sum([self.measure_text(text)[0] for text in ['Rechnungen', 'Beihilfe', 'Private KV']]) + 3 * graph_legend_space + 2 * graph_legend_section_space + 3 * graph_legend_bar_width

        if graph_legend_width > graph_width:
            texts_legend = {
                'bills': 'Rechn.',
                'allowances': 'Beihilfe',
                'insurances': 'PKV'
            }
        else:  
            texts_legend = {
                'bills': 'Rechnungen',
                'allowances': 'Beihilfe',
                'insurances': 'Private KV'
            }
        
        graph_legend_width = sum([self.measure_text(text)[0] for text in texts_legend.values()]) + 3 * graph_legend_space + 2 * graph_legend_section_space + 3 * graph_legend_bar_width

        if data_selection['type'] == 'Alle':
            offsets_bars = {'bills': -bar_width, 'allowances': 0, 'insurances': bar_width}
            # offsets_legend = {
            #     'bills': -graph_legend_bar_width - graph_legend_space - graph_legend_section_space - self.measure_text(texts_legend['bills'])[0] - (self.measure_text(texts_legend['allowances'])[0] + graph_legend_bar_width + graph_legend_space) / 2, 
            #     'allowances': -(self.measure_text(texts_legend['allowances'])[0] + graph_legend_bar_width + graph_legend_space) / 2, 
            #     'insurances': graph_legend_section_space + (self.measure_text(texts_legend['allowances'])[0] + graph_legend_bar_width + graph_legend_space) / 2
            # }
            offsets_legend = {
                'bills': -graph_legend_width / 2,
                'allowances': -graph_legend_width / 2 + (self.measure_text(texts_legend['bills'])[0] + graph_legend_bar_width + graph_legend_space + graph_legend_section_space),
                'insurances': graph_legend_width / 2 - (self.measure_text(texts_legend['insurances'])[0] + graph_legend_bar_width + graph_legend_space)
            }
        else:
            offsets_bars = {'bills': 0, 'allowances': 0, 'insurances': 0}
            offsets_legend = {
                'bills': -(self.measure_text(texts_legend['bills'])[0] + graph_legend_bar_width + graph_legend_space) / 2, 
                'allowances': -(self.measure_text(texts_legend['allowances'])[0] + graph_legend_bar_width + graph_legend_space) / 2, 
                'insurances': -(self.measure_text(texts_legend['insurances'])[0] + graph_legend_bar_width + graph_legend_space) / 2
            }

        data_types = {
            'Rechnungen': {'color': FARBE_BLAU, 'offset': offsets_bars['bills'], 'offset_legend': offsets_legend['bills'], 'key': 'bills'},
            'Beihilfe': {'color': FARBE_LILA, 'offset': offsets_bars['allowances'], 'offset_legend': offsets_legend['allowances'], 'key': 'allowances'},
            'Private KV': {'color': FARBE_GRUEN, 'offset': offsets_bars['insurances'], 'offset_legend': offsets_legend['insurances'], 'key': 'insurances'}
        }

        # Canvas zurücksetzen
        self.clear()

        # x-Achse
        with self.Stroke(line_width = 1) as x_axis:
            x_axis.move_to(graph_offset_x, graph_height + graph_offset_y)
            x_axis.line_to(graph_width + graph_offset_x, graph_height + graph_offset_y)

        # y-Achse
        with self.Stroke(line_width = 1) as y_axis:
            y_axis.move_to(graph_offset_x, graph_offset_y)
            y_axis.line_to(graph_offset_x, graph_height + graph_offset_y)

        # Legende
        for data_type, properties in data_types.items():
            if data_selection['type'] == data_type or data_selection['type'] == 'Alle':
                text_length = self.measure_text(texts_legend[properties['key']])[0]

                with self.Fill(color=FARBE_DUNKEL) as text_filler:
                    text_filler.write_text(
                        texts_legend[properties['key']], 
                        x = graph_offset_x + graph_width / 2 + properties['offset_legend'], 
                        y = graph_legend_height / 2,
                        baseline = Baseline.MIDDLE
                    )
                
                with self.Fill(color=properties['color']) as bar:
                    bar.rect(
                        graph_offset_x + graph_width / 2 + properties['offset_legend'] + graph_legend_space + text_length,
                        (graph_legend_height - graph_legend_bar_height) / 2,
                        graph_legend_bar_width,
                        graph_legend_bar_height
                    )

        # descriptions on the y-axis
        for i in range(segments_y_axis+1):
            with self.Stroke(line_width = 1) as segment:
                segment.move_to(graph_offset_x, graph_height + graph_offset_y - i * (graph_height - graph_offset) / segments_y_axis)
                segment.line_to(graph_offset_x - graph_description_line, graph_height + graph_offset_y - i * (graph_height - graph_offset) / segments_y_axis)

            with self.Fill(color=FARBE_DUNKEL) as text_filler:
                text_filler.write_text(
                    y_axis_descriptions[i], 
                    x = graph_offset + max_description_length_y - self.measure_text(y_axis_descriptions[i])[0], 
                    y = graph_offset_y + graph_height - i * (graph_height - graph_offset) / segments_y_axis + max_description_height_y / 2,
                    baseline = Baseline.BOTTOM
                )

        # Segmente zeichnen
        for i in range(segments_number):

            with self.Stroke(line_width = 1) as segment:
                segment.move_to(graph_offset_x + (i+0.5) * segment_width, graph_height + graph_offset_y)
                segment.line_to(graph_offset_x + (i+0.5) * segment_width, graph_height + graph_offset_y + graph_description_line)

            with self.Fill(color=FARBE_DUNKEL) as text_filler:
                if max_description_length_x > segment_width - graph_offset:
                    text_filler.rotate(-math.pi/2)
                    text_filler.write_text(
                        segments[i]['description'], 
                        x = -1 * (graph_height + graph_offset_y + graph_description_line + self.measure_text(segments[i]['description'])[0] + offset_description),
                        y = graph_offset_x + (i+0.5) * segment_width - max_description_height_x / 2,
                        baseline = Baseline.TOP
                    )
                else:
                    text_filler.write_text(
                        segments[i]['description'], 
                        x = graph_offset_x + (i+0.5) * segment_width - max_description_length_x / 2, 
                        y = graph_height + graph_offset_y + graph_description_line + offset_description,
                        baseline = Baseline.TOP
                    )

            for data_type, properties in data_types.items():
                if data_selection['type'] == data_type or data_selection['type'] == 'Alle':
                    with self.Fill(color=properties['color']) as bar:
                        bar.rect(
                            graph_offset_x + properties['offset'] + (i+0.5) * segment_width - bar_width / 2,
                            graph_offset_y + graph_height * (1 - segments[i][properties['key']] / max_value),
                            bar_width,
                            graph_height * segments[i][properties['key']] / max_value
                        )
        
    def clear(self):
        self.context.clear()    


class SectionOpenSum(toga.Box):
    """Erzeugt den Anzeigebereich für den offenen Betrag."""

    def __init__(self, window, value_source=True, **kwargs):
        self.value_source = value_source
        self.listener = SectionListener(self)
        self.value_source.add_listener(self.listener)
        super().__init__(style=style_box_offene_buchungen)

        self.box = toga.Box(style=style_box_row)
        self.add(self.box)
        self.info = toga.Label('Offener Betrag: ', style=style_start_summe)
        self.box.add(self.info)
        self.box.add(HelpButton(
            window      = window,
            helptitle   = 'Offener Betrag',
            helptext    = (
                'Dieser Wert zeigt Dir an, wie viel Geld Dir in Summe noch zusteht,'
                ' oder Du noch bezahlen musst.\n\n'
                'Er berechnet sich so:\n'
                '- Nicht bezahlte Rechnungen werden abgezogen.\n'
                '- Nicht eingereichte Rechnungen werden hinzugezählt.\n'
                '- Nicht erstattete Einreichungen werden hinzugezählt.\n'
            )
        ))

        self.update_info()

    def set_value_source(self, value_source):
        self.value_source = value_source
        self.value_source.add_listener(self.listener)
        self.update_info()

    def update_info(self, *args):
        result = round(self.value_source.value, 2)
        result = 0.00 if result == -0.00 else result
        self.info.text = 'Offener Betrag: ' + format(result, '.2f').replace('.', ',') + ' €'

class Section(toga.Box):
    """Create a section on the mainpage."""

    def __init__(self, list_source, style, title, on_press_show=None, on_press_new=None, new_enabled=True):

        self.list_source = list_source
        self.listener = SectionListener(self)
        self.list_source.add_listener(self.listener)
        super().__init__(style=style)

        self.button_box = toga.Box(style=style_box_buttons_start)
        self.title = toga.Label(title, style=style_label_h2_start)
        self.info = toga.Label('', style=style_label_section)
        self.button_show = toga.Button('Anzeigen', on_press=on_press_show, style=style_button)
        self.button_new = toga.Button('Neu', on_press=on_press_new, style=style_button, enabled=new_enabled)
        self.button_box.add(self.button_show)
        self.button_box.add(self.button_new)
        self.add(self.title)
        self.add(self.info)
        self.add(self.button_box)

        self.update_info()

    def set_list_source(self, list_source):
        self.list_source = list_source
        self.list_source.add_listener(self.listener)
        self.update_info()

    def hide(self):
        self.remove(self.title)
        self.remove(self.info)
        self.remove(self.button_box)

    def show(self):
        self.add(self.title)
        self.add(self.info)
        self.add(self.button_box)

    def set_info(self, info_text):
        self.info.text = info_text

    def update_info(self, *args):
        pass

    def set_enabled_new(self, status):
        self.button_new.enabled = status


class SectionBills(Section):
    """Create the section for the bills."""

    def __init__(self, list_source, on_press_show=None, on_press_new=None, **kwargs):
        super().__init__(
            list_source = list_source,
            style = kwargs.get('style', style_section_rechnungen),
            title = 'Rechnungen', 
            on_press_show = on_press_show, 
            on_press_new = on_press_new,
            new_enabled = True
        )
    
    def update_info(self, *args):
        count = len([item for item in self.list_source if not item.bezahlt])

        match count:
            case 0:
                self.info.text = 'Keine offenen Rechnungen.'
            case 1:
                self.info.text = '1 Rechnung noch nicht bezahlt.'
            case _:
                self.info.text = f'{count} Rechnungen noch nicht bezahlt.'


class SectionAllowance(Section):
    """Create the section for the allowance."""

    def __init__(self, list_source, on_press_show=None, on_press_new=None, **kwargs):
        super().__init__(
            list_source = list_source,
            style = style_section_beihilfe, 
            title = 'Beihilfe', 
            on_press_show = on_press_show, 
            on_press_new = on_press_new,
            new_enabled = False
        )

    def update_info(self, *args):
        count = len(self.list_source)
        
        match count:
            case 0:
                self.info.text = 'Keine offenen Rechnungen.'
                self.button_new.enabled = False
            case 1:
                self.info.text = '1 Rechnung noch nicht eingereicht.'
                self.button_new.enabled = True
            case _:
                self.info.text = f'{count} Rechnungen noch nicht eingereicht.'
                self.button_new.enabled = True


class SectionInsurance(Section):
    """Create the section for the insurance."""

    def __init__(self, list_source, on_press_show=None, on_press_new=None, **kwargs):
        super().__init__(
            list_source = list_source,
            style = style_section_pkv, 
            title = 'Private KV', 
            on_press_show = on_press_show, 
            on_press_new = on_press_new,
            new_enabled = False
        )

    def update_info(self, *args):
        # Anzeige und Buttons der offenen Rechnungen aktualisieren
        count = len(self.list_source)
        
        match count:
            case 0:
                self.info.text = 'Keine offenen Rechnungen.'
                self.button_new.enabled = False
            case 1:
                self.info.text = '1 Rechnung noch nicht eingereicht.'
                self.button_new.enabled = True
            case _:
                self.info.text = f'{count} Rechnungen noch nicht eingereicht.'
                self.button_new.enabled = True


class ConnectedButton(toga.Button):
    """Erzeugt einen Button, dessen Status von einer Datenquelle abhängt."""

    def __init__(self, list_source, **kwargs):
        super().__init__(kwargs.get('text', ''), style=kwargs.get('style', style_button), on_press=kwargs.get('on_press', None), enabled=kwargs.get('enabled', True))
        self.list_source = list_source
        self.listener = ButtonListener(self)
        self.list_source.add_listener(self.listener)
        self.update_status()

    def set_list_source(self, list_source):
        self.list_source = list_source
        self.list_source.add_listener(self.listener)
        self.update_status()

    def update_status(self, *args):
        if self.list_source:
            self.enabled = True
        else:
            self.enabled = False


class ArchiveButton(ConnectedButton):
    """Erzeugt den Button für die Archivierung auf der Startseite."""

    def __init__(self, list_source, on_press, **kwargs):

        super().__init__(
            list_source = list_source,
            text = '',
            style = style_button,
            on_press = on_press,
            enabled = False,
            **kwargs
        )

    def update_status(self, *args):
        if self.list_source:
            count = len(self.list_source[0].rechnung) + len(self.list_source[0].beihilfe) + len(self.list_source[0].pkv)
        else:
            count = 0

        match count:
            case 0:
                self.enabled = False
                self.text = 'Keine archivierbaren Buchungen'
            case 1:
                self.enabled = True
                self.text = '1 Buchung archivieren'
            case _:
                self.enabled = True
                self.text = f'{count} Buchungen archivieren'

        

class TopBox(toga.Box):
    """Create a box with a label and a button at the top of a window."""

    def __init__(self, label_text, style_box, target_back):
        super().__init__(style=style_box)
        self.button = toga.Button('Zurück', on_press=target_back, style=style_button)
        self.label = toga.Label(label_text, style=style_label_h1_hell)
        self.add(self.button)
        self.add(self.label)

    def set_label(self, label_text):
        self.label.text = label_text

    def _set_on_press(self, target_back):
        self.button.on_press = target_back


class InfoLabel(toga.Box):
    """Create two labels in a row with a title and a value."""

    def __init__(self, title, value=''):
        super().__init__(style=style_box_row)
        self.label_title = toga.Label(title, style=style_label_info)
        self.label_value = toga.Label(value, style=style_label_detail)
        self.add(self.label_title)
        self.add(self.label_value)

    def set_value(self, value):
        self.label_value.text = value


class InfoLink(toga.Box):
    """"Create a button with a hyperlink."""

    def __init__(self, text, on_press=None):
        super().__init__(style=style_box_row)
        self.button = toga.Button(text, on_press=on_press, style=style_button_link)
        self.add(self.button)

    def hide_button(self):
        self.remove(self.button)

    def show_button(self):
        self.add(self.button)

    def set_text(self, text):
        self.button.text = text


class HelpButton(toga.Button):
    """Create a button with a help text."""

    def __init__(self, **kwargs):
        super().__init__(
            '?', 
            on_press=lambda widget: kwargs.get('window', None).info_dialog(kwargs.get('helptitle', 'Hilfe'), kwargs.get('helptext', 'Keine Hilfe verfügbar.')), 
            style=style_button_help
        )


class TableEntry(toga.Box):
    """Erstellt eine Zeile der app-eigenen Tabellenklasse."""

    def __init__(
            self, 
            even = False, 
            texts = ['', '', ''],
            buttons = {'text': [''], 'button_id': [None], 'style': [None], 'on_press': [None]}, 
            **kwargs
        ):

        if even:
            style_box = style_table_box_even
        else:
            style_box = style_table_box_odd

        super().__init__(style=style_box)
    
        # create the elements        
        self.label_box = toga.Box(style=style_table_label_box)
        self.label_inner_box = toga.Box(style=style_box_column_left)
        self.label_inner_upper_box = toga.Box(style=style_box_row)
        self.button_box = toga.Box(style=style_table_button_box)

        self.label_top_left = toga.Label(texts[0], style=style_table_label_top_left)
        self.label_top_right = toga.Label(texts[1], style=style_table_label_top_right)
        self.label_bottom = toga.Label(texts[2], style=style_table_label_bottom) 

        self.label_box.add(self.label_inner_box)
        self.label_inner_box.add(self.label_inner_upper_box)
        self.label_inner_upper_box.add(self.label_top_left)
        self.label_inner_upper_box.add(self.label_top_right)
        self.label_inner_box.add(self.label_bottom)

        # get the maximum number of buttons in the dictionary
        number_of_buttons = max([len(buttons[key]) for key in buttons.keys()])

        # prepare the dictionary for the buttons
        # if the key text is not present or shorter than number_of_buttons fill it up with empty strings
        # if the key on_press is not present or shorter than number_of_buttons fill it up with None
        # if the key button_id is not present or shorter than number_of_buttons fill it up with None
        # if the key style is not present or shorter than number_of_buttons fill it up with style_table_button
        for key in buttons.keys():
            if key == 'text':
                if len(buttons[key]) < number_of_buttons:
                    buttons[key] += [''] * (number_of_buttons - len(buttons[key]))
            elif key == 'button_id':
                if len(buttons[key]) < number_of_buttons:
                    buttons[key] += [None] * (number_of_buttons - len(buttons[key]))
            elif key == 'style':
                if len(buttons[key]) < number_of_buttons:
                    buttons[key] += [style_table_button] * (number_of_buttons - len(buttons[key]))
            elif key == 'on_press':
                if len(buttons[key]) < number_of_buttons:
                    buttons[key] += [None] * (number_of_buttons - len(buttons[key]))
            else:
                print('+++ Kontolupe: Unbekannter Key in TableEntry.__init__(): ' + key)

        # if the key 'text' is not present in the dictionary, add it with empty strings of length number_of_buttons
        if 'text' not in buttons.keys():
            buttons['text'] = [''] * number_of_buttons

        # if the key 'button_id' is not present in the dictionary, add it with None of length number_of_buttons
        if 'button_id' not in buttons.keys():
            buttons['button_id'] = [None] * number_of_buttons

        # if the key 'style' is not present in the dictionary, add it with style_table_button of length number_of_buttons
        if 'style' not in buttons.keys():
            buttons['style'] = [style_table_button] * number_of_buttons

        # if any of the values in the list with the key 'style' is None, replace it with style_table_button
        for i in range(number_of_buttons):
            if buttons['style'][i] is None:
                buttons['style'][i] = style_table_button

        # if the key 'on_press' is not present in the dictionary, add it with None of length number_of_buttons
        if 'on_press' not in buttons.keys():
            buttons['on_press'] = [None] * number_of_buttons

        # create the buttons
        for i in range(number_of_buttons):
            self.button_box.add(toga.Button(
                buttons['text'][i], 
                id=buttons['button_id'][i], 
                style=buttons['style'][i],
                on_press=buttons['on_press'][i]
            ))

        self.add(self.label_box)
        self.add(self.button_box)

    def show(self):
        self.add(self.label_box)
        self.add(self.button_box)

    def hide(self):
        self.remove(self.label_box)
        self.remove(self.button_box)


class Table(toga.Box):
    """Grundklasse für eine app-eigene Tabelle."""

    def __init__(self, list_source, **kwargs):
        super().__init__(style=style_box_column)
        self.list_source = list_source
        self.listener = TableListener(self)
        self.list_source.add_listener(self.listener)
        self.create()

    def set_list_source(self, list_source):
        self.list_source = list_source
        self.list_source.add_listener(self.listener)
        self.update()

    def create(self):
        for index in range(len(self.list_source)):
            row = self.convert(index)
            self.add(TableEntry(
                texts   = row[0],
                even    = (index % 2 == 0),
                buttons = row[1]
            ))

    def convert(self, index):
        texts = ['', '', '']
        button = {
            'text': [''],
            'button_id': [str(index)],
            'style': [None],
            'on_press': [None]
        }
        return [texts, button]
    
    def clear(self):
        while len(self.children) > 0:
            self.remove(self.children[0])

    def change_row(self, item):
        index = self.list_source.index(item)
        row = self.convert(index)
        self.remove(self.children[index])
        self.insert(index, row)

    def insert_row(self, index, item):
        row = self.convert(index)
        self.insert(
            index,
            TableEntry(
                texts   = row[0],
                even    = (index % 2 == 0),
                buttons = row[1]
            )
        )

    def remove_row(self, index, item):
        self.remove(self.children[index])

    def update(self):
        self.clear()
        self.create()


class TableOpenBookings(Table):
    """Erstellt die Tabelle zur Anzeige der offenen Buchungen."""

    def __init__(self, list_bookings, on_press_pay, on_press_info, **kwargs):
        self.on_press_pay = on_press_pay
        self.on_press_info = on_press_info
        super().__init__(list_bookings, **kwargs)
    
    def convert(self, index):
        booking = self.list_source[index]
        texts = ['', '', '']
        button = {
            'button_id': [str(index), 'i'+str(index)],
            'style': [None, style_button_help],
            'on_press': [self.on_press_pay, self.on_press_info]
        }
        match booking.typ:
            case 'Rechnung':
                texts[0] = 'Rg. ' + booking.info
                texts[1] = ''
                texts[2] = booking.betrag_euro + (', geplant am ' + booking.buchungsdatum if booking.buchungsdatum else '')
                button['text'] = ['Bezahlt', '?']
            case 'Beihilfe':
                texts[0] = 'Beihilfe'
                texts[1] = ' vom ' + booking.datum	
                texts[2] = 'über ' + booking.betrag_euro 
                button['text'] = ['Erstattet', '?']
            case 'PKV':
                texts[0] = 'Private KV' 
                texts[1] = ' vom ' + booking.datum
                texts[2] = 'über ' + booking.betrag_euro
                button['text'] = ['Erstattet', '?']
            case _:
                texts[0] = 'Unbekannter Buchungstyp'
                texts[1] = ''
                texts[2] = 'vom ' + booking.datum + ' über ' + booking.betrag_euro
                button['text'] = ['Gebucht', '?']

        return [texts, button]


class LabeledTextInput(toga.Box):
    """Create a box with a label and a text input."""

    def __init__(self, label_text, **kwargs):
        super().__init__(style=style_box_row)
        self.validator = Validator(kwargs.get('validator', None))
        self.label_box = toga.Box(style=style_flex_box)
        self.input_box = toga.Box(style=style_flex_box)
        self.label = toga.Label(label_text, style=style_label_input_noflex)
        self.text_input = toga.TextInput(
            style=kwargs.get('style_input', style_input), 
            placeholder=kwargs.get('placeholder', None), 
            on_lose_focus=self.validator.rectify, 
            readonly=kwargs.get('readonly', False),
            on_change=kwargs.get('on_change', None)
        )

        self.label_box.add(self.label)
        self.input_box.add(self.text_input)

        if kwargs.get('suffix', None):
            self.input_box.add(toga.Label(kwargs.get('suffix'), style=style_label_input_suffix))

        self.add(self.label_box)
        self.add(self.input_box)

        if 'helptext' in kwargs and 'window' in kwargs:
            self.label_box.add(HelpButton(**kwargs))

    def _set_label(self, label_text):
        self.label.text = label_text

    def _get_label(self):
        return self.label.text
    
    def hide(self):
        self.remove(self.label_box)
        self.remove(self.input_box)

    def show(self):
        self.add(self.label_box)
        self.add(self.input_box)

    def set_value(self, value):
        self.text_input.value = value
        self.validator.rectify(self.text_input)

    def get_value(self):
        self.validator.rectify(self.text_input)
        return self.text_input.value
    
    def _set_on_lose_focus(self, on_lose_focus):
        self.text_input.on_lose_focus = on_lose_focus

    def is_empty(self):
        return not self.text_input or not self.text_input.value
    
    def is_valid(self):
        return self.validator.is_valid(self.text_input)
    

class LabeledDateInput(LabeledTextInput):
    """Create a box with a label and a text input for dates."""

    def __init__(self, label_text, **kwargs):
        super().__init__(
            label_text, 
            placeholder = 'TT.MM.JJJJ', 
            validator   = 'date', 
            on_change   = self.__on_textinput_change,
            style_input = style_input_datepicker,
            **kwargs
        )

        self.datepicker = toga.DateInput(style=style_datepicker, on_change=self.__on_datepicker_change)
        self.input_box.insert(0, self.datepicker)

    def __on_datepicker_change(self, widget):
        self.set_value(widget.value)

    def __on_textinput_change(self, widget):
        # self.datepicker.value = self.get_value_as_date()
        pass

    def get_value_as_date(self):
        return None if not self.text_input.value else datetime.strptime(self.text_input.value, '%d.%m.%Y').date()

    def get_value(self):
        self.validator.rectify(self.text_input)
        return self.text_input.value
        
    def set_value(self, value):
        if value is None:
            self.text_input.value = ''
        elif isinstance(value, str):
            self.text_input.value = value
        elif isinstance(value, datetime):
            self.text_input.value = value.strftime('%d.%m.%Y')
        else:
            self.text_input.value = value

        self.validator.rectify(self.text_input)


class LabeledFloatInput(LabeledTextInput):
    """Create a box with a label and a text input for floats."""

    def __init__(self, label_text, suffix=None, **kwargs):
        super().__init__(label_text, suffix=suffix, validator='float', **kwargs)

    def get_value(self):
        self.validator.rectify(self.text_input)
        return 0.0 if not self.text_input.value else float(self.text_input.value.replace(',', '.'))
    
    def get_value_as_str(self):
        self.validator.rectify(self.text_input)
        return self.text_input.value
    
    def set_value(self, value):     
        if value is None:
            self.text_input.value = ''
        elif isinstance(value, str):
            self.text_input.value = value
        elif isinstance(value, float):
            self.text_input.value = format(value, '.2f').replace('.', ',')
        elif isinstance(value, int):
            self.text_input.value = format(float(value), '.2f').replace('.', ',')

        self.validator.rectify(self.text_input)
    

class LabeledIntInput(LabeledTextInput):
    """Create a box with a label and a text input for integers."""

    def __init__(self, label_text, **kwargs):
        super().__init__(label_text, validator='int', **kwargs)

    def get_value(self):
        self.validator.rectify(self.text_input)
        return 0 if not self.text_input.value else int(self.text_input.value)
    
    def get_value_as_str(self):
        self.validator.rectify(self.text_input)
        return self.text_input.value
    
    def set_value(self, value):
        if value is None:
            self.text_input.value = ''
        elif isinstance(value, str):
            self.text_input.value = value
        elif isinstance(value, int):
            self.text_input.value = str(value)

        self.validator.rectify(self.text_input)


class LabeledPercentInput(LabeledTextInput):
    """Create a box with a label and a text input for percentages."""

    def __init__(self, label_text, **kwargs):
        super().__init__(label_text, validator='percent', **kwargs)

    def get_value(self):
        self.validator.rectify(self.text_input)
        return 0 if not self.text_input.value else int(self.text_input.value)
    
    def get_value_as_str(self):
        self.validator.rectify(self.text_input)
        return self.text_input.value
    
    def set_value(self, value):
        if value is None:
            self.text_input.value = ''
        elif isinstance(value, str):
            self.text_input.value = value
        elif isinstance(value, int):
            self.text_input.value = str(value)

        self.validator.rectify(self.text_input)


class LabeledPostalInput(LabeledTextInput):
    """Create a box with a label and a text input for postal codes."""

    def __init__(self, label_text, **kwargs):
        super().__init__(label_text, validator='postal', **kwargs)


class LabeledPhoneInput(LabeledTextInput):
    """Create a box with a label and a text input for phone numbers."""

    def __init__(self, label_text, **kwargs):
        super().__init__(label_text, validator='phone', **kwargs)


class LabeledEmailInput(LabeledTextInput):
    """Create a box with a label and a text input for email addresses."""

    def __init__(self, label_text, **kwargs):
        super().__init__(label_text, validator='email', **kwargs)


class LabeledWebsiteInput(LabeledTextInput):
    """Create a box with a label and a text input for website addresses."""

    def __init__(self, label_text, **kwargs):
        super().__init__(label_text, placeholder='www.', validator='website', **kwargs)


class LabeledMultilineTextInput(toga.Box):
    """Create a box with a label and a multiline text input."""

    def __init__(self, label_text, **kwargs):
        self.label = toga.Label(label_text, style=style_label_input)
        self.text_input = toga.MultilineTextInput(style=style_input, readonly=kwargs.get('readonly', False))
        
        self.label_box = toga.Box(style=style_flex_box, children=[self.label])
        self.input_box = toga.Box(style=style_flex_box, children=[self.text_input])
        super().__init__(style=style_box_row, children=[self.label_box, self.input_box])

        # Help Button
        if 'helptext' in kwargs and 'window' in kwargs:
            self.label_box.add(HelpButton(**kwargs))

    def show(self):
        self.add(self.label_box)
        self.add(self.input_box)

    def hide(self):
        self.remove(self.label_box)
        self.remove(self.input_box)

    def set_label(self, label_text):
        self.label.text = label_text

    def get_label(self):
        return self.label.text

    def set_value(self, value):
        self.text_input.value = value

    def get_value(self):
        return self.text_input.value


class LabeledSelection(toga.Box):
    """Create a box with a label and a selection."""

    def __init__(self, label_text, data, accessor=None, value=None, **kwargs):
        
        self.label = toga.Label(label_text, style=style_label_input)

        self.selection = toga.Selection(
            style=style_selection,
            items=data,
            accessor=accessor,
            value=value,
            on_change=kwargs.get('on_change', None)
        )
        
        self.label_box = toga.Box(style=style_flex_box, children=[self.label])
        self.selection_box = toga.Box(style=style_flex_box, children=[self.selection])
        super().__init__(style=style_box_row, children=[self.label_box, self.selection_box])

        # Help Button
        if 'helptext' in kwargs and 'window' in kwargs:
            self.label_box.add(HelpButton(**kwargs))

    def show(self):
        self.add(self.label_box)
        self.add(self.selection_box)

    def hide(self):
        self.remove(self.label_box)
        self.remove(self.selection_box)

    def set_label(self, label_text):
        self.label.text = label_text

    def get_label(self):
        return self.label.text

    def set_value(self, value):
        self.selection.value = value

    def get_value(self):
        return self.selection.value
    
    def set_items(self, items):
        self.selection.items = items

    def get_items(self):
        return self.selection.items
    
    def set_on_change(self, on_change):
        self.selection.on_change = on_change


class LabeledDoubleSelection(toga.Box):
    """Create a box with a label and two selection fields."""

    def __init__(self, label_text, data, accessors=[None, None], values=[None, None], **kwargs):

        self.label = toga.Label(label_text, style=style_label_input)

        self.selections = []

        self.selections.append(toga.Selection(
            style=style_selection,
            items=data[0],
            accessor=accessors[0],
            value=values[0],
            on_change=kwargs.get('on_change', [None, None])[0]
        ))

        self.selections.append(toga.Selection(
            style=style_selection_flex2,
            items=data[1],
            accessor=accessors[1],
            value=values[1],
            on_change=kwargs.get('on_change', [None, None])[1]
        ))

        # Boxes
        self.label_box = toga.Box(style=style_flex_box, children=[self.label])
        self.selection_box = toga.Box(style=style_flex_box2, children=self.selections)
        super().__init__(style=style_box_row, children=[self.label_box, self.selection_box])

        # Help Button
        if 'helptext' in kwargs and 'window' in kwargs:
            self.label_box.add(HelpButton(**kwargs))

    def set_label(self, label_text):
        self.label.text = label_text

    def get_label(self):
        return self.label.text

    def set_value(self, value, index=None):
        if index is None:
            self.selections[0].value = value[0]
            self.selections[1].value = value[1]
        else:
            self.selections[index].value = value

    def get_value(self, index=None):
        if index is None:
            return [self.selections[0].value, self.selections[1].value]
        else:
            return self.selections[index].value
    
    def set_items(self, items, index=None):
        if index is None:
            self.selections[0].items = items[0]
            self.selections[1].items = items[1]
        else:
            self.selections[index].items = items

    def get_items(self, index=None):
        if index is None:
            return [self.selections[0].items, self.selections[1].items]
        else:
            return self.selections[index].items
        
    def add_item(self, item, index=None):
        if index is None:
            self.selections[0].items.insert(0, item[0])
            self.selections[1].items.insert(0, item[1])
        else:
            self.selections[index].items.insert(0, item)
    
    def set_on_change(self, on_change, index=None):
        if index is None:
            self.selections[0].on_change = on_change[0]
            self.selections[1].on_change = on_change[1]
        else:
            self.selections[index].on_change = on_change


class LabeledSwitch(toga.Box):
    """Create a box with a label and a switch."""

    def __init__(self, label_text, **kwargs):
        super().__init__(style=style_box_row)
        self.label_box = toga.Box(style=style_flex_box)
        self.switch_box = toga.Box(style=style_noflex_box)
        self.label = toga.Label(label_text, style=style_label_input_noflex)

        self.switch = toga.Switch(
            '', 
            style=kwargs.get('style', style_switch), 
            on_change=kwargs.get('on_change', None), 
            value=kwargs.get('value', False)
        )

        self.label_box.add(self.label)
        self.switch_box.add(self.switch)
        self.add(self.label_box)
        self.add(self.switch_box)

        if 'helptext' in kwargs and 'window' in kwargs:
            self.label_box.add(HelpButton(**kwargs))

    def set_label(self, label_text):
        self.label.text = label_text

    def get_label(self):
        return self.label.text
    
    def hide(self):
        self.remove(self.label_box)
        self.remove(self.switch_box)

    def show(self):
        self.add(self.label_box)
        self.add(self.switch_box)

    def set_value(self, value):
        self.switch.value = value

    def get_value(self):
        return self.switch.value
    
    def _set_on_change(self, on_change):
        self.switch.on_change = on_change


class ButtonBox(toga.Box):
    """Create a box with up to four buttons."""

    def __init__(self, labels, targets, ids=None, enabled=True, connections=None, **kwargs):
        """Create a box with up to four buttons at the bottom of a window."""
        if not len(labels) == len(targets):
            raise ValueError('Labels and targets must have the same length.')
        
        if ids is not None and not len(labels) == len(ids):
            raise ValueError('There must be either no IDs or as many IDs as labels and targets.')
        
        if ids is None:
            ids = [None] * len(labels)

        if connections is  None:
            connections = [None] * len(labels)
        else:
            if len(connections) != len(labels):
                raise ValueError('The length of connections must be the same as labels (None allowed).')
            

        # enabled should be a list of booleans of the same length than labels and targets
        # if enabled is a boolean, it will be converted to a list of the same length than labels and targets
        # if it is a list of booleans that is shorter than labels and targets, it will be extended to the same length with True
        if isinstance(enabled, bool):
            enabled = [enabled] * len(labels)
        elif isinstance(enabled, list):
            if len(enabled) < len(labels):
                enabled.extend([True] * (len(labels) - len(enabled)))

        self.buttons = []
        for label, target, button_id, status, connection in zip(labels, targets, ids, enabled, connections):
            if isinstance(connection, ListSource):
                self.buttons.append(ConnectedButton(
                    connection, 
                    text=label, 
                    on_press=target, 
                    id=button_id, 
                    style=style_button, 
                    enabled=status
                ))
            else:
                self.buttons.append(toga.Button(label, on_press=target, id=button_id, style=style_button, enabled=status))
            

        if len(self.buttons) < 4:
            super().__init__(style=style_box_row)
            for button in self.buttons:
                self.add(button)
        elif len(self.buttons) == 4:
            super().__init__(style=style_box_column)
            self.box1 = toga.Box(style=style_box_row)
            self.box2 = toga.Box(style=style_box_row)
            for button in self.buttons[:2]:
                self.box1.add(button)
            for button in self.buttons[2:]:
                self.box2.add(button)
            self.add(self.box1)
            self.add(self.box2)

    def set_connection(self, button_id, connection):
        """Set a connection to a button by its ID."""
        for button in self.buttons:
            if button.id == button_id:
                button.set_list_source(connection)
                return
        else:
            print("+++ Kontolupe: Button mit ID " + str(button_id) + " nicht gefunden.")

    def set_enabled(self, button_id, status):
        """Enable or disable a button by its ID."""
        for button in self.buttons:
            if button.id == button_id:
                button.enabled = status
                return
        else:
            print("+++ Kontolupe: Button mit ID " + str(button_id) + " nicht gefunden.")


class SubtextDivider(toga.Box):
    """Create a divider with a subtext."""

    def __init__(self, text):
        """Create a divider with a subtext."""
        super().__init__(style=style_box_column)
        self.divider = toga.Divider(style=style_divider_subtext)
        self.label = toga.Label(text, style=style_label_subtext)
        self.add(self.divider)
        self.add(self.label)