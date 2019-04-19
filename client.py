# client.py
# Author: Kevin Chu
# Last Modified: 4/18/19

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


def upload_images(username, file_list):
    """ Uploads multiple images to the database

    This function takes a list of images and uploads them
    one by one to the database.

    Args:
        username (str): user identifier
        file_list (list): list of file paths

    Returns:
        none
    """
    if len(file_list) == 0:
        print("No files were selected.")
    else:
        for filename in file_list:
            upload_iamge(username, filename)

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
    from image import read_img_as_b64
    from image import save_b64_img

    # Read in image as b64
    b64_string = read_img_as_b64(filename)

    save_b64_img(b64_string, "new-img.jpg")

    # Format into dictionary
    img_info = {"username": username,
                "filename": filename,
                "image": b64_string}

    print("Asking server to upload image")

    r = requests.post(url + "image_upload", json=img_info)

    print("Returned: {}".format(r.text))
    print("Status: {}".format(r.status_code))

    return


def process_image(username, filename, proc_steps):
    """ Process image

    This function takes an image and sends it to the server as a
    string. The server then processes the image with the user-
    selected processing step.

    Args:
        username (str): user identifier
        filename (str): contains directory and filename
        proc_steps (list): list of booleans where each element
        indicates whether a processing step should (True) or should
        not (False) be run

    Returns:
        none
    """
    from image import read_img_as_b64

    # Read in image as b64
    b64_string = read_img_as_b64(filename)

    # Format into dictionary
    img_info = {"username": username,
                "filename": filename,
                "image": b64_string,
                "proc_steps": proc_steps}

    print("Asking server to process image")

    r = requests.post(url + "process_image", json=img_info)

    print("Returned: {}".format(r.text))
    print("Status: {}".format(r.status_code))

    return


if __name__ == "__main__":
    # add_new_user("user1")
    # upload_image("user1", "delete_this_img.jpg")
    process_image("user1", "delete_this_img.jpg", [True, True, False, False])
