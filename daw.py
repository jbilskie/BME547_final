import base64
import io
from matplotlib import pyplot as plt
import matplotlib.image as mpimg


def read_file_as_b64(image_path):
    """ Converts an image file into a base64 encoded string

    Args:
        image_path: path and name of image file to be encoded

    Returns:
        str:  string of image encoded in base64
    """
    with open(image_path, "rb") as image_file:
        x = image_file.read()
        y = base64.b64encode(x)
        z = str(y, encoding='utf-8')
        return z


def view_image(img):
    """ Shows an image

    Args:
        img: (ndarray) a numpy array containing image data
    """
    plt.imshow(img, interpolation='nearest')
    plt.show()


def decode_b64_string_to_img(base64_string):
    """ Decodes a b64 string into an ndarray containing image data

    The base64_string is decoded and saved as a "bytes" object in the
    image_bytes variable.  Then, the function io.BytesIO takes the bytes
    located in image_bytes and creates a data stream buffer in the image_buf
    variable that is used to simulate an image file.  This image file is then
    interpreted into an ndarray containing image data by matplotlib using the
    mpimg.imread function and stored in the img variable.

    Args:
        base64_string:  a base64 string containing an encoded image

    Returns:
        ndarray:  numpy array containing image data
    """
    image_bytes = base64.b64decode(base64_string)
    image_buf = io.BytesIO(image_bytes)
    img = mpimg.imread(image_buf, format='JPG')
    return img


def transform_image(img):
    """ Performs histogram equalization on an image

    Args:
        img: (ndarray) numpy array containing image to be transformed

    Returns:
        ndarray:  numpy array containing transformed image

    """

    from skimage.exposure import equalize_hist

    proc_img = equalize_hist(img)

    return proc_img


def convert_to_b64_string(img):
    """ Convert ndarray to image bytes

    Using the skimage.io.imsave function, a numpy array containing image data
    is converted into image bytes.  The image bytes are stored in a io.BytesIO
    buffer.  The plugin `pil` is referenced to access the needed image formats.
    The .getvalue() method of the buffer returns the bytes-like
    object.  This bytes-like object can then be converted into a base64
    string.

    Args:
        img: (ndarray) a numpy array containing image data

    Returns:
        str:  base64 string

    """
    from skimage.io import imsave

    f = io.BytesIO()
    imsave(f, img, plugin='pil')
    y = base64.b64encode(f.getvalue())
    z = str(y, encoding='utf-8')

    """ Note, if you wanted to save the buffer into a file, you could do
    so as follows.  
    with open("new_img.jpg", "wb") as out_file:
        out_file.write(f.getvalue())
    """
    return z


def view_b64_image(base64_string):
    """ Decodes a base64 string into an image and shows the image

    The base64_string is decoded and saved as a "bytes" object in the
    image_bytes variable.  Then, the function io.BytesIO takes the bytes
    located in image_bytes and creates a data stream buffer in the image_buf
    variable that is used to simulate an image file.  This image file is then
    interpreted into an image by matplotlib using the mpimg.imread function and
    stored in the i variable.  This i variable is then displayed.

    Args:
        base64_string: a base64 string containing an encoded image
    """
    image_bytes = base64.b64decode(base64_string)
    image_buf = io.BytesIO(image_bytes)
    i = mpimg.imread(image_buf, format='JPG')
    plt.imshow(i, interpolation='nearest')
    plt.show()


def save_image(img):
    """ Save the image using SciPy library

    Args:
        img: image to be saved

    Returns:
        None
    """
    from skimage.io import imsave

    imsave("imsave_file.jpg",img)

    f = io.BytesIO()
    imsave(f, img, plugin='pil')

    with open("new_img.jpg", "wb") as out_file:
        out_file.write(f)


    return f.getvalue()


if __name__ == '__main__':
    b64_string = read_file_as_b64("Sight.JPG")
    # Assume you received the b64_string variable above through a post request
    # First, the b64 string is decoded into an numpy array containing image
    #   data in the next function
    received_img = decode_b64_string_to_img(b64_string)
    # Next, image is viewed to make sure it we received it and decoded it.
    view_image(received_img)
    # Next, the image is transformed
    transformed_img = transform_image(received_img)
    # Next, view the transformed image to make sure it worked.
    view_image(transformed_img)
    # Convert the transformed_img from numpy array to base64 string
    transformed_b64 = convert_to_b64_string(transformed_img)
    # Finally, to ensure this worked, the new base64 string is sent to a
    #  function to view the base 64 string
    view_b64_image(transformed_b64)
