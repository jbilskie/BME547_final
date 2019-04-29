# test_client.py
# Authors: Jessica Bilskie
# Last Modified: 4/24/19

from user import User
import numpy as np
import pytest
from image import read_img_as_b64

good_img1 = read_img_as_b64("test_client/test1.jpg")
good_img2 = read_img_as_b64("test_client/test2.png")
good_img3 = read_img_as_b64("test_client/test3.tiff")
bad_img1 = "239fbn3rb0tbh0r2hvr0bh"
bad_img2 = ""
bad_img3 = good_img1 + "ruin"


@pytest.mark.parametrize("file_list, exp_status_code",
                         [([["1image1", good_img1,
                             [False, False, True, True, False]],
                            ["1image2", good_img2,
                             [False, True, True, True, False]],
                            ["1image3", good_img3,
                             [False, False, False, True, False]]],
                           [200, 200, 200]),
                          (['junk'], [400]),
                          ([[1, good_img1,
                             [False, False, True, True, False]],
                            ["2image2", good_img2,
                             [False, True, True, True, False]],
                            ["2image3", good_img3,
                             [False, False, False, True, False]]],
                           [400, 200, 200]),
                          ([["3image1", bad_img1,
                             [False, False, True, True, False]],
                            ["3image2", good_img2,
                             [False, True, True, True, False]],
                            ["3image3", good_img3,
                             [False, False, False, True, False]]],
                           [400, 200, 200]),
                          ([["4image1", good_img1,
                             [False, False, True, True, False]],
                            ["4image2", bad_img2,
                             [False, True, True, True, False]],
                            ["4image3", good_img3,
                             [False, False, False, True, False]]],
                           [200, 400, 200]),
                          ([["5image1", good_img1,
                             [False, False, True, True, False]],
                            ["5image2", good_img2,
                             [False, True, True, True, False]],
                            ["5image3", bad_img3,
                             [False, False, False, True, False]]],
                           [200, 200, 400]),
                          ([["6image1", good_img1,
                             [False, 1, True, True, False]],
                            ["6image2", good_img2,
                             [False, True, True, True, False]],
                            ["6image3", good_img3,
                             [False, False, False, True, False]]],
                           [400, 200, 200]),
                          ([["7image1", good_img1,
                             [False, False, True, True, True, False]],
                            ["7image2", good_img2,
                             [False, True, True, True, False]],
                            ["7image3", good_img3,
                             [False, False, False, True, False]]],
                           [400, 200, 200]),
                          ([["8image1", good_img1],
                            ["8image2", good_img2,
                             [False, True, True, True, False]],
                            ["8image3", good_img3,
                             [False, False, False, True, False]]],
                           [400, 200, 200]),
                          ([["9image1", good_img1,
                             [False, False, False, False, False]]], [400])])
def test_upload_check_file(file_list, exp_status_code):
    """Tests check_file

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
    from client import check_file

    status = {}
    status['code'] = []
    for file in file_list:
        i_status = check_file(file, "upload")
        status['code'].append(i_status['code'])

    assert status['code'] == exp_status_code


@pytest.mark.parametrize("file_list, exp_status_code",
                         [([["1image1", ".jpg",
                             [False, False, True, True, False]],
                            ["1image2", ".png",
                             [False, True, True, True, False]],
                            ["1image3", ".tiff",
                             [False, False, False, True, False]]],
                           [200, 200, 200]),
                          (['junk'], [400]),
                          ([[1, ".jpg",
                             [False, False, True, True, False]],
                            ["2image2", ".png",
                             [False, True, True, True, False]],
                            ["2image3", ".tiff",
                             [False, False, False, True, False]]],
                           [400, 200, 200]),
                          ([["3image1", 10,
                             [False, False, True, True, False]],
                            ["3image2", ".png",
                             [False, True, True, True, False]],
                            ["3image3", ".tiff",
                             [False, False, False, True, False]]],
                           [400, 200, 200]),
                          ([["4image1", ".jpg",
                             [False, False, True, True, False]],
                            ["4image2", "png",
                             [False, True, True, True, False]],
                            ["4image3", ".tiff",
                             [False, False, False, True, False]]],
                           [200, 400, 200]),
                          ([["5image1", ".jpg",
                             [False, False, True, True, False]],
                            ["5image2", ".png",
                             [False, True, True, True, False]],
                            ["5image3", ".gif",
                             [False, False, False, True, False]]],
                           [200, 200, 400]),
                          ([["6image1", ".jpg",
                             [False, 1, True, True, False]],
                            ["6image2", ".png",
                             [False, True, True, True, False]],
                            ["6image3", ".tiff",
                             [False, False, False, True, False]]],
                           [400, 200, 200]),
                          ([["7image1", ".jpg",
                             [False, False, True, True, True, False]],
                            ["7image2", ".png",
                             [False, True, True, True, False]],
                            ["7image3", ".tiff",
                             [False, False, False, True, False]]],
                           [400, 200, 200]),
                          ([["8image1", ".jpg"],
                            ["8image2", ".png",
                             [False, True, True, True, False]],
                            ["8image3", ".tiff",
                             [False, False, False, True, False]]],
                           [400, 200, 200]),
                          ([["9image1", ".jpg",
                             [False, False, False, False, False]]], [400])])
def test_download_check_file(file_list, exp_status_code):
    """Tests check_file

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
    from client import check_file

    status = {}
    status['code'] = []
    for file in file_list:
        i_status = check_file(file, "download")
        status['code'].append(i_status['code'])

    assert status['code'] == exp_status_code


# @pytest.mark.parametrize("zip_file, zip_path, exp_success",
#                          # Example of Folder with Pictures
#                          [('test_client_cp/Example1.zip',
#                            'test_client_cp/Example1/', True),
#                           # Example of Empty Folder
#                           ('test_client_cp/Example2.zip',
#                            'test_client_cp/Example2/', True),
#                           # Example of Pictures in Folder in Provided Folder
#                           ('test_client_cp/Example3.zip',
#                            'test_client_cp/', False),
#                           # Example of Existing Zip Folder
#                           ('test_client_cp/Example4.zip',
#                            'test_client_cp/Example4/', True)])
# def test_zipdir(zip_file, zip_path, exp_success):
#     """Tests zip_dir
#
#     Tests whether this function puts all the images in an existing folder
#     into a zipped folder.
#
#     Code outside of the function already makes sure the path is valid so
#     that isn't tested here.
#
#     Test includes the code that creates the zip folder.
#
#     Args:
#         zip_file (str): name of zip folder to be created
#         zip_path (str): location of where the pictures to be zipped are
#         located
#         exp_success (bool): expected success
#
#     Returns:
#         none
#     """
#     import zipfile
#     import os
#     from client import zipdir
#     import shutil
#
#     fail = False
#     cwd = os.getcwd()
#     try:
#         shutil.rmtree('test_client_cp/')
#     except:
#         pass
#     shutil.copytree('test_client/', 'test_client_cp/')
#     zipf = zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED)
#     success = zipdir(zip_path, zipf)
#     zipf.close()
#     os.chdir(cwd)
#     shutil.rmtree('test_client_cp/')
#
#     assert success == exp_success


@pytest.mark.parametrize("proc_steps, exp_str",
                         [([True, False, True, True, False], '10110'),
                          ([True, True, True, True, True], '11111'),
                          ([False, False, False, True, False], '00010'),
                          ([True, False, True, False, False], '10100'),
                          ([False, False, False, False, False], '00000')])
def test_proc_string(proc_steps, exp_str):
    """Tests proc_string

    Tests whether this function creates the correct string from an array of
    five Boolean terms.

    Code outside of the function already makes sure array is formatted
    correctly so that isn't tested here.

    Args:
        proc_steps (list): list of 5 Booleans

    Returns:
        proc_ext (str): string of 1's and 0's
    """
    from client import proc_string

    proc_ext = proc_string(proc_steps)

    assert proc_ext == exp_str
