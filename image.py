# image.py
# Author: Kevin Chu
# Last Modified: 4/13/19

import base64
import io
# from matplotlib import pyplot as plt
import matplotlib.image as mpimg


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
