import asyncio
from pathlib import Path

from textual.app import App as BaseApp
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.binding import Binding
from textual.reactive import var

from .config import HELIX_THEME
from .browser import Browser
from .preview import Preview
from .prompt import Prompt
from .simple_input import SimpleInput
from .utils import show_path, forward_bindings, ForwardMixin


class App(ForwardMixin, BaseApp):

    show_hidden = var(False)

    CSS_PATH = 'app.tcss'
    BINDINGS = [
        Binding('escape', 'quit'),
        Binding('alt+h', 'toggle_hidden'),
        *forward_bindings(SimpleInput, '#search'),
        *forward_bindings(Browser),
    ]

    def __init__(self, path='.'):
        super().__init__()

        path = Path(path).resolve()

        if path.is_dir():
            self.init_path = path
            self.init_selected = None
        else:
            self.init_path = path.parent
            self.init_selected = path.name

    def compose(self):
        with Horizontal():
            with Vertical(classes='pane'):
                yield SimpleInput(id='search')
                with VerticalScroll():
                    yield Browser(self.init_path, self.init_selected)
            with VerticalScroll(classes='pane'):
                yield Preview()

    def on_mount(self):
        self.register_theme(HELIX_THEME)
        self.theme = 'helix'

        browser = self.query_one(Browser)
        self.set_title(browser.path)
        self.watch(browser, 'path', self.set_title)

    def action_toggle_hidden(self):
        self.show_hidden = not self.show_hidden

    def on_key(self, event):
        if self.screen.id == '_default':
            if event.key == 'tab':
                self.query_one(Browser).action_mark()
            else:
                self.query_one('#search').on_key(event)

    def set_title(self, path):
        self.console.set_window_title(f'fb: {show_path(path)}')

    async def prompt(self, label, *, default=''):
        fut = asyncio.get_running_loop().create_future()
        self.push_screen(Prompt(label, default), fut.set_result)
        return await fut
