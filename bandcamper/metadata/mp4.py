from mimetypes import guess_type

from mutagen.mp4 import AtomDataType
from mutagen.mp4 import MP4
from mutagen.mp4 import MP4Cover

from bandcamper.metadata.track_metadata import TrackMetadata


class MP4Metadata(TrackMetadata):
    FILE_CLASS = MP4
    TITLE_TAG = "©nam"
    TRACK_NUMBER_TAG = "trkn"
    ALBUM_TAG = "©alb"
    ARTIST_TAG = "©ART"
    ALBUM_ARTIST_TAG = "aART"
    LYRICS_TAG = "©lyr"
    COVER_ART_TAG = "covr"

    def _get_first_item_of_tag_or_none(self, tag):
        items = self.file.get(tag)
        if isinstance(items, (list, tuple)):
            return items[0]
        return items

    @property
    def title(self):
        return self._get_first_item_of_tag_or_none(self.TITLE_TAG)

    @title.setter
    def title(self, val):
        self.file[self.TITLE_TAG] = val

    @property
    def track_number(self):
        return self.file.get(self.TRACK_NUMBER_TAG, [[None]])[0][0]

    @track_number.setter
    def track_number(self, val):
        old_track_number, track_total = self.file.get(self.TRACK_NUMBER_TAG, [(0, 0)])[
            0
        ]
        self.file[self.TRACK_NUMBER_TAG] = [(val, track_total)]

    @property
    def track_total(self):
        return self.file.get(self.TRACK_NUMBER_TAG, [(None, None)])[0][1]

    @track_total.setter
    def track_total(self, val):
        track_number, old_track_total = self.file.get(self.TRACK_NUMBER_TAG, [(0, 0)])[
            0
        ]
        self.file[self.TRACK_NUMBER_TAG] = [(track_number, val)]

    @property
    def album(self):
        return self._get_first_item_of_tag_or_none(self.ALBUM_TAG)

    @album.setter
    def album(self, val):
        self.file[self.ALBUM_TAG] = val

    @property
    def artist(self):
        return self._get_first_item_of_tag_or_none(self.ARTIST_TAG)

    @artist.setter
    def artist(self, val):
        self.file[self.ARTIST_TAG] = val

    @property
    def album_artist(self):
        return self._get_first_item_of_tag_or_none(self.ALBUM_ARTIST_TAG)

    @album_artist.setter
    def album_artist(self, val):
        self.file[self.ALBUM_ARTIST_TAG] = val

    @property
    def lyrics(self):
        return self._get_first_item_of_tag_or_none(self.LYRICS_TAG)

    @lyrics.setter
    def lyrics(self, val):
        self.file[self.LYRICS_TAG] = val

    @property
    def cover_art(self):
        if self.COVER_ART_TAG in self.file:
            return self.file[self.COVER_ART_TAG][0]
        return None

    def set_cover_art_from_file(self, file_path):
        mime = guess_type(file_path)[0]
        if mime == "image/jpeg":
            image_format = AtomDataType.JPEG
        elif mime == "image/png":
            image_format = AtomDataType.PNG
        else:
            raise ValueError(f"{file_path} must be either a JPEG or a PNG image.")
        with open(file_path, "rb") as file:
            cover = MP4Cover(data=file.read(), imageformat=image_format)
        self.file[self.COVER_ART_TAG] = [cover]
