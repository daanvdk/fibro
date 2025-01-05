from pathlib import Path

from textual.widget import Widget
from textual.reactive import var

from rich.style import Style
from rich.text import Text


MATCH_STYLE = Style(color='#8aadf4', bold=True)


class Directory(Widget):

    path = var(None)
    values = var([])
    show_hidden = var(False)

    def __init__(self, path='.'):
        super().__init__()
        self.path = Path(path).resolve()

    def watch_path(self):
        self.set_values()
        self.refresh(recompose=True)

    def watch_show_hidden(self):
        self.set_values()
        self.refresh(recompose=True)

    def set_values(self):
        if self.path is None:
            self.values = []
            return

        dirs = []
        files = []
        for path in self.path.iterdir():
            if path.name.startswith('.') and not self.show_hidden:
                pass
            elif path.is_dir():
                dirs.append(f'{path.name}/')
            else:
                files.append(path.name)

        dirs.sort()
        files.sort()
        self.values = ['..', *dirs, *files]

    def compose(self):
        for value in self.values:
            yield self.Child(value, self.render_value(value))

    def render_value(self, value):
        return Text(value)

    class Child(Widget):
    
        def __init__(self, value, text):
            super().__init__()
            self.value = value
            self.text = text

        def render(self):
            return self.text
