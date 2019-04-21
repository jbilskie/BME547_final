# test_server.py
# Authors: Janet Chen, Kevin Chu
# Last Modified: 4/20/19

from flask import Flask, jsonify, request
import numpy as np
import pytest
from pymodm import connect, MongoModel, fields
from gui import get_img_data
from image import image_to_b64
from server import *
from user import User

db = "mongodb+srv://jmb221:bme547@bme547-kcuog.mongodb.net"
database = connect(db + "/BME547?retryWrites=true")


@pytest.mark.parametrize("input, exp",
                         [({"username": ""},
                           {"code": 400,
                            "msg": "Field username cannot be empty."
                            }),
                          ({"username": "rando"},
                           {"code": 200,
                            "msg": "Request was successful"
                            }),
                          ({"username": "1239"},
                           {"code": 200,
                            "msg": "Request was successful"
                            })])
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
    status = process_new_user(input)
    assert status == exp

"""
@pytest.mark.parametrize("input, exp", [])
def test_register_new_user(input, exp):
    pass
"""


@pytest.mark.parametrize("input, exp",
                         [(("username", ""),
                           {"code": 400,
                            "msg": "Field username cannot be empty."
                            }),
                          (("filename", ""),
                           {"code": 400,
                            "msg": "Field filename cannot be empty."
                            }),
                          (("username", "student"),
                           {"code": 200,
                            "msg": "Request was successful"
                            }),
                          (("filename", "a.jpg"),
                           {"code": 200,
                            "msg": "Request was successful"
                            })])
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
    status = validate_input(input[0], input[1])
    assert status == exp


@pytest.mark.parametrize("input, img_exists, exp",
                         [({"username": "user1",
                            "filename": ""}, False,
                           {"code": 400,
                            "msg": "Field filename cannot be empty."
                            }),
                          ({"username": "",
                            "filename": "orion.jpg"}, True,
                           {"code": 400,
                            "msg": "Field username cannot be empty."
                            }),
                          ({"username": "user1",
                            "filename": "blah.jpg"}, False,
                           {"code": 400,
                            "msg": "Field image cannot be empty."
                            }),
                          ({"username": "user1",
                            "filename": "orion.jpg"}, True,
                           {"code": 200,
                            "msg": "Request was successful"})])
def test_process_image_upload(input, img_exists, exp):
    """Tests process_image_upload

    Tests whether request to upload images to the database is
    correctly processed. All input data have been previously
    verified as strings. If a filename doesn't correspond to an
    image, the image field will be an empty string.
    Note: the final test takes a while to run because it posts
    an image to the database.

    Args:
        input ():
        img_exists (bool): whether image exists
        exp ():
    Returns:
        none
    """
    if img_exists:
        # get_img_data takes in a list
        image, _ = get_img_data([input["filename"]])
        input["image"] = image_to_b64(image[0])
    else:
        input["image"] = ""
    output = process_image_upload(input)
    assert output == exp


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
