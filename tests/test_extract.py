from unittest.mock import MagicMock, patch

import pytest

from projects import manager
from scraper.extract import fetch_and_save


@pytest.fixture(autouse=True)
def use_tmp_data_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(manager, "DATA_DIR", tmp_path)


@pytest.fixture
def project(tmp_path):
    manager.create_project("test-proj")
    return "test-proj"


class TestFetchAndSave:
    @patch("scraper.extract.requests.get")
    def test_saves_markdown_file(self, mock_get, project, tmp_path):
        mock_response = MagicMock()
        mock_response.text = (
            "<html><head><title>Test Page</title></head>"
            "<body><p>Hello world</p></body></html>"
        )
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        doc_info = fetch_and_save("https://example.com/article", project)

        assert doc_info["source_url"] == "https://example.com/article"
        assert doc_info["title"] == "Test Page"
        assert len(doc_info["document_id"]) == 12

        # Verify file was created
        doc_path = tmp_path / project / "documents" / f"{doc_info['document_id']}.md"
        assert doc_path.exists()
        content = doc_path.read_text()
        assert "source_url: https://example.com/article" in content
        assert "Hello world" in content

    @patch("scraper.extract.requests.get")
    def test_adds_to_registry(self, mock_get, project):
        mock_response = MagicMock()
        mock_response.text = "<html><body><p>Content</p></body></html>"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        fetch_and_save("https://example.com", project)
        registry = manager.get_doc_registry(project)

        assert len(registry) == 1
        assert registry[0]["source_url"] == "https://example.com"

    @patch("scraper.extract.requests.get")
    def test_strips_script_and_style(self, mock_get, project, tmp_path):
        mock_response = MagicMock()
        mock_response.text = (
            "<html><body>"
            "<script>alert('bad')</script>"
            "<style>.x{color:red}</style>"
            "<p>Clean text</p>"
            "</body></html>"
        )
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        doc_info = fetch_and_save("https://example.com", project)
        doc_path = tmp_path / project / "documents" / f"{doc_info['document_id']}.md"
        content = doc_path.read_text()

        assert "alert" not in content
        assert "color:red" not in content
        assert "Clean text" in content
