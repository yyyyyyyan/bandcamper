from mutagen.aiff import AIFF

from bandcamper.metadata.mp3 import MP3Metadata


class AIFFMetadata(MP3Metadata):
    FILE_CLASS = AIFF
