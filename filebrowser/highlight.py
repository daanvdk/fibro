from collections import Counter
from pathlib import Path

from textual.widget import Widget
from textual.widgets import Static
from textual._tree_sitter import BUILTIN_LANGUAGES

from rich.text import Text
from rich.style import Style

from tree_sitter import Parser


QUERIES = Path(__file__).parent / 'queries'
QUERY_CACHE = {}


def get_query(language, name):
    try:
        return QUERY_CACHE[(language, name)]
    except KeyError:
        pass

    try:
        content = QUERIES.joinpath(language, name).read_text()
    except FileNotFoundError:
        query = None
    else:
        query = BUILTIN_LANGUAGES[language].query(content)

    QUERY_CACHE[(language, name)] = query
    return query


EVENT_TYPE_ORDER = {key: i for i, key in enumerate([
    'highlight_end',
    'reference_end',
    'scope_end',

    'scope_start',
    'reference_start',
    'highlight_start',

    'definition',
])}


def event_key(event):
    pos, event_type, *_ = event
    return (pos, EVENT_TYPE_ORDER[event_type])


KEY_STYLES = {
    'attribute': Style(color='#eed49f'),
    'type': Style(color='#eed49f'),
    'type.enum.variant': Style(color='#8bd5ca'),
    'constructor': Style(color='#7dc4e4'),
    'constant': Style(color='#f5a97f'),
    'constant.character': Style(color='#8bd5ca'),
    'constant.character.escape': Style(color='#f5bde6'),
    'string': Style(color='#a6da95'),
    'string.regexp': Style(color='#f5bde6'),
    'string.special': Style(color='#8aadf4'),
    'string.special.symbol': Style(color='#ed8796'),
    'comment': Style(color='#939ab7', italic=True),
    'variable': Style(color='#cad3f5'),
    'variable.parameter': Style(color='#ee99a0', italic=True),
    'variable.builtin': Style(color='#ed8796'),
    'variable.other.member': Style(color='#8aadf4'),
    'label': Style(color='#7dc4e4'),
    'punctuation': Style(color='#939ab7'),
    'punctuation.special': Style(color='#91d7e3'),
    'keyword': Style(color='#c6a0f6'),
    'keyword.control.conditional': Style(color='#c6a0f6', italic=True),
    'operator': Style(color='#91d7e3'),
    'function': Style(color='#8aadf4'),
    'function.macro': Style(color='#c6a0f6'),
    'tag': Style(color='#8aadf4'),
    'namespace': Style(color='#eed49f', italic=True),
    'special': Style(color='#8aadf4'),

    'markup.heading.marker': Style(color='#f5a97f', bold=True),
    'markup.heading.1': Style(color='#b7bdf8'),
    'markup.heading.2': Style(color='#c6a0f6'),
    'markup.heading.3': Style(color='#a6da95'),
    'markup.heading.4': Style(color='#eed49f'),
    'markup.heading.5': Style(color='#f5bde6'),
    'markup.heading.6': Style(color='#8bd5ca'),
    'markup.list': Style(color='#c6a0f6'),
    'markup.list.unchecked': Style(color='#939ab7'),
    'markup.list.checked': Style(color='#a6da95'),
    'markup.bold': Style(bold=True),
    'markup.italic': Style(italic=True),
    'markup.link.url': Style(color='#8aadf4', italic=True, underline=True),
    'markup.link.text': Style(color='#8aadf4'),
    'markup.raw': Style(color='#f0c6c6'),

    'ui.linenr': Style(color='#494d64'),
    'ui.virtual.indent-guide': Style(color='#363a4f'),
}


class Highlight(Widget):

    def __init__(self, content, language):
        super().__init__()
        self.content = content
        self.language = language

    def compose(self):
        lines = self.content.split('\n')

        while lines and not lines[-1]:
            lines.pop()

        if not lines:
            yield Static('')
            return

        # Try to autodetect indent
        for line in lines:
            if not line or not line[0].isspace():
                continue
            for i, char in enumerate(line):
                if not char.isspace():
                    break
            else:
                continue
            indent = line[:i]
            break
        else:
            indent = '    '

        indent_text = Text(
            '│' + indent.replace('\t', '    ')[1:],
            style=get_style(['ui.virtual.indent-guide']),
        )

        # Fix up indent of empty lines by matching them with the lowest indent
        # of the previous and next non empty line
        last_index = 0

        for curr_index, line in enumerate(lines):
            if not line or line.isspace():
                continue

            curr_indent = 0
            while line.startswith(indent, len(indent) * curr_indent):
                curr_indent += 1

            for index in range(last_index, curr_index):
                lines[index] = indent * curr_indent

            last_index = curr_index + 1

        for index in range(last_index, len(lines)):
            lines[index] = ''

        # Gather all events
        events = []

        if self.language is not None:
            syntax_tree = Parser(BUILTIN_LANGUAGES[self.language]).parse(self.content.encode())

            if highlights_query := get_query(self.language, 'highlights.scm'):
                for pattern, captures in highlights_query.matches(syntax_tree.root_node):
                    for key, nodes in captures.items():
                        for node in nodes:
                            events.append((node.start_point, 'highlight_start', (pattern, key)))
                            events.append((node.end_point, 'highlight_end', (pattern, key)))

            if locals_query := get_query(self.language, 'locals.scm'):
                for key, nodes in locals_query.captures(syntax_tree.root_node).items():
                    for node in nodes:
                        match key:
                            case 'local.scope':
                                events.append((node.start_point, 'scope_start'))
                                events.append((node.end_point, 'scope_end'))
                            case 'local.definition':
                                events.append((node.start_point, 'definition', node.text))
                            case 'local.reference':
                                events.append((node.start_point, 'reference_start', node.text))
                                events.append((node.end_point, 'reference_end', node.text))

            events.sort(key=event_key, reverse=True)

        # Determine chunks
        line = 0
        column = 0

        scopes = [[]]
        definitions = {}
        references = Counter()
        highlights = Counter()

        def get_curr_style():
            for reference in sorted(references):
                try:
                    return definitions[reference][-1]
                except KeyError:
                    pass
            return get_style(key for _, key in sorted(highlights))

        max_line_len = len(str(len(lines)))
        linenr_style = get_style(['ui.linenr'])
        curr_line = Text()

        end_point = (len(lines), 0)

        while line < len(lines):
            # Pop all events that should be applied
            while events and (line, column) >= events[-1][0]:
                match events.pop():
                    case (_, 'scope_start'):
                        scopes.append([])

                    case (_, 'scope_end'):
                        for key in scopes.pop():                            
                            definitions[key].pop()
                            if not definitions[key]:
                                del definitions[key]

                    case (_, 'definition', key):
                        style = get_curr_style()
                        definitions.setdefault(key, []).append(style)
                        scopes[-1].append(key)

                    case (_, 'reference_start', key):
                        references[key] += 1

                    case (_, 'reference_end', key):
                        references[key] -= 1
                        if not references[key]:
                            del references[key]

                    case (_, 'highlight_start', key):
                        highlights[key] += 1

                    case (_, 'highlight_end', key):
                        highlights[key] -= 1
                        if not highlights[key]:
                            del highlights[key]

                    case event:
                        raise ValueError(f'unknown event: {event}')

            # Either go to the next event or the end
            try:
                next_point = events[-1][0]
            except IndexError:
                next_point = end_point
            else:
                next_point = min(next_point, end_point)
            next_line, next_column = next_point

            # Add all chunks
            style = get_curr_style()

            while (line, column) < (next_line, next_column):
                if column == 0:
                    # Add line number
                    curr_line.append_text(Text(
                        str(line).rjust(max_line_len) + ' ',
                        style=linenr_style,
                    ))
                    # Add indent
                    while (
                        lines[line].startswith(indent, column) and
                        (line, column + len(indent)) <= (next_line, next_column)
                    ):
                        curr_line.append_text(indent_text)
                        column += len(indent)

                # Add rest of line
                if line < next_line:
                    curr_line.append_text(Text(lines[line][column:], style=style))
                    yield Static(curr_line)
                    curr_line = Text()
                    line += 1
                    column = 0
                else:
                    curr_line.append_text(Text(lines[line][column:next_column], style=style))
                    column = next_column                


def get_style(highlights):
    for key in highlights:
        for subkey in all_keys(key):
            try:
                return KEY_STYLES[subkey]
            except KeyError:
                pass
    return Style()


def all_keys(key):
    yield key
    key_len = len(key)

    while True:
        try:
            key_len = key.rindex('.', 0, key_len)
        except ValueError:
            break
        yield key[:key_len]
