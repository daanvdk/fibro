import subprocess
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

        self._git_root = None
        self._git_root_path = None

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

    @property
    def git_root(self):
        if self._git_root_path != self.path:
            root = self.path
            while True:
                if root.joinpath('.git').exists():
                    break
                if root.parent == root:
                    root = None
                    break
                root = root.parent

            self._git_root = root
            self._git_root_path = self.path

        return self._git_root

    def set_values(self):
        if self.path is None:
            self.values = []
            return

        paths = {
            path
            for path in self.path.iterdir()
            if not path.name.startswith('.') or self.app.show_hidden
        }

        if paths and not self.app.show_hidden and self.git_root:
            name_paths = {path.name: path for path in paths}
            res = subprocess.run(
                ['git', 'check-ignore', *name_paths],
                cwd=self.path,
                capture_output=True,
            )
            for line in res.stdout.decode().split():
                if not line:
                    continue
                paths.remove(name_paths[line])

        dirs = []
        files = []
        for path in paths:
            if path.is_dir():
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
