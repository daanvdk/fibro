import argparse

from .app import App


parser = argparse.ArgumentParser()
parser.add_argument('path', nargs='?', default='.')


def main():
    args = parser.parse_args()
    app = App(args.path)
    app.run()


if __name__ == '__main__':
    main()
