# test_image.py
# Author: Kevin Chu
# Last Modified: 4/20/19

import pytest


@pytest.mark.parametrize("file_path, b64_path",
                         # Test all image formats
                         [("test_image/test1.jpg", "test_image/test1_b64.txt"),
                          ("test_image/test2.jpg", "test_image/test2_b64.txt"),
                          ("test_image/test3.png", "test_image/test3_b64.txt"),
                          ("test_image/test4.tiff", "test_image/test4_b64.txt")
                          ])
def test_read_img_as_b64(file_path, b64_path):
    """ The the read_img_as_b64 function

    This function ensures that the read_img_as_b64 function converts
    the image into the correct string. The converted string is compared
    to the expected string, which is loaded from a text file.

    Args:
        file_path (str): path to image file
        b64_path (str): path to txt file with expected b64 string

    Returns:
        none
    """
    from image import read_img_as_b64

    # Read expected string from text file
    with open(b64_path, "r") as file_obj:
        expected = file_obj.read()

    # Strip newline
    expected = (expected.split("\n"))[0]

    b64_string = read_img_as_b64(file_path)

    assert b64_string == expected
