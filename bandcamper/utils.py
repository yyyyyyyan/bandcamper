import re
from uuid import uuid4


MUSIC_FILE_EXTENSIONS = r".*\.(aiff|flac|m4a|mp3|ogg|wav)"


def get_random_filename_template():
    return uuid4().hex[:16] + "{ext}"


def get_extension_from_dir_contents(contents):
    for filepath in contents:
        m = re.match(MUSIC_FILE_EXTENSIONS, filepath)
        if m:
            return m.group().split(".")[-1]
