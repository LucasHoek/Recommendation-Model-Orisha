from flask import Flask, jsonify, render_template, send_from_directory, abort
import json
import os
from pathlib import Path

app = Flask(__name__, static_folder="static", template_folder="templates")

DATA_FILE = Path("fillerdata") / "test-data.json"

def load_data():
    try:
        if not DATA_FILE.exists():
            return {}
        with DATA_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

@app.route("/api/data", methods=["GET"])
def get_data():
    return jsonify(load_data())

@app.route("/", methods=["GET"])
def index():
    return render_template("customerlist.html")

@app.route("/customeradvice", methods=["GET"])
def customer_advice():
    return render_template("customeradvice.html")

@app.route("/favicon.ico")
def favicon():
    fav = Path(app.static_folder) / "favicon.ico"
    if fav.exists():
        return send_from_directory(app.static_folder, "favicon.ico")
    return "", 204

@app.route("/static/<path:filename>")
def static_files(filename):
    static_dir = os.path.join(app.root_path, "static")
    full = os.path.join(static_dir, filename)
    if not os.path.exists(full):
        abort(404)
    return send_from_directory(static_dir, filename)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
