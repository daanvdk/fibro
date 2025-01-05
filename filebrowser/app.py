from pathlib import Path

from textual.app import App as BaseApp
from textual.widgets import Input
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.binding import Binding

from .browser import Browser
from .preview import Preview


HOME = Path('~').resolve()


class App(BaseApp):

    CSS_PATH = 'app.tcss'

    BINDINGS = [
        Binding('escape', 'quit', priority=True),
        Binding('up', 'nav_up', priority=True),
        Binding('down', 'nav_down', priority=True),
        Binding('enter', 'select', priority=True),
        Binding('ctrl+h', 'toggle_hidden', priority=True),
    ]

    def compose(self):
        with Horizontal():
            with Vertical(classes='pane'):
                yield Input(id='search')
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
        try:
            path = path.relative_to(HOME)
        except ValueError:
            path = str(path)
        else:
            path = f'~/{path}'

        self.console.set_window_title(f'fb: {path}')

    def action_nav_up(self):
        self.query_one(Browser).action_nav_up()

    def action_nav_down(self):
        self.query_one(Browser).action_nav_down()

    def action_select(self):
        self.query_one(Browser).action_select()

    def action_toggle_hidden(self):
        self.query_one(Browser).action_toggle_hidden()

    def action_create(self):
        self.query_one(Browser).action_create()

    def action_rename(self):
        self.query_one(Browser).action_rename()

    def action_delete(self):
        self.query_one(Browser).action_delete()
