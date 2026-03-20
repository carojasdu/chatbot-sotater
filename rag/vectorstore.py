from langchain_chroma import Chroma

from projects.manager import get_project_path
from rag.chunking import split_text
from rag.embeddings import get_embedding_model


def _get_vectorstore(project_name: str) -> Chroma:
    """Get the persistent ChromaDB vector store for a project."""
    persist_dir = str(get_project_path(project_name) / "chroma_db")
    return Chroma(
        collection_name=project_name,
        embedding_function=get_embedding_model(),
        persist_directory=persist_dir,
    )


def index_document(project_name: str, document_id: str, text: str, source_url: str) -> int:
    """Chunk, embed, and store a document in the project's vector store.

    Returns the number of chunks created.
    """
    chunks = split_text(text)
    if not chunks:
        return 0

    metadatas = [
        {
            "document_id": document_id,
            "source_url": source_url,
            "chunk_index": i,
        }
        for i in range(len(chunks))
    ]
    ids = [f"{document_id}_{i}" for i in range(len(chunks))]

    store = _get_vectorstore(project_name)
    store.add_texts(texts=chunks, metadatas=metadatas, ids=ids)

    return len(chunks)


def query_documents(project_name: str, question: str, k: int = 5) -> list[dict]:
    """Query the vector store and return the top-k matching chunks with metadata."""
    store = _get_vectorstore(project_name)
    results = store.similarity_search_with_score(question, k=k)

    return [
        {
            "content": doc.page_content,
            "source_url": doc.metadata.get("source_url", ""),
            "document_id": doc.metadata.get("document_id", ""),
            "chunk_index": doc.metadata.get("chunk_index", 0),
            "score": score,
        }
        for doc, score in results
    ]


def delete_document_chunks(project_name: str, document_id: str) -> None:
    """Remove all chunks belonging to a document from the vector store."""
    store = _get_vectorstore(project_name)
    # ChromaDB supports filtering by metadata on delete
    store._collection.delete(where={"document_id": document_id})
