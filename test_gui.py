# test_gui.py
# Authors: Jessica Bilskie
# Last Modified: 4/23/19

from user import User
import numpy as np
import pytest
from gui import *


@pytest.mark.parametrize("input, exp_paths",
                         [("pic1.jpg, pic2.tiff, pic3.png",
                           ["pic1.jpg", "pic2.tiff", "pic3.png"]),
                          ("pic1.jpg,pic2.tiff,pic3.png",
                           ["pic1.jpg", "pic2.tiff", "pic3.png"]),
                          ("pic1.jpg",
                           ["pic1.jpg"]),
                          ("pic1.jpg, pic2.tiff, pic3.png,",
                           ["pic1.jpg", "pic2.tiff", "pic3.png"]),
                          ("pic1.jpg pic2.tiff pic3.png",
                           ["pic1.jpgpic2.tiffpic3.png"])])
def test_process_img_paths(input, exp_paths):
    """Tests process_img_paths

    Tests whether a string of comma separated image paths are
    processed into a list of paths correctly. Because the GUI
    automatically makes the input a string other input types
    were not tested or necessary for testing.

    Args:
        input (str): string containing image path(s)
        exp_paths (list) : list of expected image path(s) (str)

    Returns:
        none
    """
    paths = process_img_paths(input)
    assert paths == exp_paths
