import os
import subprocess
import shutil

from textual.reactive import var, reactive
from textual.fuzzy import Matcher
from textual.binding import Binding

from rich.text import Text

from . import config
from .directory import Directory


MATCH_STYLE = config.get_style('special')


class Browser(Directory):

    matcher = None
    selected = var(0)
    selected_value = var(None)

    BINDINGS = [
        Binding('up', 'nav_up'),
        Binding('down', 'nav_down'),
        Binding('enter', 'select'),

        Binding('alt+h', 'toggle_hidden'),

        Binding('alt+c', 'create'),
        Binding('alt+r', 'rename'),
        Binding('alt+d', 'delete'),

        Binding('alt+p', 'go_prev'),
        Binding('alt+n', 'go_next'),
        Binding('alt+shift+p', 'go_prev_full'),
        Binding('alt+shift+n', 'go_next_full'),
    ]

    def __init__(self, path='.', autoselect=None):
        self.autoselect = autoselect
        self.prev_stack = []
        self.next_stack = []
        super().__init__(path)

    def on_mount(self):
        search = self.screen.query_one('#search')
        self.watch(search, 'value', self.set_filter, init=False)

    def set_filter(self, filter):
        if filter:
            self.matcher = Matcher(filter, match_style=MATCH_STYLE)
        else:
            self.matcher = None

        self.set_values()
        self.refresh(recompose=True)

    def set_values(self):
        super().set_values()

        if self.matcher:
            self.values = sorted(
                filter(self.matcher.match, self.values),
                key=self.matcher.match,
                reverse=True,
            )

        if self.autoselect:
            self.action_select_value(self.autoselect)
            self.autoselect = None
        else:
            self.selected = 0

        self.watch_selected(self.selected)

    def watch_selected(self, selected):
        if self.values:
            self.selected_value = self.values[selected]
        else:
            self.selected_value = None

    def render_value(self, value):
        if self.matcher:
            return self.matcher.highlight(value)
        else:
            return Text(value)

    def action_select_value(self, value):
        try:
            self.selected = self.values.index(value)
        except ValueError:
            self.selected = 0

    def action_nav_up(self):
        self.selected = (self.selected - 1) % len(self.values)

    def action_nav_down(self):
        self.selected = (self.selected + 1) % len(self.values)

    def action_push(self, path):
        self.prev_stack.append((self.path, self.selected_value))
        self.next_stack.clear()
        self.path = path

    def action_go_prev(self):
        try:
            path, autoselect = self.prev_stack.pop()
        except IndexError:
            return

        self.next_stack.append((self.path, self.selected_value))
        self.autoselect = autoselect
        self.path = path

    def action_go_next(self):
        try:
            path, autoselect = self.next_stack.pop()
        except IndexError:
            return

        self.prev_stack.append((self.path, self.selected_value))
        self.autoselect = autoselect
        self.path = path

    def action_go_prev_full(self):
        while self.prev_stack:
            self.action_go_prev()

    def action_go_next_full(self):
        while self.next_stack:
            self.action_go_next()

    @property
    def selected_path(self):
        match self.selected_value:
            case None:
                return None
            case '..':
                return self.path.parent
            case value:
                return self.path / value

    def action_select(self):
        if not (path := self.selected_path):
            return

        if path.is_dir():
            self.action_push(path)
            self.screen.query_one('#search').action_clear()

        elif path.is_file():
            editor = (
                os.environ.get('EDITOR') or
                os.environ.get('VISUAL') or
                'vi'
            )

            with self.app.suspend():
                subprocess.run([editor, str(path)])

            self.app.refresh()
            self.screen.query_one('Preview').refresh(recompose=True)

    def action_create(self):
        @self.app.prompt('create file or directory')
        def create_name(name):
            if name is None:
                return

            is_dir = name.endswith('/')
            path = self.path / name

            if is_dir:
                path.mkdir(exist_ok=True, parents=True)
                self.action_push(path)
            else:
                path.parent.mkdir(exist_ok=True, parents=True)
                path.touch()

                self.autoselect = path.name
                if self.path == path.parent:
                    self.set_values()
                    self.refresh(recompose=True)
                else:
                    self.action_push(path.parent)

    def action_rename(self):
        if self.selected_value in (None, '..'):
            return
        path = self.selected_path

        @self.app.prompt(f'rename {self.selected_value}', default=path.name)
        def rename(name):
            if name is None:
                return

            name = name.rstrip('/')
            is_dir = path.is_dir()

            path.rename(name)

            if is_dir:
                name += '/'

            self.values[self.selected] = name
            self.set_reactive(Browser.selected_value, name)

            child = self.children[self.selected]
            child.value = name
            child.text = self.render_value(name)
            child.refresh()

    def action_delete(self):
        if self.selected_value in (None, '..'):
            return
        path = self.selected_path

        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()

        self.values.pop(self.selected)
        if not self.values:
            self.selected_value = None
        elif self.selected == len(self.values):
            self.selected -= 1
        else:
            self.selected_value = self.values[self.selected]

        self.refresh(recompose=True)

    class Child(Directory.Child):

        selected = reactive(False)

        def on_mount(self):
            self.watch(self.parent, 'selected_value', self.check_selected)

        def check_selected(self, selected_value):
            self.selected = selected_value == self.value

        def watch_selected(self, selected):
            if selected:
                self.add_class('selected')
            else:
                self.remove_class('selected')

        def render(self):
            text = super().render()
            if self.selected:
                return Text('> ').append_text(text)
            else:
                return Text('  ').append_text(text)
