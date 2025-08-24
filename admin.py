from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash, current_app, session
)
import os
from werkzeug.utils import secure_filename

import models
from auth import login_required, master_required

# ------------------- CONFIG -------------------
admin_bp = Blueprint("admin", __name__, template_folder="templates")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


# ------------------- HELPERS -------------------
def _save_upload(file_storage):
    """Save uploaded file securely and ensure unique filename."""
    if not file_storage or file_storage.filename == "":
        return None

    filename = secure_filename(file_storage.filename)
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError("Unsupported file type.")

    upload_dir = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)

    # Ensure unique filename
    base, extdot = os.path.splitext(filename)
    candidate = filename
    i = 1
    while os.path.exists(os.path.join(upload_dir, candidate)):
        candidate = f"{base}_{i}{extdot}"
        i += 1

    path = os.path.join(upload_dir, candidate)
    file_storage.save(path)
    return candidate


# ------------------- DASHBOARD -------------------
@admin_bp.route("/")
@login_required
def dashboard():
    """Render admin dashboard with all content items."""
    items = models.list_contents(include_unpublished=True)
    edit_id = request.args.get("edit")
    edit_item = models.get_content(edit_id) if edit_id else None
    return render_template("admin_dashboard.html", items=items, edit_item=edit_item)


# ------------------- CREATE CONTENT -------------------
@admin_bp.route("/create", methods=["POST"])
@login_required
def create():
    """Create a new content item (admin access)."""
    title = request.form.get("title", "").strip()
    body = request.form.get("body", "").strip()
    is_published = request.form.get("is_published") == "on"
    image = request.files.get("image")

    try:
        image_filename = _save_upload(image) if image else None
        models.create_content(title, body, image_filename, is_published)
        flash("Content created.", "success")
    except ValueError as e:
        flash(str(e), "danger")

    return redirect(url_for("admin.dashboard"))


# ------------------- UPDATE CONTENT (MASTER ONLY) -------------------
@admin_bp.route("/update/<int:item_id>", methods=["POST"])
@login_required
@master_required
def update(item_id):
    """Update an existing content item (master admin only)."""
    title = request.form.get("title", "").strip()
    body = request.form.get("body", "").strip()
    is_published = request.form.get("is_published") == "on"

    image_filename = request.form.get("current_image") or None
    new_image = request.files.get("image")

    if new_image and new_image.filename:
        try:
            image_filename = _save_upload(new_image)
        except ValueError as e:
            flash(str(e), "danger")
            return redirect(url_for("admin.dashboard", edit=item_id))

    models.update_content(item_id, title, body, image_filename, is_published)
    flash("Content updated.", "success")
    return redirect(url_for("admin.dashboard"))


# ------------------- DELETE CONTENT (MASTER ONLY) -------------------
@admin_bp.route("/delete/<int:item_id>", methods=["POST"])
@login_required
@master_required
def delete(item_id):
    """Delete a content item (master admin only)."""
    models.delete_content(item_id)
    flash("Content deleted.", "info")
    return redirect(url_for("admin.dashboard"))
