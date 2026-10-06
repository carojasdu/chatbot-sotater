from langchain_huggingface import HuggingFaceEmbeddings

_model = None


def get_embedding_model() -> HuggingFaceEmbeddings:
    """Return a cached embedding model instance."""
    global _model
    if _model is None:
        # Force CPU: the Apple GPU backend (MPS) crashes when tools embed in parallel threads
        _model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
        )
    return _model
