from flask import Flask, render_template, send_from_directory
import os
import secrets
import models
from auth import auth  # your corrected auth blueprint
from admin import admin_bp  # your admin blueprint

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

def allowed_file(filename):
    """Check if a file has an allowed extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", secrets.token_hex(16))
    app.config["UPLOAD_FOLDER"] = os.path.join(app.instance_path, "uploads")
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # ---------------- Database ---------------- #
    models.DB_PATH = os.path.join(app.instance_path, "app.sqlite")
    models.init_db()

    # Create default master admin
    master = models.get_admin_by_username("admin")
    if not master:
        models.create_admin("admin", "admin123", role="master")

    # Register blueprints
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    @app.route("/")
    def index():
        items = models.list_contents()
        return render_template("index.html", items=items)

    @app.route("/uploads/<path:filename>")
    def uploaded_file(filename):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    @app.context_processor
    def inject_helpers():
        return {"allowed_file": allowed_file}

    return app
import models

# ---------------- Run App ---------------- #
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
