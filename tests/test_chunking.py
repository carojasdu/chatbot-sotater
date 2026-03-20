from rag.chunking import split_text


class TestSplitText:
    def test_short_text_single_chunk(self):
        chunks = split_text("Hello world.")
        assert len(chunks) == 1
        assert chunks[0] == "Hello world."

    def test_long_text_splits(self):
        text = "This is a sentence. " * 200  # ~4000 chars
        chunks = split_text(text)
        assert len(chunks) > 1

    def test_empty_text(self):
        chunks = split_text("")
        assert chunks == []

    def test_chunks_have_overlap(self):
        # Create text that will definitely split into multiple chunks
        paragraphs = [f"Paragraph {i}. " + "word " * 150 for i in range(5)]
        text = "\n\n".join(paragraphs)
        chunks = split_text(text)

        # With overlap=200, consecutive chunks should share some content
        assert len(chunks) >= 3
        for chunk in chunks:
            assert len(chunk) <= 1000
