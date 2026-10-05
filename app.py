from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import secrets
import cloudinary
import cloudinary.uploader

app = Flask(__name__)

# =========================
# CLOUDINARY
# =========================

cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
    secure=True
)

# =========================
# DATABASE
# =========================

database_url = os.environ.get("DATABASE_URL")

if database_url:
    if database_url.startswith("postgres://"):
        database_url = database_url.replace(
            "postgres://", "postgresql+psycopg2://", 1
        )
    elif database_url.startswith("postgresql://"):
        database_url = database_url.replace(
            "postgresql://", "postgresql+psycopg2://", 1
        )

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///letters.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# =========================
# LETTER MODEL
# =========================

class Letter(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    slug = db.Column(db.String(20), unique=True, nullable=False)

    pin = db.Column(db.String(4), nullable=False)

    title = db.Column(db.Text, nullable=False)

    message = db.Column(db.Text, nullable=False)

    love_line_1 = db.Column(
        db.Text,
        nullable=False,
        default="I really love you 💓"
    )

    love_line_2 = db.Column(
        db.Text,
        nullable=False,
        default="you are my everything❤️"
    )

    signature = db.Column(
        db.Text,
        nullable=False,
        default="Always yours ❤️"
    )

    song_url = db.Column(
        db.Text,
        nullable=True
    )


# =========================
# DATABASE SETUP + MIGRATION
# =========================

with app.app_context():

    db.create_all()

    try:
        db.session.execute(db.text("""
            ALTER TABLE letter
            ADD COLUMN IF NOT EXISTS love_line_1
            TEXT DEFAULT 'I really love you 💓'
        """))

        db.session.execute(db.text("""
            ALTER TABLE letter
            ADD COLUMN IF NOT EXISTS love_line_2
            TEXT DEFAULT 'you are my everything❤️'
        """))

        db.session.execute(db.text("""
            ALTER TABLE letter
            ADD COLUMN IF NOT EXISTS signature
            TEXT DEFAULT 'Always yours ❤️'
        """))

        db.session.execute(db.text("""
            ALTER TABLE letter
            ADD COLUMN IF NOT EXISTS song_url
            TEXT
        """))

        db.session.commit()

    except Exception as e:
        db.session.rollback()
        print("Database migration error:", e)


# =========================
# HOME
# =========================

@app.route("/")
def home():
    return render_template("create.html")


# =========================
# CREATE PAGE
# =========================

@app.route("/create")
def create_page():
    return render_template("create.html")


# =========================
# CREATE LETTER API
# =========================

@app.route("/api/create", methods=["POST"])
def create_letter():

    pin = str(request.form.get("pin", "")).strip()
    title = str(request.form.get("title", "")).strip()
    message = str(request.form.get("message", "")).strip()

    love_line_1 = str(
        request.form.get(
            "love_line_1",
            "I really love you 💓"
        )
    ).strip()

    love_line_2 = str(
        request.form.get(
            "love_line_2",
            "you are my everything❤️"
        )
    ).strip()

    signature = str(
        request.form.get(
            "signature",
            "Always yours ❤️"
        )
    ).strip()

    # =========================
    # VALIDATION
    # =========================

    if not pin.isdigit() or len(pin) != 4:
        return jsonify({
            "ok": False,
            "error": "PIN must be exactly 4 digits."
        }), 400

    if not title:
        return jsonify({
            "ok": False,
            "error": "Please enter a title."
        }), 400

    if not message:
        return jsonify({
            "ok": False,
            "error": "Please enter a message."
        }), 400

    # =========================
    # SONG UPLOAD
    # =========================

    song_url = None

    song = request.files.get("song")

    if song and song.filename:
        print("SONG RECEIVED:", song.filename)

        try:

            upload_result = cloudinary.uploader.upload(
                song,
                resource_type="video",
                folder="lotus-letter/songs"
            )

            song_url = upload_result.get("secure_url")

        except Exception as e:

            print("Cloudinary upload error:", e)

            return jsonify({
                "ok": False,
                "error": "Song upload failed. Please try again."
            }), 500

    # =========================
    # UNIQUE SLUG
    # =========================

    while True:

        slug = secrets.token_urlsafe(6)

        slug = slug.replace("-", "").replace("_", "")[:8]

        if not Letter.query.filter_by(slug=slug).first():
            break

    # =========================
    # CREATE LETTER
    # =========================

    new_letter = Letter(
        slug=slug,
        pin=pin,
        title=title,
        message=message,
        love_line_1=love_line_1 or "I really love you 💓",
        love_line_2=love_line_2 or "you are my everything❤️",
        signature=signature or "Always yours ❤️",
        song_url=song_url
    )

    db.session.add(new_letter)
    db.session.commit()

    return jsonify({
        "ok": True,
        "slug": slug,
        "url": f"/l/{slug}",
        "preview_url": f"/preview/{slug}"
    })


# =========================
# LETTER PAGE
# =========================

@app.route("/l/<slug>")
def letter_page(slug):

    letter = Letter.query.filter_by(slug=slug).first()

    if not letter:
        return "Letter not found ❤️", 404

    return render_template(
        "index.html",
        letter=letter,
        preview=False
    )


# =========================
# PREVIEW PAGE
# =========================

@app.route("/preview/<slug>")
def preview_letter(slug):

    letter = Letter.query.filter_by(slug=slug).first()

    if not letter:
        return "Letter not found ❤️", 404

    return render_template(
        "index.html",
        letter=letter,
        preview=True
    )


# =========================
# VERIFY PIN
# =========================

@app.route("/api/verify/<slug>", methods=["POST"])
def verify_pin(slug):

    letter = Letter.query.filter_by(slug=slug).first()

    if not letter:
        return jsonify({
            "ok": False,
            "error": "Letter not found."
        }), 404

    data = request.get_json()

    entered_pin = str(
        data.get("pin", "")
    ).strip()
    print("ENTERED PIN:", repr(entered_pin))
print("DATABASE PIN:", repr(letter.pin))

    if entered_pin == letter.pin:

        return jsonify({
            "ok": True,
            "title": letter.title,
            "message": letter.message,
            "love_line_1": letter.love_line_1,
            "love_line_2": letter.love_line_2,
            "signature": letter.signature,
            "song_url": letter.song_url
        })

    return jsonify({
        "ok": False,
        "error": "Wrong PIN."
    })


# =========================
# RUN
# =========================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )