# server.py
# Author: Kevin Chu
# Last Modified: 4/13/19

from flask import Flask, jsonify, request
from user import User
import numpy as np
from pymodm import connect, MongoModel, fields

app = Flask(__name__)


@app.route("/new_user", methods=["POST"])
def new_user():
    """ Register new user in the server

    This function implements a post request that takes
    a dictionary containing user information and saves it
    in a MongoDB database.

    Args:
        none

    Returns:
        out_data (string): status message and status code
    """
    print("Inside of new_user")
    in_data = request.get_json()

    status = process_new_user(in_data)

    return status["msg"], status["code"]


def process_new_user(user_info):
    """ Processes request to add new user

    This function processes the request to add a new user
    to the database.

    Args:
        user_info (dict): dictionary with user info

    Returns:
        status (dict): status message and status code
    """
    print("Inside of process_new_user")
    # Validate user info
    status = validate_input("username", user_info["username"])

    # Add user to database if valid request
    if status["code"] == 200:
        register_new_user(user_info["username"])

    return status


def register_new_user(username):
    """ Register new user to database

    This function takes a user's username and registers them
    to the MongoDB database.

    Args:
        username (str): user identifier

    Returns:
        none
    """
    print("Inside of register_new_user")
    # Create user object
    user = User(username=username)

    # Save user
    print("Saving user")
    user.save()

    return


def validate_input(key, value):
    """ Validate a user input

    This function ensures that the user enters a valid input
    (could be username or filename). Here, the inputs are valid
    if they are non-empty. The function then returns the appropriate
    status code and message.

    Args:
        key (str): name of input to validate (e.g. username, filename)
        value (str): value of input to validate (e.g. user1, file.png)

    Returns:
        status (dict): status message and status code
    """
    if len(value) == 0:
        status = {"code": 400,
                  "msg": "Field " + key + " cannot be empty."}
    else:
        status = {"code": 200,
                  "msg": "Request was successful"}

    return status


@app.route("/image_upload", methods=["POST"])
def image_upload():
    """ Upload images to database

    This function implements a post request that takes
    a dictionary containing an image and its metadata and
    uploads it to a MongoDB database.

    Args:
        none

    Returns:
        msg (str): displays message regarding a request
        code (int): status code that indicates whether a request
        was successful
    """
    in_data = request.get_json()

    status = process_image_upload(in_data)

    return status["msg"], status["code"]


def process_image_upload(img_info):
    """ Processes request to upload images

    This function processes the request to upload new images to
    the database.

    Args:
        img_info (dict): dictionary with image metadata including
        the username, filename, and image itself

    Returns:
        status (dict): status message and status code
    """
    from datetime import datetime

    # Validate user info
    status = validate_input("username", img_info["username"])

    # If status code indicates failure, exit from function
    if status["code"] != 200:
        return status

    # Validate filename
    status = validate_input("filename", img_info["filename"])
    if status["code"] != 200:
        return status

    # Calculate image size
    img_info["size"] = 1  # hard coded for now, CHANGE LATER

    # Get time stamp
    img_info["timestamp"] = datetime.now()

    # Upload image to database if valid request
    upload_image(img_info)

    return status


def upload_image(img_info):
    """ Uploads image to database

    This function takes an image and its metadata and uploads
    it to the MongoDB database. The image is linked to the user
    that uploaded it.

    Args:
        img_info (dict): dictionary with image metadata including
        the username, filename, size, time stamp, and image itself

    Returns:
        none
    """
    # Retrieve user from database (assumes they exist - CHANGE)
    user = User.objects.raw({"_id": img_info["username"]}).first()

    # Add image info
    user.orig_img.append(img_info)

    user.save()

    return


@app.route("/process_image", methods=["POST"])
def process_image():
    """ Process and upload image to database

    This implements the post request to process an image and store
    the processed image on the MongoDB database.

    Args:
        none

    Returns:
        msg (str): displays message regarding a request
        code (int): status code that indicates whether a request
        was successful
    """
    in_data = request.get_json()

    status = process_process_image(in_data)

    return status["msg"], status["code"]


def process_process_image(img_info):
    """ Processes request to process image

    This function processes the request to process an image. The
    function returns a status code and message to indicate
    whether the request was successful.

    Args:
        img_info (dict): dictionary with image metadata including
        the username, filename, image, and processing step to run

    Returns:
        status (dict): status message and status code
    """
    from image import b64_to_image

    # Validate user info
    status = validate_input("username", img_info["username"])
    if status["code"] != 200:
        return status

    # Validate filename
    status = validate_input("filename", img_info["filename"])
    if status["code"] != 200:
        return status

    # Decode b64
    orig_img = b64_to_image(img_info["image"])

    # Process image
    proc_img = run_image_processing(orig_img, img_info["proc_step"])

    # Upload processed image

    return status


def run_image_processing(orig_img, proc_step):
    """ Performs processing on uploaded image

    This function takes an image and performs processing.
    The image can be processed using histogram equalization,
    contrast stretching, log compression, or reverse video.

    Args:
        orig_img (np.array): unprocessed image as RGB intensities
        proc_step (str): type of processing to apply to image

    Returns:
        proc_img (np.array): processed image as RGB intensities
    """
    from skimage.exposure import equalize_hist
    from skimage.exposure import rescale_intensity
    from skimage.exposure import adjust_log

    if proc_step == "Histogram Equalization":
        # Preallocate
        proc_img = np.zeros(np.shape(orig_img))

        # Apply histogram equalization to all channels
        for i in range(0, (np.shape(orig_img))[-1]):
            proc_img[:, :, i] = equalize_hist(orig_img[:, :, i])

    elif proc_step == "Contrast Stretching":
        p2, p98 = np.percentile(orig_img, (2, 98))
        proc_img = rescale_intensity(orig_img, in_range=(p2, p98))

    elif proc_step == "Log Compression":
        proc_img = adjust_log(orig_img)

    return proc_img


if __name__ == '__main__':
    app.run()