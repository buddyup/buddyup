# Photo support functions

from collections import namedtuple

from PIL import Image

from buddyup.app import app
from buddyup.templating import img

Dimensions = namedtuple('Dimensions', 'x y')

TINY_SIZE = Dimensions(10, 10)
THUMB_SIZE = Dimensions(20, 20)
LARGE_SIZE = Dimensions(100, 100)
GENERIC_PHOTO = 'index.jpg'

# TODO: better name than 'index.jpg' for the generic profile photo

@app.template_global()
def photo_tiny(user_record):
    """
    Get the URL for a User's tiny image
    """
    return _get_photo(user_record.tiny_photo, GENERIC_PHOTO)


@app.template_global()
def photo_thumbnail(user_record):
    """
    Get the URL for a User's thumbnail image
    """
    return _get_photo(user_record.thumbnail_photo, GENERIC_PHOTO)


@app.template_global()
def photo_large(user_record):
    """
    Get the URL for a User's large image
    """
    return _get_photo(user_record.large_photo, GENERIC_PHOTO)


def _get_photo(photo_record, generic):
    if photo_record is None:
        return img(generic)
    else:
        return photo_record.url


def rescale(image, size):
    """
    Scale an image, replacing the background with alpha transparency.
    Resizing is destructive, so make a copy if you wish to preserve the
    image object. Use image.tostring() on the return value to get a
    bytestring for transmission.
    
    Use the return value, not the image passed in!
    """

    final = Image.new('RGBA', size, (255, 255, 255, 0))
    image.thumbnail(size, Image.ANTIALIAS)
    overlay_x, overlay_y = image.size
    new_x, new_y = size
    box = ((new_x - overlay_x) // 2, (new_y - overlay_y) // 2)
    final.paste(image, box)
    return final
