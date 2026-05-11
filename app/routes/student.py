from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user

from app.decorators import student_required
from app.extensions import db
from app.forms import EditProfileForm, ResumeUploadForm
from app.models import Application, Interview, Notification, PlacementDrive
from app.services import submit_application, unread_notification_count
from app.utils import save_resume


student_bp = Blueprint("student", __name__)


@student_bp.route("/dashboard")
@student_required
def dashboard():
    unread = unread_notification_count(current_user.id)
    return render_template("student/dashboard.html", unread=unread)


@student_bp.route("/profile")
@student_required
def profile():
    return render_template("student/profile.html", student=current_user.student_profile)


@student_bp.route("/edit-profile", methods=["GET", "POST"])
@student_required
def edit_profile():
    profile = current_user.student_profile
    form = EditProfileForm(obj=profile)
    if form.validate_on_submit():
        profile.full_name = form.full_name.data.strip()
        profile.department = form.department.data.strip()
        profile.cgpa = form.cgpa.data
        profile.phone = form.phone.data.strip() if form.phone.data else None
        db.session.commit()
        flash("Profile updated.", "success")
        return redirect(url_for("student.profile"))
    return render_template("student/edit_profile.html", form=form)


@student_bp.route("/upload-resume", methods=["GET", "POST"])
@student_required
def upload_resume():
    form = ResumeUploadForm()
    if form.validate_on_submit():
        try:
            filename = save_resume(form.resume.data, current_user.student_profile.id)
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template("student/upload_resume.html", form=form)
        current_user.student_profile.resume_filename = filename
        db.session.commit()
        flash("Resume uploaded successfully.", "success")
        return redirect(url_for("student.profile"))
    return render_template("student/upload_resume.html", form=form)


@student_bp.route("/drives")
@student_required
def drives():
    drive_list = PlacementDrive.query.filter_by(is_open=True).order_by(PlacementDrive.created_at.desc()).all()
    applied_drive_ids = {
        app.drive_id for app in Application.query.filter_by(student_id=current_user.student_profile.id).all()
    }
    return render_template("student/drives.html", drives=drive_list, applied_drive_ids=applied_drive_ids)


@student_bp.route("/apply/<int:drive_id>", methods=["POST"])
@student_required
def apply(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    ok, message = submit_application(current_user.student_profile, drive)
    flash(message, "success" if ok else "warning")
    return redirect(url_for("student.drives"))


@student_bp.route("/applications")
@student_required
def applications():
    rows = Application.query.filter_by(student_id=current_user.student_profile.id).order_by(Application.applied_at.desc()).all()
    return render_template("student/applications.html", applications=rows)


@student_bp.route("/notifications")
@student_required
def notifications():
    notes = Notification.query.filter_by(student_user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    unread = [note for note in notes if note.status == "Unread"]
    for note in unread:
        note.status = "Read"
    if unread:
        db.session.commit()
    return render_template("student/notifications.html", notifications=notes)


@student_bp.route("/my-interviews")
@student_required
def my_interviews():
    interviews = (
        Interview.query.join(Application)
        .filter(Application.student_id == current_user.student_profile.id)
        .order_by(Interview.interview_date.desc())
        .all()
    )
    return render_template("student/my_interviews.html", interviews=interviews)
