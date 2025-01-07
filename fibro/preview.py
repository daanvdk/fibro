import subprocess

from textual.widget import Widget
from textual.widgets import Static

from .directory import Directory
from .highlight import Highlight


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
            yield Static('')

        elif self.path.is_dir():
            yield Directory(self.path)

        elif self.path.is_file():
            try:
                new_content = self.path.read_text()
            except ValueError:
                yield Static('<binary>')
            else:
                browser = self.app.query_one('Browser')
                if browser.git_root:
                    git_path = self.path.relative_to(browser.git_root)
                    res = subprocess.run(
                        ['git', 'show', f':{git_path}'],
                        cwd=browser.git_root,
                        capture_output=True,
                    )
                    old_content = res.stdout.decode()
                else:
                    old_content = new_content

                language = LANGUAGES.get(self.path.suffix)
                yield Highlight(old_content, new_content, language)

