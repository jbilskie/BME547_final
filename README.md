# BME547_final

[![Build Status](https://travis-ci.com/jbilskie/BME547_final.svg?branch=master)](https://travis-ci.com/jbilskie/BME547_final)

## About
This repository contains programs that use a graphical user interface (GUI) to allow a user to upload images to a server, process the images, download the images, and display the images. A MongoDB database is used to store a user's information along with their uploaded images.

## Instructions
The program can be started by running `python gui.py` in the current directory. This command will open a window (shown below) with options to upload, process, download, and display images. The following list outlines the main functions of the GUI.
1. Username
2. Define Image Paths
3. Processing Images
4. Uploading Images
5. Displaying Images
6. Downloading Images

<img src="https://github.com/jbilskie/BME547_final/blob/master/README/1%20GUI.png" width="400">

### Step 1: Username
In the username field, enter your desired username. You must enter in a non-empty username to upload images to the database. This step creates an account that stores your original and processed images.

<img src="https://github.com/jbilskie/BME547_final/blob/master/README/2%20Username.png" width="400">

### Step 2: Define Image Paths
In the image paths field, enter in the file path(s) for the image(s) you wish to upload. You may upload a single image, list of images, or a zip archive of images as shown in the figures below. 

<img src="https://github.com/jbilskie/BME547_final/blob/master/README/3%20Image%20Paths.png" width="400">
<img src="https://github.com/jbilskie/BME547_final/blob/master/README/4%20Image%20Paths.png" width="400">
<img src="https://github.com/jbilskie/BME547_final/blob/master/README/5%20Image%20Paths.png" width="400">

### Step 3: Processing Images
After entering the image paths, you have the option of applying image processing steps. The processing steps field contains several options for image processing:
* Histogram Equalization (default)
* Contrast Stretching
* Log Compression
* Reverse Video

By default, the histogram equalization box is checked. However, you may select between 0 and all 4 of the processing steps. If you select 0 boxes, then the original image(s) will be uploaded. If you select more than 1 step, the selected processing steps will be applied sequentially. The figure below shows an example where multiple processing steps are selected.

<img src="https://github.com/jbilskie/BME547_final/blob/master/README/7%20Processing%20Steps.png" width="400">

### Step 4: Uploading Images
To upload images to the database, click the 'upload file' button as shown below. This step may take a few minutes depending of the size of the file(s). 

<img src="https://github.com/jbilskie/BME547_final/blob/master/README/8%20Upload.png" width="200">

When finished uploading, the program should display the following window indicating a successful upload.

<img src="https://github.com/jbilskie/BME547_final/blob/master/README/9%20Successfully%20Uploaded.png" width="200">

### Step 5: Displaying Images
After uploading the images, the program will give the option to download and display images. To display the original and process images, check the box labeled 'Display images' as shown below. 

<img src="https://github.com/jbilskie/BME547_final/blob/master/README/10%20GUI.png" width="400">

Once checked, the program opens a new window (see below figures). The top of the window shows the image metadata including the filename, upload time, processing time, and image size. Below the metadata are the original image(s), processed image(s), and their RGB histograms. The histogram shows the distribution of pixel intensities for red, green, and blue color channels.  If you are viewing multiple images, the window is a slideshow that will allow you view one image at a time. You can switch between images by selecting the arrows at the bottom of the window.

<img src="https://github.com/jbilskie/BME547_final/blob/master/readme_images/11%20Slideshow.png" width="600">

<img src="https://github.com/jbilskie/BME547_final/blob/master/readme_images/12%20Slideshow.png" width="600">

### Step 6: Downloading Images
To download image(s), you must first define the file type. You may download the image(s) as one of three file types:
* JPG
* PNG
* TIFF

<img src="https://github.com/jbilskie/BME547_final/blob/master/README/6%20Download%20Type.png" width="400">

To download the original image(s), click the 'Download original image' button as shown in the figure below. You can also download the processed image(s) by clicking the 'Download processed image(s)' button. 

<img src="https://github.com/jbilskie/BME547_final/blob/master/README/13%20Download.png" width="400">

If downloading more than one image, the software will zip the images into a zip archive. This process may take a few minutes. After the download is complete, the following window will appear to indicate a successful download.

<img src="https://github.com/jbilskie/BME547_final/blob/master/README/14%20Successfully%20Downloaded.png" width="400">

The downloaded images will appear in the current directory. Single images are downloaded as image files, and multiple images are downloaded as zip files. The figures below show downloaded zip files for the original and processed images.

Original image(s):

<img src="https://github.com/jbilskie/BME547_final/blob/master/README/15%20Downloaded%20Original%20File.png" width="400">

Processed image(s):

<img src="https://github.com/jbilskie/BME547_final/blob/master/README/16%20Downloaded%20Process%20File.png" width="400">

## Important Files
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
The virtual machine running the server can be found at http://vcm-9111.vm.duke.edu:5000/.
