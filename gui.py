from tkinter import *
from tkinter import ttk
import numpy as np
import io
import base64
from PIL import ImageTk, Image
import requests
import os
import matplotlib
from matplotlib import image as mpimg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

url = "http://127.0.0.1:5000/"


def editing_window():
    """Editing window

    Initial GUI window that lets user enter their information and
    their requested editing steps.

    Args:
        none

        Returns:
        none
    """
    def enter_data():
        """Collect inputted data

        Collects username, image paths, requested image types to send
        to server.

        Args:
            none

        Returns:
            none
        """
        success_label.grid_forget()
        from client import download_images
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
        req_img_type, proc_steps = convert_inputs(entered_img_type,
                                                  entered_1, entered_2,
                                                  entered_3, entered_4)

        orig_images, filenames, success = get_img_data(img_paths)
        print(filenames)
        print(len(orig_images[0]))
        upload_success = upload_to_server(entered_user, orig_images,
                                          filenames, success,
                                          proc_steps)
        success_label.config(text=upload_success)
        success_label.grid(column=1, row=10, sticky=W)
        display_img = BooleanVar()
        display_check = ttk.Checkbutton(root, text='Display images',
                                        variable=display_img,
                                        onvalue=True, offvalue=False,
                                        command=lambda:
                                        display_images(display_img.get(),
                                                       entered_user,
                                                       req_img_type,
                                                       img_paths,
                                                       proc_steps,
                                                       root, filenames,
                                                       orig_images,
                                                       success))
        display_check.grid(column=0, row=11, sticky=W)
        orig_file_list = get_file_list(filenames,
                                       req_img_type,
                                       [True, False, False,
                                        False, False])
        file_list = get_file_list(filenames, req_img_type, proc_steps)
        if upload_success:
            print("ALL UPLOADING DONE")
            download_btn.config(state=NORMAL)
            download_btn.config(command=lambda:
                                download_images(entered_user,
                                                orig_file_list, ''))
            download_btn2.config(state=NORMAL)
            download_btn2.config(command=lambda:
                                 download_images(entered_user,
                                                 file_list, ''))
            zip_msg = ttk.Label(root,
                                text='Multiple files saved as download.zip')
            # if success.count(True) > 1:
            zip_msg.grid(column=0, columnspan=2, row=14, sticky=N)
        return

    # Main window
    root = Tk()
    root.title("Image Editor")
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    root_w = 0.3*screen_w
    root_h = 0.3*screen_h
    root.config(height=root_h, width=root_w)
    x = 0.35*screen_w
    y = 0.35*screen_h
    root.geometry('+%d+%d' % (x, y))

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
    type_dropdown.current(0)
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
                            width=10)
    upload_btn.grid(column=0, row=9, columnspan=2, sticky=N)
    success_label = ttk.Label(root, text='')
    download_btn = Button(root,
                          text='Download original image',
                          state=DISABLED)
    download_btn.grid(column=0, columnspan=2, row=12, sticky=N)
    download_btn2 = Button(root,
                           text='Download processed image(s)',
                           state=DISABLED)
    download_btn2.grid(column=0, columnspan=2, row=13, sticky=N)
    s = ttk.Style()
    s.configure('Button', foreground=[('disabled', 'black')])
    # Show GUI window
    root.mainloop()
    return


def convert_inputs(entered_img_type, entered_1, entered_2, entered_3,
                   entered_4):
    """Converts GUI user input into function inputs

    Gets requested image type and processing steps in the desired format.

    Args:
        entered_img_type (str): selected image type from GUI dropdown
        entered_1 (bool): histogram equalization?
        entered_2 (bool): contrast stretching?
        entered_3 (bool): log compression?
        entered_4 (bool): reverse video?

    Returns:
        req_img_type (str): requested image type
        proc_steps (list): processing steps as a list of booleans
    """
    four_steps = [entered_1, entered_2, entered_3, entered_4]
    if entered_img_type == 'JPEG':
        req_img_type = '.jpg'
    elif entered_img_type == 'PNG':
        req_img_type = '.png'
    elif entered_img_type == 'TIFF':
        req_img_type = '.tiff'
    if not any(four_steps):
        proc_steps = [True, False, False, False, False]
    else:
        proc_steps = [False, entered_1, entered_2, entered_3,
                      entered_4]
    return req_img_type, proc_steps


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
        filenames (list): list of filenames to use. If zip included and
        unzipping successful, this list contains the image filenames, not
        the zip filename. Otherwise, it just states the zip filename.
        success (list): list of booleans denoting successful processing for
        each of the entries in filenames
    """
    from image import read_img_as_b64, unzip
    images = []
    filenames = []
    success = []
    is_zip = [(re.search('.zip', i) or re.search('.ZIP', i)) for i in
              img_paths]
    for i in range(len(img_paths)):
        curr_path = img_paths[i]
        # Check if image exists
        exists = os.path.isfile(curr_path)
        if exists:
            # Append unzipped images one by one
            if is_zip[i]:
                unzipped_images, names, temp_success = unzip(curr_path)
                if temp_success:
                    for j in range(len(unzipped_images)):
                        images.append(unzipped_images[j])
                        filenames.append(names[j])
                        success.append(True)
                else:
                    images.append('')
                    success.append(False)
            # Append non-zipped images normally
            elif curr_path.lower().endswith(('.png', '.jpg', 'jpeg',
                                            '.tiff')):
                """
                img_obj = Image.open(curr_path)
                img_np = np.array(img_obj)
                images.append(img_np)
                """
                images.append(read_img_as_b64(curr_path))
                success.append(True)
                curr_filename = re.split('/', curr_path)[-1]
                filenames.append(curr_filename)
                # img_obj.close()
            # Don't send data if file is not an image
            else:
                images.append('')
                success.append(False)
        # File not found
        else:
            images.append('')
            filenames.append(img_paths[i])
            success.append(False)
    return images, filenames, success


def get_file_list(filenames, file_ext, proc_steps):
    """Gets file list

    This function takes the inputted filenames, requested file ext,
    and requested processing steps.

    Args:
        filenames (list): list of filenames
        file_ext (str): requested file extension
        proc_steps (list): list of processing steps

    Returns:
        file_list (list): list of properly formatted image info
        for download_images
    """
    file_list = []
    for i in range(len(filenames)):
        file_list.append([filenames[i], file_ext, proc_steps])
    return file_list


def upload_to_server(user, images, filenames, success, proc_steps):
    """Posts image to server

    Posts b64 strings to server

    Args:
        user (str): inputted username
        images (list): list of b64 strings
        filenames (list): attached original filenames
        success (list): whether images were successfully obtained
        proc_steps (list): image processing steps to take

    Returns:
        upload_success (str): message to print below upload button
    """
    from client import add_new_user, upload_images
    status_codes = [400]
    list_for_upload = []
    for i in range(len(filenames)):
        list_for_upload.append([filenames[i], images[i], proc_steps])
        print("Filename {} is {}".format(i, filenames[i]))
    add_new_user(user)
    status_codes = upload_images(user, list_for_upload)
    print("Upload status codes:")
    print(status_codes)
    if isinstance(status_codes, list):
        if all([True if i == 200 else False for i in status_codes[0]]):
            upload_success = "Successfully uploaded"
        elif any([True if i == 400 else False for i in status_codes[0]]):
            upload_success = "One or more fields missing"
        else:
            upload_success = "Upload failed for one or more images"
    elif isinstance(status_codes, dict):
        if status_codes["code"] == 200:
            upload_success = "Successfully uploaded"
        elif status_codes["code"] == 400:
            upload_success = status_codes["msg"]
        else:
            upload_success = "Upload failed for one or more images"
    return upload_success


def display_images(run, user, img_type, img_paths, proc_steps, root,
                   filenames, orig_images, success):
    """Display images and histograms in new GUI window

    Converts image arrays to TK objects and displays them in the window.
    Also computes histogram

    Args:
        run (bool): run function or close window
        user (str): username
        img_type (str): image type to show/download
        img_paths (list): list of image paths
        proc_steps (list): list of processing steps
        root (Tk window)
        filenames (list): list of filenames
        orig_images (list): list of uploaded b64 strings
        success (list): whether image extraction was successful

    Returns:
        none
    """
    from image import b64_to_image
    from client import download_images
    global index
    index = 0
    i_row = 0
    if run:
        img_window = Toplevel(root)
        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()
        img_window.config(height=0.75*screen_h, width=0.4*screen_w)
        img_window.title("Image Viewer")
        img_width = round(0.35*screen_h)
        hist_width = round(0.35*screen_h)

        # Initialize Tk labels and frames
        global f_text
        f_text = StringVar()
        f_text.set("Processing ...")
        filename_label = ttk.Label(img_window,
                                   textvariable=f_text)
        filename_label.update()
        filename_label.grid(column=0, row=i_row, columnspan=4,
                            sticky=N)

        i_row += 1
        orig_label = ttk.Label(img_window, text='Original Image')
        orig_label.grid(column=0, row=i_row, columnspan=2,
                        sticky=N)
        new_label = ttk.Label(img_window, text='Processed Image')
        new_label.grid(column=2, row=i_row, columnspan=2,
                       sticky=N)

        i_row += 1
        orig_img_frame = ttk.Frame(img_window, width=img_width,
                                   height=img_width)
        orig_img_frame.grid(column=0, row=i_row, columnspan=2)
        proc_img_frame = ttk.Frame(img_window, width=img_width,
                                   height=img_width)
        proc_img_frame.grid(column=2, row=i_row, columnspan=2)

        i_row += 1
        orig_hist_label = ttk.Label(img_window,
                                    text='Original Image Histogram')
        orig_hist_label.grid(column=0, row=i_row, columnspan=2,
                             sticky=N)
        new_hist_label = ttk.Label(img_window,
                                   text='Processed Image Histogram')
        new_hist_label.grid(column=2, row=i_row, columnspan=2,
                            sticky=N)

        i_row += 1
        orig_hist_frame = ttk.Frame(img_window, width=hist_width,
                                    height=hist_width)
        orig_hist_frame.grid(column=0, row=i_row, columnspan=2)
        proc_hist_frame = ttk.Frame(img_window, width=hist_width,
                                    height=hist_width)
        proc_hist_frame.grid(column=2, row=i_row, columnspan=2)

        # Display
        tk_images = []
        proc_images = []
        orig_img_label = []
        proc_img_label = []
        orig_hist_plots = []
        proc_hist_plots = []
        new_w = img_width

        # Display original and processed images
        for i in range(len(orig_images)):
            image_to_load = []
            proc_img_to_load = []
            # If the image was successfully extracted
            if success[i]:
                image_string = orig_images[i]
                image_obj = b64_to_image(image_string)
                # Load original image
                try:
                    image_to_load = np.asarray(image_obj)
                    img_to_show = Image.fromarray(image_to_load)
                    w = img_to_show.width
                    h = img_to_show.height
                    final_w, final_h = resize_img_dim(w, h, new_w)
                    img_to_show = img_to_show.resize((final_w,
                                                      final_h),
                                                     Image.ANTIALIAS)
                    tk_images.append(ImageTk.PhotoImage(img_to_show))
                    orig_img_label.append(Label(orig_img_frame,
                                                image=tk_images[-1]))
                    orig_img_label[-1].img = tk_images[-1]
                except:
                    tk_images.append('')
                    orig_img_label.append(Label(orig_img_frame,
                                                text='Image not found'))
                # Load processed image
                try:
                    file_list = [[filenames[i], img_type, proc_steps]]
                    print("FILE TO GET IS")
                    print(file_list)
                    img_info, status = download_images(user,
                                                       file_list,
                                                       'none')
                    if isinstance(img_info, dict):
                        img_str = img_info["image"]
                    elif isinstance(img_info, list):
                        img_str = img_info[1]["image"]
                    if isinstance(status, dict):
                        if status["code"] != 200:
                            raise LookupError()
                    else:  # status is an int
                        if status != 200:
                            raise LookupError()
                    proc_img_obj = b64_to_image(img_str)
                    proc_img_to_load = np.asarray(proc_img_obj)
                    img_to_show2 = Image.fromarray(proc_img_to_load)
                    w2 = img_to_show2.width
                    h2 = img_to_show2.height
                    final_w2, final_h2 = resize_img_dim(w2, h2, new_w)
                    img_to_show2 = img_to_show2.resize((final_w,
                                                        final_h),
                                                       Image.ANTIALIAS)
                    proc_images.append(ImageTk.PhotoImage(img_to_show2))
                    proc_img_label.append(Label(proc_img_frame,
                                                image=proc_images[-1]))
                    proc_img_label[-1].img = proc_images[-1]
                except:
                    proc_images.append('')
                    proc_img_label.append(Label
                                          (proc_img_frame,
                                           text='Image not processed'))
            # Image not successfully extracted
            else:
                tk_images.append('')
                orig_img_label.append(Label(orig_img_frame,
                                            text='Image not found'))
                proc_images.append('')
                proc_img_label.append(Label(proc_img_frame,
                                            text='Image not processed'))
            # Compute histograms
            orig_hist_plot = plot_histograms(orig_hist_frame,
                                             image_to_load)
            orig_hist_plots.append(orig_hist_plot)
            proc_hist_plot = plot_histograms(proc_hist_frame,
                                             proc_img_to_load)
            proc_hist_plots.append(proc_hist_plot)

        # Display first original image in slideshow
        if tk_images[index] == '':
            f_text.set("Invalid image".format(filenames[index]))
            orig_img_label[index].grid(column=0, row=2,
                                       ipadx=0.35*img_width,
                                       ipady=0.45*img_width,
                                       sticky=(N, S, E, W))
            orig_hist_plots[index].grid(column=0, row=2,
                                        ipadx=0.35*img_width,
                                        ipady=0.45*img_width,
                                        sticky=(N, S, E, W))
        else:
            f_text.set("Filename: {}".format(filenames[index]))
            filename_label.update()
            orig_img_label[index].grid(column=0, row=2, columnspan=2,
                                       sticky=(N, S, E, W))
            orig_hist_plots[index].grid(column=0, row=2, columnspan=2,
                                        sticky=N)
        # Display first processed image in slideshow
        if proc_images[index] == '':
            proc_img_label[index].grid(column=0, row=2,
                                       ipadx=0.35*img_width,
                                       sticky=(N, S, E, W))
            proc_hist_plots[index].grid(column=0, row=2,
                                        ipadx=0.35*img_width,
                                        sticky=(N, S, E, W))
        else:
            proc_img_label[index].grid(column=0, row=2, columnspan=2,
                                       sticky=(N, S, E, W))
            proc_hist_plots[index].grid(column=0, row=2, columnspan=2,
                                        sticky=N)
        img_window.grid_rowconfigure("all", weight=1)
        img_window.grid_columnconfigure("all", weight=1)

        i_row += 1
        next_btn = ttk.Button(img_window, text='>>',
                              command=lambda: show_next('next',
                                                        tk_images,
                                                        filenames,
                                                        filename_label,
                                                        orig_img_label,
                                                        proc_img_label,
                                                        img_width,
                                                        orig_hist_plots,
                                                        proc_hist_plots,
                                                        hist_width),
                              width=4)
        next_btn.grid(column=1, row=i_row, sticky=E)
        prev_btn = ttk.Button(img_window, text='<<',
                              command=lambda: show_next('prev',
                                                        tk_images,
                                                        filenames,
                                                        filename_label,
                                                        orig_img_label,
                                                        proc_img_label,
                                                        img_width,
                                                        orig_hist_plots,
                                                        proc_hist_plots,
                                                        hist_width),
                              width=4)
        prev_btn.grid(column=0, row=i_row, sticky=W)

    else:
        for widget in root.winfo_children():
            if isinstance(widget, Toplevel):
                widget.destroy()


def resize_img_dim(w, h, new_w):
    """Gets dimensions for resizing input image

    Args:
        w (int): current width of image
        h (int): current height of image
        new_w (int): new width of image

    Returns:
        final_w (int): new width
        final_h (int): new height
    """
    new_h = round(h*new_w/w)
    if new_h <= new_w:
        final_w = new_w
        final_h = new_h
    else:
        final_w = round(new_w*new_w/new_h)
        final_h = new_w

    return final_w, final_h


def show_next(next, images, filenames, filename_label, orig_img_label,
              proc_img_label, img_width, orig_hist_plots,
              proc_hist_plots, hist_width):
    """Image slideshow functionality

    Shows images and histograms for next or previous file on button
    click.

    Args:
        next (str): 'next' or 'prev', depending on the button being
        pressed
        images (list): list of original Tk PhotoImages (empty string
        if image could not be uploaded
        filenames (list): list of image filenames
        filename_label (tk Label): label showing filename
        orig_img_label (tk Label): label showing original image
        proc_img_label (tk Label): label showing processed image
        img_width (int): width of image
        orig_hist_plots (tk Label): label showing histograms for
        original image
        proc_hist_plots (tk Label): label showing histograms for
        processed image
        hist_width (int): width of histogram

    Returns:
        none
    """
    global index
    if next == 'next':
        display_next = index < (len(orig_img_label))-1
    elif next == 'prev':
        display_next = index > 0
    if display_next:
        orig_img_label[index].grid_forget()
        orig_hist_plots[index].grid_forget()
        proc_img_label[index].grid_forget()
        proc_hist_plots[index].grid_forget()
        if next == 'next':
            index += 1
        elif next == 'prev':
            index -= 1
        next_olabel = orig_img_label[index]
        next_plabel = proc_img_label[index]
        next_ohist = orig_hist_plots[index]
        next_phist = proc_hist_plots[index]
        global f_text
        if images[index] != '':
            f_text.set("Filename: {}".format(filenames[index]))
            filename_label.update()
            next_olabel.grid(column=0, row=2, columnspan=2, sticky=E)
            next_ohist.grid(column=0, row=2, columnspan=2, sticky=E)
            next_plabel.grid(column=0, row=2, columnspan=2, sticky=W)
            next_phist.grid(column=0, row=2, columnspan=2, sticky=W)
        else:
            f_text.set("Filename: <>")
            filename_label.update()
            next_olabel.grid(column=0, row=2, columnspan=2,
                             ipadx=0.35*img_width,
                             ipady=0.45*img_width, sticky=E)
            next_ohist.grid(column=0, row=2, columnspan=2,
                            ipadx=0.35*img_width,
                            ipady=0.45*img_width, sticky=E)
            next_plabel.grid(column=0, row=2, columnspan=2,
                             ipadx=0.35*img_width,
                             ipady=0.45*img_width, sticky=W)
            next_phist.grid(column=0, row=2, ipadx=0.35*img_width,
                            ipady=0.45*img_width, columnspan=2,
                            sticky=W)
    return


def plot_histograms(frame, img_array):
    """Creates histogram widget and plots it.

    Converts image arrays to histograms for display

    Args:
        frame (Tk Frame): frame to put histograms of images
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
        r, g, b = calc_histograms(img_to_show)

        frame.update()
        w = frame.winfo_width()
        h = frame.winfo_height()

        plt.figure()
        hist_fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True,
                                                 sharey=False)
        hist_fig.set_tight_layout(True)
        hist_canvas = FigureCanvasTkAgg(hist_fig, master=frame)
        hist_plot = hist_canvas.get_tk_widget()
        # hist_canvas._tkcanvas.bind("<Configure>", hist_dim)
        hist_plot["width"] = 0.98*w
        hist_plot["height"] = 0.98*h
        ax1.set_title("Histograms", fontsize=10)
        ax1.plot(r, 'r')
        ax2.plot(g, 'g')
        ax3.plot(b, 'b')
        plt.xlabel('Intensity')
        ax1.set_ylabel("# red\npixels", fontsize=10)
        ax1.ticklabel_format(axis='y', style='sci', scilimits=(0, 4))
        ax2.set_ylabel("# green\npixels", fontsize=10)
        ax2.ticklabel_format(axis='y', style='sci', scilimits=(0, 4))
        ax3.set_ylabel("# blue\npixels", fontsize=10)
        ax3.ticklabel_format(axis='y', style='sci', scilimits=(0, 4))
        plt.xlabel("Intensity")
        plt.subplots_adjust(wspace=0, hspace=0)
    except:
        hist_plot = Label(frame, text='Histogram not calculated')
    return hist_plot


def calc_histograms(img_to_show):
    """Calculate histograms

    Get R, G, B histogram values from an image.

    Args:
        img_array (image obj): image object to use
    Returns:
        r (list): list of histogram values for red pixels
        g (list): list of histogram values for green pixels
        b (list): list of histogram values for blue pixels
    """
    out_hist = img_to_show.histogram()
    r = out_hist[0:256]
    g = out_hist[256:512]
    b = out_hist[512:768]
    return r, g, b


if __name__ == "__main__":
    editing_window()
