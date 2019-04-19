# image.py
# Author: Kevin Chu
# Last Modified: 4/16/19

import base64
import io
from matplotlib import pyplot as plt
import matplotlib.image as mpimg
import numpy as np
from PIL import Image


def read_img_as_b64(file_path):
    """ Reads in image as b64

    This function reads in an image and encodes it into
    a base64 string so that it can be transmitted over
    the internet.

    Args:
        file_path (str): file directory and name

    Returns:
        b64_string (str): image represented as a string
    """
    with open(file_path, "rb") as img_file:
        b64_bytes = base64.b64encode(img_file.read())
    b64_string = str(b64_bytes, encoding='utf-8')
    return b64_string


def save_b64_img(b64_string, file_path):
    """ Saves image file

    This function reads in a base64 string and decodes so that
    it can be saved.

    Args:
        b64_string (str): image represented as a string
        file_path (str): path of save file
    """
    img_bytes = base64.b64decode(b64_string)
    with open(file_path, "wb") as out_file:
        out_file.write(img_bytes)

    return


def b64_to_image(b64_string):
    """ Convert b64 string to image

    This function takes a b64 string and decodes it into
    a color image. The image is represented as a 3-dimensional
    np.array where each element represents the pixel intensity
    ranging from 0-255. The three dimensions represent red,
    blue, and green channels.

    Args:
        b64_string (str): image represented as a string

    Returns:
        img (np.array): image represented as RBG intensities
    """
    img_bytes = base64.b64decode(b64_string)
    img_buf = io.BytesIO(img_bytes)
    img = mpimg.imread(img_buf, format='PNG')
    # rgb_im =  Image.convert("RGB")
    # img = rgb_im.save("downloaded_image"+type_extension, quality=95)
    return img


def image_to_b64(img):
    """ Convert np.array image to b64 string

    This function uses the skimage.io.imsave function to convert
    an np.array image into a b64 string. The image is saved in
    a BytesIO buffer, which is then encoded in base 64 and then
    converted into a string.

    Args:
        img (np.array): image represented as np.array

    Returns:
        b64_string (string): image represented as base64 string
    """
    from skimage.io import imsave

    f = io.BytesIO()
    imsave(f, img, plugin='pil')
    y = base64.b64encode(f.getvalue())
    b64_string = str(y, encoding='utf-8')

    return b64_string
