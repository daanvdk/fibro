from textual.widgets import Input


IGNORE_KEYS = {
    'enter',
}


class SimpleInput(Input, inherit_bindings=False):

    BINDINGS = [
        binding
        for binding in Input.BINDINGS
        if binding.key not in IGNORE_KEYS
    ]
