import json
from pathlib import Path
from sys import exit

import click
from click_option_group import optgroup

import bandcamper
from bandcamper import Bandcamper
from bandcamper.requests.requester import Requester
from bandcamper.requests.utils import get_random_user_agent
from bandcamper.screamo import Screamer


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
    type=click.File(),
    metavar="FILE",
    help="Download from URLs/artists subdomains listed on file. This option can be used multiple times",
)
@optgroup.group("Audio Options")
@optgroup.option(
    "-f",
    "--format",
    "audio_formats",
    multiple=True,
    type=click.Choice(Bandcamper.DOWNLOAD_FORMATS),
    default=[
        "mp3-320",
    ],
    help="Preferred audio formats to download. This option can be used multiple times. Defaults to mp3-320.",
)
@optgroup.option(
    "--fallback/--no-fallback",
    default=True,
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
    default="{artist}/{album}/{track_num:02d} - {track}.{ext}",
    help="Output filename template. See the 'Output Template' section of the README for all the info",
)
@optgroup.option(
    "--output-extra",
    metavar="TEMPLATE",
    default="{artist}/{album}/{filename}",
    help="Output filename template for extra files. See the 'Extra Output Template' section of the README for all the info",
)
@optgroup.option(
    "-s",
    "--slash-replacement",
    metavar="STRING",
    default=".",
    help="Replace slashes in output filenames with this string. Defaults to '.'",
)
@optgroup.group("Request Options")
@optgroup.option(
    "--random-user-agent",
    is_flag=True,
    help="Use random User-Agent for Bandcamp requests",
)
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
@optgroup.option(
    "--force-https/--no-force-https",
    default=True,
    show_default=True,
    help="Rewrite every URL to use HTTPS",
)
@optgroup.group("Output Options")
@optgroup.option(
    "-v",
    "--verbose",
    "verbosity",
    flag_value=1,
    help="Run bandcamper with more verbose output",
)
@optgroup.option(
    "-q", "--quiet", "verbosity", flag_value=-1, help="Completely disable output"
)
@optgroup.option(
    "--colored/--no-colors", default=True, show_default=True, help="Use colored output"
)
@click.argument("urls", nargs=-1, metavar="URL [URL...]")
@click.option(
    "--config",
    type=click.Path(exists=True, dir_okay=False),
    callback=configure,
    is_eager=True,
    expose_value=False,
    help="Read option defaults from the specified JSON config file. Defaults to bandcamper_config.json",
)
@click.version_option(bandcamper.__version__, "-V", "--version")
@click.help_option("-h", "--help")
def main(
    input_files,
    audio_formats,
    fallback,
    destination,
    output,
    output_extra,
    slash_replacement,
    random_user_agent,
    http_proxy,
    https_proxy,
    proxy,
    force_https,
    verbosity,
    colored,
    urls,
):
    if verbosity is None:
        verbosity = 0
    screamer = Screamer(verbosity, colored)

    user_agent = get_random_user_agent() if random_user_agent else None
    http_proxy = http_proxy or proxy
    https_proxy = https_proxy or proxy

    requester = Requester(user_agent, http_proxy, https_proxy)

    urls = list(urls)
    for file in input_files:
        urls.extend(file.read().strip().splitlines())

    bandcamp_downloader = Bandcamper(
        fallback=fallback,
        force_https=force_https,
        screamer=screamer,
        requester=requester,
        slash_replacement=slash_replacement,
    )
    for url in urls:
        try:
            bandcamp_downloader.add_url(url)
        except ValueError as err:
            screamer.error(str(err))
    if not bandcamp_downloader.urls:
        screamer.critical(
            "You must provice bandcamper at least one valid URL/artist subdomain to download"
        )

    bandcamp_downloader.download_all(destination, output, output_extra, *audio_formats)


if __name__ == "__main__":
    try:
        main()
    except RuntimeError:
        exit(1)
