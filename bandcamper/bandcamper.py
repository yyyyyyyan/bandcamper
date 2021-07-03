import json
import re
from pathlib import Path
from urllib.parse import urljoin
from urllib.parse import urlparse

import click
import requests
from bs4 import BeautifulSoup

from bandcamper.requests_utils import get_download_file_extension
from bandcamper.requests_utils import get_random_user_agent


class BandcampItem:
    def __init__(self, item_type, **music_data):
        self.item_type = item_type

    @classmethod
    def from_url(cls, url):
        pass


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

    def __init__(
        self,
        base_path,
        urls,
        http_proxy=None,
        https_proxy=None,
        force_https=True,
    ):
        # TODO: properly set kwargs
        self.base_path = Path(base_path)
        self.urls = {*urls}
        for url in urls:
            self.add_url(url)
        self.proxies = {"http": http_proxy, "https": https_proxy}
        self.force_https = True
        self.headers = {"User-Agent": get_random_user_agent()}

    def _get_request_or_error(self, url, **kwargs):
        proxies = kwargs.pop("proxies", self.proxies)
        headers = kwargs.pop("headers", self.headers)
        response = requests.get(url, proxies=proxies, headers=headers, **kwargs)
        response.raise_for_status()
        return response

    def _is_valid_custom_domain(self, url):
        response = self._get_request_or_error(url, stream=True)
        return response.raw._connection.sock.getpeername()[0] == self.CUSTOM_DOMAIN_IP

    def _add_urls_from_artist(self, source_url):
        response = self._get_request_or_error(source_url)
        base_url = "https://" + urlparse(source_url).netloc.strip("/ ")
        soup = BeautifulSoup(response.content, "lxml")
        for a in soup.find("ol", id="music-grid").find_all("a"):
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
            self._add_urls_from_artist(url)
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
        response = self._get_request_or_error(url)
        soup = BeautifulSoup(response.content, "lxml")
        data = json.loads(soup.find("script", {"data-tralbum": True})["data-tralbum"])
        data["art_url"] = soup.select_one("div#tralbumArt > a.popupImage")["href"]
        return data

    def download_to_file(self, url, file_path):
        with requests.get(
            url, stream=True, proxies=self.proxies, headers=self.headers
        ) as response:
            response.raise_for_status()
            file_ext = get_download_file_extension(response.headers.get("Content-Type"))
            file_path = self.base_path / str(file_path).format(ext=file_ext)
            with file_path.open("wb") as file:
                with click.progressbar(
                    response.iter_content(chunk_size=1024),
                    length=response.headers.get("Content-Length"),
                    label=file_path.name,
                ) as bar:
                    for chunk in bar:
                        file.write(chunk)
        return file_path

    def _free_download(self, url, download_formats):
        response = self._get_request_or_error(url)
        soup = BeautifulSoup(response.content, "lxml")
        download_data = json.loads(soup.find("div", id="pagedata")["data-blob"])
        downloadable = download_data["download_items"][0]["downloads"]
        for fmt in download_formats:
            if fmt in downloadable:
                parsed_url = urlparse(downloadable[fmt]["url"])
                stat_path = parsed_url.path.replace("/download/", "/statdownload/")
                fwd_url = parsed_url._replace(path=stat_path).geturl()
                fwd_data = self._get_request_or_error(
                    fwd_url,
                    params={".vrs": 1},
                    headers={**self.headers, "Accept": "application/json"},
                ).json()
                if fwd_data["result"].lower() == "ok":
                    download_url = fwd_data["download_url"]
                elif fwd_data["result"].lower() == "err":
                    download_url = fwd_data["retry_url"]
                else:
                    raise ValueError(f"Error downloading {fmt} from {fwd_url}")
                print(download_url)
                # self.download_to_file(download
            else:
                raise ValueError(f"{fmt} download not found", True)

    def download_all(self, download_formats):
        download_formats = set(download_formats)

        for url in self.urls:
            music_data = self._get_music_data(url)
            if music_data is None:
                raise ValueError(f"Failed to get music data from {url}", True)

            if music_data.get("freeDownloadPage"):
                self._free_download(music_data["freeDownloadPage"], download_formats)
