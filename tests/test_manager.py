import json

import pytest

from projects import manager


@pytest.fixture(autouse=True)
def use_tmp_data_dir(tmp_path, monkeypatch):
    """Override DATA_DIR to use a temporary directory for each test."""
    monkeypatch.setattr(manager, "DATA_DIR", tmp_path)


class TestCreateProject:
    def test_creates_directory_structure(self, tmp_path):
        manager.create_project("my-project", "A test project")

        project_dir = tmp_path / "my-project"
        assert project_dir.exists()
        assert (project_dir / "documents").is_dir()
        assert (project_dir / "chroma_db").is_dir()
        assert (project_dir / "metadata.json").exists()
        assert (project_dir / "doc_registry.json").exists()

    def test_metadata_content(self, tmp_path):
        manager.create_project("test", "desc")
        metadata = json.loads((tmp_path / "test" / "metadata.json").read_text())

        assert metadata["name"] == "test"
        assert metadata["description"] == "desc"
        assert "created_at" in metadata

    def test_duplicate_raises(self):
        manager.create_project("dup")
        with pytest.raises(FileExistsError):
            manager.create_project("dup")

    def test_empty_registry(self, tmp_path):
        manager.create_project("test")
        registry = json.loads((tmp_path / "test" / "doc_registry.json").read_text())
        assert registry == []


class TestListProjects:
    def test_empty(self):
        assert manager.list_projects() == []

    def test_lists_created_projects(self):
        manager.create_project("alpha")
        manager.create_project("beta")
        assert manager.list_projects() == ["alpha", "beta"]

    def test_ignores_dirs_without_metadata(self, tmp_path):
        (tmp_path / "orphan").mkdir()
        manager.create_project("valid")
        assert manager.list_projects() == ["valid"]


class TestDeleteProject:
    def test_deletes_project(self, tmp_path):
        manager.create_project("to-delete")
        manager.delete_project("to-delete")
        assert not (tmp_path / "to-delete").exists()

    def test_not_found_raises(self):
        with pytest.raises(FileNotFoundError):
            manager.delete_project("nonexistent")


class TestDocRegistry:
    def test_add_and_get(self):
        manager.create_project("proj")
        doc = {"document_id": "abc123", "source_url": "https://example.com", "title": "Test"}

        manager.add_doc_to_registry("proj", doc)
        registry = manager.get_doc_registry("proj")

        assert len(registry) == 1
        assert registry[0]["document_id"] == "abc123"

    def test_remove_doc(self, tmp_path):
        manager.create_project("proj")
        doc_file = tmp_path / "proj" / "documents" / "abc123.md"
        doc_file.write_text("# Test content")

        manager.add_doc_to_registry(
            "proj",
            {"document_id": "abc123", "source_url": "https://example.com", "title": "Test"},
        )
        manager.remove_doc_from_registry("proj", "abc123")

        assert manager.get_doc_registry("proj") == []
        assert not doc_file.exists()

    def test_remove_nonexistent_doc_is_safe(self):
        manager.create_project("proj")
        manager.remove_doc_from_registry("proj", "missing")
        assert manager.get_doc_registry("proj") == []
