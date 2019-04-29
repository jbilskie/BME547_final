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


@pytest.mark.parametrize("img_paths, exp_filenames, exp_success",
                         # Test single good path
                         [(["test_gui/test1.jpg"], ["test1.jpg"], [True]),
                          # Test single bad path
                          (["test_gui/test20.jpg"], [""], [False]),
                          # Test multiple good paths
                          (["test_gui/test1.jpg", "test_gui/test2.png",
                            "test_gui/test3.tiff", "test_gui/test4.jpg"],
                           ["test1.jpg", "test2.png",
                            "test3.tiff", "test4.jpg"],
                           [True, True, True, True]),
                          # Test multiple paths, one bad
                          (["test_gui/test1.jpg", "test_gui/test20.png",
                            "test_gui/test3.tiff", "test_gui/test4.jpg"],
                           ["test1.jpg", "", "test3.tiff", "test4.jpg"],
                           [True, False, True, True]),
                          # Test no paths given
                          ([], [], []),
                          # Test multiple bad paths
                          (["test_gui/test12.jpg", "test_gui/test20.png",
                            "test_gui/test32.tiff", "test_gui/test43.jpg"],
                           ["", "", "", ""],
                           [False, False, False, False])])
def test_get_img_data(img_paths, exp_filenames, exp_success):
    """Tests get_img_data

    Tests whether numpy arrays of image data, filenames list, and success
    list are correctly extracted from img_paths.

    Imgage paths must be strings since they come from a text box on GUI.

    Args:
        img_paths (list): list of image paths to process
        exp_filenames (list): list of filenames
        exp_success (bool): expected success

    Returns:
        none
    """
    images, filenames, success = get_img_data(img_paths)

    assert (filenames == exp_filenames) or (success == exp_success) is True
