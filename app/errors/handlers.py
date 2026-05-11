from flask import render_template


def forbidden(error):
    return render_template("errors/403.html"), 403


def not_found(error):
    return render_template("errors/404.html"), 404


def server_error(error):
    return render_template("errors/500.html"), 500
