# test_server.py
# Authors: Janet Chen, Kevin Chu
# Last Modified: 4/21/19

from flask import Flask, jsonify, request
from user import User
import numpy as np
import pytest
from pymodm import connect, MongoModel, fields
from gui import get_img_data
from image import image_to_b64
from server import *
from user import User

db = "mongodb+srv://jmb221:bme547@bme547-kcuog.mongodb.net"
database = connect(db + "/BME547?retryWrites=true")


@pytest.mark.parametrize("input, times, exp",
                         [({"username": ""}, 1,
                           {"code": 400,
                            "msg": "Field username cannot be empty."
                            }),
                          ({"username": "rando"}, 1,
                           {"code": 200,
                            "msg": "Request was successful"
                            }),
                          ({"username": "1239"}, 1,
                           {"code": 200,
                            "msg": "Request was successful"
                            }),
                          ({"username": "abc"}, 2,
                           {"code": 400,
                            "msg": "User abc already exists."
                            })])
def test_process_new_user(input, times, exp):
    """Tests process_new_user

    Tests whether new user request is correctly processed. From
    the GUI functions, the username is captured as a string, so
    integer fields aren't tested. The original function also
    assumes the "username" key exists, because the GUI sends a
    string for username even if nothing was inputted.

    Args:
        input (dict): test input username
        times (int): number of times to attempt registering user
        exp (dict): tested status message

    Returns:
        none
    """
    # Delete user if it exists
    try:
        user = User.objects.raw({"_id": input["username"]}).first()
    except:
        pass
    else:
        user.delete()

    for i in range(times):
        status = process_new_user(input)
    assert status == exp


@pytest.mark.parametrize("input, exp", [("abc", True),
                                        ("USER", True),
                                        ("Holla123", True)])
def test_register_new_user(input, exp):
    """Tests register_new_user

    Check that a new user is correctly registered to the MongoDB
    database. Based on GUI code and process_new_user, the input
    is already a valid string, so we just need to test that the
    function actually adds a new user to the database.

    Args:
        input (str): inputted username
        exp (str): username found in database

    Returns:
        none
    """
    # Delete user if it does exist
    try:
        user = User.objects.raw({"_id": input}).first()
    except:
        pass
    else:
        user.delete()

    new_user = User(username=input)
    new_user.save()

    try:
        user_in_database = User.objects.raw({"_id": input}).first()
        success = True
    except:
        success = False
    assert success == exp
    new_user.delete()


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


@pytest.mark.parametrize("input, exists, exp",
                         [("new user", False,
                           {"code": 200,
                            "msg": "Request was successful"}),
                          ("existing user", True,
                           {"code": 400,
                            "msg": "User existing user already exists."
                            })])
def test_check_user_exists(input, exists, exp):
    """Tests check_user_exists function

    Tests that the check_user_exists function properly rejects attempts
    to input a user that already exists.

    Args:
        input (str): input username to save
        exists (bool): whether this user actually exists
        exp (dict): expected status message

    Returns:
        none
    """
    # If user should exist, initialize it unless it already exists
    if exists:
        try:
            user = User.objects.raw({"_id": input}).first()
        except:
            user = User(username=input)
            user.save()
    # If user should not exist, delete it if it does exist
    else:
        try:
            user = User.objects.raw({"_id": input}).first()
        except:
            pass
        else:
            user.delete()

    status = check_user_exists(input)
    assert status == exp


@pytest.mark.parametrize("img_info, exist_orig, exist_proc,"
                         "extra_orig, extra_proc",
                         # Original and processed images not already in db
                         [({"username": "user",
                            "filename": "file",
                            "image": "b64 string",
                            "proc_image": "processed",
                            "timestamp": 2019,
                            "size": [1, 1],
                            "proc_size": [1, 1],
                            "proc_time": "1s",
                            "proc_step": "Histogram Equalization"},
                           False, False, {}, {}),

                          # Original image already exists
                          ({"username": "user",
                            "filename": "file",
                            "image": "b64 string",
                            "proc_image": "processed",
                            "timestamp": 2019,
                            "size": [1, 1],
                            "proc_size": [1, 1],
                            "proc_time": "1s",
                            "proc_step": "Histogram Equalization"},
                           True, False, {}, {}),

                          # Processed image already exists
                          ({"username": "user",
                            "filename": "file",
                            "image": "b64 string",
                            "proc_image": "processed",
                            "timestamp": 2019,
                            "size": [1, 1],
                            "proc_size": [1, 1],
                            "proc_time": "1s",
                            "proc_step": "Histogram Equalization"},
                           False, True, {}, {}),

                          # Original and processed images exist
                          ({"username": "user",
                            "filename": "file",
                            "image": "b64 string",
                            "proc_image": "processed",
                            "timestamp": 2019,
                            "size": [1, 1],
                            "proc_size": [1, 1],
                            "proc_time": "1s",
                            "proc_step": "Histogram Equalization"},
                           True, True, {}, {}),

                          # Add extra original image
                          ({"username": "user",
                            "filename": "file",
                            "image": "b64 string",
                            "proc_image": "processed",
                            "timestamp": 2019,
                            "size": [1, 1],
                            "proc_size": [1, 1],
                            "proc_time": "1s",
                            "proc_step": "Histogram Equalization"},
                           False, False,
                           {"username": "user", "filename": "file2"}, {}),

                          # Add extra processed image
                          ({"username": "user",
                            "filename": "file",
                            "image": "b64 string",
                            "proc_image": "processed",
                            "timestamp": 2019,
                            "size": [1, 1],
                            "proc_size": [1, 1],
                            "proc_time": "1s",
                            "proc_step": "Histogram Equalization"},
                           False, False,
                           {},
                           {"username": "user", "filename": "file2",
                            "proc_step": "Histogram Equalization"}),

                          # Add same image but different processing
                          ({"username": "user",
                            "filename": "file",
                            "image": "b64 string",
                            "proc_image": "processed",
                            "timestamp": 2019,
                            "size": [1, 1],
                            "proc_size": [1, 1],
                            "proc_time": "1s",
                            "proc_step": "Histogram Equalization"},
                           False, False,
                           {},
                           {"username": "user", "filename": "file",
                            "proc_step": "Log Compression"}),

                          ({"username": "user",
                            "filename": "file",
                            "image": "b64 string",
                            "proc_image": "processed",
                            "timestamp": 2019,
                            "size": [1, 1],
                            "proc_size": [1, 1],
                            "proc_time": "1s",
                            "proc_step": "Histogram Equalization"},
                           False, False,
                           {},
                           {"username": "user", "filename": "file",
                            "proc_step": "Contrast Stretching"}),

                          ({"username": "user",
                            "filename": "file",
                            "image": "b64 string",
                            "proc_image": "processed",
                            "timestamp": 2019,
                            "size": [1, 1],
                            "proc_size": [1, 1],
                            "proc_time": "1s",
                            "proc_step": "Histogram Equalization"},
                           False, False,
                           {},
                           {"username": "user", "filename": "file",
                            "proc_step": "Reverse Video"}),
                          ])
def test_upload_processed_image(img_info, exist_orig, exist_proc,
                                extra_orig, extra_proc):
    """ Test the upload_processed_image function

    This function tests that the upload_processed_image function actually
    uploads the image and its metadata to the database. This also involves
    checking that the data in the database match the data within the
    server. This is done by creating fake users and adding fake image
    files.

    Args:
        img_info (dict): dictionary with image information such as
        the username, filename, original image size, processed image size
        original image, processed image, time stamp, processing time,
        and processing step

        exist_orig (bool): whether the original image already exists in db
        exist_proc (bool): whether the processed image already exists in db
        extra_orig (dict): adds extra original image if dict is non-empty
        extra_proc (dict): adds extra processed image if dict is non-empty

    Returns:
        none
    """
    from server import upload_processed_image

    # Image info for Original Image
    img_info_original = {"username": img_info["username"],
                         "filename": img_info["filename"],
                         "image": img_info["image"],
                         "timestamp": img_info["timestamp"],
                         "size": img_info["size"]}

    # Image info for Processed Image
    img_info_processed = {"username": img_info["username"],
                          "filename": img_info["filename"],
                          "image": img_info["proc_image"],
                          "timestamp": img_info["timestamp"],
                          "size": img_info["proc_size"],
                          "proc_time": img_info["proc_time"],
                          "proc_step": img_info["proc_step"]}

    # Create user object
    user = User(username=img_info["username"])

    # Add original image info
    if exist_orig:
        (user.orig_img).append(img_info_original)

    # Add processed image info
    if exist_proc:
        (user.proc_img).append(img_info_processed)

    # Add additional original image
    if extra_orig:
        (user.orig_img).append(extra_orig)

    # Add additional processed image
    if extra_proc:
        (user.proc_img).append(extra_proc)

    # Save to database
    user.save()

    # Upload additional original and processed images
    upload_processed_image(img_info)

    # Retrieve user from database
    u = User.objects.raw({"_id": img_info["username"]}).first()

    # Make sure most recent upload corresponds to current images
    assert (u.orig_img[-1] == img_info_original and
            u.proc_img[-1] == img_info_processed)

    # Delete user to reset database
    user.delete()


@pytest.mark.parametrize("input_img_info, add_user, add_orig, add_proc,"
                         "expected_status, expected_img",
                         # Empty username
                         [({"username": "",
                            "filename": "file.jpg",
                            "proc_step": "Original"},
                           False, False, False,
                           {"code": 400,
                            "msg": "Field username cannot be empty."},
                           {}),

                          # Empty filename
                          ({"username": "asdf",
                            "filename": "",
                            "proc_step": "Original"},
                           False, False, False,
                           {"code": 400,
                            "msg": "Field filename cannot be empty."},
                           {}),

                          # User and file don't exist
                          ({"username": "asdf",
                            "filename": "file.jpg",
                            "proc_step": "Original"},
                           False, False, False,
                           {"code": 404,
                            "msg": "Username not found in database."},
                           {}),

                          # User exists but file doesn't
                          ({"username": "asdf",
                            "filename": "file.jpg",
                            "proc_step": "Original"},
                           True, False, False,
                           {"code": 404,
                            "msg": "Filename/Image not found in database."},
                           {}),

                          # User doesn't exist but file does
                          ({"username": "asdf",
                            "filename": "file.jpg",
                            "proc_step": "Original"},
                           False, True, False,
                           {"code": 404,
                            "msg": "Username not found in database."},
                           {}),

                          # Add original image
                          ({"username": "asdf",
                            "filename": "file.jpg",
                            "proc_step": "Original"},
                           True, True, False,
                           {"code": 200,
                            "msg": "Request was successful"},
                           {"username": "asdf",
                            "filename": "file.jpg",
                            "proc_step": "Original"}),

                          # Try with different image formats
                          ({"username": "asdf",
                            "filename": "file.png",
                            "proc_step": "Original"},
                           True, True, False,
                           {"code": 200,
                            "msg": "Request was successful"},
                           {"username": "asdf",
                            "filename": "file.png",
                            "proc_step": "Original"}),

                          ({"username": "asdf",
                            "filename": "file.tiff",
                            "proc_step": "Original"},
                           True, True, False,
                           {"code": 200,
                            "msg": "Request was successful"},
                           {"username": "asdf",
                            "filename": "file.tiff",
                            "proc_step": "Original"}),

                          # Try with different processing steps
                          ({"username": "asdf",
                            "filename": "file.jpg",
                            "proc_step": "Histogram Equalization"},
                           True, False, True,
                           {"code": 200,
                            "msg": "Request was successful"},
                           {"username": "asdf",
                            "filename": "file.jpg",
                            "proc_step": "Histogram Equalization"}),

                          ({"username": "asdf",
                            "filename": "file.jpg",
                            "proc_step": "Contrast Stretching"},
                           True, False, True,
                           {"code": 200,
                            "msg": "Request was successful"},
                           {"username": "asdf",
                            "filename": "file.jpg",
                            "proc_step": "Contrast Stretching"}),

                          ({"username": "asdf",
                            "filename": "file.jpg",
                            "proc_step": "Log Compression"},
                           True, False, True,
                           {"code": 200,
                            "msg": "Request was successful"},
                           {"username": "asdf",
                            "filename": "file.jpg",
                            "proc_step": "Log Compression"}),

                          ({"username": "asdf",
                            "filename": "file.jpg",
                            "proc_step": "Reverse Video"},
                           True, False, True,
                           {"code": 200,
                            "msg": "Request was successful"},
                           {"username": "asdf",
                            "filename": "file.jpg",
                            "proc_step": "Reverse Video"}),
                          ])
def test_process_image_download(input_img_info, add_user, add_orig, add_proc,
                                expected_status, expected_img):
    """ Test the process_image_download function

    Args:
        input_img_info (dict): metadata of image to download
        add_user (bool): whether to add user to database
        add_orig (bool): whether to add original image to database
        add_proc (bool): whether to add processed image to database
        expected_status (dict): dictionary with expected status code and
        status message
        expected_img (dict): metadata of expected download

    Returns:
        none
    """
    from server import process_image_download

    # Create user if indicated
    if add_user:
        # Create user object
        user = User(username=input_img_info["username"])

        # Add image info
        if add_orig:
            (user.orig_img).append(input_img_info)

        # Add processed image
        if add_proc:
            (user.proc_img).append(input_img_info)

        # Save to database
        user.save()

    status, img_info = process_image_download(input_img_info)

    assert (status == expected_status and
            img_info == expected_img)

    # Remove user from database
    if add_user:
        user.delete()


@pytest.mark.parametrize("input, img_exists, exp",
                         [({"username": "lalala",
                            "filename": ""}, False,
                           {"code": 400,
                            "msg": "Field filename cannot be empty."
                            }),
                          ({"username": "",
                            "filename": "test_image/orion.jpg"},
                           True,
                           {"code": 400,
                            "msg": "Field username cannot be empty."
                            }),
                          ({"username": "whooptidoo",
                            "filename": "blah.jpg"}, False,
                           {"code": 400,
                            "msg": "Field image cannot be empty."
                            }),
                          ({"username": "jonsnow",
                            "filename": "test_image/blank.png"},
                           True,
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
        input (dict): dictionary containing username and filename
        img_exists (bool): whether image exists
        exp (dict): expected status dictionary
    Returns:
        none
    """
    # Initialize user if it does not exist
    try:
        user = User.objects.raw({"_id": input}).first()
    except:
        if input["username"] != "":
            user = User(username=input["username"])
            user.save()

    if img_exists:
        # get_img_data takes in a list
        image, _, _ = get_img_data([input["filename"]])
        input["image"] = image[0]
    else:
        input["image"] = ""
    output = process_image_upload(input)
    assert output == exp


@pytest.mark.parametrize("input, exp", [("test_image/orion.jpg",
                                         (1600, 1200)),
                                        ("test_image/sky.jpg",
                                         (930, 620)),
                                        ("test_image/test_1.jpg",
                                         (1, 1)),
                                        ("test_image/test_3.png",
                                         (1, 1)),
                                        ("test_image/test_4.tiff",
                                         (1, 1))])
def test_get_img_size(input, exp):
    """Tests get_img_size function

    Tests whether image size is correctly calculated from its base64
    representation. Assumes the function input is in the proper format.

    Args:
        input (string): input filename
        exp (tuple): expected image dimensions

    Returns:
        none
    """
    image_string, _, _ = get_img_data([input])
    out = get_img_size(image_string[0])
    assert out == exp


@pytest.mark.parametrize("inputs, exp",
                         [({"username": "danyt",
                            "filename": "test_image/orion.jpg"},
                           True),
                          ({"username": "tyrionl",
                            "filename": "test_image/blank.png"},
                           True)])
def test_upload_image(inputs, exp):
    """Tests upload_image function

    Checks whether images are properly uploaded. Assumes request is valid,
    because status is checked by function process_image_upload prior to call.

    Args:
        input (string): input filename
        exp ():

    Returns:
        none
    """


@pytest.mark.parametrize("username, add_user, filename, add_orig, add_proc,"
                         "proc_step, expected",
                         # User and file don't exist
                         [("asdf", False, "file.jpg", False, False,
                           "Original",
                           {"code": 404,
                            "msg": "Username not found in database."}),

                          # User doesn't exist but file does
                          ("asdf", False, "file.jpg", True, False,
                           "Original",
                           {"code": 404,
                            "msg": "Username not found in database."}),

                          # User exists but file doesn't
                          ("asdf", True, "file.jpg", False, False,
                           "Original",
                           {"code": 404,
                            "msg": "Filename/Image not found in database."}),

                          # User and file exist
                          ("asdf", True, "file.jpg", True, False,
                           "Original",
                           {"code": 200,
                            "msg": "Request was successful"}),

                          # Try with all processing steps
                          ("asdf", True, "file.jpg", False, True,
                           "Histogram Equalization",
                           {"code": 200,
                            "msg": "Request was successful"}),

                          ("asdf", True, "file.jpg", False, True,
                           "Contrast Stretching",
                           {"code": 200,
                            "msg": "Request was successful"}),

                          ("asdf", True, "file.jpg", False, True,
                           "Log Compression",
                           {"code": 200,
                            "msg": "Request was successful"}),

                          ("asdf", True, "file.jpg", False, True,
                           "Reverse Video",
                           {"code": 200,
                            "msg": "Request was successful"}),

                          # Check with different file types
                          ("asdf", True, "file.png", True, False,
                           "Original",
                           {"code": 200,
                            "msg": "Request was successful"}),

                          ("asdf", True, "file.tiff", True, False,
                           "Original",
                           {"code": 200,
                            "msg": "Request was successful"}),
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
        expected (dict): dictionary with expected status code and message

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

    assert (status["code"] == expected["code"] and
            status["msg"] == expected["msg"])

    # Remove user from database
    if add_user:
        user.delete()
