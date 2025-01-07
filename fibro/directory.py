import subprocess
from pathlib import Path

from textual.widget import Widget
from textual.widgets import Static
from textual.reactive import var

from rich.text import Text

from . import config


class Directory(Widget):

    path = var(None)
    values = var([])

    def __init__(self, path='.'):
        super().__init__()

        self._git_root = None
        self._git_root_path = None
        self.git_status = {}

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
            for line in res.stdout.decode().split('\n'):
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
        self.set_git_status()

    def set_git_status(self):
        self.git_status.clear()

        if not self.git_root:
            return

        res = subprocess.run(
            ['git', 'ls-files', '-t', '--modified', '--others', '--exclude-standard', '--directory'],
            cwd=self.path,
            capture_output=True,
        )
        for line in res.stdout.decode().split('\n'):
            if not line:
                continue
            type, name = line.split(' ', 1)

            parts = name.rstrip('/').split('/')
            if parts == ['.']:
                for value in self.values:
                    self.git_status[value] = 'added'
                break

            path = self.path / parts[0]
            name = path.name
            if path.is_dir():
                name += '/'

            if type == '?' and len(parts) == 1:
                self.git_status[name] = 'added'
            else:
                self.git_status[name] = 'changed'

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
            git_status = self.parent.git_status.get(self.value)

            text = Text()
            text.append_text(config.STATUS_GUTTER[git_status])
            text.append_text(self.text)
            return text
