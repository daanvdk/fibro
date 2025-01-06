from pathlib import Path

from textual.widget import Widget
from textual.widgets import Static
from textual.reactive import var

from rich.text import Text


class Directory(Widget):

    path = var(None)
    values = var([])

    def __init__(self, path='.'):
        super().__init__()
        self.set_reactive(Directory.path, Path(path).resolve())
        self.set_values()

    def watch_path(self):
        self.set_values()
        self.refresh(recompose=True)

    def on_mount(self):
        self.watch(self.app, 'show_hidden', self.watch_show_hidden, init=False)

    def watch_show_hidden(self, _):
        self.set_values()
        self.refresh(recompose=True)

    def set_values(self):
        if self.path is None:
            self.values = []
            return

        dirs = []
        files = []
        for path in self.path.iterdir():
            if path.name.startswith('.') and not self.app.show_hidden:
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
        if not self.values:
            yield Static('')

    def render_value(self, value):
        return Text(value)

    class Child(Widget):
    
        def __init__(self, value, text):
            super().__init__()
            self.value = value
            self.text = text

        def render(self):
            return self.text
