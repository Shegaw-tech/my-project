pip install -r requirements.txt
Community Notices Web App

A lightweight Flask web application for managing and displaying announcements, ads, and community notices. Admins can create, edit, and delete content, with optional image uploads.

Features

Secure admin login with hashed passwords

Admin dashboard for managing notices

Upload images for content

Display content on a public page

Track creator of each notice

Option to hide/unpublish content

Tech Stack

Python 3.x

Flask

SQLite

Jinja2 templates

Werkzeug for password hashing
websi/
│
├─ app.py              # Flask app initialization
├─ models.py           # Database models and functions
├─ admin.py            # Admin routes and content management
├─ auth.py             # Authentication & login_required decorators
├─ templates/          # HTML templates
│   ├─ base.html
│   ├─ index.html
│   └─ admin_dashboard.html
├─ static/             # CSS, JS, image uploads
├─ instance/
│   └─ app.sqlite      # SQLite database
└─ README.md
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
pip install Flask Werkzeug
