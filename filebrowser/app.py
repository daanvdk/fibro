from textual.app import App as BaseApp
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.binding import Binding

from .browser import Browser
from .preview import Preview
from .prompt import Prompt
from .simple_input import SimpleInput
from .utils import show_path


class App(BaseApp):

    CSS_PATH = 'app.tcss'

    BINDINGS = [
        Binding('escape', 'quit'),

        Binding('up', 'nav_up'),
        Binding('down', 'nav_down'),
        Binding('enter', 'select'),

        Binding('alt+h', 'toggle_hidden'),
        Binding('alt+c', 'create'),
        Binding('alt+r', 'rename'),
        Binding('alt+d', 'delete'),
    ]

    def compose(self):
        with Horizontal():
            with Vertical(classes='pane'):
                yield SimpleInput(id='search')
                with VerticalScroll():
                    yield Browser()
            with VerticalScroll(classes='pane'):
                yield Preview()

    def on_mount(self):
        self.theme = 'textual-ansi'

        browser = self.query_one(Browser)
        self.set_title(browser.path)
        self.watch(browser, 'path', self.set_title)

    def set_title(self, path):
        self.console.set_window_title(f'fb: {show_path(path)}')

    def action_select(self):
        self.query_one(Browser).action_select()

    def action_nav_up(self):
        self.query_one(Browser).action_nav_up()

    def action_nav_down(self):
        self.query_one(Browser).action_nav_down()

    def action_toggle_hidden(self):
        self.query_one(Browser).action_toggle_hidden()

    def action_create(self):
        self.query_one(Browser).action_create()

    def action_rename(self):
        self.query_one(Browser).action_rename()

    def action_delete(self):
        self.query_one(Browser).action_delete()

    def prompt(self, label, *, default='', callback=None):
        if callback is None:
            return lambda callback: self.prompt(label, default=default, callback=callback)

        input = self.query_one(SimpleInput)

        def wrapped_callback(value):
            input.focus()
            callback(value)

        input.blur()
        self.push_screen(Prompt(label, default, wrapped_callback))
