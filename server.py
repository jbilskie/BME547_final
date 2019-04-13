# server.py
# Author: Kevin Chu
# Last Modified: 4/12/19

from flask import Flask, jsonify, request
from user import User

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
    # Validate user info
    status = validate_input("username", user_info["username"])

    # Add user to database if valid request
    if status == 200:
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
    # Create user object
    user = User(username=username)

    # Save user
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

    return status


if __name__ == '__main__':
    app.run()
