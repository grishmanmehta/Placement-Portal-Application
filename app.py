from flask import Flask, render_template, request, redirect, url_for
from models import Notification, db, Student, Company, Job, Application, StudentEducation, StudentExperience, StudentProject, StudentActivity
from flask import session
from flask import request
import os
from flask import redirect, request
import smtplib
from email.mime.text import MIMEText
def send_email(to_email, subject, message):

    sender_email = "grishmanmehta@gmail.com"
    sender_password = "twmj kykr zebp jcta"

    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()

    server.login(sender_email, sender_password)

    server.sendmail(sender_email, to_email, msg.as_string())

    server.quit()
app = Flask(__name__)
app.secret_key = "secretkey"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///placement.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


@app.route("/")
def home():
    return redirect("/login")


# -----------------------
# Student Registration
# -----------------------
@app.route("/register/student", methods=["GET","POST"])
def register_student():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        skills = request.form["skills"]
        resume_file = request.files["resume"]

        resume_filename = resume_file.filename

        resume_path = os.path.join("static/resumes", resume_filename)

        resume_file.save(resume_path)

        student = Student(
            name=name,
            email=email,
            password=password,
            skills=skills,
            resume=resume_filename
        )

        db.session.add(student)
        db.session.commit()

        return redirect("/login")

    return render_template("register_student.html")


# -----------------------
# Company Registration
# -----------------------
@app.route("/register/company", methods=["GET","POST"])
def register_company():

    if request.method == "POST":

        name = request.form["name"]
        industry = request.form["industry"]
        email = request.form["email"]
        password = request.form["password"]

        company = Company(
            name=name,
            industry=industry,
            email=email,
            password=password
        )

        db.session.add(company)
        db.session.commit()

        return redirect("/login")

    return render_template("register_company.html")


# -----------------------
# Login
# -----------------------
@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        student = Student.query.filter_by(email=email, password=password).first()
        company = Company.query.filter_by(email=email, password=password).first()

        if student:
            if student.active:
                session["student_id"] = student.id
                return redirect("/student/dashboard")

            else:
                return "Your account has been deactivated by admin."

        elif company:

            if company.approved:
                session["company_id"] = company.id
                return redirect("/company/dashboard")

            else:
                return "Company not approved by admin yet."

        elif email == "admin@portal.com" and password == "admin123":
            return redirect("/admin/dashboard")

        else:
            return "Access Denied"

    return render_template("login.html")


# -----------------------
# Dashboards
# -----------------------
@app.route("/admin/dashboard")
def admin_dashboard():

    students = Student.query.all()
    companies = Company.query.all()
    jobs = Job.query.all()
    applications = Application.query.all()

    total_students = len(students)
    total_companies = len(companies)
    total_jobs = len(jobs)
    total_applications = len(applications)

    return render_template(
        "admin_dashboard.html",
        students=students,
        companies=companies,
        jobs=jobs,
        applications=applications,
        total_students=total_students,
        total_companies=total_companies,
        total_jobs=total_jobs,
        total_applications=total_applications
    )

@app.route("/search_student")
def search_student():

    query = request.args.get("query")

    
    students = Student.query.filter(
        (Student.name.contains(query)) |
        (Student.email.contains(query)) |
        (Student.id.like(f"%{query}%"))
    ).all()

    companies = Company.query.all()
    jobs = Job.query.all()
    applications = Application.query.all()

    return render_template(
        "admin_dashboard.html",
        students=students,
        companies=companies,
        jobs=jobs,
        applications=applications
    )

@app.route("/search_company")
def search_company():

    query = request.args.get("query")

    companies = Company.query.filter(
        (Company.name.contains(query)) |
        (Company.email.contains(query)) |
        (Company.id.like(f"%{query}%"))
    ).all()

    students = Student.query.all()
    jobs = Job.query.all()
    applications = Application.query.all()

    return render_template(
        "admin_dashboard.html",
        students=students,
        companies=companies,
        jobs=jobs,
        applications=applications
    )

@app.route("/search_jobs")
def search_jobs():

    query = request.args.get("query")

    jobs = Job.query.join(Company).filter(
        (Job.title.contains(query)) |
        (Company.name.contains(query))
    ).filter(Job.approved == True).all()

    student_id = session.get("student_id")

    applications = Application.query.filter_by(student_id=student_id).all()

    return render_template(
        "student_dashboard.html",
        jobs=jobs,
        applications=applications
    )

@app.route("/deactivate_student/<int:id>")
def deactivate_student(id):

    student = Student.query.get(id)

    student.active = False

    db.session.commit()

    return redirect("/admin/dashboard")

@app.route("/approve_company/<int:id>")
def approve_company(id):

    company = Company.query.get(id)

    company.approved = True

    db.session.commit()

    return redirect("/admin/dashboard")

@app.route("/reject_company/<int:id>")
def reject_company(id):

    company = Company.query.get(id)
    db.session.delete(company)
    db.session.commit()

    return redirect("/admin/dashboard")

@app.route("/student/dashboard")
def student_dashboard():

    jobs = Job.query.filter_by(approved=True).all()
    applications = Application.query.filter_by(
        student_id=session["student_id"]
    ).all()

    notifications = Notification.query.filter_by(
        student_id=session["student_id"]
    ).order_by(Notification.created_at.desc()).all()
    student_id = session.get("student_id")

    applications = Application.query.filter_by(student_id=student_id).all()

    return render_template(
        "student_dashboard.html",
        jobs=jobs,
        applications=applications
    )
@app.route("/student/profile")
def student_profile():

    student_id = session.get("student_id")

    student = Student.query.get(student_id)

    education = StudentEducation.query.filter_by(student_id=student_id).all()

    experience = StudentExperience.query.filter_by(student_id=student_id).all()

    projects = StudentProject.query.filter_by(student_id=student_id).all()

    activities = StudentActivity.query.filter_by(student_id=student_id).all()

    return render_template(
        "student_profile.html",
        student=student,
        education=education,
        experience=experience,
        projects=projects,
        activities=activities
    )
@app.route("/student/edit_profile", methods=["GET","POST"])
def edit_profile():

    student_id = session.get("student_id")

    student = Student.query.get(student_id)

    if request.method == "POST":

        student.contact = request.form["contact"]
        student.city = request.form["city"]
        student.gender = request.form["gender"]
        student.languages = request.form["languages"]

        db.session.commit()

        return redirect("/student/profile")

    return render_template("edit_profile.html", student=student)

@app.route("/apply_job/<int:job_id>")
def apply_job(job_id):

    student_id = session.get("student_id")

    existing_application = Application.query.filter_by(
        student_id=student_id,
        job_id=job_id
    ).first()

    if existing_application:
        return redirect("/student/dashboard")

    application = Application(
        student_id=student_id,
        job_id=job_id,
        status="Applied"
    )

    db.session.add(application)
    db.session.commit()

    return redirect("/student/dashboard")

@app.route("/add_education", methods=["GET","POST"])
def add_education():

    student_id = session.get("student_id")

    if request.method == "POST":

        level = request.form["level"]
        institution = request.form["institution"]
        start_year = request.form["start_year"]
        end_year = request.form["end_year"]
        degree = request.form["degree"]
        stream = request.form["stream"]
        score = request.form["score"]

        edu = StudentEducation(
            student_id=student_id,
            level=level,
            institution=institution,
            start_year=start_year,
            end_year=end_year,
            degree=degree,
            stream=stream,
            score=score
        )

        db.session.add(edu)
        db.session.commit()

        return redirect("/student/profile")

    return render_template("add_education.html")

@app.route("/add_experience", methods=["GET","POST"])
def add_experience():

    student_id = session.get("student_id")

    if request.method == "POST":

        type = request.form["type"]
        designation = request.form["designation"]
        organization = request.form["organization"]
        location = request.form["location"]
        start_date = request.form["start_date"]
        end_date = request.form["end_date"]
        description = request.form["description"]

        exp = StudentExperience(
            student_id=student_id,
            type=type,
            designation=designation,
            organization=organization,
            location=location,
            start_date=start_date,
            end_date=end_date,
            description=description
        )

        db.session.add(exp)
        db.session.commit()

        return redirect("/student/profile")

    return render_template("add_experience.html")

@app.route("/add_project", methods=["GET","POST"])
def add_project():

    student_id = session.get("student_id")

    if request.method == "POST":

        title = request.form["title"]
        start_month = request.form["start_month"]
        end_month = request.form["end_month"]
        description = request.form["description"]
        link = request.form["link"]

        proj = StudentProject(
            student_id=student_id,
            title=title,
            start_month=start_month,
            end_month=end_month,
            description=description,
            project_link=link
        )

        db.session.add(proj)
        db.session.commit()

        return redirect("/student/profile")

    return render_template("add_project.html")

@app.route("/add_activity", methods=["GET","POST"])
def add_activity():

    student_id = session.get("student_id")

    if request.method == "POST":

        activity = request.form["activity"]

        act = StudentActivity(
            student_id=student_id,
            activity=activity
        )

        db.session.add(act)
        db.session.commit()

        return redirect("/student/profile")

    return render_template("add_activity.html")

@app.route("/update_resume", methods=["GET","POST"])
def update_resume():

    student_id = session.get("student_id")

    student = Student.query.get(student_id)

    if request.method == "POST":

        resume_file = request.files["resume"]

        if resume_file:

            filename = resume_file.filename

            filepath = os.path.join("static/resumes", filename)

            resume_file.save(filepath)

            student.resume = filename

            db.session.commit()

        return redirect("/student/profile")

    return render_template("update_resume.html", student=student)

@app.route("/company/dashboard")
def company_dashboard():

    company_id = session.get("company_id")

    jobs = Job.query.filter_by(company_id=company_id).all()

    return render_template(
        "company_dashboard.html",
        jobs=jobs
    )

@app.route("/create_job", methods=["GET","POST"])
def create_job():

    if request.method == "POST":

        title = request.form["title"]
        description = request.form["description"]
        salary = request.form["salary"]
        deadline = request.form["deadline"]

        company_id = session.get("company_id")

        job = Job(
            title=title,
            description=description,
            salary=salary,
            deadline=deadline,
            company_id=company_id
        )

        db.session.add(job)
        db.session.commit()

        return redirect("/company/dashboard")

    return render_template("create_job.html")

@app.route("/approve_job/<int:id>")
def approve_job(id):

    job = Job.query.get(id)

    job.approved = True

    db.session.commit()

    return redirect("/admin/dashboard")

@app.route("/reject_job/<int:id>")
def reject_job(id):

    job = Job.query.get(id)

    db.session.delete(job)

    db.session.commit()

    return redirect("/admin/dashboard")

@app.route("/view_applications/<int:job_id>")
def view_applications(job_id):

    job = Job.query.get(job_id)

    applications = Application.query.filter_by(job_id=job_id).all()

    return render_template(
        "view_applications.html",
        job=job,
        applications=applications
    )

@app.route("/delete_job/<int:id>")
def delete_job(id):

    job = Job.query.get(id)

    db.session.delete(job)

    db.session.commit()

    return redirect("/company/dashboard")

@app.route("/shortlist/<int:app_id>")
def shortlist(app_id):

    application = Application.query.get(app_id)

    application.status = "Shortlisted"

    db.session.commit()

    send_email(
        application.student.email,
        "Application Update",
        f"You have been shortlisted for {application.job.title} at {application.job.company.name}"
    )

    return redirect(request.referrer)

@app.route("/select/<int:app_id>")
def select(app_id):

    application = Application.query.get(app_id)

    application.status = "Selected"

    db.session.commit()

    send_email(
        application.student.email,
        "Application Update",
        f"Congratulations! You have been selected for {application.job.title} at {application.job.company.name}"
    )

    return redirect(request.referrer)

@app.route("/reject/<int:app_id>")
def reject(app_id):

    application = Application.query.get(app_id)

    application.status = "Rejected"

    db.session.commit()

    send_email(
        application.student.email,
        "Application Update",
        f"Your application for {application.job.title} at {application.job.company.name} was rejected"
    )
    
    return redirect(request.referrer)

@app.route("/search_jobs_student")
def search_jobs_student():

    query = request.args.get("query")

    jobs = Job.query.join(Company).filter(
        (Job.title.contains(query)) |
        (Company.name.contains(query))
    ).filter(Job.approved == True).all()

    applications = Application.query.filter_by(
        student_id=session["student_id"]
    ).all()

    return render_template(
        "student_dashboard.html",
        jobs=jobs,
        applications=applications
    )


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)





