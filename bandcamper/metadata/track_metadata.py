from mutagen import File


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

    def save(self):
        self.file.save()
