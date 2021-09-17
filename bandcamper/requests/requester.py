from pathlib import Path

import click
from requests import Session

from bandcamper.requests.utils import get_default_user_agent
from bandcamper.requests.utils import get_download_file_extension
from bandcamper.requests.utils import humanize_bytes


class Requester:
    def __init__(self, user_agent=None, http_proxy=None, https_proxy=None):
        self.session = Session()
        self.session.headers["User-Agent"] = user_agent or get_default_user_agent()
        self.session.proxies = {
            "http": http_proxy,
            "https": https_proxy,
        }

    def close(self):
        self.session.close()

    def _request_or_error(self, method, url, **kwargs):
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response

    def get_request_or_error(self, url, **kwargs):
        return self._request_or_error("GET", url, **kwargs)

    def post_request_or_error(self, url, **kwargs):
        return self._request_or_error("POST", url, **kwargs)

    def download_to_file(self, url, save_path, filename, label=None):
        with self.session.get(url, stream=True) as response:
            response.raise_for_status()
            file_ext = get_download_file_extension(response.headers.get("Content-Type"))
            file_path = Path(save_path)
            file_path.mkdir(parents=True, exist_ok=True)
            file_path /= filename.format(ext=file_ext)
            content_length = int(response.headers.get("Content-Length"))
            label = label or file_path.name
            label += f" ({humanize_bytes(content_length)})"
            with file_path.open("wb") as file:
                with click.progressbar(
                    response.iter_content(chunk_size=1024),
                    length=content_length // 1024,
                    label=label,
                ) as bar:
                    for chunk in bar:
                        file.write(chunk)
        return file_path

    def get_ip_from_url(self, url):
        response = self.get_request_or_error(url, stream=True)
        return response.raw._connection.sock.getpeername()[0]
