from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user

from app.extensions import db
from app.forms import LoginForm, RegistrationForm
from app.models import StudentProfile, User


auth_bp = Blueprint("auth", __name__)


def redirect_for_role(user):
    if user.role == "admin":
        return redirect(url_for("admin.dashboard"))
    if user.role == "tpo":
        return redirect(url_for("tpo.dashboard"))
    return redirect(url_for("student.dashboard"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect_for_role(current_user)

    form = RegistrationForm()
    if form.validate_on_submit():
        existing = User.query.filter_by(email=form.email.data.lower()).first()
        existing_roll = StudentProfile.query.filter_by(roll_number=form.roll_number.data.strip()).first()
        if existing or existing_roll:
            flash("A student with this email or roll number already exists.", "danger")
            return render_template("auth/register.html", form=form)

        user = User(email=form.email.data.lower(), role="student", is_active=True)
        user.set_password(form.password.data)
        profile = StudentProfile(
            user=user,
            full_name=form.full_name.data.strip(),
            roll_number=form.roll_number.data.strip(),
            department=form.department.data.strip(),
            cgpa=form.cgpa.data,
        )
        db.session.add(profile)
        db.session.commit()
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("auth.student_login"))
    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def student_login():
    return login_by_role("student", "auth/login.html", "Student Login")


@auth_bp.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    return login_by_role("admin", "auth/login.html", "Admin Login")


@auth_bp.route("/tpo-login", methods=["GET", "POST"])
def tpo_login():
    return login_by_role("tpo", "auth/login.html", "TPO Login")


def login_by_role(role, template, title):
    if current_user.is_authenticated:
        return redirect_for_role(current_user)

    form = LoginForm()
    if form.validate_on_submit():
        identifier = form.email_or_username.data.strip()
        user = User.query.filter(
            ((User.email == identifier.lower()) | (User.username == identifier)),
            User.role == role,
        ).first()
        if not user or not user.check_password(form.password.data):
            flash("Invalid credentials.", "danger")
            return render_template(template, form=form, title=title, role=role)
        if not user.is_active:
            flash("This account is disabled.", "danger")
            return render_template(template, form=form, title=title, role=role)

        login_user(user, remember=False)
        request.environ.get("werkzeug.request")
        flash("Logged in successfully.", "success")
        return redirect_for_role(user)

    return render_template(template, form=form, title=title, role=role)


@auth_bp.route("/logout", methods=["POST"])
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.student_login"))
