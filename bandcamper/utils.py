from uuid import uuid4


def get_random_filename_template():
    return uuid4().hex[:16] + "{ext}"
