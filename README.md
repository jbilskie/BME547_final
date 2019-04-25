# BME547_final

## About
This repository contains programs that use a graphical user interface (GUI) to upload images to a server, process the images, download the images, and display the images. A MongoDB database is used to store a user's information along with their uploaded images.

## Instructions
### Username
In the username field, enter your desired username. This will allow you to access your images.

### Uploading Images
In the image paths field, enter in the file path(s) for the image(s) you wish to upload. You may upload a single image, list of images, or a zip archive of images. Click "Upload File" to upload the image(s) to the database.

### Processing Images
The processing steps field contains several options for image processing:
* Histogram Equalization (default)
* Contrast Stretching
* Log Compression
* Reverse Video

Select the processing step(s) you wish to apply. Note that you may apply more than one type of processing at a time.

### Downloading Images
You may download the image(s) as one of three file types:
* JPG
* PNG
* TIFF

If downloading more than one image, the software will zip the images into a zip archive.

### Displaying Images
Once uploaded, the GUI gives an option to display the images. Once checked, the program opens a new window containing the original image, processed image, and their histograms. You can select the arrows on the bottom left to view all of the images you have uploaded.

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
