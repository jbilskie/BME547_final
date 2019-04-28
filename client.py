# client.py
# Author: Kevin Chu, Jessica Bilskie
# Last Modified: 4/24/19

import requests
from pymodm import connect, MongoModel, fields

url = "http://vcm-9111.vm.duke.edu:5000/"
# url = "http://127.0.0.1:5000/"


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

    return


def delete_image(username, filename):
    """ Delete images under filename from the database

    This function takes a username and filename and searches for
    the original and processed images associated with them
    in the MongoDB database. If found, it deletes the images and
    the associated metadata.

    Args:
        username (str): user's identifier
        filename (str): file's identifier

    Returns:
        none
    """

    print("Asking server to delete image from database")

    r = requests.post(url + "delete/" + username + '/' + filename)

    return


def check_file_list(file_list, direction):
    """ Validate a user input

    This function ensures that the user enters a valid list of file lists
    where each file containts a non-empty filename, b64 image, and a valid
    processing steps array.

    Args:
        direction (str): either "upload" or download"
        file_list (list): UPLOAD list of files where each item in the list
        is a list of the file's filename, b64 image, and an array of
        what processing steps should be done
            Example: file_list = [file1, file2]
                    file1 = ["image1", b64_image1,
                             [False, False, True, True, False]]
                    file2 = ["image1", b64_image1,
                             [True, True, False, False, True]]
            Each processing steps array has a True if that process is
            desired and False if not. In this example, image1 desires to
            perform contrast stretching and log compression. Likewise,
            image2 desires the original and to perform histogram
            equalization and reverse video.
        file_list (list): DOWNLOAD list of files where each item in the
        list is a list of the file's filename, image download type, and
        an array of what processing steps should be downloaded
            Example: file_list = [file1, file2]
                    file1 = ["image1", ".jpg",
                             [False, False, True, True, False]]
                    file2 = ["image1", ".tiff",
                             [False, True, False, False, True]]
            Each processing steps array has a True if that process is
            desired and False if not. In this example, image1 desires to
            perform contrast stretching and log compression. Likewise,
            image2 desires the original and to perform histogram
            equalization and reverse video.

    Returns:
        status (dict): status message and status code
    """
    from image import is_b64

    # Default to valid file_list
    status = {"code": 200,
              "msg": "Request was successful"}

    # Check for empty list
    if len(file_list) == 0:
        status = {"code": 400,
                  "msg": "No files were selected."}
        return status

    # Check that each file has all components
    for file in file_list:
        if len(file) != 3:
            status = {"code": 400,
                      "msg": "File {} doesn't contain the correct\
                      amount of elements.".format(file[0])}
            return status

    # Check that images were selected
    image_count = 0
    for file in file_list:
        image_count = image_count + sum(file[2])
    if image_count == 0:
        status = {"code": 400,
                  "msg": "No image types were selected for given files."}
        return status

    # Make sure all filenames are non-empty strings
    for file in file_list:
        if isinstance(file[0], str) is not True:
            status = {"code": 400,
                      "msg": "Filename {} is not a string."
                      .format(file[0])}
            return status
        if len(file[0]) == 0:
            status = {"code": 400,
                      "msg": "Filename {} is empty.".format(file[0])}
            return status

    # Check if b64_image is valid or image type for download is valid
    if direction == "upload":
        for file in file_list:
            validity = is_b64(file[1])
            if validity is False:
                status = {"code": 400,
                          "msg": "Filename {} has invalid b64 image."
                          .format(file[0])}
                return status
    if direction == "download":
        img_types = [".jpg", ".tiff", ".png"]
        for file in file_list:
            if file[1] not in img_types:
                status = {"code": 400,
                          "msg": "Filename {} has invalid image type."
                          .format(file[0])}
                return status

    # Check processing array for proper format
    for file in file_list:
        if len(file[2]) != 5:
            status = {"code": 400,
                      "msg": "Processing array in file {} doesn't \
                      contain the correct amount of elements."
                      .format(file[0])}
            return status
        for proc in file[2]:
            if isinstance(proc, bool) is False:
                status = {"code": 400,
                          "msg": "Processing array contains non-Boolean \
                          elements.".format(file[0])}
                return status

    return status


def upload_images(username, file_list):
    """ Uploads multiple images to the database

    This function takes a list of images and uploads them
    one by one to the database.

    Args:
        username (str): user identifier
        file_list (list): list of files where each item in the list
        is a list of the file's filename, b64 image, and an array of
        what processing steps should be done
            Example: file_list = [file1, file2]
                    file1 = ["image1", b64_image1,
                             [False, False, True, True, False]]
                    file2 = ["image1", b64_image1,
                             [False, True, False, False, True]]
            Each processing steps array has a True if that process is
            desired and False if not. In this example, image1 desires to
            perform contrast stretching and log compression. Likewise,
            image2 desired to perform histogram equalization and reverse
            video.

    Returns:
        files_status (dict of two lists): dictionary of a list of status codes
        and list of status messages for each file being uploaded
    """
    # Make sure input is valid
    status = check_file_list(file_list, "upload")
    if status["code"] != 200:
        return status

    # Complete all uploading tasks and append with their status codes
    files_status = {}
    msg = []
    code = []
    for file in file_list:
        file_status = []
        if file[2] == [True, False, False, False, False]:
            file_status = upload_image(username, file[0], file[1])
        else:
            file_status = process_image(username, file[0], file[1], file[2])
        msg.append(file_status['msg'])
        code.append(file_status['code'])
    files_status['msg'] = msg
    files_status['code'] = code

    return files_status


def download_images(username, file_list, zip_path):
    """ Downloads multiple images from the database

    This function takes a list of images and downloads them
    from the database. If the list is larger than one image,
    the images are put into a zip_path

    Args:
        username (str): user identifier
        file_list (list): list of files where each item in the list
        is a list of the file's filename, image type, and an array of
        what processing steps should be done
            Example: file_list = [file1, file2, file3]
                    file1 = ["image1", ".jpg",
                             [False, False, True, True, False]]
                    file2 = ["image2", ".png",
                             [False, True, False, False, True]]
                    file3 = ["image3", ".tiff",
                             [True, False, False, False, False]]
            Each processing steps array has a 1 if that process is
            desired and 0 if not. In this example, image1 desires to
            perform contrast stretching and log compression. Likewise,
            image2 desired to perform histogram equalization and reverse
            video. Image3 only desires the original image.

    Returns:
        files_status (dict of two lists): dictionary of status codes and
        and messages for each file being downloaded
        files_img_infos (list): list of img_info for each file being
        downloaded
    """
    import zipfile
    import os
    import time

    # Make sure input is valid
    status = check_file_list(file_list, "download")
    if status["code"] != 200:
        return status['msg'], status['code']

    # Define Processing Options
    procs = ["Original", "Histogram Equalization", "Contrast Stretching",
             "Log Compression", "Reverse Video"]

    # If one photo, just download it
    if len(file_list) == 1:
        img_info, status_code = download_image(username, file_list[0][0],
                                               zip_path, file_list[0][2],
                                               file_list[0][1])
        return img_info, status_code

    # Complete all downloading tasks and append with their status codes
    files_status = {}
    msg = []
    code = []
    files_img_infos = []
    cwd = os.getcwd()
    os.mkdir(zip_path + 'temp')
    for file in file_list:
        img_info, status = download_image(username, file[0],
                                          zip_path + 'temp/',
                                          file[2], file[1])
        msg.append(status['msg'])
        code.append(status['code'])
        files_img_infos.append(img_info)

    # Zip the downloads
    t = str(time.time())
    if zip_path != 'none':
        zipf = zipfile.ZipFile(zip_path + 'downloaded_' + t + '.zip',
                               'w', zipfile.ZIP_DEFLATED)
        zipdir(zip_path + 'temp/', zipf)
        zipf.close()
    os.chdir(cwd)
    os.rmdir(zip_path + 'temp')

    files_status['msg'] = msg
    files_status['code'] = code

    return files_img_infos, files_status


def zipdir(path, ziph):
    """ Function for putting everything under an existing folder into
    a zip folder.

    This function puts all the files in an existing folder into a zipped
    folder and then removes it from the existing folder.

    Args:
        path (str): path to folder desired to be zipped
        ziph: zipfile handle

    Returns:
        none
    """
    import os

    os.chdir(path)
    for root, dirs, files in os.walk('.'):
        for file in files:
            ziph.write(os.path.join(root, file))
            os.remove(file)


def upload_image(username, filename, b64_string):
    """ Upload an image to the database

    This function takes an image filename, reads in the image
    and converts it into a string so it can be sent to the server.

    Args:
        username (str): user identifier
        filename (str): name of file
        b64_string (str): image string to upload

    Returns:
        status (dict): status message and status code
    """
    from image import save_b64_img

    print("Asking server to upload image")
    status = {}

    # See if get_img_data was able to read the image
    if b64_string == "":
        status = {"code": 404,
                  "msg": "Image path is not valid."}
        return status_code

    # Format into dictionary
    img_info = {"username": username,
                "filename": filename,
                "image": b64_string}

    r = requests.post(url + "image_upload", json=img_info)
    status['code'] = r.status_code
    status['msg'] = r.text

    return status


def download_image(username, filename, path, proc_steps, type_ext=".png"):
    """ Download an image from the database

    This function takes an image filename, finds the image in the
    database then displays it.

    Args:
        username (str): user identifier
        filename (str): name of file
        path (str): path to where image should be downloaded
            If path is 'none', image isn't saved to a location.
        proc_steps (list): list of Booleans containing requested
        processing steps such as [False, True, False, False, True]
        for "Original" ,"Histogram Equalization", "Contrast
        Stretching", "Log Compression", and "Reverse Video"
        type_ext (str): image type including ".jpg", ".tiff",
        and ".png" where "png" is default

    Returns:
        img_info (dict): dictionary containing image information
        status (dict): status code and status message
    """
    from image import save_b64_img
    import json
    from PIL import Image

    print("Asking server to download image")

    # Create Processing Steps Extension
    proc_ext = ""
    for ind, step in enumerate(proc_steps):
        if step is True:
            proc_ext = proc_ext + "1"
        else:
            proc_ext = proc_ext + "0"

    r = requests.get(url + "image_download/" + username + "/" +
                     filename + "/" + proc_ext)

    status_code = r.status_code
    if status_code != 200:
        img_info = {}
        msg = r.text
    else:
        results = json.loads(r.text)
        img_info = results[0]
        msg = results[1]
        if path == 'none':
            pass
        elif path == 'nonetemp/':
            pass
        else:
            save_b64_img(img_info["image"],
                         path + filename + '_' + proc_ext + type_ext)

    status = {'code': status_code,
              'msg': msg}

    return img_info, status


def process_image(username, filename, b64_string, proc_steps):
    """ Process image

    This function takes an image and sends it to the server as a
    string. The server then processes the image with the user-
    selected processing step.

    Args:
        username (str): user identifier
        filename (str): name of file
        b64_string (str): image string to process
        proc_steps (list): list of Booleans containing requested
        processing steps such as [False, True, False, False, True]
        for "Original" ,"Histogram Equalization", "Contrast
        Stretching", "Log Compression", and "Reverse Video"

    Returns:
        status (dict): status message and status code
    """
    from image import read_img_as_b64
    from image import is_b64

    print("Asking server to process image")
    status = {}

    # See if image is b64 string
    validity = is_b64(b64_string)
    if validity is False:
        status = {"code": 400,
                  "msg": "Filename {} has invalid b64 image."
                  .format(file[0])}
        return status

    # Check processing array for proper format
    if len(proc_steps) != 5:
        status = {"code": 400,
                  "msg": "Processing array doesn't contain the correct \
                  amount of elements."}
        return status
    for proc in proc_steps:
        if isinstance(proc, bool) is False:
            status = {"code": 400,
                      "msg": "Processing array contains non-Boolean \
                      elements.".format(file[0])}
            return status

    # Obtain processing extension
    proc_ext = ""
    for ind, step in enumerate(proc_steps):
        if step is True:
            proc_ext = proc_ext + "1"
        else:
            proc_ext = proc_ext + "0"

    # Format into dictionary
    img_info = {"username": username,
                "filename": filename,
                "image": b64_string,
                "proc_step": proc_ext}

    r = requests.post(url + "process_image", json=img_info)
    status['code'] = r.status_code
    status['msg'] = r.text

    return status


if __name__ == "__main__":
    from image import read_img_as_b64
    delete_user("user1")
    add_new_user("user1")

    # Uploading Examples
    puppy1 = read_img_as_b64("Pictures/Original/puppy1.jpg")
    puppy6 = read_img_as_b64("Pictures/Original/puppy6.jpg")
    puppy8 = read_img_as_b64("Pictures/Original/puppy8.jpg")
    file1 = ["puppy1", puppy1, [True, True, False, False, False]]
    file2 = ["puppy6", puppy6, [True, True, True, True, True]]
    file3 = ["puppy8", puppy8, [True, False, False, False, False]]
    # Example uploading multiple images
    status = upload_images("user1", [file1, file2])
    print(status['code'])
    # Example uploading single image
    status = upload_images("user1", [file3])
    print(status['code'])

    # Downloading Examples
    file1 = ["puppy1", ".jpg", [True, True, False, False, False]]
    file2 = ["puppy6", ".png", [True, True, True, True, True]]
    file3 = ["puppy8", ".tiff", [True, False, False, False, False]]
    file4 = ["puppy1", ".png", [True, False, False, False, False]]
    file5 = ["puppy1", ".jpg", [True, True, True, False, False]]
    # Example download (no saving) multiple images
    img_info, status = download_images("user1", [file1, file2, file3],
                                       "none")
    print(status['code'])
    # Example download (no saving) multiple images (some exist)
    img_info, status = download_images("user1", [file4, file5],
                                       "none")
    print(status['code'])
    # Example download (no saving) single image
    img_info, status = download_images("user1", [file3], "none")
    print(status['code'])
    # Example download (saving) multiple images
    img_info, status = download_images("user1", [file1, file2, file3],
                                       "Pictures/Downloaded/")
    print(status['code'])
    # Example download (saving) multiple images (some exist)
    img_info, status = download_images("user1", [file4, file5],
                                       "Pictures/Downloaded/")
    print(status['code'])
    # Example download (saving) single image
    img_info, status = download_images("user1", [file3],
                                       "Pictures/")
    print(status['code'])
    # Example download (saving) single image that doesn't exist
    img_info, status = download_images("user1", [file5],
                                       "Pictures/")
    print(status['code'])
