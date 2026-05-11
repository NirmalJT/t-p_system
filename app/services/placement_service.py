from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Application, Company, Interview, Notification, PlacementDrive


def create_drive(form):
    company = Company.query.filter_by(name=form.company_name.data.strip()).first()
    if company is None:
        company = Company(name=form.company_name.data.strip())
        db.session.add(company)
        db.session.flush()

    drive = PlacementDrive(
        company=company,
        role=form.role.data.strip(),
        package=form.package.data.strip(),
        min_cgpa=form.min_cgpa.data,
        department=form.department.data.strip(),
        drive_date=form.drive_date.data,
    )
    db.session.add(drive)
    db.session.commit()
    return drive


def submit_application(student_profile, drive):
    if student_profile.is_placed:
        return False, "Already placed students cannot apply for more drives."
    if not drive.is_open:
        return False, "This placement drive is closed."
    if student_profile.cgpa < drive.min_cgpa or student_profile.department != drive.department:
        return False, "You are not eligible for this drive."
    if Application.query.filter_by(student_id=student_profile.id, drive_id=drive.id).first():
        return False, "You have already applied for this drive."

    application = Application(student=student_profile, drive=drive)
    db.session.add(application)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return False, "You have already applied for this drive."
    return True, "Applied successfully."


def notify(student_user_id, message):
    db.session.add(Notification(student_user_id=student_user_id, message=message))


def set_application_status(application, status, message):
    application.status = status
    notify(application.student.user_id, message)
    db.session.commit()


def approve_application(application):
    set_application_status(
        application,
        "Approved",
        "Congratulations! Your application has been approved.",
    )


def reject_application(application):
    set_application_status(application, "Rejected", "Your application has been rejected.")


def select_application(application):
    application.status = "Selected"
    application.student.is_placed = True
    notify(application.student.user_id, "Congratulations! You have been selected.")
    db.session.commit()


def schedule_interview(application, form):
    interview = Interview(
        application=application,
        interview_date=form.interview_date.data,
        interview_time=form.interview_time.data,
        venue=form.venue.data.strip(),
    )
    db.session.add(interview)
    notify(
        application.student.user_id,
        (
            f"Your interview has been scheduled on {form.interview_date.data} "
            f"at {form.interview_time.data}. Venue: {form.venue.data.strip()}"
        ),
    )
    db.session.commit()
    return interview
