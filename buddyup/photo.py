# Photo support functions
# Includes resizing and Amazon S3 functionality

from collections import namedtuple
from io import BytesIO

from PIL import Image, ImageOps, ExifTags
import boto
from boto.s3.key import Key

from buddyup.app import app
from buddyup.templating import img

Dimensions = namedtuple('Dimensions', 'x y')


THUMB_SIZE = Dimensions(50, 50)
LARGE_SIZE = Dimensions(200, 200)

SIZES = [THUMB_SIZE, LARGE_SIZE]
GENERIC_PHOTO = 'default-profile-{0.x}x{0.y}.png'


# def to_image_name(user, x, y):
#     return "{}-{}-{}.png".format(user.user_name, x, y)
to_image_name = "{.user_name}-{}-{}.png".format


class ImageError(Exception):
    pass


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
    Scale an image, cropping centered to a specified size.
    Use tobytes() on the return value to get a bytestring for transmission.
    """
    resized = ImageOps.fit(image, size, method=Image.ANTIALIAS, centering=(0.5, 0.5))
    return resized


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

        try:
            for orientation in ExifTags.TAGS.keys() : 
                if ExifTags.TAGS[orientation]=='Orientation' : break 
            exif=dict(base_image._getexif().items())
            
            if orientation in exif:
                if   exif[orientation] == 3 : 
                    base_image=base_image.rotate(180, expand=True)
                elif exif[orientation] == 6 : 
                    base_image=base_image.rotate(270, expand=True)
                elif exif[orientation] == 8 : 
                    base_image=base_image.rotate(90, expand=True)
        except AttributeError, KeyError:
            pass

        images = [scale(base_image, size) for size in SIZES]
        # Upload the original.
        images.append(base_image)
    except IndexError:
        raise ImageError("Incorrectly formatted image")
    upload(user, images)
    user.has_photos = True


def upload(user, images):
    conn = boto.connect_s3()
    try:
        bucket = conn.create_bucket(app.config['AWS_S3_BUCKET'])
    except:
        bucket = conn.get_bucket(app.config['AWS_S3_BUCKET'])
        pass
    try:
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