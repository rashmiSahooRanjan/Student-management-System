# app.py — Flask application factory

import os
from datetime import timedelta
from flask import Flask, redirect, url_for
from dotenv import load_dotenv

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY", "edunova-dev-secret-key-2025")
    app.permanent_session_lifetime = timedelta(hours=8)
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

    from routes.auth    import auth_bp
    from routes.admin   import admin_bp
    from routes.teacher import teacher_bp
    from routes.student import student_bp

    for bp in (auth_bp, admin_bp, teacher_bp, student_bp):
        app.register_blueprint(bp)

    @app.route("/")
    def root():
        return redirect(url_for("auth.login"))

    @app.errorhandler(404)
    def not_found(e):
        from flask import render_template
        return render_template("404.html"), 404

    @app.errorhandler(403)
    def forbidden(e):
        from flask import render_template
        return render_template("403.html"), 403

    with app.app_context():
        try:
            from models.user    import User
            from models.student import Student
            from models.marks   import Marks
            from models.fees    import Fees
            from models.attendance import Attendance

            # 1. Seed demo user accounts (flagged is_demo=True)
            User.seed_admin()

            # 2. Seed demo student records (flagged is_demo=True)
            Student.seed_demo()

            # 3. Seed demo marks / fees / attendance only for demo student_ids
            demo_ids = Student.get_ids(is_demo=True)
            Marks.seed_demo(demo_ids)
            Fees.seed_demo(demo_ids)
            Attendance.seed_demo(demo_ids)

            print("✅  EduNova ready — demo data isolated from real data.")
        except Exception as ex:
            print(f"⚠️   Seed skipped — check MONGO_URI in .env  [{ex}]")

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(
        debug=os.getenv("FLASK_DEBUG", "True") == "True",
        port=int(os.getenv("PORT", 5000)),
        host="0.0.0.0",
    )
