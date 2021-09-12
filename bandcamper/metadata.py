from mimetypes import guess_type

from mutagen import File
from mutagen.aiff import AIFF
from mutagen.id3 import APIC
from mutagen.id3 import TALB
from mutagen.id3 import TIT2
from mutagen.id3 import TPE1
from mutagen.id3 import TPE2
from mutagen.id3 import TRCK
from mutagen.id3 import USLT
from mutagen.mp3 import MP3
from mutagen.mp4 import AtomDataType
from mutagen.mp4 import MP4
from mutagen.mp4 import MP4Cover


class TrackMetadata:
    """Handles the metadata of track files.

    Parameters
    ----------
    filename : str or path-like object.
        The filename or file-path of the respective file to read/write metadata.

    Attributes
    ----------
    file : mutagen.FileType
        The track file.
    title : str or None
        The title of the track.
    track_number : int or None
        The number of the track.
    track_total : int or None
        The total number of tracks in the album.
    album : str or None
        The name of the album.
    artist : str or None
        The name of the artist.
    album_artist : str or None
        The name of the album artist.
    lyrics : str or None
        The lyrics of the track.
    cover_art : bytes or None
        The cover art.
    """

    FILE_CLASS = File

    def __init__(self, filename):
        self.file = self.FILE_CLASS(filename)
        self.title = None
        self.track_number = None
        self.track_total = None
        self.album = None
        self.artist = None
        self.album_artist = None
        self.lyrics = None
        self.cover_art = None

    def save(self):
        self.file.save()


class MP3Metadata(TrackMetadata):
    FILE_CLASS = MP3
    TITLE_TAG = "TIT2"
    TRACK_NUMBER_TAG = "TRCK"
    ALBUM_TAG = "TALB"
    ARTIST_TAG = "TPE1"
    ALBUM_ARTIST_TAG = "TPE2"
    LYRICS_TAG = "USLT"
    COVER_ART_TAG = "APIC:cover"

    @property
    def title(self):
        return self.file.get(self.TITLE_TAG, [None])[0]

    @title.setter
    def title(self, val):
        if self.TITLE_TAG not in self.file:
            self.file[self.TITLE_TAG] = TIT2()
        self.file[self.TITLE_TAG].text = val

    @property
    def track_number(self):
        return (
            int("0" + self.file.get(self.TRACK_NUMBER_TAG, [""])[0].split("/")[0])
            or None
        )

    @track_number.setter
    def track_number(self, val):
        if self.TRACK_NUMBER_TAG not in self.file:
            self.file[self.TRACK_NUMBER_TAG] = TRCK()
            self.file[self.TRACK_NUMBER_TAG].text = str(val)
        else:
            track_numbers = self.file[self.TRACK_NUMBER_TAG][0].split("/")
            if len(track_numbers) < 2:
                self.file[self.TRACK_NUMBER_TAG].text = str(val)
            else:
                self.file[self.TRACK_NUMBER_TAG].text = f"{val}/{track_numbers[1]}"

    @property
    def track_total(self):
        track_numbers = self.file.get(self.TRACK_NUMBER_TAG, [""])[0].split("/")
        if len(track_numbers) < 2:
            return None
        return int("0" + track_numbers[1]) or None

    @track_total.setter
    def track_total(self, val):
        if self.TRACK_NUMBER_TAG not in self.file:
            self.file[self.TRACK_NUMBER_TAG] = TRCK()
            self.file[self.TRACK_NUMBER_TAG].text = f"0/{val}"
        else:
            track_numbers = self.file[self.TRACK_NUMBER_TAG][0].split("/")
            if len(track_numbers) < 2:
                self.file[self.TRACK_NUMBER_TAG].text = f"0/{val}"
            else:
                self.file[self.TRACK_NUMBER_TAG].text = f"{track_numbers[0]}/{val}"

    @property
    def album(self):
        return self.file.get(self.ALBUM_TAG, [None])[0]

    @album.setter
    def album(self, val):
        if self.ALBUM_TAG not in self.file:
            self.file[self.ALBUM_TAG] = TALB()
        self.file[self.ALBUM_TAG].text = val

    @property
    def artist(self):
        return self.file.get(self.ARTIST_TAG, [None])[0]

    @artist.setter
    def artist(self, val):
        if self.ARTIST_TAG not in self.file:
            self.file[self.ARTIST_TAG] = TPE1()
        self.file[self.ARTIST_TAG].text = val

    @property
    def album_artist(self):
        return self.file.get(self.ALBUM_ARTIST_TAG, [None])[0]

    @album_artist.setter
    def album_artist(self, val):
        if self.ALBUM_ARTIST_TAG not in self.file:
            self.file[self.ALBUM_ARTIST_TAG] = TPE2()
        self.file[self.ALBUM_ARTIST_TAG].text = val

    @property
    def lyrics(self):
        lyrics_tags = self.file.tags.getall(self.LYRICS_TAG)
        if lyrics_tags:
            return lyrics_tags[0].text
        return None

    @lyrics.setter
    def lyrics(self, val):
        lyrics_tags = self.file.tags.getall(self.LYRICS_TAG)
        if lyrics_tags:
            lyrics_tags[0].text = val
        else:
            self.file[self.LYRICS_TAG] = USLT()
            self.file[self.LYRICS_TAG].text = val

    @property
    def cover_art(self):
        if self.COVER_ART_TAG in self.file:
            return self.file[self.COVER_ART_TAG].data
        return None

    def set_cover_art_from_file(self, file_path):
        apic = APIC()
        apic.mime = guess_type(file_path)[0]
        apic.desc = "cover"
        with open(file_path, "rb") as file:
            apic.data = file.read()
        self.file[self.COVER_ART_TAG] = apic


class AIFFMetadata(MP3Metadata):
    FILE_CLASS = AIFF


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
