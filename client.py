# client.py
# Author: Kevin Chu, Jessica Bilskie
# Last Modified: 4/24/19

import requests
from pymodm import connect, MongoModel, fields

url = "http://vcm-9111.vm.duke.edu:5000/"


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

    print("Returned: {}".format(r.text))
    print("Status: {}".format(r.status_code))

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
                             [True, True, False, False, True]]
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
        status_codes (list): list of status codes for each file being
        uploaded
            Each file has a list of status codes where the first one is
            for uploading the original image and the preceding are for
            uploading the processed versions specified through the
            processing steps array provided.
            If file_list is invalid, this return is a single status code.
    """
    # Make sure input is valid
    status = check_file_list(file_list, "upload")
    if status["code"] != 200:
        return status

    # Define Processing Options
    procs = ["Original", "Histogram Equalization", "Contrast Stretching",
             "Log Compression", "Reverse Video"]

    # Complete all uploading tasks and append with their status codes
    status_codes = []
    print("UPLOAD THIS MANY FILES")
    print(len(file_list))
    for file in file_list:
        file_status = []
        for proc, do_proc in enumerate(file[2]):
            if proc == 0:
                file_status.append(upload_image(username, file[0], file[1]))
            else:
                if do_proc is True:
                    proc_status = process_image(username, file[0],
                                                file[1], procs[proc])
                    file_status.append(proc_status)
        status_codes.append(file_status)

    return status_codes


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
        status_codes (list): list of status codes for each file being
        downloaded
            Each file has a list of status codes which is of length one if
            only one version (Original or Processed) of the image is
            downloaded. If file_list is invalid, this return is a single
            status code.
        img_infos (list): list of img_info for each file being
        downloaded
            Each file has a list of img_info dictionaries which is of
            length one if only one version (Original or Processed) of
            the image is downloaded. If file_list is invalid, this return
            is a single img_info dictionary.
    """
    import zipfile
    import os

    # Make sure input is valid
    status = check_file_list(file_list, "download")
    img_info = {}
    if status["code"] != 200:
        return img_info, status

    # Define Processing Options
    procs = ["Original", "Histogram Equalization", "Contrast Stretching",
             "Log Compression", "Reverse Video"]

    # If one photo, just download it
    print(len(file_list))
    if len(file_list) == 1:
        if file_list[0][2].count(True) == 1:
            for proc, do_proc in enumerate(file_list[0][2]):
                if do_proc is True:
                    proc_step = procs[proc]
            img_info, status_code = download_image(username, file_list[0][0],
                                                   zip_path, proc_step,
                                                   file_list[0][1])
            return img_info, status_code

    # Complete all downloading tasks and append with their status codes
    status_codes = []
    img_infos = []
    cwd = os.getcwd()
    os.mkdir(zip_path + 'temp')
    for file in file_list:
        file_status = []
        file_infos = []
        for proc, do_proc in enumerate(file[2]):
            if do_proc is True:
                proc_infos, proc_status = download_image(username, file[0],
                                                         zip_path + 'temp/',
                                                         procs[proc],
                                                         file[1])
                file_status.append(proc_status)
                file_infos.append(proc_infos)
        status_codes.append(file_status)
        img_infos.append(file_infos)

    # Zip the downloads
    if zip_path != 'none':
        zipf = zipfile.ZipFile(zip_path + 'downloads.zip',
                               'w', zipfile.ZIP_DEFLATED)
        zipdir(zip_path + 'temp/', zipf)
        zipf.close()
    os.chdir(cwd)
    os.rmdir(zip_path + 'temp')

    return img_infos, status_codes


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
        status_code (int): whether image was successfully uploaded
    """
    from image import save_b64_img

    print("Asking server to upload image")

    # See if get_img_data was able to read the image
    if b64_string == "":
        status_code = 404
        msg = "Image path is not valid."
        print("Returned: {}".format(msg))
        print("Status: {}".format(status_code))

        return status_code

    # Format into dictionary
    img_info = {"username": username,
                "filename": filename,
                "image": b64_string}

    r = requests.post(url + "image_upload", json=img_info)
    status_code = r.status_code
    print("Returned: {}".format(r.text))
    print("Status: {}".format(status_code))

    return status_code


def download_image(username, filename, path, proc_step, type_ext=".png"):
    """ Download an image from the database

    This function takes an image filename, finds the image in the
    database then displays it.

    Args:
        username (str): user identifier
        filename (str): name of file
        path (str): path to where image should be downloaded
            If path is 'none', image isn't saved to a location.
        proc_step (str): type of image being asked for such as
        "Original", "Histogram Equalization", "Contrast Stretching",
        "Log Compression", "Reverse Video"
        type_ext (str): image type including ".jpg", ".tiff",
        and ".png" where "png" is default

    Returns:
        img_info (dict): dictionary containing image information
        status_code (int): status code
    """
    from image import save_b64_img
    import json
    from PIL import Image

    print("Asking server to download image")

    r = requests.get(url + "image_download/" + username + "/" +
                     filename + "/" + proc_step)
    status_code = r.status_code
    if status_code != 200:
        print("{} FAILED HERE".format(filename))
        img_info = {}
        msg = r.text[1]
    else:
        results = json.loads(r.text)
        img_info = results[0]
        msg = results[1]
        if path == 'none':
            pass
        elif path == 'nonetemp/':
            pass
        else:
            save_b64_img(img_info["image"], path+filename+proc_step+type_ext)
    print("Returned: {}".format(msg))
    print("Status: {}".format(status_code))

    return img_info, status_code


def process_image(username, filename, b64_string, proc_step):
    """ Process image

    This function takes an image and sends it to the server as a
    string. The server then processes the image with the user-
    selected processing step.

    Args:
        username (str): user identifier
        filename (str): name of file
        b64_string (str): image string to process
        proc_step (list): list containing requested processing
        steps

    Returns:
        status_code (int): whether image was successfully processed
    """
    from image import read_img_as_b64

    print("Asking server to process image")

    # See if get_img_data was able to read the image
    if b64_string == "":
        status_code = 404
        msg = "Image path is not valid."
        print("Returned: {}".format(msg))
        print("Status: {}".format(status_code))

        return status_code

    # Format into dictionary
    img_info = {"username": username,
                "filename": filename,
                "image": b64_string,
                "proc_step": proc_step}

    r = requests.post(url + "process_image", json=img_info)
    status_code = r.status_code
    print("Returned: {}".format(r.text))
    print("Status: {}".format(status_code))

    return status_code


if __name__ == "__main__":
    from image import read_img_as_b64
    delete_user("user1")
    add_new_user("user1")

    # Uploading Examples
    puppy1 = read_img_as_b64("Pictures/Original/puppy1.jpg")
    puppy2 = read_img_as_b64("Pictures/Original/puppy2.jpg")
    puppy3 = read_img_as_b64("Pictures/Original/puppy3.jpg")
    puppy4 = read_img_as_b64("Pictures/Original/puppy4.jpg")
    file1 = ["puppy1", puppy1, [True, True, False, False, False]]
    file2 = ["puppy2", puppy2, [True, True, True, True, True]]
    file3 = ["puppy3", puppy3, [True, False, False, False, False]]
    file4 = ["puppy4", puppy4, [True, False, False, False, False]]
    # Example uploading multiple images
    status = upload_images("user1", [file1, file2, file3])
    # Example uploading single image
    status = upload_images("user1", [file4])
    print(status)

    # Downloading Examples
    file1 = ["puppy1", ".jpg", [True, True, False, False, False]]
    file2 = ["puppy2", ".png", [True, True, True, True, True]]
    file3 = ["puppy3", ".tiff", [True, False, False, False, False]]
    # Example download (no saving) multiple images
    img_info, status = download_images("user1", [file1, file2, file3],
                                       "none")
    print(status)
    # Example download (no saving) single image
    img_info, status = download_images("user1", [file3], "none")
    print(status)
    # Example download (saving) multiple images
    img_info, status = download_images("user1", [file1, file2, file3],
                                       "Pictures/Downloaded/")
    print(status)
    # Exampe download (saving) single image
    img_info, status = download_images("user1", [file3],
                                       "Pictures/")
    print(status)
