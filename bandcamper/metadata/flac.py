from mimetypes import guess_type

from mutagen.flac import FLAC
from mutagen.flac import Picture

from bandcamper.metadata.mp4 import MP4Metadata


class FLACMetadata(MP4Metadata):
    FILE_CLASS = FLAC
    TITLE_TAG = "title"
    TRACK_NUMBER_TAG = "tracknumber"
    TRACK_TOTAL_TAG = "tracktotal"
    ALBUM_TAG = "album"
    ARTIST_TAG = "artist"
    ALBUM_ARTIST_TAG = "albumartist"
    LYRICS_TAG = "unsyncedlyrics"

    def _get_first_item_of_tag_or_none(self, tag):
        return self.file.get(tag, [None])[0]

    @property
    def track_number(self):
        return int("0" + self.file.get(self.TRACK_NUMBER_TAG, [""])[0]) or None

    @track_number.setter
    def track_number(self, val):
        self.file[self.TRACK_NUMBER_TAG] = str(val)

    @property
    def track_total(self):
        return int("0" + self.file.get(self.TRACK_TOTAL_TAG, [""])[0]) or None

    @track_total.setter
    def track_total(self, val):
        self.file[self.TRACK_TOTAL_TAG] = str(val)

    @property
    def cover_art(self):
        if self.file.pictures:
            return self.file.pictures[0].data
        return None

    def set_cover_art_from_file(self, file_path):
        picture = Picture()
        picture.mime = guess_type(file_path)[0]
        picture.desc = "cover"
        with open(file_path, "rb") as file:
            picture.data = file.read()
        self.file.clear_pictures()
        self.file.add_picture(picture)
