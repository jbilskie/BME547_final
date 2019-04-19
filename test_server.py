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
        input (dict): tested username
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
