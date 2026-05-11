from flask import Blueprint, flash, redirect, render_template, url_for

from app.decorators import tpo_required
from app.forms import CompanyDriveForm, InterviewForm
from app.models import Application, PlacementDrive
from app.services import (
    approve_application,
    create_drive,
    reject_application,
    schedule_interview,
    select_application,
)


tpo_bp = Blueprint("tpo", __name__)


@tpo_bp.route("/tpo-dashboard")
@tpo_required
def dashboard():
    return render_template(
        "tpo/dashboard.html",
        total_drives=PlacementDrive.query.count(),
        total_applications=Application.query.count(),
    )


@tpo_bp.route("/add-company", methods=["GET", "POST"])
@tpo_required
def add_company():
    form = CompanyDriveForm()
    if form.validate_on_submit():
        create_drive(form)
        flash("Placement drive added successfully.", "success")
        return redirect(url_for("tpo.dashboard"))
    return render_template("company/add_company.html", form=form)


@tpo_bp.route("/view-applications")
@tpo_required
def view_applications():
    applications = Application.query.order_by(Application.applied_at.desc()).all()
    return render_template("tpo/view_applications.html", applications=applications)


@tpo_bp.route("/approve/<int:application_id>", methods=["POST"])
@tpo_required
def approve(application_id):
    application = Application.query.get_or_404(application_id)
    approve_application(application)
    flash("Application approved.", "success")
    return redirect(url_for("tpo.view_applications"))


@tpo_bp.route("/reject/<int:application_id>", methods=["POST"])
@tpo_required
def reject(application_id):
    application = Application.query.get_or_404(application_id)
    reject_application(application)
    flash("Application rejected.", "info")
    return redirect(url_for("tpo.view_applications"))


@tpo_bp.route("/select/<int:application_id>", methods=["POST"])
@tpo_required
def select_student(application_id):
    application = Application.query.get_or_404(application_id)
    select_application(application)
    flash("Student marked as selected.", "success")
    return redirect(url_for("tpo.view_applications"))


@tpo_bp.route("/schedule-interview/<int:application_id>", methods=["GET", "POST"])
@tpo_required
def schedule_interview_view(application_id):
    application = Application.query.get_or_404(application_id)
    form = InterviewForm()
    if form.validate_on_submit():
        schedule_interview(application, form)
        flash("Interview scheduled and notification sent.", "success")
        return redirect(url_for("tpo.view_applications"))
    return render_template("tpo/schedule_interview.html", form=form, application=application)
