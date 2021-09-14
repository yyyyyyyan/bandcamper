import re
from pathlib import Path

from bandcamper.metadata.aiff import AIFFMetadata
from bandcamper.metadata.flac import FLACMetadata
from bandcamper.metadata.mp3 import MP3Metadata
from bandcamper.metadata.mp4 import MP4Metadata
from bandcamper.metadata.vorbis import VorbisMetadata
from bandcamper.metadata.wave import WAVEMetadata

FILENAME_REGEX = re.compile(
    r"(?P<artist>.+) - (?P<album>.+) - (?P<track_number>\d{2,}) (?P<title>.+)\.(aiff|flac|m4a|mp3|ogg|wav)",
    flags=re.I,
)


def get_track_metadata(file_path):
    file_path = Path(file_path)
    ext = file_path.suffix
    if ext == ".mp3":
        return MP3Metadata(file_path)
    if ext == ".aiff":
        return AIFFMetadata(file_path)
    if ext == ".wav":
        return WAVEMetadata(file_path)
    if ext == ".m4a":
        return MP4Metadata(file_path)
    if ext == ".flac":
        return FLACMetadata(file_path)
    if ext == ".ogg":
        return VorbisMetadata(file_path)
    raise ValueError(f"Extension {ext} not recognized")


def parse_filename(filename):
    match = FILENAME_REGEX.match(filename)
    if match is None:
        raise ValueError(f"Error parsing filename '{filename}'")
    track_data = match.groupdict()
    track_data["track_number"] = int(track_data["track_number"])
    return track_data


def get_track_output_context(track_path, artist, album, year):
    track_metadata = get_track_metadata(track_path)
    filename = Path(track_metadata.file.filename).name
    return
