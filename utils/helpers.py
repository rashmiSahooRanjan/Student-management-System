# utils/helpers.py

import os, io, base64
from functools import wraps
from flask import session, redirect, url_for, flash, jsonify, request, render_template


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            if request.is_json or request.path.startswith("/api/") or "/api/" in request.path:
                return jsonify({"error": "Not authenticated"}), 401
            flash("Please login to continue.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if "user_id" not in session:
                return redirect(url_for("auth.login"))
            if session.get("role") not in roles:
                if request.is_json or "/api/" in request.path:
                    return jsonify({"error": "Access denied."}), 403
                return render_template("403.html"), 403
            return f(*args, **kwargs)
        return decorated
    return decorator


ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
