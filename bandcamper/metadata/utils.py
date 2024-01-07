import re
from pathlib import Path

from bandcamper.metadata.aiff import AIFFMetadata
from bandcamper.metadata.flac import FLACMetadata
from bandcamper.metadata.mp3 import MP3Metadata
from bandcamper.metadata.mp4 import MP4Metadata
from bandcamper.metadata.vorbis import VorbisMetadata
from bandcamper.metadata.wave import WAVEMetadata

FILENAME_REGEX = re.compile(
    r"(?P<artist>.+) - (?P<album>.+)? - (?P<track_number>\d{2,}) (?P<title>.+)\.(aiff|flac|m4a|mp3|ogg|wav)",
    flags=re.I,
)

suffix_to_metadata = {
    ".mp3": MP3Metadata,
    ".aiff": AIFFMetadata,
    ".wav": WAVEMetadata,
    ".m4a": MP4Metadata,
    ".flac": FLACMetadata,
    ".ogg": VorbisMetadata,
}


def get_track_metadata(file_path):
    file_path = Path(file_path)
    ext = file_path.suffix
    if ext not in suffix_to_metadata:
        raise ValueError(f"Extension {file_path} not recognized")
    return suffix_to_metadata[ext](file_path)


def parse_filename(filename):
    match = FILENAME_REGEX.match(filename)
    if match is None:
        return dict()
    return match.groupdict()


def get_track_output_context(track_path, tracks, slash_replacement):
    track_metadata = get_track_metadata(track_path)
    file_path = Path(track_metadata.file.filename)
    filename_data = parse_filename(file_path.name)
    track_number = track_metadata.track_number or int(
        filename_data.get("track_number", 0)
    )
    track_title = (
        tracks.get(track_number)
        or track_metadata.title
        or filename_data.get("title", "")
    )
    context = {
        "track": track_title.replace("/", slash_replacement),
        "track_num": track_number,
        "ext": file_path.suffix.split(".")[-1],
    }
    return context
