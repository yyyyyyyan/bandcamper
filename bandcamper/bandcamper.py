import json
import re
from os import getenv
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from tqdm import tqdm

from bandcamper.requests_utils import get_random_user_agent
from bandcamper.screamo import Screamer


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

    def __init__(self, base_path, *urls, **kwargs):
        self.params = {
            "quiet": 0,
            "colored": True,
            "ignore_errors": False,
            "force_https": True,
            "proxies": {"http": getenv("HTTP_PROXY"), "https": getenv("HTTPS_PROXY")},
            "headers": {"User-Agent": get_random_user_agent()},
            "download_formats": ["mp3-320", "flac"],
        }
        self.base_path = Path(base_path)
        self.params.update(kwargs)
        self.proxies = self.params.pop("proxies")
        self.screamer = Screamer(self.params.pop("quiet"), self.params.pop("colored"), self.params.pop("ignore_errors"))
        self.headers = self.params.pop("headers")
        self.urls = set()
        for url in urls:
            self.add_url(url)

    def _get_request_or_error(self, url, **kwargs):
        headers = {**self.headers, **kwargs.pop("headers", dict())}
        try:
            response = requests.get(url, proxies=self.proxies, headers=headers, **kwargs)
            response.raise_for_status()
        except RequestException as err:
            self.screamer.error(str(err), True)
            return None
        return response

    def _is_valid_custom_domain(self, url):
        valid = False
        response = self._get_request_or_error(url, stream=True)
        if response is not None:
            valid = (
                response.raw._connection.sock.getpeername()[0] == self.CUSTOM_DOMAIN_IP
            )
        return valid

    def _add_urls_from_artist(self, source_url):
        self.screamer.info(f"Scraping URLs from {source_url}...", True)
        response = self._get_request_or_error(source_url)
        if response is not None:
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
            elif self.params.get("force_https"):
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
                self.screamer.error(f"{name} is not a valid Bandcamp URL or subdomain")

    def _get_music_data(self, url):
        response = self._get_request_or_error(url)
        soup = BeautifulSoup(response.content, "lxml")
        data = json.loads(soup.find("script", {"data-tralbum": True})["data-tralbum"])
        data["art_url"] = soup.select_one("div#tralbumArt > a.popupImage")["href"]
        return data

    def download_to_file(self, url, file_path):
        file_path = self.base_path / file_path
        try:
            with requests.get(url, stream=True, proxies=self.proxies, headers=self.headers) as response:
                response.raise_for_status()
                with file_path.open("wb") as file:
                    for chunk in tqdm(response.iter_content(chunk_size=1024), desc=file_path.name, total=response.headers.get("Content-Length"), unit="KiB", colour="#39d017"):
                        file.write(chunk)
        except RequestException as err:
            self.screamer.error(str(err), True)

    def _free_download(self, url):
        response = self._get_request_or_error(url)
        soup = BeautifulSoup(response.content, "lxml")
        download_data = json.loads(soup.find("div", id="pagedata")["data-blob"])
        downloadable = download_data["download_items"][0]["downloads"]
        for fmt in self.params["download_formats"]:
            if fmt in downloadable:
                self.screamer.info(f"Downloading {fmt}...", True)
                parsed_url = urlparse(downloadable[fmt]["url"])
                stat_path = parsed_url.path.replace("/download/", "/statdownload/")
                fwd_url = parsed_url._replace(path=stat_path).geturl()
                fwd_data = self._get_request_or_error(fwd_url, params={".vrs": 1}, headers={"Accept": "application/json"}).json()
                if fwd_data["result"].lower() == "ok":
                    self.download_to_file(fwd_data["download_url"])
                elif fwd_data["result"].lower() == "err":
                    self.download_to_file(fwd_data["retry_url"])
            else:
                self.screamer.warning(f"{fmt} download not found", True)

    def download_from_url(self, url):
        music_data = self._get_music_data(url)
        if music_data.get("freeDownloadPage"):
            self.screamer.info("Free download link available", True)
            self._free_download(music_data["freeDownloadPage"])

    def download_all(self):
        for url in self.urls:
            self.download_from_url(url)