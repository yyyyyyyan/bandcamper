from abc import ABC
from abc import abstractmethod

from mutagen import File


class TrackMetadata(ABC):
    """Handles the metadata of track files.

    Parameters
    ----------
    filename : str or path-like object.
        The filename or file-path of the respective file to read/write metadata.

    Attributes
    ----------
    file : mutagen.FileType
        The track file.
    """

    FILE_CLASS = File

    def __init__(self, filename):
        self.file = self.FILE_CLASS(filename)

    def save(self):
        self.file.save()

    @property
    @abstractmethod
    def title(self):
        """The title of the track.

        Returns
        -------
        str or None
        """

    @title.setter
    @abstractmethod
    def title(self, val):
        pass

    @property
    @abstractmethod
    def track_number(self):
        """The number of the track.

        Returns
        -------
        int or None
        """

    @track_number.setter
    @abstractmethod
    def track_number(self, val):
        pass

    @property
    @abstractmethod
    def track_total(self):
        """The total number of tracks in the album.

        Returns
        -------
        int or None
        """

    @track_total.setter
    @abstractmethod
    def track_total(self, val):
        pass

    @property
    @abstractmethod
    def album(self):
        """The title of the album.

        Returns
        -------
        str or None
        """

    @album.setter
    @abstractmethod
    def album(self, val):
        pass

    @property
    @abstractmethod
    def artist(self):
        """The name of the artist.

        Returns
        -------
        str or None
        """

    @artist.setter
    @abstractmethod
    def artist(self, val):
        pass

    @property
    @abstractmethod
    def album_artist(self):
        """The name of the album artist.

        Returns
        -------
        str or None
        """

    @album_artist.setter
    @abstractmethod
    def album_artist(self, val):
        pass

    @property
    @abstractmethod
    def lyrics(self):
        """The lyrics of the track.

        Returns
        -------
        str or None
        """

    @lyrics.setter
    @abstractmethod
    def lyrics(self, val):
        pass

    @property
    @abstractmethod
    def cover_art(self):
        """The cover art.

        Returns
        -------
        bytes or None
        """
