"""Constant values that do not make sense to read from a config.yml, environment variables, or CLI arguments."""

MODEL_BUCKET_GH_SECRET = "object-store-ai"

DEFAULT__YOUTUBE_MODEL__GH_SECRET_ID = "yt-similarity-model-id"
DEFAULT__INSTAGRAM_MODEL__GH_SECRET_ID = "ig-similarity-model-id"
DEFAULT__MAX_SIMILARITY_RESULTS = 25

MAX_PRODUCTIONS_IN_SIMILARITY_QUERY = 100
MAX_ALLOWED_SIMILARITY_RESULTS_PER_PRODUCTION = 1024

# hyperparameter for FAISS index search
DEFAULT__FAISS_INDEX_N_PROBE = 10
