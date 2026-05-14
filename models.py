from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# -------------------
# Admin Table
# -------------------
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(200))


# -------------------
# Company Table
# -------------------
class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    industry = db.Column(db.String(100))
    approved = db.Column(db.Boolean, default=False)

    jobs = db.relationship('Job', backref='company')


# -------------------
# Student Table
# -------------------
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    contact = db.Column(db.String(20))
    city = db.Column(db.String(100))
    gender = db.Column(db.String(20))
    languages = db.Column(db.String(200))
    skills = db.Column(db.String(200))
    resume = db.Column(db.String(200))
    active = db.Column(db.Boolean, default=True)

    applications = db.relationship('Application', backref='student')

class StudentEducation(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))

    level = db.Column(db.String(50))  
    # graduation / XII / X / diploma / PhD

    institution = db.Column(db.String(200))

    start_year = db.Column(db.String(10))
    end_year = db.Column(db.String(10))

    degree = db.Column(db.String(100))
    stream = db.Column(db.String(100))

    board = db.Column(db.String(100))

    score = db.Column(db.String(20))

    status = db.Column(db.String(50))

class StudentExperience(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))

    type = db.Column(db.String(20))  
    # job / internship

    designation = db.Column(db.String(100))
    organization = db.Column(db.String(200))
    location = db.Column(db.String(100))

    work_from_home = db.Column(db.Boolean)

    start_date = db.Column(db.String(20))
    end_date = db.Column(db.String(20))

    description = db.Column(db.Text)

class StudentProject(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))

    title = db.Column(db.String(200))

    start_month = db.Column(db.String(20))
    end_month = db.Column(db.String(20))

    description = db.Column(db.Text)

    project_link = db.Column(db.String(200)) 

class StudentActivity(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))

    activity = db.Column(db.Text)

 
# -------------------
# Job / Placement Drive
# -------------------
class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    salary = db.Column(db.Integer)
    deadline = db.Column(db.String(50))

    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    approved = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=True)
    applications = db.relationship('Application', backref='job')


# -------------------
# Application Table
# -------------------
class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'))

    status = db.Column(db.String(50), default="Applied")

class Notification(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))

    message = db.Column(db.String(200))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)