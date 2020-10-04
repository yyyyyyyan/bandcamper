from argparse import ArgumentParser

from bandcamper import Bandcamper
from bandcamper.screamo import Screamer

if __name__ == "__main__":
    parser = ArgumentParser(description="Download tracks and albums from Bandcamp")
    parser.add_argument(
        "urls",
        nargs="*",
        metavar="URL",
        help="URLs/artists subdomains to download songs from.",
    )
    parser.add_argument(
        "-f",
        "--file",
        dest="files",
        metavar="<file>",
        default=[],
        action="append",
        help="Download from URLs/artists subdomains listed on file. This option can be used multiple times.",
    )
    parser.add_argument(
        "-i",
        "--ignore-errors",
        action="store_true",
        help="Don't end the program in case of any (predictable) error; show warning instead.",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="count",
        default=0,
        help="Run bandcamper with less output. Use this flag 3 times to completely disable any output.",
    )
    parser.add_argument(
        "--no-colors",
        dest="colored",
        action="store_false",
        help="Disable colored output.",
    )

    args = parser.parse_args()
    screamer = Screamer(args.quiet, args.colored, args.ignore_errors)
    urls = args.urls
    for filename in args.files:
        try:
            with open(filename) as url_list:
                urls.extend(url_list.read().split())
        except FileNotFoundError:
            screamer.error(f"File '{filename}' not found!")

    bandcamper = Bandcamper(screamer, *urls)
    if not bandcamper.urls:
        screamer.error(
            "You must give at least one URL/artist subdomain to download",
            force_error=True,
        )

    screamer.info(f"Downloading from {len(bandcamper.urls)} URLs...", True)
    bandcamper.download_all()
