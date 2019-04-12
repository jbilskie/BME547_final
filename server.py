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

    return jsonify(in_data)


if __name__ == '__main__':
    app.run()
