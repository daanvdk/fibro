# FileBrowser
A fuzzy search oriented file browser.

This basically tries to resemble what it would be like if
[helix](https://github.com/helix-editor/helix) implemented something like
[telescope-file-browser.nvim](https://github.com/nvim-telescope/telescope-file-browser.nvim).

## Usage
### Launching
This package installs a command `fb` that opens the filebrowser.
It optionally takes a path to open which defaults to the current working
directory.
If the supplied path is a file it will open the directory instead and select
the file by default.

### Keybindings
- `escape` closes the application
- `up` moves the cursor up
- `down` moves the cursor down
- `enter` selects the item under the cursor, if its a directory it will change
   to this directory, otherwise it will open the item in `$EDITOR`
- `tab` marks the item under the cursor
- `alt+a` marks all items, if everything is already marked it unmarks
  everything instead
- `shift+up` marks the item under the cursor and then moves the cursor up
- `shift+down` marks the item under the cursor and then moves the cursor down
- `alt+h` toggles the display of hidden files
- `alt+c` creates a file or directory, if the name endswith a / its assumed to
  be a directory, otherwise a file, parent directories are also created
  automatically
- `alt+r` renames the item under the cursor
- `alt+m` moves all marked items to the current path
- `alt+shift+m` copies all marked items to the current path
- `alt+d` deletes all marked items, if there are none it deletes the item under
  the cursor
- `alt+p` goes back in history 
- `alt+n` goes forward in history
- `alt+shift+p` goes all the way back in history
- `alt+shift+n` goes all the way forward in history
- any other form of typing changes the current fuzzy search

## Configuration
Since this filebrowser is very much aimed at helix users it reuses the config
from helix.
It takes the following things from the helix config:
- theme
