# Magic Sender by Marcelo Diaz
# CS50x Harvard final project

from flask import Flask, flash, abort, redirect, render_template, request, session, send_from_directory, make_response
from flask_session import Session
from werkzeug.utils import secure_filename
import datetime

from helpers import uniqueid, unique_sequence, generateFileTimeList, allowed_file, os, time

# Configure application
app = Flask(__name__)

# Folder where all the files uploaded by the users will be stored
USER_FOLDER = './static/users'
app.config['UPLOAD_FOLDER'] = USER_FOLDER

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"

    # Auto delete files that has more than 1 day of time elapsed since upload
    for folder in os.listdir(USER_FOLDER):
        if folder:
            actualTime = time.time()
            # Path for every folder
            folder = os.path.join(USER_FOLDER, folder)
            for file in os.listdir(folder):
                # Path for every file
                file = os.path.join(folder, file)
                if os.stat(file).st_mtime < actualTime - 86400:
                    if os.path.isfile(file):
                        os.remove(file)
    return response


# Configure session to be permanent
app.config['SESSION_TYPE'] = 'filesystem'
app.config["SESSION_PERMANENT"] = True
Session(app)


@app.route("/", methods=["GET", "POST"])
def index():
    """ Main page """
    if request.method == "POST":
        # Check if any file has been sended
        if not request.files.getlist('files[]'):
            abort(400, "Missing File")

        # List of files uploaded by the user
        files_list = request.files.getlist('files[]')

        for file in files_list:
            # Check if the file is valid
            if not allowed_file(file.filename):
                filetype = file.filename.rsplit('.', 1)[1]
                abort(403, filetype.upper() + " Filetype isn't allowed, you can use just upload files with the following extensions: 'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'csv', 'xlsx', 'xls', 'ppt', 'pptx', 'pub', 'epub', 'mp3', 'mp4', 'mkv', 'mov', 'gif'")

        # Check if the user have a upload folder
        if request.cookies.get('userID') not in os.listdir(USER_FOLDER):
            os.mkdir('./static/users/' + request.cookies.get('userID'))

        # List of user files, used to display in page
        user_files = os.listdir(os.path.join(USER_FOLDER, request.cookies.get('userID')))


        if files_list:
            for file in files_list:
                if file:
                    filename = secure_filename(file.filename)
                    # If the file already exits, add a 2 in the name
                    if filename in user_files:
                        filename = filename.rsplit('.', 1)[0] + "(2)" + "." + filename.rsplit('.', 1)[1]
                    file.save(os.path.join(USER_FOLDER,request.cookies.get('userID'),filename))

                    # Update user files including the new one
                    user_files = os.listdir(os.path.join(USER_FOLDER, request.cookies.get('userID')))

            # Check the time elapsed since every user file was created
            timeList = generateFileTimeList(user_files=user_files)

        return render_template("index.html", userid=request.cookies.get('userID'), user_files=user_files, time=timeList)
    else:
        """ GET REQUEST """
        # Check if the user have any user file upload (and cookie)
        try:
            user_files = os.listdir(os.path.join(USER_FOLDER, request.cookies.get('userID')))
        except:
            # Check if the user have a cookie, if not create one
            if not request.cookies.get('userID'):
                resp = app.make_response(render_template('index.html'))
                resp.set_cookie('userID', value=str(next(unique_sequence)), expires=datetime.datetime.now() + datetime.timedelta(days=9999))
                return resp
            else:
                return render_template("index.html")
        else:
            # Check the time elapsed since every user file was created
            timeList = generateFileTimeList(user_files=user_files)

            return render_template("index.html", userid=request.cookies.get('userID'), user_files=user_files, time=timeList)


@app.route('/uploads/<path:file>')
def uploads(file):
    """ This function allows the user to download any file from the server """
    return send_from_directory(USER_FOLDER, file, as_attachment=True)


@app.route('/download', methods=["POST", "GET"])
def download():
    """ This function is invoked when the user inserts an another device ID, in order to display the files uploaded with that ID """
    if request.method == 'POST':
        try:
            # Checking if there's any uploaded file in the id introduced
            guest_files = os.listdir(os.path.join(USER_FOLDER, request.form.get("id")))
        except FileNotFoundError:
            try:
                # If there's no guest_files at the given ID, look for user_files, finally notify the user
                user_files = os.listdir(os.path.join(USER_FOLDER, request.cookies.get('userID')))
            except:
                flash("The id " + request.form.get("id") + " doesn't exits or have no files uploaded.")
                return render_template("index.html")
            else:
                # user_files exists but guest_files don't
                timeList = generateFileTimeList(user_files=user_files)

                flash("The id " + request.form.get("id") + " doesn't exits or have no files uploaded.")
                return render_template("index.html", userid=request.cookies.get('userID'), user_files=user_files, time=timeList)

        # If guest_files exits, next line is executed looking for user_files
        try:
            user_files = os.listdir(os.path.join(USER_FOLDER, request.cookies.get("userID")))
        except:
            timeList = generateFileTimeList(guest_files=guest_files)
            return render_template("index.html", guestid=request.form.get("id"), guest_files=guest_files, time2=timeList)
        else:
            if len(user_files) != 0:
                timeList = generateFileTimeList(user_files=user_files, guest_files=guest_files)
                return render_template("index.html", guestid=request.form.get("id"), userid=request.cookies.get('userID'), guest_files=guest_files, user_files=user_files, time=timeList["user"],time2=timeList["guest"])
            else:
                timeList = generateFileTimeList(guest_files=guest_files)
                return render_template("index.html", guestid=request.form.get("id"), guest_files=guest_files, time2=timeList)

    else:
        try:
            user_files = os.listdir(os.path.join(USER_FOLDER, request.cookies.get("userID")))
        except:
            return redirect("/")
        else:
            # Time elapsed since each user file has been uploaded
            timeList = generateFileTimeList(user_files=user_files)

            return render_template("index.html", guestid=request.form.get("id"), userid=request.cookies.get('userID'), user_files=user_files, time=timeList)

@app.route("/delete/<path:file>", methods=["POST"])
def delete(file):
    """ File deletion requested by user"""
    path = os.path.join(USER_FOLDER, file)
    os.remove(path)
    return redirect("/")


if __name__ == '__main__':
    app.run(host = '0.0.0.0',port=8080, debug=False)
