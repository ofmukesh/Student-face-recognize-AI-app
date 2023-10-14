from flask import Flask, render_template, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, FileField
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

# Configuration settings
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SECRET_KEY'] = "your_secret_key"
app.config['UPLOAD_FOLDER'] = 'media'  # Location for uploaded media files
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png', 'gif'}

db = SQLAlchemy(app)

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

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
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            student.photo = filename  # Store only the filename in the database

            db.session.add(student)
            db.session.commit()
            return redirect(url_for('students'))

    return render_template('add_student.html', form=form)

@app.route('/')
def home():
    return render_template('Home.html')

@app.route('/students')
def students():
    students = Student.query.all()
    return render_template('students.html', students=students)

@app.route('/media/<filename>')
def media(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Function to check if a file has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
