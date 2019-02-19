from pyglui import ui
from plugin import Plugin
from glfw import *
import gi
from threading import Thread
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class EEG(Plugin):
    # Calling add_menu() will create an icon in the icon bar that represents
    # your plugin. You can customize this icon with a symbol of your choice.
    icon_chr = '@'  # custom menu icon symbol

    # The default icon font is Roboto: https://fonts.google.com/specimen/Roboto
    # Alternatively, you can use icons from the Pupil Icon font:
    # https://github.com/pupil-labs/pupil-icon-font
    icon_font = 'roboto'  # or `pupil_icons` when using the Pupil Icon font

    def __init__(self, g_pool, example_param=1.0):
        super().__init__(g_pool)
        self.show_conf0 = True
        # persistent attribute

        self.example_param = example_param

    def init_ui(self):
        # Create a floating menu
        self.add_menu()
        self.menu.label = 'EEG'
        # Create a simple info text
        help_str = "Example info text."

        self.menu.append(ui.Info_Text(help_str))
        # Add a slider that represents the persistent value
        self.menu.append(ui.Slider('example_param', self, min=0.0, step=0.05, max=1.0, label='Example Param'))
        # self.menu.append(ui.Switch("show_conf0", self.open_window, label="Display confidence for eye 0"))
        # get glfw started

        # init()
        # basic_gl_setup()

        thread = Thread(target = self.open_window)
        thread.start()




    def open_window(self):
        print('Otwieram okno')
        win = Gtk.Window()
        win.connect("destroy", Gtk.main_quit)
        win.show_all()
        Gtk.main()

    def deinit_ui(self):
        self.remove_menu()

    def get_init_dict(self):
        # all keys need to exists as keyword arguments in __init__ as well
        return {'example_param': self.example_param}

    def get_eeg_value(self):
        return 12.98

    # Callback functions
    def on_resize(window, w, h):
        pass
