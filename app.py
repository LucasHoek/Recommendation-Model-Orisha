# app.py
from flask import Flask, jsonify, render_template, send_from_directory, abort, request
from pathlib import Path
import os
import logging
import recommender  # the module above

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
@app.route("/customeradvice", methods=["GET"])
def customer_advice():
    salesrep = request.args.get("salesrep")
    if not salesrep:
        return render_template("customeradvice.html", salesrep_id=None, recommendations=[])

    try:
        salesrep_id = int(salesrep)
    except ValueError:
        salesrep_id = None

    recommendations = []
    if salesrep_id is not None:
        try:
            # compute top-5 recommendations for this salesrep id
            recs = recommender.get_recommendations_for_user(salesrep_id, topn=5)
            # recs is list of (item_id, score)
            artifacts = recommender.get_artifacts()
            items_full = artifacts.get("items_full", {})

            # Build a lookup dict: item_id -> metadata dict
            lookup = {}
            if hasattr(items_full, "iterrows"):  # pandas DataFrame
                # try common id column names; adjust if your DF uses different column names
                id_col = None
                for candidate in ("item_id", "id", "itemId", "itemId_str"):
                    if candidate in items_full.columns:
                        id_col = candidate
                        break
                if id_col is None:
                    # fallback: use index as key
                    for idx, row in items_full.iterrows():
                        lookup[str(idx)] = row.to_dict()
                else:
                    for _, row in items_full.iterrows():
                        key = row.get(id_col)
                        if key is None:
                            key = str(row.name)
                        lookup[str(key)] = row.to_dict()
            elif isinstance(items_full, dict):
                # assume keys are item ids
                lookup = {str(k): (v if isinstance(v, dict) else {"title": str(v)}) for k, v in items_full.items()}
            else:
                # unknown format: leave lookup empty
                lookup = {}

            # Build recommendations with item_name and optional description
            recommendations = []
            for item_id, score in recs:
                key = str(item_id)
                meta = lookup.get(key, {})
                name = meta.get("title") or meta.get("name") or meta.get("item_name") or meta.get("title_text") or key
                desc = meta.get("description") or meta.get("desc") or meta.get("summary") or ""
                recommendations.append({
                    "item_id": item_id,
                    "item_name": name,
                    "item_desc": desc,
                    "score": score
                })
        except Exception:
            logging.exception("Failed to compute recommendations for %s", salesrep)
            recommendations = []

    return render_template("customeradvice.html", salesrep_id=salesrep_id, recommendations=recommendations)

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
    logging.info("Starting app; artifacts dir: %s", recommender.ARTIFACTS_DIR)
    app.run(debug=True, port=5000)
