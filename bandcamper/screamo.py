from collections import namedtuple
from contextlib import contextmanager
from math import ceil

import click

WarnType = namedtuple("WarnType", ["symbol", "attrs"])


class Screamer:
    ERROR = WarnType(("Error:", "[!]"), {"fg": "red", "bold": True})
    WARNING = WarnType(("Warning:", "[!]"), {"fg": "bright_yellow"})
    SUCCESS = WarnType(("Success:", "[+]"), {"fg": "bright_green", "bold": True})
    PROCESSING = WarnType(("Processing:", "[~]"), {"fg": "bright_cyan", "blink": True})
    INFO = WarnType(("Info:", "[?]"), {"fg": "bright_blue", "bold": True})

    def __init__(self, verbosity=0, colored=True):
        self.colored = colored

    def get_message(self, text, warn_type, short_symbol, **kwargs):
        symbol = self.style(warn_type.symbol[short_symbol], **warn_type.attrs) + " "
        text = self.style(text, **kwargs)
        return symbol + text

    def scream(self, text, warn_type, short_symbol, **kwargs):
        click.echo(self.get_message(text, warn_type, short_symbol, **kwargs))

    def style(self, text, **kwargs):
        if kwargs and self.colored:
            return click.style(text, **kwargs)
        return text

    def error(self, text, short_symbol=True):
        self.scream(text, self.ERROR, short_symbol)

    def critical(self, text):
        self.error(text, False)
        raise RuntimeError

    def warning(self, text, short_symbol=True):
        self.scream(text, self.WARNING, short_symbol)

    def success(self, text, short_symbol=True):
        self.scream(text, self.SUCCESS, short_symbol)

    @contextmanager
    def processing(
        self, text, success_text, short_symbol=True, success_short_symbol=None
    ):
        self.scream(text, self.PROCESSING, short_symbol)
        yield
        terminal_width = click.get_terminal_size()[0]
        success_short_symbol = (
            short_symbol if success_short_symbol is None else success_short_symbol
        )
        success_message = self.get_message(
            success_text, self.SUCCESS, success_short_symbol
        )
        click.echo("\033[A\033[A" * ceil(len(text) / terminal_width))
        success_message += " " * (len(text) % terminal_width - len(success_message))
        click.echo(success_message)

    def info(self, text, short_symbol=True):
        self.scream(text, self.INFO, short_symbol)
