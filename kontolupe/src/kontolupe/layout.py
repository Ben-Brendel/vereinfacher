from toga.style.pack import COLUMN, LEFT, RIGHT, ROW, TOP, BOTTOM, CENTER, Pack

FARBE_DUNKEL                    = '#222222'
FARBE_HELL                      = '#FFFFFF'
FARBE_BLAU                      = '#368ba8'
FARBE_LILA                      = '#7758a8'
FARBE_GRUEN                     = '#4c9c60'
FARBE_GRAU                      = '#444444'
FARBE_MITTEL                    = '#666666' 

# Allgemeine Styles
style_box_column                = Pack(direction=COLUMN, alignment=CENTER)
style_box_row                   = Pack(direction=ROW, alignment=CENTER)
style_scroll_container          = Pack(flex=1)
style_webview                   = Pack(flex=1)
style_label_h1                  = Pack(font_size=14, font_weight='bold', text_align=CENTER, padding=5, padding_top=10, padding_bottom=20, color=FARBE_DUNKEL)
style_label_h1_hell             = Pack(font_size=14, font_weight='bold', text_align=CENTER, padding=5, padding_top=10, padding_bottom=20, color=FARBE_HELL)
style_label_h2                  = Pack(font_size=11, font_weight='bold', text_align=CENTER, padding=5, padding_top=20, color=FARBE_DUNKEL)
style_label_h2_hell             = Pack(font_size=11, font_weight='bold', text_align=CENTER, padding=5, padding_top=20, color=FARBE_HELL)
style_label                     = Pack(font_weight='normal', text_align=LEFT, padding_left=5, padding_right=5, color=FARBE_DUNKEL)
style_label_hell                = Pack(font_weight='normal', text_align=LEFT, padding_left=5, padding_right=5, color=FARBE_HELL)
style_label_center              = Pack(font_weight='normal', text_align=CENTER, padding_left=5, padding_right=5, color=FARBE_DUNKEL)
style_label_center_hell         = Pack(font_weight='normal', text_align=CENTER, padding_left=5, padding_right=5, color=FARBE_HELL)
style_button                    = Pack(flex=1, padding=5, color=FARBE_DUNKEL)
style_input                     = Pack(flex=1, padding=5, color=FARBE_DUNKEL) 
style_selection                 = Pack(flex=1, padding=5, padding_top=20, color=FARBE_DUNKEL)
style_label_input               = Pack(flex=1, padding=5, text_align=LEFT, color=FARBE_DUNKEL)
style_label_input_hell          = Pack(flex=1, padding=5, text_align=LEFT, color=FARBE_HELL)
style_table                     = Pack(flex=1, padding=5, color=FARBE_DUNKEL)
style_table_hell                = Pack(flex=1, padding=5, color=FARBE_HELL)
style_switch                    = Pack(flex=1, padding=5, color=FARBE_DUNKEL)
style_switch_hell               = Pack(flex=1, padding=5, color=FARBE_HELL)
style_divider                   = Pack(padding=5, background_color=FARBE_MITTEL)

# Spezifische Styles
style_table_auswahl             = Pack(flex=1, padding=5, height=200, color=FARBE_DUNKEL)
style_label_info                = Pack(flex=1, padding=5, padding_top=10, text_align=LEFT, color=FARBE_DUNKEL)
style_label_detail              = Pack(flex=1, padding=5, padding_top=10, text_align=LEFT, color=FARBE_DUNKEL)
style_label_subtext             = Pack(flex=1, padding=5, padding_top=0, text_align=RIGHT, color=FARBE_MITTEL, font_size=8)
style_divider_subtext           = Pack(padding=5, padding_bottom=0, padding_top=10, background_color=FARBE_MITTEL)
style_button_link               = Pack(padding=5, padding_top=10, text_align=CENTER, background_color=FARBE_HELL, color=FARBE_BLAU, font_weight='bold')
style_display                   = Pack(flex=1, padding=5, padding_top=10, text_align=LEFT, color=FARBE_DUNKEL)

# Startseite
style_box_offene_buchungen      = Pack(direction=COLUMN, alignment=CENTER, background_color=FARBE_BLAU)
style_start_summe               = Pack(font_size=14, font_weight='bold', text_align=CENTER, padding=20, color=FARBE_HELL, background_color=FARBE_BLAU)
style_table_offene_buchungen    = Pack(flex=1, padding=5, height=200, color=FARBE_DUNKEL)
style_section_start             = Pack(direction=COLUMN, alignment=CENTER, padding=0)
style_section_rechnungen        = Pack(direction=COLUMN, alignment=CENTER, padding=0, padding_top=5, padding_bottom=5, background_color=FARBE_BLAU)
style_section_beihilfe          = Pack(direction=COLUMN, alignment=CENTER, padding=0, padding_top=5, padding_bottom=5, background_color=FARBE_LILA)
style_section_pkv               = Pack(direction=COLUMN, alignment=CENTER, padding=0, padding_top=5, padding_bottom=5, background_color=FARBE_GRUEN)
style_section_daten             = Pack(direction=COLUMN, alignment=CENTER, padding=0, padding_top=5, padding_bottom=5,)
style_label_h2_start            = Pack(font_size=11, font_weight='bold', text_align=CENTER, padding=5, padding_top=20, color=FARBE_HELL)
style_box_buttons_start         = Pack(padding=5, padding_bottom=10, direction=ROW, alignment=CENTER)
style_label_section             = Pack(font_weight='normal', text_align=CENTER, padding_left=5, padding_right=5, color=FARBE_HELL)

# Farbige Themenbereiche
style_box_column_rechnungen     = Pack(direction=COLUMN, alignment=CENTER, background_color=FARBE_BLAU, padding_bottom=10)
style_box_column_beihilfe       = Pack(direction=COLUMN, alignment=CENTER, background_color=FARBE_LILA, padding_bottom=10)
style_box_column_pkv            = Pack(direction=COLUMN, alignment=CENTER, background_color=FARBE_GRUEN, padding_bottom=10)
style_box_column_dunkel         = Pack(direction=COLUMN, alignment=CENTER, background_color=FARBE_GRAU, padding_bottom=10)