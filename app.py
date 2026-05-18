# app.py
from flask import Flask, jsonify, render_template, send_from_directory, abort, request
from pathlib import Path
import os
import logging
from recommender import load_artifacts, get_hybrid_topn

artifacts = load_artifacts("artifacts")
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

app = Flask(__name__, static_folder="static", template_folder="templates")

DATA_FILE = Path("fillerdata") / "test-data.json"


def load_data():
    if not DATA_FILE.exists():
        return {}
    import json
    with DATA_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)

@app.route("/api/data", methods=["GET"])
def get_data():
    return jsonify(load_data())

@app.route("/", methods=["GET"])
def index():
    return render_template("customerlist.html")

@app.route("/customeradvice", methods=["GET"])
def customer_advice():
    klantcode = request.args.get("klantcode")
    if not klantcode:
        return "Missing klantcode", 400
    klantcode = int(klantcode)

    results = get_hybrid_topn(
        klantcode,
        topn=5,
        artifacts=artifacts
    )

    print("results =", results)

    return render_template(
        "customeradvice.html",
        klantcode=klantcode,
        results=results
    )

@app.route("/api/customeradvice", methods=["GET"])
def customer_advice_api():
    klantcode = request.args.get("klantcode")
    if not klantcode:
        return {"error": "Missing klantcode"}, 400

    klantcode = int(klantcode)

    results = get_hybrid_topn(
        klantcode,
        topn=5,
        artifacts=artifacts
    )

    return {"klantcode": klantcode, "results": results}


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
