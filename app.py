from flask import Flask, render_template, redirect, url_for, Response, send_from_directory,request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, FileField
from wtforms.validators import DataRequired
import os
import cv2
import face_recognition

app = Flask(__name__)

# Initialize OpenCV face recognition
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
global users_data
users_data = {}  # Dictionary to store user data (name and image)

# Configuration settings
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SECRET_KEY'] = "your_secret_key"
app.config['UPLOAD_FOLDER'] = 'media'  # Location for uploaded media files
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png', 'gif'}

# Create directories if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

video_capture = None

# Define the Student database model
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    studentID = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    roll_no = db.Column(db.String(20), nullable=False)
    class_name = db.Column(db.String(50), nullable=False)
    photo = db.Column(db.String(100), nullable=True)

# Define the form for adding a student
class StudentForm(FlaskForm):
    studentID = StringField('Student ID', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    roll_no = StringField('Roll No', validators=[DataRequired()])
    class_name = StringField('Class', validators=[DataRequired()])
    photo = FileField('Photo')

with app.app_context():
    db.create_all()  # Create the database tables if they don't exist

@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    form = StudentForm()
    if form.validate_on_submit():
        student = Student(
            studentID=form.studentID.data,
            name=form.name.data,
            roll_no=form.roll_no.data,
            class_name=form.class_name.data
        )

        # Handle photo upload
        file = form.photo.data
        if allowed_file(file.filename):
            # Construct a unique filename based on student's name, roll number, and studentID
            filename = f"{form.name.data}_{form.roll_no.data}_{form.studentID.data}.jpg"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            student.photo = filename  # Store the filename in the database

            # Extract face encoding from the uploaded image and add it to users_data
            image = face_recognition.load_image_file(file_path)
            face_encoding = face_recognition.face_encodings(image)[0]  # Assuming there's only one face per image
            users_data[form.name.data] = face_encoding.tolist()

            db.session.add(student)
            db.session.commit()
            return redirect(url_for('students'))

    return render_template('add_student.html', form=form)


def detect_faces():
    global video_capture

    if video_capture is None:
        video_capture = cv2.VideoCapture(0)

    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in faces:
            name = recognize_face(frame[y:y+h, x:x+w])

            # Draw a rectangle around the face
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            if name:
                # Display the recognized name, roll number, and student ID above the face
                cv2.putText(frame, f"Name: {name.split('_')[0]}", (x, y - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                cv2.putText(frame, f"Roll No.: {name.split('_')[1]}", (x, y - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                cv2.putText(frame, f"Student ID: {name.split('_')[2].split('.')[0]}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            else:
                # Display "Unknown" above the face
                cv2.putText(frame, "Unknown", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)


        # Display the video stream
        ret, jpeg = cv2.imencode('.jpg', frame)
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


def recognize_face(face_image):
    rgb_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_image)
    
    if len(face_locations) == 0:
        return None  # No faces found
    
    face_encodings = face_recognition.face_encodings(rgb_image, face_locations)

    for face_encoding in face_encodings:
        for name, known_encoding in users_data.items():
            # Compare the detected face with known faces
            match = face_recognition.compare_faces([known_encoding], face_encoding, tolerance=0.6)
            if match[0]:
                return name  # Return the name of the recognized user

    # If no recognized faces are found, return "Unknown"
    return None

@app.route('/video_feed')
def video_feed():
    return Response(detect_faces(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/delete_student/<int:id>', methods=['POST'])
def delete_student(id):
    student = Student.query.get(id)
    if student:
        if request.method == 'POST':
            # Remove the user data if it exists
            if student.photo in users_data:
                del users_data[student.photo]

            # Check if the student has a photo and delete it from the media folder
            if student.photo:
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], student.photo)
                if os.path.exists(file_path):
                    os.remove(file_path)

            db.session.delete(student)
            db.session.commit()
    return redirect(url_for('students'))

@app.route('/')
def home():
    global video_capture  # Declare the video_capture as a global variable

    if video_capture is not None:
        video_capture.release()  # Release the camera when leaving the / route
        video_capture = None

    return render_template('Home.html')

@app.route('/students')
def students():
    students = Student.query.all()
    return render_template('students.html', students=students)

@app.route('/live')
def live():
    return render_template('video_feed_live.html')

@app.route('/media/<filename>')
def media(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Function to check if a file has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

if __name__ == '__main__':
    # Load known user images from the 'media' folder and create face encodings
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        if allowed_file(filename):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image = face_recognition.load_image_file(file_path)
            face_encoding = face_recognition.face_encodings(image)[0]  # Assuming there's only one face per image
            users_data[filename] = face_encoding.tolist()
    app.run(debug=True, host='0.0.0.0', port=8000)