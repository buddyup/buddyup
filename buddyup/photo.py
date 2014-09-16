# Photo support functions
# Includes resizing and Amazon S3 functionality

from collections import namedtuple
from io import BytesIO

from PIL import Image
import boto
from boto.s3.key import Key

from buddyup.app import app
from buddyup.templating import img

Dimensions = namedtuple('Dimensions', 'x y')

TINY_SIZE = Dimensions(20, 20)
THUMB_SIZE = Dimensions(50, 50)
LARGE_SIZE = Dimensions(200, 200)

SIZES = [TINY_SIZE, THUMB_SIZE, LARGE_SIZE]
GENERIC_PHOTO = 'default-profile-{0.x}x{0.y}.png'


# def to_image_name(user, x, y):
#     return "{}-{}-{}.png".format(user.user_name, x, y)
to_image_name = "{.user_name}-{}-{}.png".format


class ImageError(Exception):
    pass



@app.template_global()
def photo_tiny(user_record):
    """
    Get the URL for a User's tiny image
    """
    return get_photo_url(user_record, TINY_SIZE)


@app.template_global()
def photo_thumbnail(user_record):
    """
    Get the URL for a User's thumbnail image
    """
    return get_photo_url(user_record, THUMB_SIZE)


@app.template_global()
def photo_large(user_record):
    """
    Get the URL for a User's large image
    """
    return get_photo_url(user_record, LARGE_SIZE)


def get_photo_url(user_record, size, bucket=None):
    """
    Get a photo size's URL based on the given Dimensions
    """
    if user_record.has_photos and ('AWS_S3_BUCKET' in app.config):
        if bucket is None:
            bucket = app.config['AWS_S3_BUCKET']
        return "http://{bucket}.s3.amazonaws.com/{key}".format(
            bucket=bucket,
            key=to_image_name(user_record, size.x, size.y))
    else:
        return img(GENERIC_PHOTO.format(size))


def scale(image, size):
    """
    Scale an image, replacing the background with alpha transparency.
    Use tobytes() on the return value to get a bytestring for transmission.
    """

    final = Image.new('RGBA', size, (255, 255, 255, 0))
    resized = image.copy()
    resized.thumbnail(size, Image.ANTIALIAS)
    overlay_x, overlay_y = resized.size
    new_x, new_y = size
    box = ((new_x - overlay_x) // 2, (new_y - overlay_y) // 2)
    final.paste(resized, box)
    return final


def change_profile_photo(user, storage):
    """
    user: User record. The record is modified but not committed.
    stream: File or file-like object
    """
    
    # request.file doesn't have tell() so we have to wrap it in BytesIO
    # instead of stream.
    stream = getattr(storage, "stream", storage)
    try:
        if hasattr(stream, "tell") and hasattr(stream, "seek"):
            base_image = Image.open(stream)
        else:
            base_image = Image.open(BytesIO(stream.read()))
        images = [scale(base_image, size) for size in SIZES]
    except IndexError:
        raise ImageError("Incorrectly formatted image")
    upload(user, images)
    user.has_photos = True


def upload(user, images):
    conn = boto.connect_s3()
    try:
        bucket = conn.create_bucket(app.config['AWS_S3_BUCKET'])
        for image in images:
            upload_one(bucket, image, user)
    finally:
        conn.close()


def upload_one(bucket, image, user):
    x, y = image.size
    name = to_image_name(user, x, y)
    app.logger.info("Uploading to %s for user %s", name, user.user_name)
    k = Key(bucket, name)
    k.content_type = "image/png"
    pseudofile = BytesIO()
    image.save(pseudofile, format="png")
    k.set_contents_from_string(pseudofile.getvalue())
    k.set_acl("public-read")


def clear_images(user):
    """
    Remove all images for the given user. Changes to the record are not
    committed!
    """
    conn = boto.connect_s3()
    try:
        bucket = conn.create_bucket(app.config['AWS_S3_BUCKET'])
        image_names = [to_image_name(user, size.x, size.y)
                       for size in SIZES]
        bucket.delete_keys(image_names)
        user.has_photos = False
    finally:
        conn.close()