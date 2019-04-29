# test_gui.py
# Authors: Jessica Bilskie
# Last Modified: 4/23/19

from user import User
import numpy as np
import pytest
from gui import *
from user import User
from image import b64_to_image, read_img_as_b64


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
                          # Test zip file
                          (["test_gui/test.zip"],
                           ["test8.png", "test9.tiff", "test10.png"],
                           [True, True, True]),
                          # Test zip file and an image
                          (["test_gui/test.zip", "test_gui/test6.tiff"],
                           ["test8.png", "test9.tiff",
                            "test10.png", "test6.tiff"],
                           [True, True, True, True]),
                          # Test empty zip file
                          (["test_gui/test_empty.zip"], [], []),
                          # Test folder within zip file
                          (["test_gui/test_inner.zip"], ["test5.png"], [True]),
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
    from image import is_b64

    images, filenames, _ = get_img_data(img_paths)

    success = []
    for img in images:
        success.append(is_b64(img))

    assert (filenames == exp_filenames) or (success == exp_success) is True


@pytest.mark.parametrize("filenames, file_ext, proc_steps, success, \
                          exp_file_list",
                         # Test one success
                         [(['name1'], '.jpg',
                           [True, False, False, False, False],
                           [True],
                           [['name1', '.jpg',
                             [True, False, False, False, False]]]),
                          # Test one bad
                          (['name1'], '.jpg',
                           [True, False, False, False, False],
                           [False], []),
                          # Test multiple successes
                          (['name1', 'name2'], '.jpg',
                           [True, False, False, False, False],
                           [True, True],
                           [['name1', '.jpg',
                             [True, False, False, False, False]],
                            ['name2', '.jpg',
                             [True, False, False, False, False]]]),
                          # Test multiple, some succes
                          (['name1', 'name2'], '.jpg',
                           [True, False, False, False, False],
                           [False, True],
                           [['name2', '.jpg',
                             [True, False, False, False, False]]]),
                          # Different file extension
                          (['name1', 'name2'], '.tiff',
                           [True, False, False, False, False],
                           [False, True],
                           [['name2', '.tiff',
                             [True, False, False, False, False]]]),
                          # Different processing steps
                          (['name1', 'name2'], '.tiff',
                           [False, True, True, True, False],
                           [False, True],
                           [['name2', '.tiff',
                             [False, True, True, True, False]]])])
def test_get_file_list(filenames, file_ext, proc_steps, success,
                       exp_file_list):
    """Tests get_file_list

    Tests the formatting of file_list to be usedfor client functions is
    formatted correctly given all the correct inputs.

    Input types were guaranteed via GUI user inputs.

    Args:
        filenames (list): list of filenames
        file_ext (str): requested file extension
        proc_steps (list): list of processing steps
        success (list): list of upload success
        exp_file_list (list): list of properly formatted image info
        for download_images

    Returns:
        none
    """
    file_list = get_file_list(filenames, file_ext, proc_steps, success)

    assert file_list == exp_file_list


@pytest.mark.parametrize("w, h, new_w, exp_w, exp_h",
                         [(1024, 1024, 500, 500, 500),
                          (1024, 512, 500, 500, 250),
                          (100, 220, 1000, 455, 1000),
                          (1, 1000, 1000, 1, 1000)])
def test_resize_img_data(w, h, new_w, exp_w, exp_h):
    """Tests resize_img_dim

    Tests whether given a new width, the new height is calculated
    correctly. If new width is smaller than new hegiht, the final
    width is scaled by new width over calculated new height.

    Existing width and height as well as new width are determined
    through image and screen methods that only provide integers so
    type is not tested here.

    Args:
        input (str): string containing image path(s)
        exp_paths (list) : list of expected image path(s) (str)

    Returns:
        none
    """
    final_w, final_h = resize_img_dim(w, h, new_w)

    assert (final_w == exp_w) or (final_h == exp_h) is True


# Good Image 1
img_string = read_img_as_b64("test_gui/test6.tiff")
image_obj = b64_to_image(img_string)
image_to_load = np.asarray(image_obj)
img_to_show1 = Image.fromarray(image_to_load)
# Good Image 2
img_string = read_img_as_b64("test_gui/test7.jpg")
image_obj = b64_to_image(img_string)
image_to_load = np.asarray(image_obj)
img_to_show2 = Image.fromarray(image_to_load)
# Good Image 3
img_string = read_img_as_b64("test_gui/test2.png")
image_obj = b64_to_image(img_string)
image_to_load = np.asarray(image_obj)
img_to_show3 = Image.fromarray(image_to_load)


@pytest.mark.parametrize("img_to_show",
                         # Test good images
                         [(img_to_show1),
                          (img_to_show2),
                          (img_to_show3)])
def test_calc_histograms(img_to_show):
    """Tests calc_histograms

    Tests whether a image is properly split into RGB components
    for a histogram for display.

    img_to_show is assumed to be a valid image based it only ever
    runs if the image was extracted.

    Args:
        img_array (image obj): image object to use

    Returns:
        none
    """
    exp_r = img_to_show.getchannel('R').histogram()
    exp_b = img_to_show.getchannel('B').histogram()
    exp_g = img_to_show.getchannel('G').histogram()
    r, g, b = calc_histograms(img_to_show)

    assert (r == exp_r) or (g == exp_g) or (b == exp_b) is True
