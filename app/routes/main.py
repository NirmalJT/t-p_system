from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user


main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    if current_user.is_authenticated:
        if current_user.role == "admin":
            return redirect(url_for("admin.dashboard"))
        if current_user.role == "tpo":
            return redirect(url_for("tpo.dashboard"))
        return redirect(url_for("student.dashboard"))
    return render_template("auth/home.html")
