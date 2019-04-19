from tkinter import *
from tkinter import ttk
import numpy as np
from PIL import ImageTk, Image
import requests
import os

url = "http://127.0.0.1:5000/"


def editing_window():
    def enter_data():
        """Collect inputted data

        Collects username, image paths, requested image types to send
        to server.

        Args:
            none

        Returns:
            none
        """
        entered_user = user.get()
        print("User: {}".format(entered_user))
        entered_img_paths = img_path.get()
        img_paths = process_img_paths(entered_img_paths)
        print("Image paths:")
        for i in img_paths:
            print("\t{}".format(i))
        entered_img_type = img_type.get()
        entered_1 = hist_eq.get()
        entered_2 = contr_stretch.get()
        entered_3 = log_comp.get()
        entered_4 = rev_vid.get()
        proc_steps = [entered_1, entered_2, entered_3, entered_4]
        orig_images, success = get_img_data(img_paths)
        img_window = Toplevel(root)
        img_window.title("Image Viewer")
        upload_success = upload_to_server(user, orig_images,
                                          success, proc_steps)
        success_label = ttk.Label(root, text=upload_success)
        success_label.grid(column=1, row=9, sticky=W)
        proc_images = []
        display_images(img_window, img_paths, orig_images,
                       proc_images)
        return

    # Main window
    root = Tk()
    root.title("Image Editor")

    top_label = ttk.Label(root, text='Edit Your Image On Our Server!')
    top_label.grid(column=0, row=0, columnspan=2, sticky=N)

    # Enter username
    user_label = ttk.Label(root, text="Username:")
    user_label.grid(column=0, row=1, sticky=E)
    user = StringVar()
    user_entry = ttk.Entry(root, textvariable=user, width=25)
    user_entry.grid(column=1, row=1, sticky=W)

    # Enter image paths
    img_label = ttk.Label(root, text="Image paths:")
    img_label.grid(column=0, row=2, sticky=E)
    img_path = StringVar()
    img_path_entry = ttk.Entry(root, textvariable=img_path,
                               width=25)
    img_path_entry.grid(column=1, row=2, sticky=W)

    # Check processing steps
    steps_label = ttk.Label(root, text="Processing steps:")
    steps_label.grid(column=0, row=4, sticky=E)

    hist_eq = BooleanVar()
    hist_eq.set(True)
    contr_stretch = BooleanVar()
    log_comp = BooleanVar()
    rev_vid = BooleanVar()

    hist_check = ttk.Checkbutton(root, text='Histogram Equalization',
                                 variable=hist_eq,
                                 onvalue=True, offvalue=False)
    hist_check.grid(column=1, row=4, sticky=W)
    contr_check = ttk.Checkbutton(root, text='Contrast Stretching',
                                  variable=contr_stretch,
                                  onvalue=True, offvalue=False)
    contr_check.grid(column=1, row=5, sticky=W)
    log_check = ttk.Checkbutton(root, text='Log Compression',
                                variable=log_comp,
                                onvalue=True, offvalue=False)
    log_check.grid(column=1, row=6, sticky=W)
    rev_check = ttk.Checkbutton(root, text='Reverse video',
                                variable=rev_vid,
                                onvalue=True, offvalue=False)
    rev_check.grid(column=1, row=7, sticky=W)

    display_img = StringVar()
    display_check = ttk.Checkbutton(root, text='Display images',
                                    variable=display_img,
                                    onvalue=True, offvalue=False)

    # Select download image type
    img_type = StringVar()
    type_label = ttk.Label(root, text="Download image type:")
    type_label.grid(column=0, row=3, sticky=E)
    type_dropdown = ttk.Combobox(root, textvariable=img_type)
    type_dropdown['values'] = ('JPEG', 'PNG', 'TIFF')
    type_dropdown.grid(column=1, row=3, sticky=W)
    type_dropdown.config(state='readonly')

    upload_btn = ttk.Button(root, text='Upload file', command=enter_data,
                            width=5)
    upload_btn.grid(column=1, row=8, sticky=W)
    global img_row
    img_row = 9
    # Show GUI window
    root.mainloop()
    return


def process_img_paths(input):
    """Processes image paths
    If one path is entered, return list of length 1 containing location.
    If multiple (comma-separated) paths are entered, return list containing
    all paths.

    Args:
        input (string): string containing image path(s)

    Returns:
        paths (list): list containing image path, or separated image paths
    """
    paths = input.split(",")
    paths = [i.strip(" ") for i in paths]
    return paths


def get_img_data(img_paths):
    """Gets image data

    Upload: Extracts data from image paths to upload to server as numpy
    arrays (later converted to strings). Unzips images if necessary.
    Download: Unzips downloaded files.

    Args:
        img_paths (list): list of image paths to process

    Returns:
        images (list): list of numpy arrays containing image data
        success (list): list of booleans denoting successful processing for
        each image path entered
    """
    from image import image_to_b64, unzip
    images = []
    success = [True for i in img_paths]
    is_zip = [(re.search('.zip', i) or re.search('.ZIP', i)) for i in
              img_paths]
    for i in range(len(img_paths)):
        curr_path = img_paths[i]
        exists = os.path.isfile(curr_path)
        if exists:
            # Append unzipped images one by one
            if is_zip[i]:
                unzipped_images, success[i] = unzip(curr_path)
                if success[i]:
                    for j in unzipped_images:
                        images.append(j)
                else:
                    images.append('')
            # Append non-zipped images normally
            elif curr_path.lower().endswith(('.png', '.jpg', 'jpeg',
                                            '.tiff')):
                img_obj = Image.open(curr_path)
                img_np = np.array(img_obj)
                images.append(img_np)
                img_obj.close()
            # Don't send data if file is not an image
            else:
                images.append('')
                success[i] = False
        # File not found
        else:
            images.append('')
            success[i] = False
    print("Image successfully extracted?")
    print(success)
    return images, success


def upload_to_server(user, images, success, proc_steps):
    """Posts image to server

    Converts image objects to b64 strings and posts them to server

    Args:
        user (string): inputted username
        images (list): list of np array images
        success (list): whether images were successfully obtained
        proc_steps (list): image processing steps to take

    Returns:
        upload_success (str): message to print below upload button
    """
    from image import image_to_b64
    from client import process_image
    imgs_for_upload = []
    for img in images:
        try:
            imgs_for_upload.append(image_to_b64(img))
        except:
            imgs_for_upload.append('')
    # status = process_image(user, imgs_for_upload, proc_steps)
    status = 0
    if status == 200:
        upload_success = "Successfully uploaded"
    elif status == 400:
        upload_success = "One or more fields missing"
    else:
        upload_success = "Upload failed"
    return upload_success


def display_images(img_window, img_paths, orig_images, proc_images):
    """Display images in GUI window

    Converts image arrays to TK objects and displays them in the window

    Args:
        img_window (Tk window): image display window
        img_paths (list): list of image paths
        orig_images (list): list of uploaded np array images
        proc_images (list): list of images downloaded from server

    Returns:
        none
    """
    orig_label = ttk.Label(img_window, text='Original Images')
    orig_label.grid(column=0, row=0, sticky=N)
    new_label = ttk.Label(img_window, text='Processed Images')
    new_label.grid(column=1, row=0, sticky=N)

    orig_img_frame = ttk.Frame(img_window, width=300)
    orig_img_frame.grid(column=0, row=1)
    new_img_frame = ttk.Frame(img_window, width=300)
    new_img_frame.grid(column=1, row=1)

    tk_images = []
    img_label = []
    new_w = 300
    img_row = 0
    for i in range(len(orig_images)):
        image_to_load = orig_images[i]
        try:
            img_to_show = Image.fromarray(image_to_load)
            h = img_to_show.height
            w = img_to_show.width
            new_h = round(h*new_w/w)
            img_to_show = img_to_show.resize((new_w, new_h), Image.ANTIALIAS)
            tk_images.append(ImageTk.PhotoImage(img_to_show))
            img_label.append(Label(orig_img_frame, image=tk_images[-1]))
            img_label[-1].img = tk_images[-1]
            img_label[-1].grid(column=0, row=img_row)
            img_row += 1
        except:
            img_label.append(Label(orig_img_frame, text='Image not found'))
            img_label[-1].grid(column=0, row=img_row, pady=20)
            img_label[-1]
            img_row += 1


if __name__ == "__main__":
    editing_window()
