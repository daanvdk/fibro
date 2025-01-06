from textual.screen import ModalScreen
from textual.binding import Binding
from textual.widgets import Static

from .simple_input import SimpleInput
from .utils import forward_bindings, ForwardMixin


class Prompt(ForwardMixin, ModalScreen):

    BINDINGS = [
        Binding('escape', 'close'),
        Binding('enter', 'accept'),
        *forward_bindings(SimpleInput),
    ]

    def __init__(self, label, default):
        super().__init__()
        self.label = label
        self.default = default

    def action_close(self):
        self.dismiss(None)

    def action_accept(self):
        value = self.query_one(SimpleInput).value
        self.dismiss(value)

    def on_key(self, event):
        self.query_one('SimpleInput').on_key(event)

    def compose(self):
        yield Static(self.label)
        yield SimpleInput(value=self.default)
