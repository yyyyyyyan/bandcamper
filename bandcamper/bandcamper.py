import json
import re
from pathlib import Path
from platform import system as platform_system
from time import sleep
from urllib.parse import urljoin
from urllib.parse import urlparse
from zipfile import ZipFile

from bs4 import BeautifulSoup
from onesecmail import OneSecMail
from onesecmail.validators import FromAddressValidator
from pathvalidate import sanitize_filepath
from requests import HTTPError

from bandcamper.metadata.utils import get_track_output_context
from bandcamper.metadata.utils import suffix_to_metadata
from bandcamper.requests.requester import Requester
from bandcamper.screamo import Screamer
from bandcamper.utils import get_random_filename_template


class Bandcamper:
    """Represents .

    Bandcamper objects are responsible of downloading and organizing
    the music from Bandcamp, among with writing their metadata.
    """

    # Bandcamp subdomain and URL Regexes taken from the pick_subdomain step of creating an artist page.
    # Rules for subdomains are:
    #   - At least 4 characters long
    #   - Only lowercase letters, numbers and hyphens are allowed
    #   - Must not end with hyphen
    _BANDCAMP_SUBDOMAIN_PATTERN = r"[a-z0-9][a-z0-9-]{2,}[a-z0-9]"
    BANDCAMP_SUBDOMAIN_REGEX = re.compile(
        _BANDCAMP_SUBDOMAIN_PATTERN, flags=re.IGNORECASE
    )
    BANDCAMP_URL_REGEX = re.compile(
        r"(?:www\.)?" + _BANDCAMP_SUBDOMAIN_PATTERN + r"\.bandcamp\.com",
        flags=re.IGNORECASE,
    )

    # Bandcamp IP for custom domains taken from the article "How do I set up a custom domain on Bandcamp?".
    # Article available on:
    #   https://get.bandcamp.help/hc/en-us/articles/360007902973-How-do-I-set-up-a-custom-domain-on-Bandcamp-
    CUSTOM_DOMAIN_IP = "35.241.62.186"
    DOWNLOAD_FORMATS = [
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

    BANDCAMP_EMAIL_VALIDATOR = FromAddressValidator(r".+@email\.bandcamp\.com")

    PLATFORMS = {
        "Darwin": "macOS",
    }

    def __init__(
        self,
        *urls,
        fallback=True,
        force_https=True,
        screamer=None,
        requester=None,
    ):
        self.urls = set()
        self.fallback = fallback
        self.force_https = force_https
        self.screamer = screamer or Screamer()
        self.requester = requester or Requester()
        for url in urls:
            self.add_url(url)

    def _is_valid_custom_domain(self, url):
        return self.requester.get_ip_from_url(url) == self.CUSTOM_DOMAIN_IP

    def _add_urls_from_artist(self, source_url):
        response = self.requester.get_request_or_error(source_url)
        base_url = "https://" + urlparse(source_url).netloc.strip("/ ")
        soup = BeautifulSoup(response.content, "lxml")
        music_grid = soup.find("ol", id="music-grid")
        if music_grid is None:
            raise ValueError
        for a in music_grid.find_all("a"):
            parsed_url = urlparse(a.get("href"))
            if parsed_url.scheme:
                url = urljoin(
                    f"{parsed_url.scheme}://" + parsed_url.netloc.strip("/ "),
                    parsed_url.path.strip("/ "),
                )
            else:
                url = urljoin(base_url, parsed_url.path.strip("/ "))
            self.urls.add(url)

    def add_url(self, name):
        if self.BANDCAMP_SUBDOMAIN_REGEX.fullmatch(name):
            url = f"https://{name.lower()}.bandcamp.com/music"
            try:
                self._add_urls_from_artist(url)
            except HTTPError as exc:
                if exc.response.status_code == 404:
                    self.screamer.error(f"{name} not found")
                else:
                    self.screamer.error(f"Request error while getting URLs for {name}")
            except ValueError:
                self.screamer.error(f"No releases found for {name}")
        else:
            parsed_url = urlparse(name)
            if not parsed_url.scheme:
                parsed_url = urlparse("https://" + name)
            elif self.force_https:
                parsed_url = parsed_url._replace(scheme="https")
            url = parsed_url.geturl()
            if self.BANDCAMP_URL_REGEX.fullmatch(
                parsed_url.netloc
            ) or self._is_valid_custom_domain(url):
                if parsed_url.path.strip("/ ") in ["music", ""]:
                    url = f"{parsed_url.scheme}://{parsed_url.netloc}/music"
                    self._add_urls_from_artist(url)
                else:
                    self.urls.add(url)
            else:
                raise ValueError(f"{name} is not a valid Bandcamp URL or subdomain")

    def _get_music_data(self, url):
        try:
            response = self.requester.get_request_or_error(url)
        except HTTPError as exc:
            if exc.response.status_code == 404:
                raise ValueError(f"{url} not found")
            raise exc
        else:
            soup = BeautifulSoup(response.content, "lxml")
            data = json.loads(
                soup.find("script", {"data-tralbum": True})["data-tralbum"]
            )
            data["art_url"] = soup.select_one("div#tralbumArt > a.popupImage")["href"]
            from_album_span = soup.select_one("span.fromAlbum")
            if from_album_span is not None:
                data["album_title"] = from_album_span.text
            return data

    def _free_download(self, url, destination, item_type, *download_formats):
        response = self.requester.get_request_or_error(url)
        soup = BeautifulSoup(response.content, "lxml")
        download_data = json.loads(soup.find("div", id="pagedata")["data-blob"])
        downloadable = download_data["download_items"][0]["downloads"]
        downloaded_paths = []
        for fmt in download_formats:
            if fmt in downloadable:
                parsed_url = urlparse(downloadable[fmt]["url"])
                stat_path = parsed_url.path.replace("/download/", "/statdownload/")
                fwd_url = parsed_url._replace(path=stat_path).geturl()
                fwd_data = self.requester.get_request_or_error(
                    fwd_url,
                    params={".vrs": 1},
                    headers={"Accept": "application/json"},
                ).json()
                if fwd_data["result"].lower() == "ok":
                    download_url = fwd_data["download_url"]
                elif fwd_data["result"].lower() == "err":
                    download_url = fwd_data["retry_url"]
                else:
                    self.screamer.error(f"Error downloading {fmt} from {fwd_url}")
                    continue
                label = f"{fmt}.zip" if item_type == "album" else None
                file_path = self.requester.download_to_file(
                    download_url,
                    destination,
                    get_random_filename_template(),
                    label,
                )
                if file_path.suffix == ".zip":
                    extract_to_path = file_path.parent / file_path.stem
                    with ZipFile(file_path) as zip_file:
                        zip_file.extractall(extract_to_path)
                    file_path.unlink()
                    downloaded_paths.append(extract_to_path)
                else:
                    downloaded_paths.append(file_path)
            else:
                self.screamer.error(f"{fmt} download not found", short_symbol=True)
        return downloaded_paths

    def _get_download_url_from_email(
        self,
        url,
        item_id,
        item_type,
        country="US",
        postcode="0",
        encoding_name="none",
        timeout=60,
    ):
        artist_subdomain = urlparse(url).netloc
        download_url = f"https://{artist_subdomain}/email_download"
        mailbox = OneSecMail.generate_random_mailbox(
            proxies=self.requester.session.proxies,
            headers=self.requester.session.headers,
        )
        form_data = {
            "encoding_name": encoding_name,
            "item_id": item_id,
            "item_type": item_type,
            "address": mailbox.address,
            "country": country,
            "postcode": postcode,
        }
        response = self.requester.post_request_or_error(download_url, data=form_data)
        if not response.json()["ok"]:
            raise ValueError(f"Email download request failed: {response.text}")
        msgs = []
        time_sleeping = 0
        while not msgs:
            if time_sleeping > timeout:
                raise ValueError(
                    "Bandcamp email not received. Try increasing the timeout."
                )
            sleep(1)
            time_sleeping += 1
            msgs = mailbox.get_messages(validators=[self.BANDCAMP_EMAIL_VALIDATOR])
        soup = BeautifulSoup(msgs[0].html_body, "lxml")
        return soup.find("a")["href"]

    def _sanitize_file_path(self, file_path):
        platform = platform_system()
        platform = self.PLATFORMS.get(platform, platform)
        return sanitize_filepath(file_path, platform=platform)

    def move_file(self, file_path, destination, output, output_extra, tracks, context):
        if file_path.suffix in suffix_to_metadata:
            context.update(get_track_output_context(file_path, tracks))
        else:
            output = output_extra
            context["filename"] = file_path.name
        move_to = self._sanitize_file_path(destination / output.format(**context))
        move_to.parent.mkdir(parents=True, exist_ok=True)
        file_path.replace(move_to)
        return move_to

    def download_fallback_mp3(self, track_info, artist, album, title, destination):
        file_paths = []
        for track in track_info:
            if track.get("file"):
                track_num = f"{track['track_num'] or 0:02d}"
                if title is None:
                    title = track["title"]
                file_paths.append(
                    self.requester.download_to_file(
                        track["file"]["mp3-128"],
                        destination,
                        f"{artist} - {album} - {track_num} {title}{{ext}}",
                        f"{track_num}.mp3",
                    )
                )
        return file_paths

    def download_from_url(
        self, url, destination, output, output_extra, *download_formats
    ):
        self.screamer.info(f"Searching available downloads for URL {url}")
        destination = Path(destination)
        download_formats = set(download_formats)
        download_mp3 = False
        if "mp3-128" in download_formats:
            download_formats.remove("mp3-128")
            download_mp3 = True

        music_data = dict()
        try:
            music_data = self._get_music_data(url)
        except ValueError as exc:
            self.screamer.error(str(exc))
            return
        except HTTPError as exc:
            self.screamer.error(
                f"Request error ({exc.response.status_code}) when getting music data from {url}"
            )
            return
        if not music_data:
            self.screamer.error(f"Failed to get music data from {url}")
            return

        tracks = {
            track["track_num"]: track["title"] for track in music_data["trackinfo"]
        }
        artist = music_data["artist"]
        title = music_data["current"]["title"]
        year = (
            music_data["current"].get("release_date")
            or music_data["current"]["publish_date"]
        ).split()[2]

        downloading_str = f"Downloading {artist} - {title}"
        if music_data["item_type"] == "album":
            album = title
            title = None
        else:
            album = music_data.get("album_title", "")

        if music_data.get("freeDownloadPage"):
            self.screamer.success(f"Free download found! {downloading_str}")
            file_paths = self._free_download(
                music_data["freeDownloadPage"],
                destination,
                music_data["item_type"],
                *download_formats,
            )
        elif music_data["current"].get("require_email"):
            self.screamer.success(f"Email download found! {downloading_str}")
            download_url = self._get_download_url_from_email(
                url, music_data["id"], music_data["item_type"]
            )
            file_paths = self._free_download(
                download_url, destination, music_data["item_type"], *download_formats
            )
        elif self.fallback or download_mp3:
            self.screamer.success(f"MP3-128 download found! {downloading_str}")
            file_paths = self.download_fallback_mp3(
                music_data["trackinfo"], artist, album, title, destination
            )
            download_mp3 = False
        else:
            raise ValueError(
                f"No free download found for {url}. Try setting fallback to True."
            )

        if download_mp3:
            file_paths.extend(
                self.download_fallback_mp3(
                    music_data["trackinfo"], artist, album, title, destination
                )
            )

        context = {
            "artist": artist,
            "album": album,
            "year": year,
        }
        for file_path in file_paths:
            if file_path.is_dir():
                dir_contents = list(file_path.iterdir())
                context["ext"] = get_track_output_context(dir_contents[-1], tracks)[
                    "ext"
                ]
                for track_path in dir_contents:
                    new_path = self.move_file(
                        track_path, destination, output, output_extra, tracks, context
                    )
                    self.screamer.success(
                        f"New file: {new_path}", verbose=True, short_symbol=True
                    )
                self.screamer.success(
                    f"New directory: {new_path.parent}", short_symbol=True
                )
                file_path.rmdir()
            else:
                new_path = self.move_file(
                    file_path, destination, output, output_extra, tracks, context
                )
                self.screamer.success(f"New file: {new_path}", short_symbol=True)

    def download_all(self, destination, output, output_extra, *download_formats):
        for url in self.urls:
            self.download_from_url(
                url, destination, output, output_extra, *download_formats
            )
