from pathlib import Path

from textual.binding import Binding


HOME = Path('~').resolve()


def forward_bindings(Widget, query=None):
    if query is None:
        query = Widget.__name__
    else:
        query = str(query)

    for binding in Widget.BINDINGS:
        action, has_args, tail = binding.action.partition('(')
        if not has_args:
            tail = ')'
        yield Binding(binding.key, f'forward({query!r}, {action!r}{tail}')


class ForwardMixin:

    def action_forward(self, query, action, *args):
        node = self.query_one(query)
        getattr(node, f'action_{action}')(*args)


def show_path(path):
    try:
        path = path.relative_to(HOME)
    except ValueError:
        return str(path)
    else:
        return f'~/{path}'
