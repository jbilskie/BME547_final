from flask import Flask, jsonify, request
import numpy as np
import pytest
from pymodm import connect, MongoModel, fields
from server import *


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
