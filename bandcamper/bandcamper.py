import re
from os import getenv
from urllib.parse import urlparse

import requests
from requests.exceptions import RequestException


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

    def __init__(self, screamer, *urls, **kwargs):
        self.params = {
            "force_https": True,
            "proxies": {"http": getenv("HTTP_PROXY"), "https": getenv("HTTPS_PROXY")},
            "ignore_errors": False,
        }
        self.screamer = screamer
        self.params.update(kwargs)
        self.urls = set()
        for url in urls:
            url = self._get_url(url)
            if url:
                self.urls.add(url)

    def _is_valid_custom_domain(self, url):
        valid = False
        try:
            res = requests.get(url, stream=True, proxies=self.params.get("proxies"))
        except RequestException:
            self.screamer.error(f"Unable to connect to {url}!")
        else:
            valid = res.raw._connection.sock.getpeername()[0] == self.CUSTOM_DOMAIN_IP
        finally:
            return valid

    def _get_url(self, name):
        valid_url = ""
        if self.BANDCAMP_SUBDOMAIN_REGEX.fullmatch(name):
            valid_url = f"https://{name.lower()}.bandcamp.com"
        else:
            parsed_url = urlparse(name)
            if not parsed_url.scheme:
                parsed_url = urlparse("https://" + name)
            elif self.params.get("force_https"):
                parsed_url = parsed_url._replace(scheme="https")
            url = parsed_url.geturl()
            if self.BANDCAMP_URL_REGEX.match(
                parsed_url.netloc
            ) or self._is_valid_custom_domain(url):
                valid_url = url
            else:
                self.screamer.error(f"{name} is not a valid Bandcamp URL or subdomain")
        return valid_url
