# test_server.py
# Authors: Janet Chen, Kevin Chu
# Last Modified: 4/25/19

from flask import Flask, jsonify, request
from user import User
import numpy as np
import pytest
from pymodm import connect, MongoModel, fields
from gui import get_img_data
from image import image_to_b64, read_img_as_b64
from client import delete_user, add_new_user
from server import *
from datetime import datetime as dt
app = Flask(__name__)

db = "mongodb+srv://jmb221:bme547@bme547-kcuog.mongodb.net"
connect(db + "/BME547?retryWrites=true")


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
        # delete_user(input["username"])

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
        # delete_user(input)

    new_user = User(username=input)
    new_user.save()
    # add_new_user(input)

    try:
        user_in_database = User.objects.raw({"_id": input}).first()
        success = True
        user_in_database.delete()
        # delete_user(input)
    except:
        success = False
    assert success == exp


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
            # add_new_user(input)
    # If user should not exist, delete it if it does exist
    else:
        try:
            user = User.objects.raw({"_id": input}).first()
        except:
            pass
        else:
            user.delete()
            # delete_user(input)

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
            # add_new_user(input["username"])

    if img_exists:
        # get_img_data takes in a list
        image, _, _ = get_img_data([input["filename"]])
        input["image"] = image[0]
    else:
        input["image"] = ""
    output = process_image_upload(input)
    assert output == exp


@pytest.mark.parametrize("username, add_user, expected_status",
                         [("asdf", False,
                           {"code": 404,
                            "msg": "Username not found in database."}),
                          ("asdf", True,
                           {"code": 200,
                            "msg": "Request was successful"})])
def test_validate_user(username, add_user, expected_status):
    """ Test the validate_user function

    This function tests that validate_user correctly identifies whether
    a user exists in the database.

    Args:
        username (str): username
        add_user (bool): whether to add user to database
        expected_status (dict): expected status code and message

    Returns:
        none
    """
    from server import validate_user

    if add_user:
        user = User(username=username)
        user.save()

    user, status = validate_user(username)

    assert status == expected_status

    if add_user:
        user.delete()


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


@pytest.mark.parametrize("img_info, first_image, exp_i, exp_i2, exp_a",
                         [({"username": "danyt",
                            "filename": "orion.jpg",
                            "image":
                            read_img_as_b64("test_image/orion.jpg")},
                           True, 2, 2, "Uploaded Image"),
                          ({"username": "danyt",
                            "filename": "orion.jpg",
                            "image":
                            read_img_as_b64("test_image/orion.jpg")},
                           False, 1, 3, "Updated Image"),
                          ({"username": "tyrionl",
                            "filename": "blank.png",
                            "image":
                            read_img_as_b64("test_image/blank.png")},
                           True, 2, 2, "Uploaded Image")])
def test_upload_image(img_info, first_image, exp_i, exp_i2, exp_a):
    """Tests upload_image function

    Checks whether images are properly uploaded. Assumes request is valid,
    because status is checked by function process_image_upload prior to call.
    Also checks that, if an image is uploaded by a user with a filename
    they previously used, the function updates (overwrites) that image.

    Args:
        img_info (dict): dictionary containing image information (username,
        filename, image, size, timestamp, b64 string)
        first_image (bool): whether this is the first image with this
        filename uploaded by the user
        exp_i (int): expected index of the image that has been uploaded
        exp_i2 (int): expected index of the action string
        exp_a (str): expected string added to user.actions

    Returns:
        none
    """
    time_1 = str(dt.now())
    time_2 = str(dt.now())
    time_3 = str(dt.now())
    time_4 = str(dt.now())
    # Delete user if it already exists
    try:
        existing_user = User.objects.raw({"_id": img_info["username"]}).first()
    except:
        pass
    else:
        existing_user.delete()
        # delete_user(img_info["username"])
    # Create user
    user = User(username=img_info["username"])
    user.save()
    # add_new_user(img_info["username"])

    # Other images
    img2_path = "test_image/sky.jpg"
    img2_info = {"username": img_info["username"],
                 "filename": "sky.jpg",
                 "image": read_img_as_b64(img2_path),
                 "timestamp": time_1}
    img2_info["size"] = get_img_size(img2_info["image"])
    img3_path = "test_image/test_4.tiff"
    img3_info = {"username": img_info["username"],
                 "filename": "test_4.tiff",
                 "image": read_img_as_b64(img3_path),
                 "timestamp": time_3}
    img3_info["size"] = get_img_size(img3_info["image"])

    # Upload image 2
    upload_image(img2_info)

    img_info["size"] = list(get_img_size(img_info["image"]))
    if not first_image:
        # First time this image was uploaded for test case 2
        img_info["timestamp"] = time_2
        upload_image(img_info)

    # Helps test that the correct index is replaced
    upload_image(img3_info)
    # Upload image. If "first_image" is false, this is the second time
    # the same image is uploaded. If it's true, this is the first time.
    # If false, expect this image to replace the previous image of the
    # same filename at the same location.
    img_info["timestamp"] = time_4
    upload_image(img_info)

    # Collect user information
    user = User.objects.raw({"_id": img_info["username"]}).first()
    print(user.actions)

    # Check that image information and action for user are as expected
    # at the specific index
    assert (user.orig_img[exp_i] == img_info and
            user.actions[exp_i2] == exp_a)


@pytest.mark.parametrize("img_info, expected_status, add_user",
                         # Username is empty
                         [({"username": "",
                            "filename": "file.jpg",
                            "image": "invalid"},
                           {"code": 400,
                            "msg": "Field username cannot be empty."},
                           False),

                          # Filename is empty
                          ({"username": "user",
                            "filename": "",
                            "image": "invalid"},
                           {"code": 400,
                            "msg": "Field filename cannot be empty."},
                           False),

                          # Image is empty
                          ({"username": "user",
                            "filename": "file.jpg",
                            "image": ""},
                           {"code": 400,
                            "msg": "Field image cannot be empty."},
                           False),

                          # User doesn't exist
                          ({"username": "user",
                            "filename": "file.jpg",
                            "image": "image"},
                           {"code": 404,
                            "msg": "Username not found in database."},
                           False),

                          # Invalid processing step
                          ({"username": "user",
                            "filename": "file.jpg",
                            "proc_step": "invalid",
                            "image": """iVBORw0KGgoAAAANSUhEUgAAAAEAA"""
                            """AABCAAAAAA6fptVAAAACklEQVR4nGNgA"""
                            """AAAAgABSK+kcQAAAABJRU5ErkJggg=="""},
                           {"code": 404,
                            "msg": "Processing method not defined"},
                           True),

                          # Try with all processing steps
                          ({"username": "user",
                            "filename": "file.jpg",
                            "proc_step": "Histogram Equalization",
                            "image": """iVBORw0KGgoAAAANSUhEUgAAAAEAA"""
                            """AABCAAAAAA6fptVAAAACklEQVR4nGNgA"""
                            """AAAAgABSK+kcQAAAABJRU5ErkJggg=="""},
                           {"code": 200,
                            "msg": "Request was successful"},
                           True),

                          ({"username": "user",
                            "filename": "file.jpg",
                            "proc_step": "Contrast Stretching",
                            "image": """iVBORw0KGgoAAAANSUhEUgAAAAEAA"""
                            """AABCAAAAAA6fptVAAAACklEQVR4nGNgA"""
                            """AAAAgABSK+kcQAAAABJRU5ErkJggg=="""},
                           {"code": 200,
                            "msg": "Request was successful"},
                           True),

                          ({"username": "user",
                            "filename": "file.jpg",
                            "proc_step": "Log Compression",
                            "image": """iVBORw0KGgoAAAANSUhEUgAAAAEAA"""
                            """AABCAAAAAA6fptVAAAACklEQVR4nGNgA"""
                            """AAAAgABSK+kcQAAAABJRU5ErkJggg=="""},
                           {"code": 200,
                            "msg": "Request was successful"},
                           True),

                          ({"username": "user",
                            "filename": "file.jpg",
                            "proc_step": "Reverse Video",
                            "image": """iVBORw0KGgoAAAANSUhEUgAAAAEAA"""
                            """AABCAAAAAA6fptVAAAACklEQVR4nGNgA"""
                            """AAAAgABSK+kcQAAAABJRU5ErkJggg=="""},
                           {"code": 200,
                            "msg": "Request was successful"},
                           True),
                          ])
def test_process_process_image(img_info, expected_status, add_user):
    """ Tests the process_process_image function

    This function tests whether the process_process_image function returns
    the correct status code and message. There is no need to test the image
    to base64 conversions or processing steps since those are covered by
    other unit tests.

    Args:
        img_info (dict): dictionary with image information
        expected_status (dict): dictionary with expected code and message
        add_user (bool): whether to add user for purpose of testing

    Returns:
        none
    """
    from server import process_process_image

    if add_user:
        user = User(username=img_info["username"])
        user.save()

    status = process_process_image(img_info)

    assert status == expected_status

    # Reset database
    if add_user:
        user.delete()


@pytest.mark.parametrize("orig_img, proc_step, expected",
                         [((np.array([[0, 128], [128, 255]], dtype="uint8")),
                           "Histogram Equalization",
                           (np.array([[63, 191], [191, 255]], dtype="uint8"))),

                          ((np.array([[0, 128], [128, 255]], dtype="uint8")),
                           "Contrast Stretching",
                           (np.array([[0, 128], [128, 255]], dtype="uint8"))),

                          ((np.array([[0, 128], [128, 255]], dtype="uint8")),
                           "Log Compression",
                           (np.array([[0, 149], [149, 255]], dtype="uint8"))),

                          ((np.array([[0, 128], [128, 255]], dtype="uint8")),
                           "Reverse Video",
                           (np.array([[255, 127], [127, 0]], dtype="uint8"))),
                          ])
def test_run_image_processing(orig_img, proc_step, expected):
    """ Test the run_image_processing function

    This function ensures that run_image_processing processes the image with
    the correct processing step.

    Args:
        orig_img (np.array): unprocessed image as RGB or grayscale intensities
        proc_step (str): type of processing to apply to image
        expected (np.array): expected processed image

    Returns:
        none
    """
    from server import run_image_processing

    proc_img = run_image_processing(orig_img, proc_step)
    print(proc_img)

    assert np.array_equal(proc_img, expected)


@pytest.mark.parametrize("orig_img, expected",
                         # Grayscale image
                         [((np.array([[0, 128], [128, 255]], dtype="uint8")),
                           (np.array([[63, 191], [191, 255]], dtype="uint8"))),

                          # Color image
                          ((np.array([[[255, 0, 0], [0, 255, 0]]],
                                     dtype="uint8")),
                           (np.array([[[255, 127, 255], [127, 255, 255]]],
                                     dtype="uint8"))),
                          ])
def test_equalize_histogram(orig_img, expected):
    """ Test the equalize_histogram function

    This function ensures that the equalize_histogram function properly
    computes the histogram equalized image.

    Args:
        orig_img (np.array): unprocessed image as RGB or grayscale intensities
        expected (np.array): expected processed image

    Returns:
        none
    """
    from server import equalize_histogram

    proc_img = equalize_histogram(orig_img)

    assert np.array_equal(proc_img, expected)


@pytest.mark.parametrize("orig_img, expected",
                         # Grayscale image
                         [((np.array([[100, 128], [128, 200]], dtype="uint8")),
                           (np.array([[0, 71], [71, 255]], dtype="uint8"))),

                          # Color image
                          ((np.array([[[255, 200, 200], [200, 255, 200]]],
                                     dtype="uint8")),
                           (np.array([[[255, 0, 0], [0, 255, 0]]],
                                     dtype="uint8"))),
                          ])
def test_stretch_contrast(orig_img, expected):
    """ Test the stretch_constrast function

    This function ensures that the stretch_contrast function properly
    computes the contrast stretched image.

    Args:
        orig_img (np.array): unprocessed image as RGB or grayscale intensities
        expected (np.array): expected processed image

    Returns:
        none
    """
    from server import stretch_contrast

    proc_img = stretch_contrast(orig_img)

    assert np.array_equal(proc_img, expected)


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


@pytest.mark.parametrize("username, add_user, expected_status, expected_found",
                         # Invalid username
                         [("", False,
                           {"code": 400,
                            "msg": "Field username cannot be empty."},
                           False),

                          # User not in database
                          ("asdf", False,
                           {"code": 404,
                            "msg": "Username not found in database."},
                           False),

                          # Add and delete user
                          ("asdf", True,
                           {"code": 200,
                            "msg": "Request was successful"},
                           False),
                          ])
def test_delete_user(username, add_user, expected_status, expected_found):
    """ Test the delete_user function
    Args:
        username (str): username
        add_user (bool): whether to add user to database
        expected_status (dict): expected status code and status message
        expected_found (bool): whether the user is expected to exist in db
    Returns:
        none
    """
    from server import delete_user

    # Create user if indicated
    if add_user:
        # Create user object
        user = User(username=username)

        # Save to database
        user.save()

    status = delete_user(username)

    # Indicates whether deleted user is found (should be False)
    try:
        user = User.objects.raw({"_id": username}).first()
        found = True
    except:
        user = None
        found = False

    assert (status["code"] == expected_status["code"] and
            status["msg"] == expected_status["msg"] and
            found is expected_found)


@pytest.mark.parametrize("username, add_user, filename, add_img,"
                         "expected_status, expected_found",
                         # Invalid username
                         [("", False, "file.jpg", False,
                           {"code": 400,
                            "msg": "Field username cannot be empty."},
                           False),

                          # Username not found
                          ("asdf", False, "file.jpg", False,
                           {"code": 404,
                            "msg": "Username not found in database."},
                           False),

                          # Filename not found
                          ("asdf", True, "file.jpg", False,
                           {"code": 404,
                            "msg": "Filename not found in database."},
                           False),

                          # File is found
                          ("asdf", True, "file.jpg", True,
                           {"code": 200,
                            "msg": "Request was successful"},
                           False),
                          ])
def test_delete_img(username, add_user, filename, add_img,
                    expected_status, expected_found):
    """ Test the delete_img function
    Args:
        username (str): username linked to filename to delete
        add_user (bool): whether to add user to database
        filename (str): filename to delete
        add_img (bool): whether to add image to database
        expected_status (dict): expected status code and status message
        expected_found (bool): whether the file is expected to exist in db
    """
    from server import delete_img

    # Create user if indicated
    if add_user:
        # Create user object
        user = User(username=username)

        # Create original and processed images if indicated
        if add_img:
            user.orig_img.append({"filename": filename})
            user.proc_img.append({"filename": filename})

        # Save to database
        user.save()

    status = delete_img(username, filename)

    # Indicates whether deleted image is found (should be False)
    try:
        user = User.objects.raw({"_id": username}).first()
        orig_img = user.orig_img[-1]
        proc_img = user.proc_img[-1]
        found = True
    except:
        found = False

    assert (status["code"] == expected_status["code"] and
            status["msg"] == expected_status["msg"] and
            found is expected_found)

    # Delete added user
    if add_user:
        user.delete()
