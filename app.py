from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

PIN = "0607"


@app.route("/")
def home():
    return render_template("index.html")


@app.post("/verify")
def verify():
    data = request.get_json(silent=True) or {}

    if data.get("pin") == PIN:
        return jsonify({"ok": True})

    return jsonify({"ok": False})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)