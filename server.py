# server.py
# Author: Kevin Chu
# Last Modified: 4/16/19

from flask import Flask, jsonify, request
from user import User
import numpy as np
from pymodm import connect, MongoModel, fields

app = Flask(__name__)


connect("mongodb+srv://jmb221:bme547@bme547-kcuog.mongodb.net/test?retryWrites=true")
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
    img_info["size"] = get_img_size(img_info["image"])

    # Get time stamp
    img_info["timestamp"] = datetime.now()

    # Upload image to database if valid request
    # upload_image(img_info)

    return status


def get_img_size(b64_string):
    """ Obtain the size of the image in pixels

    This function takes an image represented as a base 64 string
    and converts it into an np.array. The np.array is then used
    to determine the size of the image in pixels.

    Args:
        b64_string (str): image represented as base 64 string

    Returns:
        sz (tuple): dimensions of image expressed as (width x height)
    """
    from image import b64_to_image

    img = b64_to_image(b64_string)

    # Only interested in width and height, not color channels
    sz = (np.shape(img))[0:2]

    return sz


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
        the username, filename, image, and processing steps to run

    Returns:
        status (dict): status message and status code
    """
    from datetime import datetime
    from image import b64_to_image
    from image import image_to_b64

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
    proc_list = ["Histogram Equalization", "Contrast Stretching",
                 "Log Compression", "Reverse Video"]

    proc_img = orig_img

    t1 = datetime.now()

    # Apply (possibly multiple) processing steps
    for i in range(0, len(proc_list)):
        if (img_info["proc_steps"])[i] is True:
            proc_img = run_image_processing(proc_img, proc_list[i])

    t2 = datetime.now()

    # Store processed image
    img_info["image"] = image_to_b64(proc_img)

    # Processing time
    img_info["proc_time"] = t2-t1

    # Calculate image size
    img_info["size"] = get_img_size(img_info["image"])

    # Get time stamp
    img_info["timestamp"] = datetime.now()

    # Upload processed image
    # upload_image(img_info)

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
    from skimage.exposure import adjust_log
    from skimage.util import invert

    if proc_step == "Histogram Equalization":
        proc_img = equalize_histogram(orig_img)

    elif proc_step == "Contrast Stretching":
        proc_img = stretch_contrast(orig_img)

    elif proc_step == "Log Compression":
        proc_img = adjust_log(orig_img)

    elif proc_step == "Reverse Video":
        proc_img = invert(orig_img)

    return proc_img


def equalize_histogram(orig_img):
    """ Performs histogram equalization on uploaded image

    This function uses the skimage.exposure.equalize_hist to
    equalize the histogram of the uploaded image. The function
    then returns the processed image as an np.array.

    Args:
        orig_img (np.array): original, raw image

    Returns:
        proc_img (np.array): processed image
    """
    from skimage.exposure import equalize_hist

    # Preallocate
    proc_img = np.zeros(np.shape(orig_img))

    # Apply histogram equalization to all channels
    for i in range(0, (np.shape(orig_img))[-1]):
        proc_img[:, :, i] = equalize_hist(orig_img[:, :, i])

    # equalize_hist outputs np.array with floats in range [0-1]
    # Cast this to uint8 in range [0-255]
    proc_img = np.uint8(proc_img * 255)

    return proc_img


def stretch_contrast(orig_img):
    """ Performs contrast stretching on uploaded image

    This function uses the skimage.exposure.rescale_intensity
    function to stretch the contrast of the uploaded image. The
    function then returns the processed image an an np.array.

    Args:
        orig_img (np.array): original, raw image

    Returns:
        proc_img (np.array): processed image
    """
    from skimage.exposure import rescale_intensity

    p2, p98 = np.percentile(orig_img, (2, 98))
    proc_img = rescale_intensity(orig_img, in_range=(p2, p98))

    return proc_img


if __name__ == '__main__':
    app.run()
