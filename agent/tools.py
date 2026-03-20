from langchain_core.tools import tool
from tavily import TavilyClient

from projects.manager import get_doc_registry, get_project_path
from rag.vectorstore import index_document, query_documents
from scraper.extract import fetch_and_save


@tool
def web_search(query: str) -> str:
    """Search the web for articles, blog posts, and scientific papers on a topic.

    Use this tool when you need to discover new sources of information.
    Returns a list of results with titles, URLs, and snippets.
    """
    client = TavilyClient()
    response = client.search(query, max_results=5)

    results = []
    for r in response.get("results", []):
        results.append(f"**{r['title']}**\n  URL: {r['url']}\n  {r.get('content', '')[:200]}")
    return "\n\n".join(results) if results else "No results found."


@tool
def scrape_and_index(url: str, project_name: str) -> str:
    """Download a web page, extract its text content, and index it into the project's
    knowledge base for future retrieval.

    Use this after finding relevant sources with web_search. The content will be
    saved locally and made searchable via RAG.
    """
    doc_info = fetch_and_save(url, project_name)

    # Read the saved content and index it
    doc_path = get_project_path(project_name) / "documents" / doc_info["filename"]
    text = doc_path.read_text(encoding="utf-8")

    chunk_count = index_document(
        project_name=project_name,
        document_id=doc_info["document_id"],
        text=text,
        source_url=url,
    )

    # Update chunk count in registry
    registry = get_doc_registry(project_name)
    for entry in registry:
        if entry["document_id"] == doc_info["document_id"]:
            entry["chunk_count"] = chunk_count
    registry_path = get_project_path(project_name) / "doc_registry.json"
    import json

    registry_path.write_text(json.dumps(registry, indent=2))

    return (
        f"Indexed '{doc_info['title']}' from {url}. "
        f"Created {chunk_count} chunks in the knowledge base."
    )


@tool
def rag_query(question: str, project_name: str) -> str:
    """Search the project's indexed documents to find relevant information.

    Use this tool when the user asks about topics that may already be covered
    by previously indexed documents. Returns relevant text chunks with source URLs.
    """
    results = query_documents(project_name, question, k=5)

    if not results:
        return "No relevant documents found in the knowledge base. Try using web_search first."

    chunks = []
    for r in results:
        chunks.append(
            f"[Source: {r['source_url']}]\n{r['content']}"
        )
    return "\n\n---\n\n".join(chunks)
