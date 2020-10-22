from argparse import ArgumentParser
from pathlib import Path

from bandcamper import Bandcamper


def read_file(*names, **kwargs):
    params = {"encoding": "utf8"}
    params.update(kwargs)
    file_path = Path(Path(__file__).parent.resolve(), *names)
    with file_path.open(**params) as open_file:
        content = open_file.read().strip()
    return content


def main():
    parser = ArgumentParser(
        description="Download tracks and albums from Bandcamp", add_help=False
    )
    general_options = parser.add_argument_group(title="General Options")
    general_options.add_argument(
        "-h", "--help", action="help", help="Print this help message and exit"
    )
    general_options.add_argument(
        "-V",
        "--version",
        action="version",
        version=read_file("VERSION"),
        help="Print program version and exit",
    )
    general_options.add_argument(
        "-i",
        "--ignore-errors",
        action="store_true",
        help="Don't end the program in case of any (predictable) error; show warning instead",
    )
    input_options = parser.add_argument_group(title="Input Options")
    input_options.add_argument(
        "urls",
        nargs="*",
        metavar="URL",
        help="URLs/artists subdomains to download songs from",
    )
    input_options.add_argument(
        "-F",
        "--file",
        dest="files",
        metavar="<file>",
        default=[],
        action="append",
        help="Download from URLs/artists subdomains listed on file. This option can be used multiple times",
    )
    download_options = parser.add_argument_group(title="Download Options")
    audio_format_options = download_options.add_mutually_exclusive_group()
    audio_format_options.add_argument(
        "-f",
        "--format",
        dest="download_formats",
        default=["mp3-320", "flac"],
        action="append",
        choices=[
            "aac-hi",
            "aiff-lossless",
            "alac",
            "flac",
            "mp3-128",
            "mp3-320",
            "mp3-v0",
            "vorbis",
            "wav",
        ],
        help="Preferred audio formats to download. This option can be used multiple times",
    )
    audio_format_options.add_argument(
        "-a",
        "--all-formats",
        dest="download_formats",
        action="store_const",
        const=[
            "aac-hi",
            "aiff-lossless",
            "alac",
            "flac",
            "mp3-128",
            "mp3-320",
            "mp3-v0",
            "vorbis",
            "wav",
        ],
        help="Download all available audio formats",
    )
    download_options.add_argument(
        "--no-fallback",
        dest="allow_fallback",
        action="store_false",
        help="Do NOT download fallback mp3-128 in case there are no free downloads available",
    )
    file_options = parser.add_argument_group(title="File Options")
    file_options.add_argument(
        "-d",
        "--destination",
        default=".",
        help="Base destination folder for downloaded files. Defaults to current folder",
    )
    file_options.add_argument(
        "-o",
        "--output",
        default="{artist_name}/{album_title}/{track_title}.{ext}",
        help="Output filename template. See the 'Output Template' section of the README for all the info",
    )

    output_options = parser.add_argument_group(title="Console Output Options")
    verbosity_options = output_options.add_mutually_exclusive_group()
    verbosity_options.add_argument(
        "-q",
        "--quiet",
        action="count",
        default=0,
        help="Run bandcamper with less output. Use this flag 3 times to completely disable any output",
    )
    verbosity_options.add_argument(
        "-v",
        "--verbose",
        dest="quiet",
        action="store_const",
        const=-1,
        help="Run bandcamper with more verbose output.",
    )
    output_options.add_argument(
        "--no-colors",
        dest="colored",
        action="store_false",
        help="Disable colored output.",
    )

    args = vars(parser.parse_args())
    download_formats = args.pop("download_formats")
    urls = args.pop("urls")
    bandcamper = Bandcamper(args.pop("destination"), *urls, **args)
    if not bandcamper.urls:
        bandcamper.screamer.error(
            "You must give at least one URL/artist subdomain to download",
            force_error=True,
        )

    bandcamper.download_all(download_formats)


if __name__ == "__main__":
    try:
        main()
    except RuntimeError:
        exit(1)
