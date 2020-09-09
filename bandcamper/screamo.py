from collections import namedtuple

from colorama import Fore, Style
from colorama import init

WarnType = namedtuple("WarnType", ["verbose_level", "symbol", "color"])


class Screamer:
    ERROR = WarnType(3, ("Error:", "[-]"), Fore.RED)
    WARNING = WarnType(2, ("Warning:", "[!]"), Fore.YELLOW)

    def __init__(self, quiet_level, colored, color_autoreset=True):
        init(autoreset=color_autoreset)
        self.quiet_level = quiet_level
        self.colored = colored

    @property
    def quiet_level(self):
        return self._quiet_level

    @quiet_level.setter
    def quiet_level(self, level):
        self._quiet_level = int(level)

    def scream(self, text, importance_level=float("inf")):
        if importance_level > self.quiet_level:
            print(text)

    def _scream_warn(self, msg, warn_type, short_symbol):
        symbol = warn_type.symbol[short_symbol]
        if self.colored:
            text = Style.BRIGHT + warn_type.color + symbol + Style.RESET_ALL + msg
        else:
            text = warn_type.symbol + msg
        self.scream(text, warn_type.verbose_level)

    def error(self, msg, short_symbol=False):
        self._scream_warn(msg, self.ERROR, short_symbol)

    def warning(self, msg, short_symbol=False):
        self._scream_warn(msg, self.WARNING, short_symbol)
