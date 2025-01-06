from pathlib import Path

from textual.app import App as BaseApp
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.binding import Binding

from .browser import Browser
from .preview import Preview
from .prompt import Prompt
from .simple_input import SimpleInput
from .utils import show_path, forward_bindings, ForwardMixin


class App(ForwardMixin, BaseApp):

    CSS_PATH = 'app.tcss'
    BINDINGS = [
        Binding('escape', 'quit'),
        *forward_bindings(SimpleInput, '#search'),
        *forward_bindings(Browser),
    ]

    def __init__(self, path='.', selected=None):
        super().__init__()
        self.init_path = Path(path).resolve()
        self.init_selected = selected

    def compose(self):
        with Horizontal():
            with Vertical(classes='pane'):
                yield SimpleInput(id='search')
                with VerticalScroll():
                    yield Browser(self.init_path, self.init_selected)
            with VerticalScroll(classes='pane'):
                yield Preview()

    def on_mount(self):
        self.theme = 'textual-ansi'

        browser = self.query_one(Browser)
        self.set_title(browser.path)
        self.watch(browser, 'path', self.set_title)

    def on_key(self, event):
        if self.screen.id == '_default':
            self.query_one('#search').on_key(event)

    def set_title(self, path):
        self.console.set_window_title(f'fb: {show_path(path)}')

    def prompt(self, label, *, default='', callback=None):
        if callback is None:
            return lambda callback: self.prompt(label, default=default, callback=callback)

        self.push_screen(Prompt(label, default), callback)
