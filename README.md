# BME547_final

[![Build Status](https://travis-ci.com/jbilskie/BME547_final.svg?branch=master)](https://travis-ci.com/jbilskie/BME547_final)

## About
This repository contains programs that use a graphical user interface (GUI) to upload images to a server, process the images, download the images, and display the images. A MongoDB database is used to store a user's information along with their uploaded images.

## Instructions
<img src="https://github.com/jbilskie/BME547_final/blob/master/README/1%20GUI.png" width="400">

### Username
<img src="https://github.com/jbilskie/BME547_final/blob/master/README/2%20Username.png" width="400">

In the username field, enter your desired username. This will allow you to access your images.

### Uploading Images
<img src="https://github.com/jbilskie/BME547_final/blob/master/README/3%20Image%20Paths.png" width="400">
<img src="https://github.com/jbilskie/BME547_final/blob/master/README/4%20Image%20Paths.png" width="400">
<img src="https://github.com/jbilskie/BME547_final/blob/master/README/5%20Image%20Paths.png" width="400">

In the image paths field, enter in the file path(s) for the image(s) you wish to upload. You may upload a single image, list of images, or a zip archive of images. Click "Upload File" to upload the image(s) to the database.

### Processing Images
<img src="https://github.com/jbilskie/BME547_final/blob/master/README/7%20Processing%20Steps.png" width="400">

The processing steps field contains several options for image processing:
* Histogram Equalization (default)
* Contrast Stretching
* Log Compression
* Reverse Video

Select the processing step(s) you wish to apply. Note that you may apply more than one type of processing at a time.

### Uploading Images
<img src="https://github.com/jbilskie/BME547_final/blob/master/README/8%20Upload.png" width="200">

To upload images to the database, click the upload file button. Note that this step may take a few minutes. When finished uploading, the program should display a window indicating a successful upload.

<img src="https://github.com/jbilskie/BME547_final/blob/master/README/9%20Successfully%20Uploaded.png" width="200">

### Displaying Images
After uploading the images, the program will give the option to download and display images.

<img src="https://github.com/jbilskie/BME547_final/blob/master/README/10%20GUI.png" width="400">

To display the original and process images, check the box labeled 'Display images'. Once checked, the program opens a new window containing the original image, processed image, and their histograms. You can select the arrows on the bottom left to view all of the images you have uploaded.

<img src="https://github.com/jbilskie/BME547_final/blob/master/README/11%20Slideshow.png" width="600">

<img src="https://github.com/jbilskie/BME547_final/blob/master/README/12%20Slideshow.png" width="600">

### Downloading Images
<img src="https://github.com/jbilskie/BME547_final/blob/master/README/6%20Download%20Type.png" width="400">

You may download the image(s) as one of three file types:
* JPG
* PNG
* TIFF

If downloading more than one image, the software will zip the images into a zip archive. This process may take a few minutes. After the download is complete, a window will appear to indicate a successful download.
<img src="https://github.com/jbilskie/BME547_final/blob/master/README/14%20Successfully%20Downloaded.png" width="400">

The downloaded images will appear in the current directory. Single images are downloaded as image files, and multiple images are downloaded as zip files.

The downloaded original images will look like

<img src="https://github.com/jbilskie/BME547_final/blob/master/README/15%20Downloaded%20Original%20File.png" width="400">

The downloaded processed images will look like

<img src="https://github.com/jbilskie/BME547_final/blob/master/README/16%20Downloaded%20Process%20File.png" width="400">

## Files
### Python Modules
* `client.py`: runs a client that interacts with a server
* `gui.py`: program to display images, processed images, and histograms
* `image.py`: program that handles conversion between images and base64 strings
* `server.py`: runs a server that interacts with a MongoDB database
* `test_client.py`: contains unit tests for `client.py`
* `test_gui.py`: contains unit tests for `gui.py`
* `test_image.py`: contains unit tests for `image.py`
* `test_server.py`: contains unit tests for `server.py`
* `user.py`: module that contains MongoDB User class

### Miscellaneous
* .gitignore
* .travis.yml
* license.txt
* requirements.txt: run `install -r requirements.txt` to setup virtual environment

## Virtual Machine
