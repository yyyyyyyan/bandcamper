import re
from copy import deepcopy
from os import getenv
from socket import gethostbyname
from urllib.parse import urlparse, urljoin


class Bandcamper:
    """Bandcamper class.

    Bandcamper objects are responsible of downloading and organizing
    the music from Bandcamp, among with writing their metadata.
    """
    # Bandcamp subdomain and URL Regexes taken from the pick_subdomain step of creating an artist page.
    # Rules for subdomains are:
    #   - At least 4 characters long
    #   - Only lowercase letters, numbers and hyphens are allowed
    #   - Must not end with hyphen
    _BANDCAMP_SUBDOMAIN_PATTERN = r"^[a-z0-9][a-z0-9-]{2,}[a-z0-9]"
    BANDCAMP_SUBDOMAIN_REGEX = re.compile(_BANDCAMP_SUBDOMAIN_PATTERN, flags=re.IGNORECASE)
    BANDCAMP_URL_REGEX = re.compile(_BANDCAMP_SUBDOMAIN_PATTERN + r"\.bandcamp\.com$", flags=re.IGNORECASE)

    # Bandcamp IP for custom domains taken from the article "How do I set up a custom domain on Bandcamp?".
    # Article available on:
    #   https://get.bandcamp.help/hc/en-us/articles/360007902973-How-do-I-set-up-a-custom-domain-on-Bandcamp-
    CUSTOM_DOMAIN_IP = "35.241.62.186"

    def __init__(self, *names, **kwargs):
        self.params = {
            "preferred_scheme": "https",
            "proxies": {
                "http": getenv("HTTP_PROXY"),
                "https": getenv("HTTPS_PROXY")
            },
            "ignore_errors": False,
        }
        self.params.update(deepcopy(kwargs))
        self.urls = set()
        for name in names:
            url = self._get_url(name)
            if name:
                self.urls.add(url)

    def _get_url(self, name):
        url = ""
        parsed_url = urlparse(name)
        if parsed_url.scheme and parsed_url.netloc:
            domain = parsed_url.netloc
            # TODO: Consider changing gethostbyname by something that supports proxies.
            if self.BANDCAMP_URL_REGEX.match(domain) or gethostbyname(domain) == self.CUSTOM_DOMAIN_IP:
                scheme = self.params.get("preferred_scheme") or parsed_url.scheme
                url = urljoin(f"{scheme}://{domain.lower()}", parsed_url.path)
            elif self.params.get("ignore_errors"):
                # TODO: Add warning.
                pass
            else:
                raise ValueError(f"{name} is not a valid Bandcamp URL")
        elif self.BANDCAMP_SUBDOMAIN_REGEX.match(name):
            url = f"https://{name.lower()}.bandcamp.com"
        elif self.params.get("ignore_errors"):
            # TODO: Add warning.
            pass
        else:
            raise ValueError(f"{name} is not a valid Bandcamp subdomain")
        return url