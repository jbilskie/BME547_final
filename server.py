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
    status = {"code": 200,
              "msg": "Request was successful"}

    # Validate user info

    # Add user to database

    return status


if __name__ == '__main__':
    app.run()
