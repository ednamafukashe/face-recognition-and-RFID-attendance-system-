from flask import Flask,render_template,flash ,redirect,request,url_for,session,logging
from flask_mysqldb import MySQL
import MySQLdb
from wtforms import Form, StringField,TextAreaField,PasswordField,validators
from passlib.handlers.sha2_crypt import sha256_crypt
from passlib.apps import custom_app_context as pwd_context
#from passlib.hash import 
#from passlib.hash import sha256_crypt
from functools import wraps
import serial
import face_recognition
import cv2
import numpy as np
import time


app = Flask(__name__)



#configMYSQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ""
app.config['MYSQL_DB'] = 'myflaskdb'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# init MYSQL
mysql = MySQL(app)


device = 'COM6' #this will have to be changed to the serial port you are using

#Students = Students()

@app.route('/')
def index():
    return  render_template('home.html')

@app.route('/newpage')
def newpage():
    msg = 'Please stand directly infront of the Camera'
    return  render_template('attendance.html', msg=msg)       

@app.route('/attendance')
def about():
    video_capture = cv2.VideoCapture(0)


    imgGamu = face_recognition.load_image_file('gamu.jpg')
    imgGamu_encoding = face_recognition.face_encodings(imgGamu)[0]

    imgEdna = face_recognition.load_image_file('edna.jpg')
    imgEdna_encoding = face_recognition.face_encodings(imgEdna)[0]

    imgMasimba = face_recognition.load_image_file('masimba.jpg')
    imgMasimba_encoding = face_recognition.face_encodings(imgMasimba)[0]

    imgAziz = face_recognition.load_image_file('Aziz.jpeg')
    imgAziz_encoding = face_recognition.face_encodings(imgAziz)[0]

    imgAysa = face_recognition.load_image_file('Aysa.jpeg')
    imgAysa_encoding = face_recognition.face_encodings(imgAysa)[0]

    imgResa = face_recognition.load_image_file('Resa.jpeg')
    imgResa_encoding = face_recognition.face_encodings(imgResa)[0]




# Create arrays of known face encodings and their names
    known_face_encodings = [
        imgGamu_encoding,
        imgEdna_encoding,
        imgAziz_encoding,
        imgMasimba_encoding,
        imgAysa_encoding,
        imgResa_encoding,
    
]
    known_face_names = [
        "Gamu",
        "Edna",
        "Aziz",
        "Masimba",
        "Aysa",
        "Resa",
    
    
]

# Initialize some variables
    face_locations = []
    face_encodings = []
    face_names = []
    process_this_frame = True

    while True:
    # Grab a single frame of video
        ret, frame = video_capture.read()

    # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]

    # Only process every other frame of video to save time
        if process_this_frame:
        # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_names = []
            for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"

            # # If a match was found in known_face_encodings, just use the first one.
            # if True in matches:
            #     first_match_index = matches.index(True)
            #     name = known_face_names[first_match_index]

            # Or instead, use the known face with the smallest distance to the new face
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]

                face_names.append(name)
       
        process_this_frame = not process_this_frame


    # Display the results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

        # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
          
    # Display the resulting image
        qa = cv2.imshow('Video', frame)

    
    # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Release handle to the webcam

    return  render_template('attendance.html')

@app.route('/camera')
def camera():
    key = cv2. waitKey(1)
    webcam = cv2.VideoCapture(0)
    time.sleep(2)
    while True:
        try:
            check, frame = webcam.read()
         #prints true as long as the webcam is running
         #prints matrix values of each framecd 
            cv2.imshow("Capturing", frame)
            key = cv2.waitKey(1)
            if key == ord('s'): 
                cv2.imwrite(filename='saved_img.jpg', img=frame)
                webcam.release()
                img_ = cv2.imread('saved_img.jpg', cv2.IMREAD_ANYCOLOR)
                gray = cv2.cvtColor(img_, cv2.COLOR_BGR2GRAY)
                img_ = cv2.resize(gray,(28,28))
                img_resized = cv2.imwrite(filename='/templates/saved_img-final.jpg', img=img_)            
                break
        
            elif key == ord('q'):
                webcam.release()
                cv2.destroyAllWindows()
                break
    
        except(KeyboardInterrupt):
            webcam.release()
            cv2.destroyAllWindows()
            break

    return  render_template('camera.html')

@app.route('/students')
def students():
    # Create cursor
    cur = mysql.connection.cursor()

    # Get students
    result = cur.execute("SELECT * FROM students")
    # Show students only from the user logged in 
   # result = cur.execute("SELECT * FROM students WHERE department = %s", [session['username']])

    students = cur.fetchall()

    if result > 0:
        return render_template('students.html', students=students)
    else:
        msg = 'No Students Found'
        return render_template('students.html', msg=msg)
    # Close connection
    cur.close()

@app.route('/student/<string:id>/')
def student(id):
    return  render_template('students.html',id=id)

#Register Form Class
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password') 

# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # Create cursor
        cur = mysql.connection.cursor()

        # Execute query
        cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('You are now registered and can log in', 'success')

        return redirect(url_for('login'))
    return render_template('register.html', form=form)


# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']

        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['password']

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            # Close connection
            cur.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')

 # Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

# Logout
@app.route('/logout')
@is_logged_in
#@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    # Create cursor
    cur = mysql.connection.cursor()

    # Get students
    result = cur.execute("SELECT * FROM students")
    # Show students only from the user logged in 
   # result = cur.execute("SELECT * FROM students WHERE department = %s", [session['username']])

    students = cur.fetchall()

    if result > 0:
        return render_template('dashboard.html', students=students)
    else:
        msg = 'No Students Found'
        return render_template('dashboard.html', msg=msg)
    # Close connection
    cur.close()


 # Student Form Class
class StudentForm(Form):
    id= StringField('id', [validators.Length(min=1, max=10)])
    name = StringField('name', [validators.Length(min=1, max=50)])
    surname = StringField('surname', [validators.Length(min=1, max=50)])
    department = StringField('department', [validators.Length(min=1, max=100)])
    datelog = StringField('datelog', [validators.Length(min=1, max=100)])


# Add Student
@app.route('/add_student', methods=['GET', 'POST'])
@is_logged_in
def add_student():
    form = StudentForm(request.form)
    if request.method == 'POST' and form.validate():
        id = form.id.data
        name = form.name.data
        surname = form.surname.data
        department = form.department.data
        card = index1()

        # Create Cursor
        cur = mysql.connection.cursor()

        # Execute
        cur.execute("INSERT INTO students(id, name, surname,department ,card) VALUES(%s, %s, %s, %s,%s)",(id, name, surname, department, card))

        # Commit to DB
        mysql.connection.commit()

        #Close connection
        cur.close()

        flash('Student Created', 'success')

        return redirect(url_for('dashboard'))

    return render_template('add_student.html', form=form)

      # Edit Student
@app.route('/edit_student/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_student(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Get student by id
    cur.execute("SELECT * FROM students WHERE id = %s", [id])

    student = cur.fetchone()
    cur.close()
    # Get form
    form = StudentForm(request.form)

    # Populate student form fields
    form.id.data = student['id']
    form.name.data = student['name']
    form.surname.data = student['surname']
    form.department.data = student['department']
      

    if request.method == 'POST' and form.validate():
        id = request.form['id']
        name = request.form['name']
        surname = request.form['surname']
        department = request.form['department']

        # Create Cursor
        cur = mysql.connection.cursor()
        #app.logger.info(name)
        # Execute
        cur.execute ("UPDATE students SET id=%s, name=%s, surname=%s, department=%s WHERE id=%s",(id, name, surname, department, id))
        # Commit to DB
        mysql.connection.commit()

        #Close connection
        cur.close()

        flash('Student Updated', 'success')

        return redirect(url_for('dashboard'))

    return render_template('edit_student.html', form=form)


 # Delete Student
@app.route('/delete_student/<string:id>', methods=['POST'])
@is_logged_in
def delete_student(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Execute
    cur.execute("DELETE FROM students WHERE id = %s", [id])

    # Commit to DB
    mysql.connection.commit()

    #Close connection
    cur.close()

    flash('Student Deleted', 'success')

    return redirect(url_for('dashboard'))

@app.route("/")
def index1():
        arduino = serial.Serial(device, 9600)
        while True:
                time.sleep(1)
                data = arduino.readline()
                card = data.split()
                return (card)

@app.route('/logs')
def index2():
    try:
        cur = mysql.connection.cursor()
        car = index1()
        cur.execute("INSERT INTO logs1 SELECT * FROM students WHERE card=(%s)",(car))
        mysql.connection.commit()
        res = cur.execute("SELECT * FROM logs1")
        students = cur.fetchall()
        if res > 0:
            return render_template('logs.html', students=students) 
        else:
            msg = 'Student not registered'
            return render_template('logs.html',  msg=msg, students=students)

    except MySQLdb.IntegrityError:
        msg = 'Card already exists'
        mysql.connection.commit()
        res = cur.execute("SELECT * FROM logs1")
        students = cur.fetchall()
        return render_template('logs.html', msg = msg, students=students)     
    cur.close()

@app.route('/srender')
def render():       
    msg = 'Please press the Scan Button and Tap your card on the Receiver'
    return render_template('logs.html', msg = msg)

if __name__ == "__main__":
    app.secret_key='secret123'
    app.run(debug=True)
