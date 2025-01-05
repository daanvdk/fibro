from textual.widget import Widget
from textual.widgets import TextArea, Static

from .directory import Directory


LANGUAGES = {
    '.sh': 'bash',
    '.bash': 'bash',
    '.css': 'css',
    '.tcss': 'css',
    '.go': 'go',
    '.html': 'html',
    '.java': 'java',
    '.js': 'javascript',
    '.json': 'json',
    '.md': 'markdown',
    '.py': 'python',
    '.rs': 'rust',
    '.sql': 'sql',
    '.toml': 'toml',
    '.xml': 'xml',
    '.yaml': 'yaml',
}


class Preview(Widget):

    path = None

    def on_mount(self):
        browser = self.screen.query_one('Browser')

        self.browser_path = browser.path
        self.browser_selected_value = browser.selected_value
        self.set_path()

        self.watch(browser, 'path', self.set_browser_path)
        self.watch(browser, 'selected_value', self.set_browser_selected_value)

    def set_browser_path(self, browser_path):
        self.browser_path = browser_path
        self.set_path()

    def set_browser_selected_value(self, browser_selected_value):
        self.browser_selected_value = browser_selected_value
        self.set_path()

    def set_path(self):
        match self.browser_selected_value:
            case None:
                path = None
            case '..':
                path = self.browser_path.parent
            case name:
                path = self.browser_path / name

        if path != self.path:
            self.path = path
            self.refresh(recompose=True)

    def compose(self):
        if self.path is None:
            return

        elif self.path.is_dir():
            yield Directory(self.path)

        elif self.path.is_file():
            try:
                text = self.path.read_text()
            except ValueError:
                text = '<binary>'
                language = None
            else:
                language = LANGUAGES.get(self.path.suffix)
            yield TextArea(text, language=language, read_only=True)

