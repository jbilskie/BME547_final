# user.py
# Author: Kevin Chu
# Last Modified: 4/12/19

from pymodm import MongoModel, fields


class User(MongoModel):
    """ User class

    This class is used to create objects with user-specific
    information that is saved in the MongoDB database.

    Args:
        username (str): user identifier

    Returns:
        User (User object): specific instance of User class

    The objects in the class have the following attributes.

    username (str): user identifier

    actions (list): info about processing steps a user has performed,
    each element contains a dictionary with the name of the processing
    step, the number of times it has been run, and the average latency

    orig_img (list): info about the raw images a user has uploaded,
    each element contains a dictionary with the file name, image file
    (represented as a str) and the time stamp when the file was
    uploaded

    proc_img (list): info aobut the processed images a user has uploaded,
    each element contains a dictionary with the file name, image file
    (represented as a str), the processing step that was performed, and
    the time stamp when the file was uploaded
    """
    username = fields.CharField(primary_key=True)
    actions = fields.ListField()
    orig_img = fields.ListField(blank=True)
    proc_img = fields.ListField(blank=True)
