from flask import Flask, jsonify, request
import numpy as np
import pytest
from pymodm import connect, MongoModel, fields
from gui import get_img_data
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


@pytest.mark.parametrize("input, exp",
                         [({"username": "abc",
                            "filename": "",
                            "image": get_img_data("orion.jpg")},
                           {"code": 400,
                            "msg": "Field filename cannot be empty."
                            })])
def test_process_image_upload(input, exp):
    """Tests process_image_upload

    Tests whether request to upload images to the database is
    correctly processed. All input data have been previously
    verified as strings

    Args:
        input ():
        exp ():
    Returns:
        none
    """
    output = process_image_upload(input)
    assert output == exp
