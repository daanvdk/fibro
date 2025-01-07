from textual.theme import Theme

from rich.text import Text
from rich.style import Style

import tomllib
from os import environ
from pathlib import Path


XDG_CONFIG_HOME = Path(environ.get('XDG_CONFIG_HOME', '~/.config')).expanduser().resolve()


with XDG_CONFIG_HOME.joinpath('helix/config.toml').open('rb') as f:
    CONFIG = tomllib.load(f)


NO_DEFAULT = object()


def get(*keys, default=NO_DEFAULT):
    value = CONFIG
    for key in keys:
        try:
            value = value[key]
        except KeyError:
            if default is NO_DEFAULT:
                raise
            else:
                return default
    return value            


HELIX = Path(__file__).parent / 'helix'


def load_theme(theme):
    match theme:
        case 'default':
            path = HELIX / 'theme.toml'
        case 'base16_default':
            path = HELIX / 'base16_theme.toml'
        case _:
            path = HELIX / f'runtime/themes/{theme}.toml'

    with path.open('rb') as f:
        data = tomllib.load(f)

    try:
        base_theme = data.pop('inherits')
    except KeyError:
        return data

    base_data = load_theme(base_theme)
    base_data.update(data)
    return base_data


THEME = get('theme', default='default')
THEME_STYLES = load_theme(THEME)


palette = THEME_STYLES.pop('palette')
modifier_translations = {
    'bold': 'bold',
    'italic': 'italic',
    'underlined': 'underline',
    'dim': 'dim',
}


for key, value in THEME_STYLES.items():
    if isinstance(value, str):
        value = {'fg': value}

    kwargs = {}

    if fg := value.get('fg'):
        kwargs['color'] = palette.get(fg, fg)

    if bg := value.get('bg'):
        kwargs['bgcolor'] = palette.get(bg, bg)

    for modifier in value.get('modifiers', []):
        try:
            modifier = modifier_translations[modifier]
        except KeyError:
            pass
        else:
            kwargs[modifier] = True

    THEME_STYLES[key] = Style(**kwargs)


def get_style(keys):
    if isinstance(keys, str):
        keys = [keys]

    for key in keys:
        for subkey in all_keys(key):
            try:
                return THEME_STYLES[subkey]
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


HELIX_THEME = Theme(
    name='helix',
    primary=get_style('special').color.name,
    secondary=get_style('special').color.name,
    accent=get_style('special').color.name,
    foreground=get_style('ui.text').color.name,
    background=get_style('ui.background').bgcolor.name,
    success=get_style('diff.plus').color.name,
    warning=get_style('warning').color.name,
    error=get_style('error').color.name,
    surface=get_style('ui.popup').bgcolor.name,
    panel=get_style('ui.popup').bgcolor.name,
    dark=True,
)


STATUS_GUTTER = {
    None: Text(' '),
    'added': Text('▍', style=get_style('diff.plus')),
    'changed': Text('▍', style=get_style('diff.delta')),
}
