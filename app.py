import os
import secrets

from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)


# ================= DATABASE =================

database_url = os.environ.get("DATABASE_URL")

if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace(
        "postgres://",
        "postgresql+psycopg2://",
        1
    )

elif database_url and database_url.startswith("postgresql://"):
    database_url = database_url.replace(
        "postgresql://",
        "postgresql+psycopg2://",
        1
    )


app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ================= LETTER TABLE =================

class Letter(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    slug = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    )

    pin = db.Column(
        db.String(4),
        nullable=False
    )

    title = db.Column(
        db.Text,
        nullable=False
    )

    message = db.Column(
        db.Text,
        nullable=False
    )


# ================= CREATE TABLE =================

with app.app_context():
    db.create_all()


# ================= HOME =================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# ================= CREATE PAGE =================

@app.route("/create")
def create():

    return render_template(
        "create.html"
    )


# ================= CREATE LETTER =================

@app.post("/api/create")
def create_letter():

    data = request.get_json(
        silent=True
    ) or {}

    pin = data.get(
        "pin",
        ""
    ).strip()

    title = data.get(
        "title",
        ""
    ).strip()

    message = data.get(
        "message",
        ""
    ).strip()


    # Check PIN

    if len(pin) != 4 or not pin.isdigit():

        return jsonify({
            "ok": False,
            "error": "PIN must be exactly 4 digits."
        }), 400


    # Check title/message

    if not title or not message:

        return jsonify({
            "ok": False,
            "error": "Title and message are required."
        }), 400


    # Generate unique link

    slug = secrets.token_urlsafe(
        6
    ).replace(
        "-",
        ""
    ).replace(
        "_",
        ""
    )[:8]


    # Create letter

    letter = Letter(

        slug=slug,

        pin=pin,

        title=title,

        message=message

    )


    db.session.add(
        letter
    )

    db.session.commit()


    return jsonify({

        "ok": True,

        "slug": slug,

        "url": f"/l/{slug}"

    })


# ================= LETTER PAGE =================

@app.route("/l/<slug>")
def letter_page(slug):

    letter = Letter.query.filter_by(
        slug=slug
    ).first()


    if not letter:

        return "Letter not found ❤️", 404


    return render_template(
        "index.html",
        letter_slug=slug
    )


# ================= VERIFY PIN =================

@app.post("/api/verify/<slug>")
def verify_pin(slug):

    data = request.get_json(
        silent=True
    ) or {}


    letter = Letter.query.filter_by(
        slug=slug
    ).first()


    if not letter:

        return jsonify({
            "ok": False
        }), 404


    if data.get("pin") == letter.pin:

        return jsonify({

            "ok": True,

            "title": letter.title,

            "message": letter.message

        })


    return jsonify({
        "ok": False
    })


# ================= RUN =================

if __name__ == "__main__":

    app.run(

        host="0.0.0.0",

        port=5000,

        debug=True

    )