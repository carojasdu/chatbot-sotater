import streamlit as st

from projects.manager import get_doc_registry, remove_doc_from_registry
from rag.vectorstore import delete_document_chunks


def render_documents_tab(project_name: str) -> None:
    """Render the document browser with delete functionality."""
    registry = get_doc_registry(project_name)

    if not registry:
        st.info("No documents yet. Use the chat to search and index content.")
        return

    st.markdown(f"**{len(registry)} document(s) indexed**")

    for doc in registry:
        with st.container(border=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{doc.get('title', doc['document_id'])}**")
                st.caption(f"Source: [{doc['source_url']}]({doc['source_url']})")
                st.caption(
                    f"Downloaded: {doc.get('downloaded_at', 'N/A')} | "
                    f"Chunks: {doc.get('chunk_count', 'N/A')}"
                )
            with col2:
                if st.button("Delete", key=f"del_{doc['document_id']}"):
                    delete_document_chunks(project_name, doc["document_id"])
                    remove_doc_from_registry(project_name, doc["document_id"])
                    st.rerun()
