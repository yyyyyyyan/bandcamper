from pathlib import Path

from bandcamper.bandcamper import Bandcamper


def read_file(*names, **kwargs):
    params = {"encoding": "utf-8"}
    params.update(kwargs)
    file_path = Path(Path(__file__).parent.resolve(), *names)
    with file_path.open(**params) as open_file:
        content = open_file.read().strip()
    return content


__version__ = read_file("VERSION")

__all__ = ["Bandcamper"]
