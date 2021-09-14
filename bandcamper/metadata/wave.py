from mutagen.wave import WAVE

from bandcamper.metadata.mp3 import MP3Metadata


class WAVEMetadata(MP3Metadata):
    FILE_CLASS = WAVE
