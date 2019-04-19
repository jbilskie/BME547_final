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

    # Read in image as b64
    b64_string = read_img_as_b64(path)

    # Format into dictionary
    img_info = {"username": username,
                "filename": filename,
                "image": b64_string}

    print("Asking server to upload image")

    r = requests.post(url + "image_upload", json=img_info)

    print("Returned: {}".format(r.text))
    print("Status: {}".format(r.status_code))

    return


def download_image(username, filename, path, proc_step):
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

    Returns:
        none
    """
    from image import save_b64_img
    import json

    print("Asking server to download image")

    r = requests.get(url + "image_download/" + username + "/" +
                     filename + "/" + proc_step)
    results = json.loads(r.text)
    img_info = results[0]
    msg = results[1]
    save_b64_img(img_info["image"], path+filename+"download.jpg")
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

    # Read in image as b64
    b64_string = read_img_as_b64(path)

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
    add_new_user("user1")
    add_new_user("user2")
    upload_image("user1", "puppy1", "Pictures/Original/puppy1.jpg")
    upload_image("user2", "puppy2", "Pictures/Original/puppy2.jpg")
    process_image("user1", "puppy1", "Pictures/Original/puppy1.jpg",
                  "Reverse Video")
    process_image("user2", "puppy3", "Pictures/Original/puppy3.jpg",
                  "Reverse Video")
    process_image("user2", "puppy4", "Pictures/Original/puppy4.jpg",
                  "Histogram Equalization")
    download_image("user1", "puppy1", "Pictures/Downloaded/",
                   "Original")
    download_image("user2", "puppy3", "Pictures/Downloaded/",
                   "Reverse Video")
