# recommender.py (updated)
import os
import pickle
import joblib
from pathlib import Path
from scipy import sparse
import numpy as np
from sklearn.metrics.pairwise import linear_kernel
import onnxruntime as ort
import pandas as pd
import gzip, bz2, lzma, io

ARTIFACTS_DIR = Path("artifacts")

# -------------------------
# Robust loader for interactions_df
# -------------------------
def _coerce_extension_string_dtypes_to_object(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert extension string dtypes (and other problematic extension dtypes)
    to plain object dtype so downstream code can operate without dtype constructor errors.
    """
    for col in df.columns:
        try:
            # If it's an extension string dtype or object-like, coerce to object
            if pd.api.types.is_string_dtype(df[col].dtype) or pd.api.types.is_object_dtype(df[col].dtype):
                df[col] = df[col].astype("object")
        except Exception:
            # If dtype checks fail for any reason, coerce anyway
            df[col] = df[col].astype("object")
    return df

def safe_load_interactions(path: Path):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"{p} not found")

    try:
        obj = joblib.load(p)
    except Exception as e:
        raise RuntimeError(f"joblib.load failed for {p}: {e}") from e

    if isinstance(obj, pd.DataFrame):
        return _coerce_extension_string_dtypes_to_object(obj)
    return obj


# -------------------------
# Artifact loading (uses safe loader)
# -------------------------
def load_artifacts(artifacts_dir=ARTIFACTS_DIR, onnx_providers=None):
    if onnx_providers is None:
        onnx_providers = ["CPUExecutionProvider"]

    artifacts_dir = Path(artifacts_dir)

    # required maps
    with open(artifacts_dir / "cf_user_id_map.pkl", "rb") as f:
        cf_user_id_map = pickle.load(f)
    with open(artifacts_dir / "cf_item_id_map.pkl", "rb") as f:
        cf_item_id_map = pickle.load(f)

    # interactions_df: prefer Parquet if present (more robust across pandas versions)
    parquet_path = artifacts_dir / "interactions_df.parquet"
    joblib_path = artifacts_dir / "interactions_df.joblib"
    if parquet_path.exists():
        interactions_df = pd.read_parquet(parquet_path)
        interactions_df = _coerce_extension_string_dtypes_to_object(interactions_df)
    elif joblib_path.exists():
        interactions_df = safe_load_interactions(joblib_path)
    else:
        raise FileNotFoundError("No interactions_df.parquet or interactions_df.joblib found in artifacts directory")

    # other artifacts (try joblib, fall back to pickle where appropriate)
    try:
        items_full = joblib.load(artifacts_dir / "items_full.joblib")
    except Exception:
        with open(artifacts_dir / "items_full.joblib", "rb") as f:
            items_full = pickle.load(f)

    try:
        tfidf = joblib.load(artifacts_dir / "tfidf_vectorizer.joblib")
    except Exception:
        with open(artifacts_dir / "tfidf_vectorizer.joblib", "rb") as f:
            tfidf = pickle.load(f)

    tfidf_matrix = sparse.load_npz(artifacts_dir / "tfidf_matrix.npz")

    with open(artifacts_dir / "item_idx_to_id.pkl", "rb") as f:
        item_idx_to_id = pickle.load(f)
    with open(artifacts_dir / "user_idx_to_id.pkl", "rb") as f:
        user_idx_to_id = pickle.load(f)

    # ONNX session if path saved
    cf_model = None
    onnx_path_joblib = artifacts_dir / "ncf_model_path.joblib"
    if onnx_path_joblib.exists():
        onnx_path = joblib.load(onnx_path_joblib)
        if os.path.exists(onnx_path):
            cf_model = ort.InferenceSession(onnx_path, providers=onnx_providers)

    return {
        "cf_user_id_map": cf_user_id_map,
        "cf_item_id_map": cf_item_id_map,
        "interactions_df": interactions_df,
        "items_full": items_full,
        "tfidf": tfidf,
        "tfidf_matrix": tfidf_matrix,
        "item_idx_to_id": item_idx_to_id,
        "user_idx_to_id": user_idx_to_id,
        "cf_model": cf_model,
    }


def _build_all_item_indices(cf_item_id_map):
    return np.arange(len(cf_item_id_map), dtype=np.int32)

def cf_scores_for_user(user_idx, cf_session, item_indices):
    user_array = np.full((len(item_indices), 1), user_idx, dtype=np.int32)
    item_array = item_indices.reshape(-1, 1).astype(np.int32)
    inputs = {}
    for inp in cf_session.get_inputs():
        if "user" in inp.name.lower():
            inputs[inp.name] = user_array
        else:
            inputs[inp.name] = item_array
    preds = cf_session.run(None, inputs)[0].reshape(-1)
    return preds

def get_cf_topn(user_id, topn, artifacts, exclude_seen=True):
    cf_user_id_map = artifacts["cf_user_id_map"]
    cf_item_id_map = artifacts["cf_item_id_map"]
    interactions_df = artifacts["interactions_df"]
    item_idx_to_id = artifacts["item_idx_to_id"]
    cf_model = artifacts["cf_model"]
    if cf_model is None:
        return []
    if user_id not in cf_user_id_map:
        return []
    user_idx = cf_user_id_map[user_id]
    all_item_indices = _build_all_item_indices(cf_item_id_map)
    scores = cf_scores_for_user(user_idx, cf_model, all_item_indices)
    if exclude_seen:
        seen = set(interactions_df[interactions_df["user_id"] == user_id]["item_idx"].tolist())
        for s in seen:
            if 0 <= s < len(scores):
                scores[int(s)] = -np.inf
    topn = min(topn, len(scores))
    top_idx = np.argpartition(-scores, topn - 1)[:topn]
    top_sorted = top_idx[np.argsort(-scores[top_idx])]
    return [(artifacts["item_idx_to_id"][int(i)], float(scores[int(i)])) for i in top_sorted]

def get_content_topn_by_user(user_id, topn, artifacts, exclude_seen=True):
    interactions_df = artifacts["interactions_df"]
    tfidf_matrix = artifacts["tfidf_matrix"]
    cf_item_id_map = artifacts["cf_item_id_map"]
    item_idx_to_id = artifacts["item_idx_to_id"]

    user_interactions = interactions_df[interactions_df["user_id"] == user_id]
    if user_interactions.empty:
        sims = np.zeros(tfidf_matrix.shape[0], dtype=np.float32)
    else:
        threshold = user_interactions["rating"].mean()
        positive = user_interactions[user_interactions["rating"] >= threshold]["item_idx"].unique()
        if len(positive) == 0:
            sims = np.zeros(tfidf_matrix.shape[0], dtype=np.float32)
        else:
            sims_list = [linear_kernel(tfidf_matrix[int(pid)], tfidf_matrix).reshape(-1) for pid in positive]
            sims = np.mean(np.vstack(sims_list), axis=0)

    if exclude_seen:
        seen = set(user_interactions["item_idx"].tolist())
        for s in seen:
            if 0 <= s < len(sims):
                sims[int(s)] = -np.inf

    topn = min(topn, len(sims))
    top_idx = np.argpartition(-sims, topn - 1)[:topn]
    top_sorted = top_idx[np.argsort(-sims[top_idx])]
    return [(item_idx_to_id[int(i)], float(sims[int(i)])) for i in top_sorted]

def get_hybrid_topn(user_id, topn, artifacts, alpha=0.6):
    cf_user_id_map = artifacts["cf_user_id_map"]
    cf_item_id_map = artifacts["cf_item_id_map"]
    interactions_df = artifacts["interactions_df"]
    tfidf_matrix = artifacts["tfidf_matrix"]
    item_idx_to_id = artifacts["item_idx_to_id"]
    cf_model = artifacts["cf_model"]

    if user_id not in cf_user_id_map:
        return []

    all_item_indices = _build_all_item_indices(cf_item_id_map)

    if cf_model is not None:
        user_idx = cf_user_id_map[user_id]
        cf_scores = cf_scores_for_user(user_idx, cf_model, all_item_indices)
    else:
        cf_scores = np.zeros(len(all_item_indices), dtype=np.float32)

    user_interactions = interactions_df[interactions_df["user_id"] == user_id]
    if user_interactions.empty:
        content_scores = np.zeros_like(cf_scores)
    else:
        threshold = user_interactions["rating"].mean()
        positive = user_interactions[user_interactions["rating"] >= threshold]["item_idx"].unique()
        if len(positive) == 0:
            content_scores = np.zeros_like(cf_scores)
        else:
            sims = [linear_kernel(tfidf_matrix[int(pid)], tfidf_matrix).reshape(-1) for pid in positive]
            content_scores = np.mean(np.vstack(sims), axis=0)

    def normalize(x):
        x = np.array(x, dtype=np.float32)
        mn, mx = np.nanmin(x), np.nanmax(x)
        if mx <= mn:
            return np.zeros_like(x)
        return (x - mn) / (mx - mn)

    cf_n = normalize(cf_scores)
    content_n = normalize(content_scores)
    hybrid = alpha * cf_n + (1 - alpha) * content_n

    seen = set(user_interactions["item_idx"].tolist())
    for s in seen:
        if 0 <= s < len(hybrid):
            hybrid[int(s)] = -np.inf

    topn = min(topn, len(hybrid))
    top_idx = np.argpartition(-hybrid, topn - 1)[:topn]
    top_sorted = top_idx[np.argsort(-hybrid[top_idx])]
    return [(item_idx_to_id[int(i)], float(hybrid[int(i)])) for i in top_sorted]

# caching
_cached_artifacts = None

def get_artifacts():
    global _cached_artifacts
    if _cached_artifacts is None:
        _cached_artifacts = load_artifacts()
    return _cached_artifacts

def get_recommendations_for_user(user_id, topn=10, alpha=0.6):
    artifacts = get_artifacts()
    if artifacts.get("cf_model") is not None:
        return get_hybrid_topn(user_id, topn, artifacts, alpha=alpha)
    else:
        return get_content_topn_by_user(user_id, topn, artifacts, exclude_seen=True)
