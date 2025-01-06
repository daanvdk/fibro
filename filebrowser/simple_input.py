from textual.widget import Widget
from textual.binding import Binding
from textual.reactive import reactive

from rich.text import Text


class SimpleInput(Widget):

    BINDINGS = [
        Binding('left', 'left'),
        Binding('right', 'right'),
        Binding('backspace', 'backspace'),
    ]

    value = reactive('')
    cursor = reactive(0)

    def __init__(self, value='', **kwargs):
        super().__init__(**kwargs)
        self.set_reactive(SimpleInput.value, str(value))
        self.set_reactive(SimpleInput.cursor, len(self.value))

    def action_clear(self):
        self.action_replace('')

    def action_replace(self, value):
        self.value = str(value)
        self.cursor = len(self.value)

    def action_left(self):
        self.cursor = max(self.cursor - 1, 0)

    def action_right(self):
        self.cursor = min(self.cursor + 1, len(self.value))

    def action_backspace(self):
        if self.cursor == 0:
            return

        self.value = self.value[:self.cursor - 1] + self.value[self.cursor:]
        self.cursor -= 1

    def on_key(self, event):
        if not event.is_printable:
            return

        event.stop()
        event.prevent_default()

        self.value = self.value[:self.cursor] + event.character + self.value[self.cursor:]
        self.cursor += 1
        
    def render(self):
        value = self.value + ' '
        result = Text(value[:self.cursor])
        result.append_text(Text(value[self.cursor], style='underline'))
        result.append_text(Text(value[self.cursor + 1:]))
        return result
