import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "projects"


def _project_path(name: str) -> Path:
    return DATA_DIR / name


def list_projects() -> list[str]:
    """Return names of all existing projects (directories with metadata.json)."""
    if not DATA_DIR.exists():
        return []
    return sorted(
        d.name
        for d in DATA_DIR.iterdir()
        if d.is_dir() and (d / "metadata.json").exists()
    )


def create_project(name: str, description: str = "") -> Path:
    """Create a new project with its directory structure and metadata."""
    project_dir = _project_path(name)
    if project_dir.exists():
        raise FileExistsError(f"Project '{name}' already exists")

    project_dir.mkdir(parents=True)
    (project_dir / "documents").mkdir()
    (project_dir / "chroma_db").mkdir()

    metadata = {
        "name": name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "description": description,
    }
    (project_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))
    (project_dir / "doc_registry.json").write_text("[]")

    return project_dir


def delete_project(name: str) -> None:
    """Delete a project and all its data."""
    project_dir = _project_path(name)
    if not project_dir.exists():
        raise FileNotFoundError(f"Project '{name}' not found")
    shutil.rmtree(project_dir)


def get_project_path(name: str) -> Path:
    """Return the base path for a project."""
    path = _project_path(name)
    if not path.exists():
        raise FileNotFoundError(f"Project '{name}' not found")
    return path


def get_metadata(name: str) -> dict:
    """Read project metadata."""
    path = get_project_path(name) / "metadata.json"
    return json.loads(path.read_text())


def get_doc_registry(name: str) -> list[dict]:
    """Read the document registry for a project."""
    path = get_project_path(name) / "doc_registry.json"
    return json.loads(path.read_text())


def add_doc_to_registry(name: str, doc_info: dict) -> None:
    """Append a document entry to the registry."""
    registry = get_doc_registry(name)
    registry.append(doc_info)
    path = get_project_path(name) / "doc_registry.json"
    path.write_text(json.dumps(registry, indent=2))


def remove_doc_from_registry(name: str, document_id: str) -> None:
    """Remove a document entry from the registry and delete its file."""
    registry = get_doc_registry(name)
    registry = [d for d in registry if d["document_id"] != document_id]
    path = get_project_path(name) / "doc_registry.json"
    path.write_text(json.dumps(registry, indent=2))

    doc_file = get_project_path(name) / "documents" / f"{document_id}.md"
    if doc_file.exists():
        doc_file.unlink()
