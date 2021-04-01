import json
from pathlib import Path
from sys import exit

import click
from click_option_group import optgroup

import bandcamper
from bandcamper import Bandcamper


def configure(ctx, param, config_path=None):
    config_path = (
        Path("bandcamper_config.json") if config_path is None else Path(config_path)
    )
    if config_path.is_file():
        with config_path.open(encoding="utf8") as config_file:
            try:
                ctx.default_map = json.load(config_file)
            except json.JSONDecodeError:
                click.echo(
                    click.style("[!]", fg="red", bold=True)
                    + f" Invalid config file: {config_path}"
                )
                exit(1)


@click.command()
@optgroup.group("Input Options")
@optgroup.option(
    "-i",
    "--input",
    "input_files",
    multiple=True,
    type=click.File(lazy=True),
    metavar="FILE",
    help="Download from URLs/artists subdomains listed on file. This option can be used multiple times",
)
@optgroup.group("Audio Options")
@optgroup.option(
    "-f",
    "--format",
    "audio_formats",
    multiple=True,
    type=click.Choice(
        [
            "aac-hi",
            "aiff-lossless",
            "alac",
            "flac",
            "mp3-128",
            "mp3-320",
            "mp3-v0",
            "vorbis",
            "wav",
        ]
    ),
    default=[
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
    help="Preferred audio formats to download. This option can be used multiple times. If not specified, bandcamper will try to download every format available.",
)
@optgroup.option(
    "--fallback/--no-fallback",
    default=False,
    help="Download fallback mp3-128 audio file in case there are no other free downloads available",
)
@optgroup.group("Download Options")
@optgroup.option(
    "-d",
    "--destination",
    type=click.Path(exists=True, file_okay=False, writable=True, resolve_path=True),
    default=".",
    help="Base destination folder for downloaded files. Defaults to current folder",
)
@optgroup.option(
    "-o",
    "--output",
    metavar="TEMPLATE",
    default="{artist_name}/{album_title}/{track_title}.{ext}",
    help="Output filename template. See the 'Output Template' section of the README for all the info",
)
@optgroup.group("Request Options")
@optgroup.option(
    "--http-proxy",
    metavar="URL",
    envvar="HTTP_PROXY",
    help="Proxy to use for HTTP connections",
)
@optgroup.option(
    "--https-proxy",
    metavar="URL",
    envvar="HTTPS_PROXY",
    help="Proxy to use for HTTPS connections",
)
@optgroup.option(
    "--proxy",
    metavar="URL",
    help="Proxy to use for all connections. This option overrides --http-proxy and --https-proxy",
)
@optgroup.group("Output Options")
@optgroup.option(
    "-v",
    "--verbose",
    "verbosity",
    count=True,
    help="Run bandcamper with more verbose output",
)
@optgroup.option(
    "-q", "--quiet", "verbosity", flag_value=-1, help="Completely disable output"
)
@optgroup.option(
    "--colors/--no-colors", default=True, show_default=True, help="Use colored output"
)
@click.argument("urls", nargs=-1, metavar="URL [URL...]")
@click.option(
    "--ignore-errors",
    is_flag=True,
    help="Don't end the program in case of any (predictable) error; show warning instead",
)
@click.option(
    "--config",
    type=click.Path(exists=True, dir_okay=False),
    callback=configure,
    is_eager=True,
    expose_value=False,
    help="Read option defaults from the specified JSON config file. Defaults to bandcamper_config.json",
)
@click.version_option(bandcamper.__version__, "-v", "--version")
@click.help_option("-h", "--help")
def main(
    input_files,
    audio_formats,
    fallback,
    destination,
    output,
    http_proxy,
    https_proxy,
    proxy,
    verbosity,
    colors,
    urls,
    ignore_errors,
):
    bandcamp_downloader = Bandcamper(destination, *urls)
    if not bandcamp_downloader.urls:
        bandcamp_downloader.screamer.error(
            "You must pass at least one URL/artist subdomain to download",
            force_error=True,
        )
    bandcamp_downloader.download_all(audio_formats)


if __name__ == "__main__":
    try:
        main()
    except RuntimeError:
        exit(1)
