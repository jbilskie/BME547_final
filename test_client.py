# test_client.py
# Authors: Jessica Bilskie
# Last Modified: 4/24/19

from user import User
import numpy as np
import pytest
from client import *
from image import read_img_as_b64

good_img1 = read_img_as_b64("test_client_images/test1.jpg")
good_img2 = read_img_as_b64("test_client_images/test2.png")
good_img3 = read_img_as_b64("test_client_images/test3.tiff")
bad_img1 = "239fbn3rb0tbh0r2hvr0bh"
bad_img2 = ""
bad_img3 = good_img1 + "ruin"


@pytest.mark.parametrize("file_list, exp_status_code",
                         [([["1image1", good_img1, [0, 0, 1, 1, 0]],
                            ["1image2", good_img2, [0, 1, 1, 1, 0]],
                            ["1image3", good_img3, [0, 0, 0, 1, 0]]], 200),
                          ([], 400),
                          ([[1, good_img1, [0, 0, 1, 1, 0]],
                            ["2image2", good_img2, [0, 1, 1, 1, 0]],
                            ["2image3", good_img3, [0, 0, 0, 1, 0]]], 400),
                          ([["3image1", bad_img1, [0, 0, 1, 1, 0]],
                            ["3image2", good_img2, [0, 1, 1, 1, 0]],
                            ["3image3", good_img3, [0, 0, 0, 1, 0]]], 400),
                          ([["4image1", good_img1, [0, 0, 1, 1, 0]],
                            ["4image2", bad_img2, [0, 1, 1, 1, 0]],
                            ["4image3", good_img3, [0, 0, 0, 1, 0]]], 400),
                          ([["5image1", good_img1, [0, 0, 1, 1, 0]],
                            ["5image2", good_img2, [0, 1, 1, 1, 0]],
                            ["5image3", bad_img3, [0, 0, 0, 1, 0]]], 400),
                          ([["6image1", good_img1, [0, 2, 1, 1, 0]],
                            ["6image2", good_img2, [0, 1, 1, 1, 0]],
                            ["6image3", bad_img3, [0, 0, 0, 1, 0]]], 400),
                          ([["7image1", good_img1, [0, 0, 1, 1, 1, 0]],
                            ["7image2", good_img2, [0, 1, 1, 1, 0]],
                            ["7image3", bad_img3, [0, 0, 0, 1, 0]]], 400),
                          ([["8image1", good_img1],
                            ["8image2", good_img2, [0, 1, 1, 1, 0]],
                            ["8image3", bad_img3, [0, 0, 0, 1, 0]]], 400),
                          ([["9image1", good_img1, [0, 0, 0, 0, 0]]], 400)])
def test_upload_check_file_list(file_list, exp_status_code):
    """Tests check_file_list

    Tests whether a filelist contains the correct type and amount
    of elements for uploading multiple images.

    Args:
        file_list (list): UPLOAD list of files where each item in the list
        is a list of the file's filename, b64 image, and an array of
        what processing steps should be done
            Example: file_list = [file1, file2]
                    file1 = ["image1", b64_image1, [0, 0, 1, 1, 0]]
                    file2 = ["image1", b64_image1, [1, 1, 0, 0, 1]]
            Each processing steps array has a 1 if that process is
            desired and 0 if not. In this example, image1 desires to
            perform contrast stretching and log compression. Likewise,
            image2 desires the original and to perform histogram
            equalization and reverse video.
        exp_status_code (int): status code either 200 or 400

    Returns:
        none
    """
    status = check_file_list(file_list, "upload")
    assert status['code'] == exp_status_code
