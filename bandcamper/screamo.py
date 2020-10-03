from collections import namedtuple
from sys import exit

from colorama import Fore, Style
from colorama import init

WarnType = namedtuple("WarnType", ["verbose_level", "symbol", "color"])


class Screamer:
    ERROR = WarnType(3, ("Error:", "[-]"), Fore.RED)
    WARNING = WarnType(2, ("Warning:", "[!]"), Fore.YELLOW)
    SUCCESS = WarnType(1, ("Success:", "[+]"), Fore.GREEN)
    INFO = WarnType(0, ("Info:", "[~]"), Fore.CYAN)

    def __init__(self, quiet_level, colored, ignore_errors, color_autoreset=True):
        init(autoreset=color_autoreset)
        self.quiet_level = quiet_level
        self.colored = colored
        self.ignore_errors = ignore_errors

    @property
    def quiet_level(self):
        return self._quiet_level

    @quiet_level.setter
    def quiet_level(self, level):
        self._quiet_level = int(level)

    def scream(self, text, importance_level=float("inf")):
        if not self.quiet_level or importance_level > self.quiet_level:
            print(text)

    def _scream_warn(self, msg, warn_type, short_symbol):
        symbol = warn_type.symbol[short_symbol] + " "
        if self.colored:
            text = Style.BRIGHT + warn_type.color + symbol + Style.RESET_ALL + msg
        else:
            text = symbol + msg
        self.scream(text, warn_type.verbose_level)

    def error(self, msg, force_error=False, short_symbol=False):
        if self.ignore_errors and not force_error:
            self.warning(msg, short_symbol)
        else:
            self._scream_warn(msg, self.ERROR, short_symbol)
            exit(1)

    def warning(self, msg, short_symbol=False):
        self._scream_warn(msg, self.WARNING, short_symbol)

    def success(self, msg, short_symbol=False):
        self._scream_warn(msg, self.SUCCESS, short_symbol)

    def info(self, msg, short_symbol=False):
        self._scream_warn(msg, self.INFO, short_symbol)
