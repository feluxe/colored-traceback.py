import sys
import os


def add_hook(always=False, style='default', colors=None, debug=False):
    no_color = os.environ.get("NO_COLOR", "")   # https://no-color.org
    if no_color:
        return
    isatty = getattr(sys.stderr, 'isatty', lambda: False)
    if always or isatty():
        try:
            import pygments  # flake8:noqa
            colorizer = Colorizer(style, colors, debug)
            sys.excepthook = colorizer.colorize_traceback
        except ImportError:
            if debug:
                sys.stderr.write("Failed to add coloring hook; pygments not available\n")


class Colorizer(object):

    def __init__(self, style, colors, debug=False):
        self.style = style
        self.colors = colors
        self.debug = debug

    def colorize_traceback(self, type, value, tb):
        import traceback
        import pygments.lexers
        tb_text = "".join(traceback.format_exception(type, value, tb))
        lexer_name = "pytb" if sys.version_info.major < 3 else "py3tb"
        lexer = pygments.lexers.get_lexer_by_name(lexer_name)
        tb_colored = pygments.highlight(tb_text, lexer, self.formatter)
        self.stream.write(tb_colored)

    @property
    def formatter(self):
        colors = self.colors or _get_term_color_support()
        if self.debug:
            sys.stderr.write("Detected support for %s colors\n" % colors)
        if colors == 256:
            fmt_options = {'style': self.style}
        elif self.style in ('light', 'dark'):
            fmt_options = {'bg': self.style}
        else:
            fmt_options = {'bg': 'dark'}
        from pygments.formatters import get_formatter_by_name
        import pygments.util
        fmt_alias = 'terminal256' if colors == 256 else 'terminal'
        try:
            return get_formatter_by_name(fmt_alias, **fmt_options)
        except pygments.util.ClassNotFound as ex:
            if self.debug:
                sys.stderr.write(str(ex) + "\n")
            return get_formatter_by_name(fmt_alias)

    @property
    def stream(self):
        try:
            import colorama
            return colorama.AnsiToWin32(sys.stderr)
        except ImportError:
            return sys.stderr


def _get_term_color_support():
    try:
        import curses
    except ImportError:
        # Probably Windows, which doesn't have great curses support
        return 16
    curses.setupterm()
    return curses.tigetnum('colors')
