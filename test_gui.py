# test_gui.py
# Authors: Jessica Bilskie
# Last Modified: 4/23/19

from user import User
import numpy as np
import pytest
from gui import *
from user import User


@pytest.mark.parametrize("img_typ, ent1, ent2, ent3, ent4, \
                          exp_req_typ, exp_proc_steps",
                         [('JPEG', False, True, True, False,
                           '.jpg', [False, False, True, True, False]),
                          ('PNG', False, True, True, False,
                           '.png', [False, False, True, True, False]),
                          ('TIFF', False, True, True, False,
                           '.tiff', [False, False, True, True, False]),
                          ('JPEG', True, True, True, True,
                           '.jpg', [False, True, True, True, True]),
                          ('JPEG', False, False, False, False,
                           '.jpg', [True, False, False, False, False]),
                          ('TIFF', False, False, False, False,
                           '.tiff', [True, False, False, False, False])])
def test_convert_inputs(img_typ, ent1, ent2, ent3, ent4,
                        exp_req_typ, exp_proc_steps):
    """Tests convert_inputs

    Tests whether requested image type and processing steps are formatted
    as desired.

    img_type is selected from a drop down so it is expected to be one of
    three strings, 'JPEG', 'PNG', or 'TIFF'
    ent1 - ent4 are from Boolean GUI returns so type is not tested.

    Args:
        img_typ (str): type of picture desired
        ent1 (bool) : whether histogram equalization processing is desired
        ent2 (bool) : whether contrast stretching processing is desired
        ent3 (bool) : whether log compression processing is desired
        ent4 (bool) : whether reverse video processing is desired

    Returns:
        none
    """
    req_typ, proc_steps = convert_inputs(img_typ, ent1, ent2, ent3, ent4)

    assert (req_typ == exp_req_typ) or (proc_steps == exp_proc_steps) is True


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
