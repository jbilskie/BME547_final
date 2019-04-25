# test_client.py
# Authors: Jessica Bilskie
# Last Modified: 4/24/19

from user import User
import numpy as np
import pytest
from image import read_img_as_b64

good_img1 = read_img_as_b64("test_client_images/test1.jpg")
good_img2 = read_img_as_b64("test_client_images/test2.png")
good_img3 = read_img_as_b64("test_client_images/test3.tiff")
bad_img1 = "239fbn3rb0tbh0r2hvr0bh"
bad_img2 = ""
bad_img3 = good_img1 + "ruin"


@pytest.mark.parametrize("file_list, exp_status_code",
                         [([["1image1", good_img1,
                             [False, False, True, True, False]],
                            ["1image2", good_img2,
                             [False, True, True, True, False]],
                            ["1image3", good_img3,
                             [False, False, False, True, False]]], 200),
                          ([], 400),
                          ([[1, good_img1,
                             [False, False, True, True, False]],
                            ["2image2", good_img2,
                             [False, True, True, True, False]],
                            ["2image3", good_img3,
                             [False, False, False, True, False]]], 400),
                          ([["3image1", bad_img1,
                             [False, False, True, True, False]],
                            ["3image2", good_img2,
                             [False, True, True, True, False]],
                            ["3image3", good_img3,
                             [False, False, False, True, False]]], 400),
                          ([["4image1", good_img1,
                             [False, False, True, True, False]],
                            ["4image2", bad_img2,
                             [False, True, True, True, False]],
                            ["4image3", good_img3,
                             [False, False, False, True, False]]], 400),
                          ([["5image1", good_img1,
                             [False, False, True, True, False]],
                            ["5image2", good_img2,
                             [False, True, True, True, False]],
                            ["5image3", bad_img3,
                             [False, False, False, True, False]]], 400),
                          ([["6image1", good_img1,
                             [False, 1, True, True, False]],
                            ["6image2", good_img2,
                             [False, True, True, True, False]],
                            ["6image3", good_img3,
                             [False, False, False, True, False]]], 400),
                          ([["7image1", good_img1,
                             [False, False, True, True, True, False]],
                            ["7image2", good_img2,
                             [False, True, True, True, False]],
                            ["7image3", good_img3,
                             [False, False, False, True, False]]], 400),
                          ([["8image1", good_img1],
                            ["8image2", good_img2,
                             [False, True, True, True, False]],
                            ["8image3", good_img3,
                             [False, False, False, True, False]]], 400),
                          ([["9image1", good_img1,
                             [False, False, False, False, False]]], 400)])
def test_upload_check_file_list(file_list, exp_status_code):
    """Tests check_file_list

    Tests whether a filelist contains the correct type and amount
    of elements for uploading multiple images.

    Args:
        file_list (list): UPLOAD list of files where each item in the list
        is a list of the file's filename, b64 image, and an array of
        what processing steps should be done
            Example: file_list = [file1, file2]
                    file1 = ["image1", b64_image1,
                             [False, False, True, True, False]]
                    file2 = ["image1", b64_image1,
                             [True, True, False, False, True]]
            Each processing steps array has a True if that process is
            desired and False if not. In this example, image1 desires to
            perform contrast stretching and log compression. Likewise,
            image2 desires the original and to perform histogram
            equalization and reverse video.
        exp_status_code (int): status code either 200 or 400

    Returns:
        none
    """
    from client import check_file_list

    status = check_file_list(file_list, "upload")
    assert status['code'] == exp_status_code


@pytest.mark.parametrize("file_list, exp_status_code",
                         [([["1image1", ".jpg",
                             [False, False, True, True, False]],
                            ["1image2", ".png",
                             [False, True, True, True, False]],
                            ["1image3", ".tiff",
                             [False, False, False, True, False]]], 200),
                          ([], 400),
                          ([[1, ".jpg",
                             [False, False, True, True, False]],
                            ["2image2", ".png",
                             [False, True, True, True, False]],
                            ["2image3", ".tiff",
                             [False, False, False, True, False]]], 400),
                          ([["3image1", 10,
                             [False, False, True, True, False]],
                            ["3image2", ".png",
                             [False, True, True, True, False]],
                            ["3image3", ".tiff",
                             [False, False, False, True, False]]], 400),
                          ([["4image1", ".jpg",
                             [False, False, True, True, False]],
                            ["4image2", "png",
                             [False, True, True, True, False]],
                            ["4image3", ".tiff",
                             [False, False, False, True, False]]], 400),
                          ([["5image1", ".jpg",
                             [False, False, True, True, False]],
                            ["5image2", ".png",
                             [False, True, True, True, False]],
                            ["5image3", ".gif",
                             [False, False, False, True, False]]], 400),
                          ([["6image1", ".jpg",
                             [False, 1, True, True, False]],
                            ["6image2", ".png",
                             [False, True, True, True, False]],
                            ["6image3", ".tiff",
                             [False, False, False, True, False]]], 400),
                          ([["7image1", ".jpg",
                             [False, False, True, True, True, False]],
                            ["7image2", ".png",
                             [False, True, True, True, False]],
                            ["7image3", ".tiff",
                             [False, False, False, True, False]]], 400),
                          ([["8image1", ".jpg"],
                            ["8image2", ".png",
                             [False, True, True, True, False]],
                            ["8image3", ".tiff",
                             [False, False, False, True, False]]], 400),
                          ([["9image1", ".jpg",
                             [False, False, False, False, False]]], 400)])
def test_download_check_file_list(file_list, exp_status_code):
    """Tests check_file_list

    Tests whether a filelist contains the correct type and amount
    of elements for downloading multiple images.

    Args:
        file_list (list): DOWNLOAD list of files where each item in the
        list is a list of the file's filename, image download type, and
        an array of what processing steps should be downloaded
            Example: file_list = [file1, file2]
                    file1 = ["image1", ".jpg",
                             [False, False, True, True, False]]
                    file2 = ["image1", ".tiff",
                             [True, True, False, False, True]]
            Each processing steps array has a 1 if that process is
            desired and 0 if not. In this example, image1 desires to
            perform contrast stretching and log compression. Likewise,
            image2 desires the original and to perform histogram
            equalization and reverse video.
        exp_status_code (int): status code either 200 or 400

    Returns:
        none
    """
    from client import check_file_list

    status = check_file_list(file_list, "download")
    print(status['msg'])
    assert status['code'] == exp_status_code
