from colorama import Fore, Style


def error(msg, short=False):
    symbol = "[-] " if short else "Error: "
    return Style.BRIGHT + Fore.RED + symbol + Style.RESET_ALL + msg


def warn(msg, short=False):
    symbol = "[!] " if short else "Warning: "
    return Style.BRIGHT + Fore.YELLOW + symbol + Style.RESET_ALL + msg
