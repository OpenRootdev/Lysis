"""Add a language name to CATALOG_LANGUAGES and the weekly job picks it up."""

CATALOG_LANGUAGES = ["python", "javascript", "go", "typescript", "java", "rust"]
# Languages the model was trained and tested on. Their repos get a full fetch;
# the others are catalog-only and shown as "unvalidated".
TRAIN_LANGUAGES = {"python", "javascript"}