import asyncio
import inspect
from pathlib import Path

from textual.binding import Binding


def forward_bindings(Widget, query=None):
    if query is None:
        query = Widget.__name__
    else:
        query = str(query)

    for binding in Widget.BINDINGS:
        action, has_args, tail = binding.action.partition('(')
        if has_args:
            tail = f', {tail}'
        else:
            tail = ')'
        yield Binding(binding.key, f'forward({query!r}, {action!r}{tail}')


class ForwardMixin:

    def action_forward(self, query, action, *args):
        node = self.query_one(query)
        result = getattr(node, f'action_{action}')(*args)
        if inspect.iscoroutine(result):
            asyncio.create_task(result)


HOME = Path('~').resolve()


def show_path(path):
    try:
        path = path.relative_to(HOME)
    except ValueError:
        return str(path)
    else:
        return f'~/{path}'
