"""Layout-Definitionen für die Kontolupe-App."""

from toga.style.pack import COLUMN, LEFT, RIGHT, ROW, TOP, BOTTOM, CENTER, Pack

FARBE_DUNKEL                    = '#222222'
FARBE_HELL                      = '#FFFFFF'
FARBE_BLAU                      = '#368ba8'
FARBE_AKZENTBLAU                = '#18799E'
FARBE_LILA                      = '#7758a8'
FARBE_GRUEN                     = '#4c9c60'
FARBE_GRAU                      = '#444444'
FARBE_MITTEL                    = '#666666' 
FARBE_HELLGRAU                  = '#EEEEEE'
FARBE_ROT                       = '#AE133E'

# Allgemeine Styles
style_box_column                = Pack(direction=COLUMN, alignment=CENTER)
style_box_column_left           = Pack(direction=COLUMN, alignment=LEFT)
style_box_row                   = Pack(direction=ROW, alignment=CENTER)
style_scroll_container          = Pack(flex=1)
style_webview                   = Pack(flex=1)
style_label_h1                  = Pack(font_size=14, font_weight='bold', text_align=CENTER, padding=10, padding_bottom=20, color=FARBE_DUNKEL)
style_label_h1_hell             = Pack(font_size=14, font_weight='bold', text_align=CENTER, padding=10, padding_bottom=20, color=FARBE_HELL)
style_label_h2                  = Pack(font_size=11, font_weight='bold', text_align=CENTER, padding=10, color=FARBE_DUNKEL)
style_label_h2_hell             = Pack(font_size=11, font_weight='bold', text_align=CENTER, padding=10, color=FARBE_HELL)
style_label                     = Pack(text_align=LEFT, padding=10, color=FARBE_DUNKEL)
style_label_hell                = Pack(text_align=LEFT, padding=10, color=FARBE_HELL)
style_label_center              = Pack(text_align=CENTER, padding=10, color=FARBE_DUNKEL)
style_label_center_hell         = Pack(text_align=CENTER, padding=10, color=FARBE_HELL)
style_button                    = Pack(flex=1, padding=5, color=FARBE_DUNKEL)
style_input                     = Pack(flex=1, padding=10, color=FARBE_DUNKEL)
style_input_datepicker          = Pack(flex=1, padding=10, padding_left=0, color=FARBE_DUNKEL)
style_selection                 = Pack(flex=1, padding=10, color=FARBE_DUNKEL)
style_selection_flex2           = Pack(flex=2, padding=10, color=FARBE_DUNKEL)
style_selection_noflex          = Pack(padding=10, color=FARBE_DUNKEL)
style_label_input               = Pack(flex=1, padding=10, text_align=LEFT, color=FARBE_DUNKEL)
style_label_input_hell          = Pack(flex=1, padding=10, text_align=LEFT, color=FARBE_HELL)
style_label_input_noflex        = Pack(padding=10, color=FARBE_DUNKEL)
style_label_input_hell_noflex   = Pack(padding=10, color=FARBE_HELL)
style_label_input_suffix        = Pack(padding=10, padding_left=0, color=FARBE_DUNKEL)
style_label_form                = Pack(padding=0, color=FARBE_DUNKEL)
style_table                     = Pack(flex=1, padding=10, color=FARBE_DUNKEL)
style_table_hell                = Pack(flex=1, padding=10, color=FARBE_HELL)
style_switch                    = Pack(flex=1, padding=10, color=FARBE_DUNKEL)
style_switch_center             = Pack(padding=5, color=FARBE_DUNKEL)
style_switch_hell               = Pack(flex=1, padding=10, color=FARBE_HELL)
style_switch_center_hell        = Pack(padding=10, color=FARBE_HELL)
style_switch_box_center         = Pack(direction=ROW, alignment=CENTER)
style_divider                   = Pack(padding=10, background_color=FARBE_MITTEL)
style_datepicker                = Pack(flex=0, padding=10, padding_right=0, color=FARBE_DUNKEL, width=40)   

# Spezifische Styles
style_table_auswahl             = Pack(flex=1, padding=10, height=200, color=FARBE_DUNKEL)
style_label_info                = Pack(flex=1, padding=10, text_align=LEFT, color=FARBE_DUNKEL)
style_label_detail              = Pack(flex=1, padding=10, text_align=LEFT, color=FARBE_DUNKEL)
style_label_subtext             = Pack(flex=1, padding=10, padding_top=0, text_align=RIGHT, color=FARBE_MITTEL, font_size=8)
style_divider_subtext           = Pack(padding=10, padding_bottom=0, background_color=FARBE_MITTEL)
style_button_link               = Pack(padding=10, text_align=CENTER, background_color=FARBE_HELL, color=FARBE_BLAU, font_weight='bold')
style_display                   = Pack(flex=1, padding=10, text_align=LEFT, color=FARBE_DUNKEL)
style_flex_box                  = Pack(flex=1, direction=ROW, alignment=CENTER)
style_flex_box2                 = Pack(flex=2, direction=ROW, alignment=CENTER)
style_noflex_box                = Pack(direction=ROW, alignment=CENTER)

# Startseite
style_box_offene_buchungen      = Pack(direction=COLUMN, alignment=CENTER, background_color=FARBE_BLAU)
style_start_summe               = Pack(font_size=14, font_weight='bold', text_align=CENTER, padding=20, color=FARBE_HELL, background_color=FARBE_BLAU)
style_table_offene_buchungen    = Pack(flex=1, padding=10, color=FARBE_DUNKEL, height=200)
style_section_start             = Pack(direction=COLUMN, alignment=CENTER, padding=0)
style_section_rechnungen        = Pack(direction=COLUMN, alignment=CENTER, padding=0, padding_top=10, padding_bottom=10, background_color=FARBE_BLAU)
style_section_beihilfe          = Pack(direction=COLUMN, alignment=CENTER, padding=0, padding_top=10, padding_bottom=10, background_color=FARBE_LILA)
style_section_pkv               = Pack(direction=COLUMN, alignment=CENTER, padding=0, padding_top=10, padding_bottom=10, background_color=FARBE_GRUEN)
style_section_daten             = Pack(direction=COLUMN, alignment=CENTER, padding=0, padding_bottom=10)
style_label_h2_start            = Pack(font_size=14, font_weight='bold', text_align=CENTER, padding=10, padding_bottom=5, padding_top=15, color=FARBE_HELL)
style_box_buttons_start         = Pack(padding_bottom=10, padding_top=5, padding_left=0, padding_right=0, direction=ROW, alignment=CENTER)
style_label_section             = Pack(font_weight='normal', text_align=CENTER, padding_left=10, padding_right=10, color=FARBE_HELL)

# Farbige Themenbereiche
style_box_column_rechnungen     = Pack(direction=COLUMN, alignment=CENTER, background_color=FARBE_BLAU, padding_bottom=10)
style_box_column_beihilfe       = Pack(direction=COLUMN, alignment=CENTER, background_color=FARBE_LILA, padding_bottom=10)
style_box_column_pkv            = Pack(direction=COLUMN, alignment=CENTER, background_color=FARBE_GRUEN, padding_bottom=10)
style_box_column_dunkel         = Pack(direction=COLUMN, alignment=CENTER, background_color=FARBE_GRAU, padding_bottom=10)

# Init-Seite
style_box_part                  = Pack(direction=COLUMN, alignment=CENTER, padding_top=10, background_color=FARBE_HELLGRAU)
style_box_part_beihilfe         = Pack(direction=COLUMN, alignment=CENTER, background_color=FARBE_LILA)
style_box_part_pkv              = Pack(direction=COLUMN, alignment=CENTER, background_color=FARBE_GRUEN)
style_box_part_button           = Pack(direction=COLUMN, alignment=CENTER, padding_top=10, padding_bottom=10, background_color=FARBE_GRAU)
style_init_button               = Pack(padding=20, color=FARBE_DUNKEL)
style_box_headline              = Pack(direction=COLUMN, alignment=CENTER, background_color=FARBE_BLAU, padding_bottom=10)
style_label_subline             = Pack(font_size=14, font_weight='bold', text_align=CENTER, padding=10, padding_top=15, color=FARBE_DUNKEL)
style_label_subline_hell        = Pack(font_size=14, font_weight='bold', text_align=CENTER, padding=10, padding_top=15, color=FARBE_HELL)
style_label_headline            = Pack(font_size=14, font_weight='bold', text_align=CENTER, padding=10, padding_top=20, padding_bottom=20, color=FARBE_HELL)
style_description               = Pack(font_weight='normal', text_align=CENTER, padding=10, padding_top=0, color=FARBE_DUNKEL)
style_description_hell          = Pack(font_weight='normal', text_align=CENTER, padding=10, padding_top=0, color=FARBE_HELL)

# Table styles
style_table_label_top_left      = Pack(color=FARBE_DUNKEL, font_weight='bold')
style_table_label_top_right     = Pack(color=FARBE_DUNKEL)
style_table_label_bottom        = Pack(color=FARBE_DUNKEL)
style_table_button              = Pack(flex=0, padding=0, color=FARBE_DUNKEL, height=40, font_size=9)
style_button_help               = Pack(flex=0, padding=0, color=FARBE_DUNKEL, width=35, height=40, font_size=9)
style_table_label_box           = Pack(flex=1, direction=ROW, alignment=LEFT, padding=10)
style_table_button_box          = Pack(direction=ROW, alignment=RIGHT, padding_right=10)
style_table_box_odd             = Pack(direction=ROW, alignment=CENTER, background_color=FARBE_HELLGRAU)
style_table_box_even            = Pack(direction=ROW, alignment=CENTER, background_color=FARBE_HELL)

# Statistik
style_canvas                    = Pack()