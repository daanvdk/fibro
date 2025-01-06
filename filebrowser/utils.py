from pathlib import Path


HOME = Path('~').resolve()


def show_path(path):
    try:
        path = path.relative_to(HOME)
    except ValueError:
        return str(path)
    else:
        return f'~/{path}'
