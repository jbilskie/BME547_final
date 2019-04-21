# test_server.py
# Authors: Janet Chen, Kevin Chu
# Last Modified: 4/20/19

from flask import Flask, jsonify, request
import numpy as np
import pytest
from pymodm import connect, MongoModel, fields
from server import *
from user import User

db = "mongodb+srv://jmb221:bme547@bme547-kcuog.mongodb.net"
database = connect(db + "/BME547?retryWrites=true")


@pytest.mark.parametrize("input, exp", [({"username": ""},
                                         {"code": 400}),
                                        ({"username": "rando"},
                                         {"code": 200}),
                                        ({"username": "1239"},
                                         {"code": 200})])
def test_process_new_user(input, exp):
    """Tests process_new_user

    Tests whether new user request is correctly processed. From
    the GUI functions, the username is captured as a string, so
    integer fields aren't tested. The original function also
    assumes the "username" key exists, because the GUI sends a
    string for username even if nothing was inputted.

    Args:
        input (dict): test input username
        exp (dict): tested status message

    Returns:
        none
    """
    if exp["code"] == 200:
        exp["msg"] = "Request was successful"
    elif exp["code"] == 400:
        exp["msg"] = "Field username cannot be empty."
    status = process_new_user(input)
    assert status == exp


@pytest.mark.parametrize("input, exp", [(("username", ""),
                                         {"code": 400}),
                                        (("filename", ""),
                                         {"code": 400}),
                                        (("username", "student"),
                                         {"code": 200}),
                                        (("filename", "a.jpg"),
                                         {"code": 200})])
def test_validate_new_input(input, exp):
    """Tests validate_new_input

    Tests whether a dictionary value is non-empty. Original
    function assumes the second argument is a string based on
    GUI input handling.

    Args:
        input (list): test inputs
        exp (dict): tested status message

    Returns:
        none
    """
    if exp["code"] == 200:
        exp["msg"] = "Request was successful"
    elif exp["code"] == 400:
        exp["msg"] = "Field {} cannot be empty.".format(input[0])
    status = validate_input(input[0], input[1])
    assert status == exp


# @pytest.mark.parametrize("img_info, add_orig, add_proc",
#                          [({"username": "user", "filename": "file"},
#                            False, False)])
# def test_upload_processed_image(img_info, add_orig, add_proc):
#     """ Test the upload_processed_image function

#     This function tests that the upload_processed_image function actually
#     uploads the image and its metadata to the database. This also involves
#     checking that the data in the database match the data within the
#     server. This is done by creating fake users and adding fake image
#     files.

#     Args:
#         img_info (dict): dictionary with image information such as
#         the username, filename, original image size, processed image size
#         original image, processed image, time stamp, processing time,
#         and processing step

#         add_orig (bool): whether we want to add extra original images
#         add_proc (bool): whether we want to add extra processed images

#     Returns:
#         none
#     """
#     from server import upload_processed_image

#     # Create user object
#     user = User(username=img_info["username"])

#     # Add image info
#     if add_orig:
#         (user.orig_img).append(img_info)

#     # Add processed image
#     if add_proc:
#         (user.proc_img).append(img_info)

#     # Save to database
#     user.save()

#     # Upload additional original and processed images
#     upload_processed_image(img_info)

#     # Retrieve user from database
#     u = User.objects.raw({"_id": img_info["username"]}).first()

#     # Delete user to reset database
#     user.delete()


@pytest.mark.parametrize("username, add_user, filename, add_orig, add_proc,"
                         "proc_step, expected",
                         # User and file don't exist
                         [("asdf", False, "file.jpg", False, False,
                           "Original", 404),

                          # User doesn't exist but file does
                          ("asdf", False, "file.jpg", True, False,
                           "Original", 404),

                          # User exists but file doesn't
                          ("asdf", True, "file.jpg", False, False,
                           "Original", 404),

                          # User and file exist
                          ("asdf", True, "file.jpg", True, False,
                           "Original", 200),

                          # Try with all processing steps
                          ("asdf", True, "file.jpg", False, True,
                           "Histogram Equalization", 200),
                          ("asdf", True, "file.jpg", False, True,
                           "Contrast Stretching", 200),
                          ("asdf", True, "file.jpg", False, True,
                           "Log Compression", 200),
                          ("asdf", True, "file.jpg", False, True,
                           "Reverse Video", 200),

                          # Check with different file types
                          ("asdf", True, "file.png", True, False,
                           "Original", 200),
                          ("asdf", True, "file.tiff", True, False,
                           "Original", 200),
                          ])
def test_exist_input(username, add_user, filename, add_orig, add_proc,
                     proc_step, expected):
    """ Test the exist_input function

    This function tests that the exist_input function correclty identifies
    whether the username and/or filename exists. This is done by optionally
    adding a user with username and filename to the database and verifying
    that they do/do not exist.

    Args:
        username (str): username
        add_user (bool): whether to add user to database
        filename (str): filename
        add_orig (bool): whether to add original image to database
        add_proc (bool): whether to add processed image to database
        proc_step (str): type of processing to apply
        expected (int): expected status code

    Returns:
        none
    """
    from server import exist_input

    # Create dictionary
    img_info = {"username": username,
                "filename": filename,
                "proc_step": proc_step}

    # Create user if indicated
    if add_user:
        # Create user object
        user = User(username=username)

        # Add image info
        if add_orig:
            (user.orig_img).append(img_info)

        # Add processed image
        if add_proc:
            (user.proc_img).append(img_info)

        # Save to database
        user.save()

    status = exist_input(username, filename, proc_step)

    assert status["code"] == expected

    # Remove user from database
    if add_user:
        user.delete()
