# create_test_images.py
# Author: Kevin Chu
# Last Modified: 4/19/19

# This module creates images to test the image.py module.

import numpy as np


def save_array_as_img(img, file_path):
    """ Saves array as an image

    This function takes an np.array of pixel intensities and
    saves it as an image file.

    Args:
        image (np.array): image represented as pixel intensity
        file_path (str): includes directory and file name

    Returns:
        none
    """
    from skimage.io import imsave

    imsave(file_path, img)

    return


if __name__ == '__main__':
    # Test image 1
    img1 = (np.array([0], dtype="uint8")).reshape((1, 1))
    test_image1 = "test_image/test1.jpg"
    save_array_as_img(img1, test_image1)

    # Test image 2
    img2 = (np.array([255], dtype="uint8")).reshape((1, 1))
    test_image2 = "test_image/test2.jpg"
    save_array_as_img(img2, test_image2)

    # Test image 3
    test_image3 = "test_image/test3.png"
    save_array_as_img(img1, test_image3)

    # Test image 4
    test_image4 = "test_image/test4.tiff"
    save_array_as_img(img1, test_image4)

    # Test image 5
    img5 = (np.array([[[255, 0, 0]]], dtype="uint8"))
    test_image5 = "test_image/test5.png"
    save_array_as_img(img5, test_image5)
