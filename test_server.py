from flask import Flask, jsonify, request
import numpy as np
import pytest
from pymodm import connect, MongoModel, fields
from gui import get_img_data
from image import image_to_b64
from server import *


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
