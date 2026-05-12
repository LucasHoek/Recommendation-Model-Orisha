import os
import joblib
import numpy as np
from scipy import sparse
from sklearn.metrics.pairwise import linear_kernel
import onnxruntime as ort


# ---------------------------------------------------------
# Load all artifacts (ONCE at startup)
# ---------------------------------------------------------
def load_artifacts(artifacts_dir, onnx_providers=None):
    if onnx_providers is None:
        onnx_providers = ["CPUExecutionProvider"]

    # Encoders & data
    print("Loading user_encoder")
    user_encoder = joblib.load(os.path.join(artifacts_dir, "user_encoder.joblib"))
    print("Loading item_encoder")
    item_encoder = joblib.load(os.path.join(artifacts_dir, "item_encoder.joblib"))
    print("Loading interactions_df")
    interactions_df = joblib.load(os.path.join(artifacts_dir, "interactions_df.joblib"))
    print("Loading item_meta")
    item_meta = joblib.load(os.path.join(artifacts_dir, "item_meta.joblib"))
    tfidf = joblib.load(os.path.join(artifacts_dir, "tfidf_vectorizer.joblib"))
    tfidf_matrix = sparse.load_npz(os.path.join(artifacts_dir, "tfidf_matrix.npz"))

    # ONNX model
    cf_model = None
    onnx_path_file = os.path.join(artifacts_dir, "ncf_model_path.joblib")

    if os.path.exists(onnx_path_file):
        onnx_path = joblib.load(onnx_path_file)
        if os.path.exists(onnx_path):
            cf_model = ort.InferenceSession(onnx_path, providers=onnx_providers)

    return {
        "user_encoder": user_encoder,
        "item_encoder": item_encoder,
        "interactions_df": interactions_df,
        "item_meta": item_meta,
        "tfidf": tfidf,
        "tfidf_matrix": tfidf_matrix,
        "cf_model": cf_model,
    }


# ---------------------------------------------------------
# Collaborative filtering scoring
# ---------------------------------------------------------
def cf_scores_for_user(user_idx, cf_session, item_indices):
    user_array = np.full((len(item_indices), 1), user_idx, dtype=np.int32)
    item_array = item_indices.reshape(-1, 1).astype(np.int32)

    zeros = np.zeros_like(item_array)

    inputs = {
        "user_id": user_array,
        "item_id": item_array,
        "address_city": zeros,
        "address_state": zeros,
        "unit": zeros,
        "classValue_itemClassId": zeros,
    }

    preds = cf_session.run(None, inputs)[0].reshape(-1)
    return preds


def get_cf_topn(user_id, topn, artifacts, exclude_seen=True):
    user_encoder = artifacts["user_encoder"]
    item_encoder = artifacts["item_encoder"]
    interactions_df = artifacts["interactions_df"]
    cf_model = artifacts["cf_model"]

    if cf_model is None:
        raise RuntimeError("ONNX model not loaded.")

    if user_id not in user_encoder.classes_:
        return []

    user_idx = user_encoder.transform([user_id])[0]
    all_item_indices = np.arange(len(item_encoder.classes_))

    scores = cf_scores_for_user(user_idx, cf_model, all_item_indices)

    if exclude_seen:
        seen_items = interactions_df[interactions_df["user_id"] == user_idx]["item_id"].unique()
        for s in seen_items:
            scores[s] = -np.inf

    top_idx = np.argsort(-scores)[:topn]
    item_ids = item_encoder.inverse_transform(top_idx)

    return [(int(i), float(scores[int(i)])) for i in top_idx]


# ---------------------------------------------------------
# Content-based similarity
# ---------------------------------------------------------
def get_content_topn_by_item(item_id, topn, artifacts):
    item_encoder = artifacts["item_encoder"]
    tfidf_matrix = artifacts["tfidf_matrix"]

    if item_id not in item_encoder.classes_:
        return []

    idx = item_encoder.transform([item_id])[0]

    sims = linear_kernel(tfidf_matrix[idx], tfidf_matrix).reshape(-1)
    sims[idx] = -np.inf

    top_idx = np.argsort(-sims)[:topn]
    item_ids = item_encoder.inverse_transform(top_idx)

    return list(zip(item_ids, sims[top_idx]))


# ---------------------------------------------------------
# Hybrid recommender
# ---------------------------------------------------------
def get_hybrid_topn(user_id, topn, artifacts, alpha=0.6):
    user_encoder = artifacts["user_encoder"]
    item_encoder = artifacts["item_encoder"]
    interactions_df = artifacts["interactions_df"]
    item_meta = artifacts["item_meta"]
    tfidf_matrix = artifacts["tfidf_matrix"]
    cf_model = artifacts["cf_model"]

    if user_id not in user_encoder.classes_:
        return []
    print("1 CF score")
    # 1. CF scores
    cf = get_cf_topn(user_id, topn=500, artifacts=artifacts, exclude_seen=True)
    cf_dict = {i: s for i, s in cf}
    print("CF scores calculated")
    # 2. Content-based expansion
    content_scores = {}
    print("2 Content-based")
    for item_id, cf_score in cf:
        sims = get_content_topn_by_item(item_id, topn=20, artifacts=artifacts)
        for sim_item, sim_score in sims:
            content_scores[sim_item] = content_scores.get(sim_item, 0) + sim_score
    print("CF generated")

    # 3. Normalization helper
    def norm(x):
        print("Normalizing scores")
        if not x:
            return {}
        arr = np.array(list(x.values()), dtype=np.float32)
        mn, mx = arr.min(), arr.max()
        if mx <= mn:
            return {k: 0.0 for k in x}
        return {k: (v - mn) / (mx - mn + 1e-9) for k, v in x.items()}
    print("3 Normalizing scores")

    cf_norm = norm(cf_dict)
    content_norm = norm(content_scores)
    print("Normalizing done")

    # 4. Hybrid score
    print("4 Calculating hybrid scores")
    hybrid = {}
    for item in set(cf_norm) | set(content_norm):
        hybrid[item] = alpha * cf_norm.get(item, 0) + (1 - alpha) * content_norm.get(item, 0)

    # 5. Sort
    print("5 Sorting items")
    top_items = sorted(hybrid.items(), key=lambda x: -x[1])[:topn]

    # 6. Enrich with metadata
    print("6 Enriching with metadata")
    enriched = []
    for item_id, score in top_items:
        row = item_meta[item_meta["item_id"] == item_id]
        if row.empty:
            continue
        row = row.iloc[0]

        enriched.append({
            "item_id": item_id,
            "item_code": row["itemCode"],
            "item_name": row["name"],
            "item_description": row["classValue_description"],
            "score": float(score),
        })

    return enriched
