# server.py
# Author: Kevin Chu
# Last Modified: 4/12/19

from flask import Flask, jsonify, request

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
    status = validate_user(user_info["username"])

    # Add user to database

    return status


def validate_user(username):
    """ Validate a user's username

    This function ensures that the user enters an allowable
    username. Here, usernames are allowed if they are non-empty.
    The function then returns the appropriate status code and
    message

    Args:
        username (str): user identifier

    Returns:
        status (dict): status message and status code
    """
    if len(username) == 0:
        status = {"code": 400,
                  "msg": "Username cannot be empty."}
    else:
        status = {"code": 200,
                  "msg": "Request was successful"}

    return status


if __name__ == '__main__':
    app.run()
