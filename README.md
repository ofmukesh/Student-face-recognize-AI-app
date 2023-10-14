# Student Face Recognition System Documentation

## Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
   - [Prerequisites](#prerequisites)
   - [Installation](#installation)
3. [Usage](#usage)
   - [Adding Students](#adding-students)
   - [Live Face Recognition](#live-face-recognition)
   - [Viewing Students](#viewing-students)
   - [Deleting Students](#deleting-students)
4. [Project Structure](#project-structure)
5. [Contributing](#contributing)
6. [License](#license)

## Introduction
The Student Face Recognition System is a Python application that allows users to manage student information and perform real-time face recognition. The application is built using Flask, OpenCV, and face_recognition library and provides features for adding, viewing, and deleting student records.

## Getting Started

### Prerequisites
Before you can run the Student Face Recognition System, ensure you have the following prerequisites installed:

- Python 3.x
- Flask
- Flask-WTF
- OpenCV (cv2)
- face_recognition library

### Installation
1. Clone the project repository from GitHub.
   ```
   git clone https://github.com/your_username/student-face-recognition.git
   ```

2. Change your working directory to the project folder.
   ```
   cd student-face-recognition
   ```

3. Install the required Python libraries using pip.
   ```
   pip install -r requirements.txt
   ```

## Usage

### Adding Students
1. Run the application by executing `app.py`.
   ```
   python app.py
   ```

2. Access the web interface via a web browser (e.g., http://localhost:8000).
   - Click on the "Add Student" link.
   - Fill in the student's information, including Student ID, Name, Roll No, and Class.
   - Upload a photo of the student.
   - Click the "Add Student" button to save the student's information.

### Live Face Recognition
- Click on the "Live Page" link to access the live face recognition page.
- The application will automatically detect and recognize faces from your webcam feed.
- Recognized students' names will be displayed in the console.

### Viewing Students
- Click on the "View Students" link to see the list of added students.
- The students' details, including Student ID, Name, Roll No, Class, and photos, will be displayed.

### Deleting Students
- In the "View Students" page, each student's entry will have a "Delete" button.
- Click the "Delete" button to remove a student from the database.
- The student's photo will also be deleted from the media folder.

## Project Structure
- **app.py**: The main application script.
- **templates/**: HTML templates used for rendering web pages.
- **media/**: Directory to store uploaded student photos.
- **known_faces/**: Directory to store known faces for face recognition.
- **requirements.txt**: Lists the required Python packages.

## Contributing
Contributions to this project are welcome. To contribute, follow these steps:
1. Fork the repository on GitHub.
2. Create a new branch for your feature or bug fix.
3. Make your changes and test them.
4. Create a pull request to the original repository.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

Feel free to customize and expand this documentation to fit your project's specific needs. Documenting your project helps both users and potential contributors understand and engage with your work more effectively.