from functools import wraps

from flask import abort
from flask_login import current_user, login_required


def role_required(role):
    def decorator(view):
        @wraps(view)
        @login_required
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                abort(403)
            return view(*args, **kwargs)

        return wrapped

    return decorator


admin_required = role_required("admin")
student_required = role_required("student")
tpo_required = role_required("tpo")
