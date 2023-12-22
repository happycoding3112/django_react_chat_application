import os

from django.core.exceptions import ValidationError

from PIL import Image


def validate_icon_image_size(image):
    if image:
        with Image.open(image) as img:
            if img.width > 70 or img.height > 70:
                raise ValidationError(
                    "The maximum allowed dimensions for the image are 70 X 70 - size of the image you uploaded: {image_size}".format(
                        image_size=img.size
                    )
                )


def validate_image_file_extension(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = [".jpeg", ".jpg", ".png", ".jpg", ".gif"]

    if not ext.lower() in valid_extensions:
        raise ValidationError(
            "The {extension} extension is not supported!".format(extension=ext)
        )
