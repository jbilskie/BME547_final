# client.py
# Author: Kevin Chu
# Last Modified: 4/19/19

import requests
from pymodm import connect, MongoModel, fields

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


def delete_user(username):
    """ Delete user from the database

    This function takes a username and searches for it
    in the MongoDB database. If found, it deletes the user.

    Args:
        username (str): user's identifier

    Returns:
        none
    """

    print("Asking server to delete user from database")

    r = requests.post(url + "delete/" + username)

    print("Returned: {}".format(r.text))
    print("Status: {}".format(r.status_code))

    return


def upload_images(username, file_list, path):
    """ Uploads multiple images to the database

    This function takes a list of images and uploads them
    one by one to the database.

    Args:
        username (str): user identifier
        file_list (list): list of file paths
        path (str): path to images being uploaded

    Returns:
        none
    """
    if len(file_list) == 0:
        print("No files were selected.")
    else:
        for filename in file_list:
            upload_iamge(username, filename, path)

    return


def upload_image(username, filename, path):
    """ Upload an image to the database

    This function takes an image filename, reads in the image
    and converts it into a string so it can be sent to the server.

    Args:
        username (str): user identifier
        filename (str): name of file
        path (str): path to image being uploaded

    Returns:
        none
    """
    from image import read_img_as_b64
    from image import save_b64_img

    print("Asking server to upload image")

    # Read in image as b64
    try:
        b64_string = read_img_as_b64(path)
    except FileNotFoundError:
        status_code = 404
        msg = "Image path is not valid."
        print("Returned: {}".format(msg))
        print("Status: {}".format(status_code))

        return

    # Format into dictionary
    img_info = {"username": username,
                "filename": filename,
                "image": b64_string}

    r = requests.post(url + "image_upload", json=img_info)

    print("Returned: {}".format(r.text))
    print("Status: {}".format(r.status_code))

    return


def download_image(username, filename, path, proc_step, type_ext=".png"):
    """ Download an image from the database

    This function takes an image filename, finds the image in the
    database then displays it.

    Args:
        username (str): user identifier
        filename (str): name of file
        path (str): path to where image should be downloaded
        proc_step (str): type of image being asked for such as
        "Original", "Histogram Equalization", "Contrast Stretching",
        "Log Compression", "Reverse Video"
        type_ext (str): image type including ".jpg", ".tiff",
        and ".png" where "png" is default

    Returns:
        none
    """
    from image import save_b64_img
    import json
    from PIL import Image

    print("Asking server to download image")

    r = requests.get(url + "image_download/" + username + "/" +
                     filename + "/" + proc_step)
    if r.status_code != 200:
        msg = r.text
    else:
        results = json.loads(r.text)
        img_info = results[0]
        msg = results[1]
        save_b64_img(img_info["image"], path+filename+"download"+type_ext)
    print("Returned: {}".format(msg))
    print("Status: {}".format(r.status_code))

    return


def process_image(username, filename, path, proc_step):
    """ Process image

    This function takes an image and sends it to the server as a
    string. The server then processes the image with the user-
    selected processing step.

    Args:
        username (str): user identifier
        filename (str): name of file
        path (str): path to image being uploaded
        proc_step (str): type of image being asked for such as
        "Original", "Histogram Equalization", "Contrast Stretching",
        "Log Compression", "Reverse Video"

    Returns:
        none
    """
    from image import read_img_as_b64

    print("Asking server to process image")

    # Read in image as b64
    try:
        b64_string = read_img_as_b64(path)
    except FileNotFoundError:
        status_code = 404
        msg = "Image path is not valid."
        print("Returned: {}".format(msg))
        print("Status: {}".format(status_code))

        return

    # Format into dictionary
    img_info = {"username": username,
                "filename": filename,
                "image": b64_string,
                "proc_step": proc_step}

    r = requests.post(url + "process_image", json=img_info)

    print("Returned: {}".format(r.text))
    print("Status: {}".format(r.status_code))

    return


if __name__ == "__main__":
    add_new_user("user1")
    delete_user("user1")
    delete_user("user_100")
#    add_new_user("user2")
#    upload_image("user2", "puppy8", "Pictures/Original/puppy8.jpg")
#    upload_image("user2", "puppy2", "Pictures/Original/puppy11.jpg")
#    process_image("user1", "puppy11", "Pictures/Original/puppy11.jpg",
#                  "Reverse Video")
#    process_image("user2", "puppy3", "Pictures/Original/puppy3.jpg",
#                 "Reverse Image")
#    process_image("user4", "puppy4", "Pictures/Original/puppy4.jpg",
#                  "Histogram Equalization")
#    download_image("user5", "puppy1", "Pictures/Downloaded/",
#                   "Original", ".tiff")
#    download_image("user2", "puppy3", "Pictures/Downloaded/",
#                   "Reverse Image")
#    download_image("user2", "puppy8", "Pictures/Downloaded/",
#                   "Reverse Image")
