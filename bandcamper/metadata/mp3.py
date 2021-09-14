from mimetypes import guess_type

from mutagen.id3 import APIC
from mutagen.id3 import TALB
from mutagen.id3 import TIT2
from mutagen.id3 import TPE1
from mutagen.id3 import TPE2
from mutagen.id3 import TRCK
from mutagen.id3 import USLT
from mutagen.mp3 import MP3

from bandcamper.metadata.track_metadata import TrackMetadata


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
