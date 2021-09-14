from mutagen.oggvorbis import OggVorbis

from bandcamper.metadata.flac import FLACMetadata


class VorbisMetadata(FLACMetadata):
    FILE_CLASS = OggVorbis

    @property
    def cover_art(self):
        return None

    def set_cover_art_from_file(self, file_path):
        raise ValueError("Can't set cover art for Vorbis file")
