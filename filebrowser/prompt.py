from textual.screen import ModalScreen
from textual.binding import Binding
from textual.widgets import Static

from .simple_input import SimpleInput


class Prompt(ModalScreen):

    BINDINGS = [
        Binding('escape', 'close'),
        Binding('enter', 'accept'),
    ]

    def __init__(self, label, default, callback):
        super().__init__()
        self.label = label
        self.default = default
        self.callback = callback

    def action_close(self):
        self.app.pop_screen()

    def action_accept(self):
        value = self.query_one(SimpleInput).value
        self.action_close()
        self.callback(value)

    def compose(self):
        yield Static(self.label)
        yield SimpleInput(value=self.default)
