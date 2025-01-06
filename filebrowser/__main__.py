import argparse

from .app import App


parser = argparse.ArgumentParser()
parser.add_argument('path', nargs='?', default='.')
parser.add_argument('-s', '--selected')


if __name__ == '__main__':
    args = parser.parse_args()
    app = App(args.path, args.selected)
    app.run()
