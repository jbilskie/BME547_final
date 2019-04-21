# server.py
# Authors: Jessica Bilskie, Kevin Chu
# Last Modified: 4/21/19

from flask import Flask, jsonify, request
from user import User
import numpy as np
from pymodm import connect, MongoModel, fields
import logging

app = Flask(__name__)
db = "mongodb+srv://jmb221:bme547@bme547-kcuog.mongodb.net"
connect(db + "/BME547?retryWrites=true")


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
    logging.info("Starting process for adding new user: {}"
                 .format(user_info["username"]))

    # Validate user info
    logging.info("Checking that username is valid")
    status = validate_input("username", user_info["username"])
    if status["code"] != 200:
        return status

    # Check whether user exists
    logging.info("Checking whether user already exists")
    status = check_user_exists(user_info["username"])

    # Add user to database if valid request
    if status["code"] == 200:
        register_new_user(user_info["username"])

    return status


def check_user_exists(username):
    """ Check whether user with username exists

    This function checks whether the user with username is already
    registered to the database. The function returns a status code
    of 200 if the user does not already exist and 400 if the user
    does already exist.

    Args:
        username (str): username

    Returns:
        status (dict): status message and status code
    """
    # Check to see if user exists
    try:
        user = User.objects.raw({"_id": img_info["username"]}).first()

    # If user doesn't exist, status code indicates success
    except:
        msg = "Request was successful"
        logging.info(msg)
        status = {"code": 200, "msg": msg}
        return status

    # If user does exist, status code indicates bad request
    else:
        msg = "User {} already exists.".format(username)
        logging.info(msg)
        status = {"code": 400, "msg": msg}
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
    # Create user object
    user = User(username=username)

    # Save user
    logging.info("Saving user: {}".format(username))
    user.actions.append("Created User")
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
        logging.warning("Field " + key + " cannot be empty.")
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
    logging.info("Starting process for uploading {} to user {}"
                 .format(img_info["filename"], img_info["username"]))

    keys = ["username", "filename", "image"]

    # Input data validation
    for key in keys:
        # Make sure keys are non-empty
        status = validate_input(key, img_info[key])

        # If status code indicates failure, exit from function
        if status["code"] != 200:
            return status

    # Calculate image size
    img_info["size"] = get_img_size(img_info["image"])

    # Get time stamp
    logging.info("Providing a timestamp")
    img_info["timestamp"] = datetime.now()

    # Upload image to database if valid request
    upload_image(img_info)

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
    logging.info("Calculating image size")

    img = b64_to_image(b64_string)

    # Only interested in width and height, not color channels
    h = (np.shape(img))[0]
    w = (np.shape(img))[1]
    sz = (w, h)

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
    # Retrieve user from database
    user = User.objects.raw({"_id": img_info["username"]}).first()

    # Add image info
    found = False
    for ind, img_infos in enumerate(user.orig_img):
        if img_infos["filename"] == img_info["filename"]:
            logging.info("Uploading image to existing filename in database")
            user.orig_img[ind] = img_info
            user.actions.append("Updated Image")
            found = True
    if found is False:
        logging.info("Uploading image to database")
        user.orig_img.append(img_info)
        user.actions.append("Uploaded Image")

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
    import time
    from image import b64_to_image
    from image import image_to_b64
    logging.info("Starting process for processing {} to user {}"
                 .format(img_info["filename"], img_info["username"]))

    keys = ["username", "filename", "image"]

    # Input data validation
    for key in keys:
        # Make sure keys are non-empty
        status = validate_input(key, img_info[key])

        # If status code indicates failure, exit from function
        if status["code"] != 200:
            return status

    # Decode b64
    orig_img = b64_to_image(img_info["image"])

    # Process image
    t1 = time.time()
    proc_img = run_image_processing(orig_img, img_info["proc_step"])
    t2 = time.time()

    # Store processed image
    img_info["proc_image"] = image_to_b64(proc_img)

    # Processing time
    logging.info("Storing processing time")
    img_info["proc_time"] = t2-t1

    # Calculate image size
    img_info["size"] = get_img_size(img_info["image"])
    img_info["proc_size"] = get_img_size(img_info["proc_image"])

    # Get time stamp
    logging.info("Providing a timestamp")
    img_info["timestamp"] = datetime.now()

    # Upload processed image
    upload_processed_image(img_info)

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
        logging.info("Performing log compression processing")
        proc_img = adjust_log(orig_img)

    elif proc_step == "Reverse Video":
        logging.info("Performing reverse video processing")
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
    logging.info("Performing histogram equalization processing")

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
    logging.info("Performing stretch contrast processing")

    p2, p98 = np.percentile(orig_img, (2, 98))
    proc_img = rescale_intensity(orig_img, in_range=(p2, p98))

    return proc_img


def upload_processed_image(img_info):
    """ Uploads image to database

    This function takes a processed image and its metadata and uploads
    it to the MongoDB database. The image is linked to the user
    that uploaded it.

    Args:
        img_info (dict): dictionary with image metadata including
        the username, filename, size of original image, size of
        processed image, time stamp, processing time,
        processing step, original image, and processed image itself

    Returns:
        none
    """
    # Image info for Original Image
    img_info_original = {"username": img_info["username"],
                         "filename": img_info["filename"],
                         "image": img_info["image"],
                         "timestamp": img_info["timestamp"],
                         "size": img_info["size"]}

    # Image info for Processed Imaged
    img_info_processed = {"username": img_info["username"],
                          "filename": img_info["filename"],
                          "image": img_info["proc_image"],
                          "timestamp": img_info["timestamp"],
                          "size": img_info["proc_size"],
                          "proc_time": img_info["proc_time"],
                          "proc_step": img_info["proc_step"]}

    # Retrieve user from database
    user = User.objects.raw({"_id": img_info["username"]}).first()

    # Add original image info
    found = False
    for ind, img_infos in enumerate(user.orig_img):
        if img_infos["filename"] == img_info_original["filename"]:
            found = True
    if found is False:
        logging.info("Uploading original image to database")
        user.orig_img.append(img_info_original)
        user.actions.append("Uploaded Original Image")
    user.save()

    # Add processed image info
    found = False
    for ind, img_infos in enumerate(user.proc_img):
        if img_infos["filename"] == img_info_processed["filename"]:
            if img_infos["proc_step"] == img_info_processed["proc_step"]:
                logging.info("Uploading processed image to existing\
                             filename in database")
                user.proc_img[ind] = img_info_processed
                user.actions.append("Updated Processed Image")
                found = True
    if found is False:
        logging.info("Uploading processed image to database")
        user.proc_img.append(img_info_processed)
        user.actions.append("Uploaded Processed Image")
    user.save()

    return


@app.route("/image_download/<username>/<filename>/<proc_step>",
           methods=["GET"])
def image_download(username, filename, proc_step):
    """ Download images to database

    This function implements a get request that takes
    a dictionary containing a username and filename and
    downloads the file from a MongoDB database.

    Args:
        username (str): name of input username
        filename (str): name of input filename
        proc_step (str): name of that image is desired such as "Original",
        "Histogram Equalization", "Contrast Stretching", "Log
        Compression", "Reverse Video"

    Returns:
        json of image info and status message
        code (int): status code that indicates whether a request
        was successful
    """
    in_data = {"username": username,
               "filename": filename,
               "proc_step": proc_step}
    status, img_info = process_image_download(in_data)

    return jsonify(img_info, status["msg"]), status["code"]


def process_image_download(input_img_info):
    """ Processes request to download images

    This function processes the request to download images from
    the database.

    Args:
        input_img_info (dict): dictionary with a username, filename,
        image process

    Returns:
        status (dict): status message and status code
        img_info (dict): dictionary with a username, filename,
        metadata, and image
    """
    logging.info("Starting process for downloading {} to user {}"
                 .format(input_img_info["filename"],
                         input_img_info["username"]))

    # Validate user info
    logging.info("Checking that username is valid")
    status = validate_input("username", input_img_info["username"])
    if status["code"] != 200:
        return status

    # Validate filename
    logging.info("Checking that filename is valid")
    status = validate_input("filename", input_img_info["filename"])
    if status["code"] != 200:
        return status

    # Does user, filename, and image exist in data based
    status = exist_input(input_img_info["username"],
                         input_img_info["filename"],
                         input_img_info["proc_step"])
    if status["code"] != 200:
        return status

    # Retrieve user from database
    user = User.objects.raw({"_id": input_img_info["username"]}).first()

    # Find desired image
    if input_img_info["proc_step"] == "Original":
        for ind, img_info in enumerate(user.orig_img):
            if img_info["filename"] == input_img_info["filename"]:
                img_info = user.orig_img[ind]
    else:
        for ind, img_info in enumerate(user.proc_img):
            if img_info["filename"] == input_img_info["filename"]:
                if img_info["proc_step"] == input_img_info["proc_step"]:
                    img_info = user.proc_img[ind]

    user.actions.append("Downloaded Image")

    return status, img_info


def exist_input(username, filename, proc_step):
    """ Validate whether input exists in database

    This function ensures that the user enters an input username,
    filename, and image exists in the database. The function then
    returns the appropriate status code and message.

    Args:
        username (str): name of input username
        filename (str): name of input filename
        proc_step (str): name of that image is desired such as "Original",
        "Histogram Equalization", "Contrast Stretching", "Log
        Compression", "Reverse Video"

    Returns:
        status (dict): status message and status code
    """
    logging.info("Checking that desired image exists")

    # Retrieve user from database, exit if user not found
    try:
        user = User.objects.raw({"_id": username}).first()
    except:
        status = {"code": 404,
                  "msg": "Username not found in database."}
        logging.warning("Username {} not found in database."
                        .format(username))

        return status

    # Find desired image
    else:
        found = False
        if proc_step == "Original":
            for img_info in user.orig_img:
                if img_info["filename"] == filename:
                    found = True
        else:
            for img_info in user.proc_img:
                if img_info["filename"] == filename:
                    if img_info["proc_step"] == proc_step:
                        found = True
        if found is False:
            status = {"code": 404,
                      "msg": "Filename/Image not found in database."}
            logging.warning("Desired image not found in database."
                            .format(username))
        else:
            status = {"code": 200,
                      "msg": "Request was successful"}

    return status

if __name__ == '__main__':
    logging.basicConfig(filename='LOGFILE.log', level=logging.INFO)
    app.run()
