from langchain_huggingface import HuggingFaceEmbeddings

_model = None


def get_embedding_model() -> HuggingFaceEmbeddings:
    """Return a cached embedding model instance."""
    global _model
    if _model is None:
        _model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return _model
