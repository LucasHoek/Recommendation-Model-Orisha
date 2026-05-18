import sys
import json
from recommender import load_artifacts, get_hybrid_topn

ARTIFACTS_DIR = "artifacts"
artifacts = load_artifacts(ARTIFACTS_DIR)

if __name__ == "__main__":
    klantcode = int(sys.argv[1])
    topn = int(sys.argv[2])

    results = get_hybrid_topn(klantcode, topn, artifacts)
    print(json.dumps(results))
