from tkinter import *
from tkinter import ttk
import re
from PIL import ImageTk, Image
import zipfile
import requests

url = "http://127.0.0.1:5000/"


def image_window():
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
        print("Requested image type: {}".format(entered_img_type))
        entered_1 = hist_eq.get()
        entered_2 = contr_stretch.get()
        entered_3 = log_comp.get()
        entered_4 = rev_vid.get()
        proc_steps = [entered_1, entered_2, entered_3, entered_4]
        print("Processing steps:")
        print("\tHistogram Equalization: {}".format(entered_1))
        print("\tContrast Stretching: {}".format(entered_2))
        print("\tLog Compression: {}".format(entered_3))
        print("\tReverse Video: {}".format(entered_4))
        # upload_to_server(img_paths, proc_steps)

    # Main window
    root = Tk()
    root.title("Image Editor")

    top_label = ttk.Label(root, text='Edit Your Image On Our Server!')
    top_label.grid(column=0, row=0, columnspan=2, sticky=N)

    # Enter username
    user_label = ttk.Label(root, text="Username:")
    user_label.grid(column=0, row=1, sticky=E)
    user = StringVar()
    user_entry = ttk.Entry(root, textvariable=user)
    user_entry.grid(column=1, row=1, sticky=W)

    # Enter image paths
    img_label = ttk.Label(root, text="Image paths:")
    img_label.grid(column=0, row=2, sticky=E)
    img_path = StringVar()
    img_path_entry = ttk.Entry(root, textvariable=img_path,
                               width=30)
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


def unzip(filename):
    """Searches for '.zip' extension

    Returns Boolean value based on whether input string contains zip

    Args:
        filename (string): image path to unzip

    Returns:
        imgs (list): list containing image data
    """
    imgs = []
    zip_files = zipfile.ZipFile(filename, "r")
    filenames = zip_files.namelist()
    for i in range(len(filenames)):
        file = filenames[i]
        # Ignores garbage files in Mac
        if not re.search('._', file):
            with zip_files.open(file) as new_img:
                im = Image.open(new_img)
                imgs.append(im.load())
    zip_files.close()
    return imgs


if __name__ == "__main__":
    image_window()
