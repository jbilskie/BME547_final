# client.py
# Author: Kevin Chu
# Last Modified: 4/13/19

import requests

url = "http://127.0.0.1:5000/"


def add_new_user(username):
    """ Add new user to server

    This function takes a dictionary with a user's information
    and registers their data to the server.

    Args:
        username (str): user's identifier

    Returns:
        none
    """
    # Format into dictionary
    user = {"username": username}

    print("Asking server to register new user")

    r = requests.post(url + "new_user", json=user)

    print("Returned: {}".format(r.text))
    print("Status: {}".format(r.status_code))

    return


def upload_image(username, filename):
    """ Upload an image to the database

    This function takes an image filename, reads in the image
    and converts it into a string so it can be sent to the server.

    Args:
        username (str): user identifier
        filename (str): contains directory and filename

    Returns:
        none
    """
    # Read in image as b64
    b64_img = "replace this string"

    # Format into dictionary
    img_info = {"username": username,
                "filename": filename,
                "image": b64_img}

    print("Asking server to upload image")

    r = requests.post(url + "image_upload", json=img_info)

    print("Returned: {}".format(r.text))
    print("Status: {}".format(r.status_code))

    return


if __name__ == "__main__":
    add_new_user("user1")
    upload_image("user1", "file.png")
