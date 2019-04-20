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


@pytest.mark.parametrize("b64_path, file_path, expected_path",
                         # Test all image formats
                         [("test_image/test1_b64.txt", "test_image/test_1.jpg",
                           "test_image/test1.jpg"),
                          ("test_image/test2_b64.txt", "test_image/test_2.jpg",
                           "test_image/test2.jpg"),
                          ("test_image/test3_b64.txt", "test_image/test_3.png",
                           "test_image/test3.png"),
                          ("test_image/test4_b64.txt",
                           "test_image/test_4.tiff",
                           "test_image/test4.tiff")
                          ])
def test_save_b64_img(b64_path, file_path, expected_path):
    """ Test the save_b64_img function

    This function ensures that the save_b64_img function correctly
    converts the base64 string into an image. The converted image is
    compared to the expected image, which is loaded from a file.

    Args:
        b64_path (str): path to txt file with expected b64 string
        file_path (str): path to image file
        expected_path (str): path to expected image file

    Returns:
        none
    """
    from image import save_b64_img
    import matplotlib.image as mpimg

    # Read base64 string from text file
    with open(b64_path, "r") as file_obj:
        b64_string = file_obj.read()

    # Strip newline
    b64_string = (b64_string.split("\n"))[0]

    # Save image
    save_b64_img(b64_string, file_path)

    # Read in saved image and expected image
    img = mpimg.imread(file_path)
    expected = mpimg.imread(expected_path)

    assert img == expected


@pytest.mark.parametrize("b64_path, expected_path",
                         [("test_image/test1_b64.txt", "test_image/test1.jpg"),
                          ("test_image/test2_b64.txt", "test_image/test2.jpg"),
                          ("test_image/test3_b64.txt", "test_image/test3.png"),
                          ("test_image/test4_b64.txt", "test_image/test4.tiff")
                          ])
def test_b64_to_image(b64_path, expected_path):
    """ Test the b64_to_image function

    This function ensures that the b64_to_image function correctly
    converts a base64 string into an image. The converted image is
    compared to the expected image, which is loaded from a file.

    Args:
        b64_path (str): path to txt file with base64 string
        expected_path (str): path to expected image file

    Returns:
        none
    """
    from image import b64_to_image
    import matplotlib.image as mpimg

    # Read base64 string from text file
    with open(b64_path, "r") as file_obj:
        b64_string = file_obj.read()

    # Convert
    img = b64_to_image(b64_string)

    # Read in expected image
    expected = mpimg.imread(expected_path)

    assert img == expected
