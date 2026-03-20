import uuid
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

from projects.manager import add_doc_to_registry, get_project_path


def fetch_and_save(url: str, project_name: str) -> dict:
    """Fetch a URL, extract text content, and save as a markdown file.

    Returns the document info dict (also added to the project's registry).
    """
    response = requests.get(url, timeout=30, headers={"User-Agent": "Sotater/0.1"})
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove script, style, and nav elements
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    title = soup.title.string.strip() if soup.title and soup.title.string else url
    text = soup.get_text(separator="\n", strip=True)

    # Build markdown content with source metadata
    document_id = uuid.uuid4().hex[:12]
    md_content = f"---\nsource_url: {url}\ntitle: {title}\n---\n\n# {title}\n\n{text}"

    # Save to project documents folder
    project_path = get_project_path(project_name)
    doc_path = project_path / "documents" / f"{document_id}.md"
    doc_path.write_text(md_content, encoding="utf-8")

    doc_info = {
        "document_id": document_id,
        "filename": f"{document_id}.md",
        "source_url": url,
        "title": title,
        "downloaded_at": datetime.now(timezone.utc).isoformat(),
        "chunk_count": 0,  # Updated after indexing
    }
    add_doc_to_registry(project_name, doc_info)

    return doc_info


def read_document(project_name: str, document_id: str) -> str:
    """Read the content of a saved document."""
    doc_path = get_project_path(project_name) / "documents" / f"{document_id}.md"
    return doc_path.read_text(encoding="utf-8")
