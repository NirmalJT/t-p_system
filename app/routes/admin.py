from flask import Blueprint, render_template
from sqlalchemy import func

from app.decorators import admin_required
from app.models import Application, Company, StudentProfile


admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin-dashboard")
@admin_required
def dashboard():
    return render_template(
        "admin/dashboard.html",
        total_students=StudentProfile.query.count(),
        total_companies=Company.query.count(),
        total_applications=Application.query.count(),
    )


@admin_bp.route("/manage-students")
@admin_required
def manage_students():
    students = StudentProfile.query.order_by(StudentProfile.full_name.asc()).all()
    return render_template("admin/manage_students.html", students=students)


@admin_bp.route("/reports")
@admin_required
def reports():
    total_students = StudentProfile.query.count()
    selected_students = Application.query.filter_by(status="Selected").count()
    placement_percentage = round((selected_students / total_students) * 100, 2) if total_students else 0

    department_report = (
        StudentProfile.query.with_entities(StudentProfile.department, func.count(Application.id))
        .join(Application)
        .filter(Application.status == "Selected")
        .group_by(StudentProfile.department)
        .all()
    )
    company_report = (
        Application.query.with_entities(Company.name, func.count(Application.id))
        .join(Application.drive)
        .join(Company)
        .filter(Application.status == "Selected")
        .group_by(Company.name)
        .all()
    )
    return render_template(
        "admin/reports.html",
        total_students=total_students,
        selected_students=selected_students,
        placement_percentage=placement_percentage,
        department_report=department_report,
        company_report=company_report,
    )
