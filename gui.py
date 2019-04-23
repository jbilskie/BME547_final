from tkinter import *
from tkinter import ttk
import numpy as np
from PIL import ImageTk, Image
import requests
import os
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
matplotlib.use("TkAgg")

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
        upload_success = upload_to_server(user, orig_images,
                                          success, proc_steps)
        success_label = ttk.Label(root, text=upload_success)
        success_label.grid(column=1, row=10, sticky=W)
        proc_images = []
        display_img = BooleanVar()
        display_check = ttk.Checkbutton(root, text='Display images',
                                        variable=display_img,
                                        onvalue=True, offvalue=False,
                                        command=lambda:
                                        display_images(display_img.get(),
                                                       root, img_paths,
                                                       orig_images,
                                                       proc_images))
        display_check.grid(column=0, row=11, sticky=W)
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

    instructions = "Separate pathnames with commas."
    instructions_label = ttk.Label(root, text=instructions)
    instructions_label.grid(column=0, row=2, columnspan=2, sticky=N)

    # Enter image paths
    img_label = ttk.Label(root, text="Image paths:")
    img_label.grid(column=0, row=3, sticky=E)
    img_path = StringVar()
    img_path_entry = ttk.Entry(root, textvariable=img_path,
                               width=25)
    img_path_entry.grid(column=1, row=3, sticky=W)

    # Select download image type
    img_type = StringVar()
    type_label = ttk.Label(root, text="Download image type:")
    type_label.grid(column=0, row=4, sticky=E)
    type_dropdown = ttk.Combobox(root, textvariable=img_type)
    type_dropdown['values'] = ('JPEG', 'PNG', 'TIFF')
    type_dropdown.grid(column=1, row=4, sticky=W)
    type_dropdown.config(state='readonly')

    # Check processing steps
    steps_label = ttk.Label(root, text="Processing steps:")
    steps_label.grid(column=0, row=5, sticky=E)

    hist_eq = BooleanVar()
    hist_eq.set(True)
    contr_stretch = BooleanVar()
    log_comp = BooleanVar()
    rev_vid = BooleanVar()

    hist_check = ttk.Checkbutton(root, text='Histogram Equalization',
                                 variable=hist_eq,
                                 onvalue=True, offvalue=False)
    hist_check.grid(column=1, row=5, sticky=W)
    contr_check = ttk.Checkbutton(root, text='Contrast Stretching',
                                  variable=contr_stretch,
                                  onvalue=True, offvalue=False)
    contr_check.grid(column=1, row=6, sticky=W)
    log_check = ttk.Checkbutton(root, text='Log Compression',
                                variable=log_comp,
                                onvalue=True, offvalue=False)
    log_check.grid(column=1, row=7, sticky=W)
    rev_check = ttk.Checkbutton(root, text='Reverse video',
                                variable=rev_vid,
                                onvalue=True, offvalue=False)
    rev_check.grid(column=1, row=8, sticky=W)

    upload_btn = ttk.Button(root, text='Upload file', command=enter_data,
                            width=5)
    upload_btn.grid(column=1, row=9, sticky=W)
    # Show GUI window
    root.mainloop()
    return


def process_img_paths(input):
    """Processes image paths
    If one path is entered, return list of length 1 containing location.
    If multiple (comma-separated) paths are entered, return list containing
    all paths.

    Args:
        input (str): string containing image path(s)

    Returns:
        paths (list): list containing image path, or separated image paths
    """
    input = input.replace(" ", "")
    paths = input.split(",")
    if '' in paths:
        paths.remove("")
    return paths


def get_img_data(img_paths):
    """Gets image data

    Upload: Extracts data from image paths to upload to server as b64
    strings. Unzips images if necessary.
    Download: Unzips downloaded files.

    Args:
        img_paths (list): list of image paths to process

    Returns:
        images (list): list of numpy arrays containing image data
        success (list): list of booleans denoting successful processing for
        each image path entered
    """
    from image import read_img_as_b64, unzip
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
                # img_obj = Image.open(curr_path)
                # img_np = np.array(img_obj)
                # images.append(img_np)
                images.append(read_img_as_b64(curr_path))
                # img_obj.close()
            # Don't send data if file is not an image
            else:
                images.append('')
                success[i] = False
        # File not found
        else:
            images.append('')
            success[i] = False
    return images, success


def upload_to_server(user, images, success, proc_steps):
    """Posts image to server

    Posts b64 strings to server

    Args:
        user (str): inputted username
        images (list): list of b64 strings
        success (list): whether images were successfully obtained
        proc_steps (list): image processing steps to take

    Returns:
        upload_success (str): message to print below upload button
    """
    # from image import image_to_b64
    from client import process_image
    imgs_for_upload = images
    status_codes = [400]
    """
    for img in images:
        try:
            imgs_for_upload.append(image_to_b64(img))
        except:
            imgs_for_upload.append('')
    """
    # status_codes = upload_images(user, imgs_for_upload, proc_steps)
    if all([True if i == 200 else False for i in status_codes]):
        upload_success = "Successfully uploaded"
    elif any([True if i == 400 else False for i in status_codes]):
        upload_success = "One or more fields missing"
    else:
        upload_success = "Upload failed for one or more images"
    return upload_success


def display_images(run, root, img_paths, orig_images, proc_images):
    """Display images and histograms in new GUI window

    Converts image arrays to TK objects and displays them in the window.
    Also computes histogram

    Args:
        run (bool): run function or close window
        root (Tk window)
        img_paths (list): list of image paths
        orig_images (list): list of uploaded b64 strings
        proc_images (list): list of images downloaded from server

    Returns:
        none
    """
    from image import b64_to_image
    global index
    index = 0

    if run:
        img_window = Toplevel(root)
        img_window.config(height=1200, width=1000)
        img_window.title("Image Viewer")
        img_width = 400
        hist_width = 400

        orig_label = ttk.Label(img_window, text='Original Image')
        orig_label.grid(column=0, row=0, columnspan=2, ipady=50, sticky=N)
        new_label = ttk.Label(img_window, text='Processed Image')
        new_label.grid(column=2, row=0, columnspan=2, ipady=50,
                       sticky=N)

        orig_img_frame = ttk.Frame(img_window, width=img_width,
                                   height=img_width)
        orig_img_frame.grid(column=0, row=1, columnspan=2)
        new_img_frame = ttk.Frame(img_window, width=img_width,
                                  height=img_width)
        new_img_frame.grid(column=2, row=1, columnspan=2)

        orig_hist_label = ttk.Label(img_window,
                                    text='Original Image Histogram')
        orig_hist_label.grid(column=0, row=2, columnspan=2, ipady=50,
                             sticky=N)
        new_hist_label = ttk.Label(img_window,
                                   text='Processed Image Histogram')
        new_hist_label.grid(column=2, row=2, columnspan=2, ipady=50,
                            sticky=N)

        orig_hist_frame = ttk.Frame(img_window, width=hist_width,
                                    height=hist_width)
        orig_hist_frame.grid(column=0, row=3, columnspan=2)
        new_hist_frame = ttk.Frame(img_window, width=hist_width,
                                   height=hist_width)
        new_hist_frame.grid(column=2, row=3, columnspan=2)

        right_top_frame = ttk.Frame(img_window, width=0,
                                    height=img_width+50)
        right_top_frame.grid(column=4, row=1)
        right_bott_frame = ttk.Frame(img_window, width=0,
                                     height=hist_width+50)
        right_bott_frame.grid(column=4, row=3)

        tk_images = []
        img_label = []
        hist_plots = []
        hist_canvases = []
        new_w = img_width
        img_row = 0
        for i in range(len(orig_images)):
            image_string = orig_images[i]
            image_to_load = b64_to_image(image_string)
            # Load image
            try:
                img_to_show = Image.fromarray(image_to_load)
                h = img_to_show.height
                w = img_to_show.width
                new_h = round(h*new_w/w)
                if new_h <= img_width:
                    img_to_show = img_to_show.resize((new_w, new_h),
                                                     Image.ANTIALIAS)
                else:
                    new_new_w = round(new_w*img_width/new_h)
                    new_new_h = img_width
                    img_to_show = img_to_show.resize((new_new_w,
                                                      new_new_h),
                                                     Image.ANTIALIAS)
                tk_images.append(ImageTk.PhotoImage(img_to_show))
                img_label.append(Label(orig_img_frame, image=tk_images[-1]))
                img_label[-1].img = tk_images[-1]
            except:
                tk_images.append('')
                img_label.append(Label(orig_img_frame, text='Image not found'))
            # Compute histogram
            hist_plot = plot_histograms(orig_hist_frame, new_hist_frame,
                                        image_to_load)
            hist_plots.append(hist_plot)

        if tk_images[index] == '':
            img_label[index].grid(column=0, row=1, ipadx=0.35*img_width,
                                  ipady=0.35*img_width, sticky=(N, S, E, W))
            hist_plots[index].grid(column=0, row=1, ipadx=0.35*img_width,
                                   ipady=0.35*img_width, sticky=(N, S, E, W))
            img_window.grid_rowconfigure("all", weight=1)
            img_window.grid_columnconfigure("all", weight=1)
        else:
            img_label[index].grid(column=0, row=1, columnspan=2,
                                  sticky=(N, S, E, W))
            hist_plots[index].grid(column=0, row=1, columnspan=2,
                                   sticky=N)
            img_window.grid_rowconfigure("all", weight=1)
            img_window.grid_columnconfigure("all", weight=1)

        next_btn = ttk.Button(img_window, text='>>',
                              command=lambda: show_next(tk_images, img_label,
                                                        img_width, hist_plots,
                                                        hist_width),
                              width=4)
        next_btn.grid(column=1, row=4, sticky=E)
        prev_btn = ttk.Button(img_window, text='<<',
                              command=lambda: show_prev(tk_images, img_label,
                                                        img_width, hist_plots,
                                                        hist_width),
                              width=4)
        prev_btn.grid(column=0, row=4, sticky=W)

    else:
        for widget in root.winfo_children():
            if isinstance(widget, Toplevel):
                widget.destroy()


def show_next(images, img_label, img_width, hist_plots, hist_width):
    global index
    if index < (len(img_label))-1:
        img_label[index].grid_forget()
        hist_plots[index].grid_forget()
        index += 1
        next_label = img_label[index]
        next_hist = hist_plots[index]
        if images[index] != '':
            next_label.grid(column=0, row=1, columnspan=2, sticky=E)
            next_hist.grid(column=0, row=1, columnspan=2, sticky=E)
        else:
            next_label.grid(column=0, row=1, ipadx=0.35*img_width,
                            ipady=0.35*img_width, sticky=E)
            next_hist.grid(column=0, row=1, columnspan=2, sticky=E)
    return


def show_prev(images, img_label, img_width, hist_plots, hist_width):
    global index
    if index > 0:
        img_label[index].grid_forget()
        hist_plots[index].grid_forget()
        index -= 1
        next_label = img_label[index]
        next_hist = hist_plots[index]
        if images[index] != '':
            next_label.grid(column=0, row=1, columnspan=2, sticky=E)
            next_hist.grid(column=0, row=1, columnspan=2, sticky=E)
        else:
            next_label.grid(column=0, row=1, ipadx=0.35*img_width,
                            ipady=0.35*img_width, sticky=E)
            next_hist.grid(column=0, row=1, columnspan=2, sticky=E)
    return


def plot_histograms(orig_hist_frame, new_hist_frame, img_array):
    """Creates histogram widget and plots it.

    Converts image arrays to histograms for display

    Args:
        orig_hist_frame (Tk Frame): frame to put histograms of uploaded
        images
        new_hist_frame (Tk Frame): frame to put histograms of processed
        images
        img_array (np array): np array containing image data

    Returns:
        hist_plots (Widget): histogram widget to implement
    """
    from matplotlib import pyplot as plt
    hist_plots = []
    image_exists = []
    img_label = []

    try:
        img_to_show = Image.fromarray(img_array)
        out_hist = img_to_show.histogram()
        r = out_hist[0:256]
        g = out_hist[256:512]
        b = out_hist[512:768]

        orig_hist_frame.update()
        w = orig_hist_frame.winfo_width()
        h = orig_hist_frame.winfo_height()

        plt.figure()
        hist_fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True,
                                                 sharey=False)
        hist_fig.set_tight_layout(True)
        hist_canvas = FigureCanvasTkAgg(hist_fig, master=orig_hist_frame)
        hist_plot = hist_canvas.get_tk_widget()
        # hist_canvas._tkcanvas.bind("<Configure>", hist_dim)
        hist_plot["width"] = w-50
        hist_plot["height"] = h-50
        ax1.set_title("Histograms", fontsize=10)
        ax1.plot(r, 'r')
        ax2.plot(g, 'g')
        ax3.plot(b, 'b')
        plt.xlabel('Intensity')
        ax1.set_ylabel("# red pixels", fontsize=10)
        ax2.set_ylabel("# green pixels", fontsize=10)
        ax3.set_ylabel("# blue pixels", fontsize=10)
        plt.xlabel("Intensity")
    except:
        hist_plot = Label(orig_hist_frame, text='Histogram not calculated')
    return hist_plot


if __name__ == "__main__":
    editing_window()
