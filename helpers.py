import time
import random
import os

from flask import request

# Folder where all the files uploaded by the users will be stored
USER_FOLDER = './static/users'

# Extensions that the users are allowed to upload
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'csv', 'xlsx', 'xls', 'ppt', 'pptx', 'pdb', 'pub', 'epub', 'mp3', 'mp4', 'mkv', 'mov', 'gif', 'psd', 'rar', 'zip', 'pages', 'key', 'numbers'])

def allowed_file(filename):
    """ Check if the str argument corresponding to a filename is inside the allowed_extensions list """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def uniqueid():
    """ This function generates an unique ID for users"""
    seed = random.getrandbits(24)
    while True:
       yield seed
       seed = random.getrandbits(24)
unique_sequence = uniqueid()


def generateFileTimeList(guest_files=None, user_files=None):
    """ This function generates a list of time elapsed since a file has been created from every file at a given path """
    if (guest_files == None) and (user_files != None):
            # Check the time elapsed since every user file was created
            actualTime = time.time()
            timeList = []
            for file in user_files:
                if file:
                    timeList.append(round((os.stat(os.path.join(USER_FOLDER, request.cookies.get('userID'), file)).st_mtime - actualTime) * -1 / 60))
                else:
                    return False
            return timeList

    elif (user_files == None) and (guest_files != None):
        # Check the time elapsed since every guest file was created
        actualTime = time.time()
        timeList = []
        for file in guest_files:
            if file:
                timeList.append(round((os.stat(os.path.join(USER_FOLDER, request.form.get('id'), file)).st_mtime - actualTime) * -1 / 60))
            else:
                return False
        return timeList

    elif (user_files != None) and (guest_files != None):
        # Check the time elapsed since every user and guest file was created
        actualTime = time.time()

        userAndguest_time = {}
        userAndguest_time["user"] = []
        userAndguest_time["guest"] = []

        for file in user_files:
            userAndguest_time["user"].append(round((os.stat(os.path.join(USER_FOLDER, request.cookies.get('userID'), file)).st_mtime - actualTime) * -1 / 60))
        for file in guest_files:
            userAndguest_time["guest"].append(round((os.stat(os.path.join(USER_FOLDER, request.form.get('id'), file)).st_mtime - actualTime) * -1 / 60))
        return userAndguest_time