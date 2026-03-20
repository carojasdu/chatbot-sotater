from langchain_text_splitters import RecursiveCharacterTextSplitter

_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", ". ", " ", ""],
)


def split_text(text: str) -> list[str]:
    """Split text into chunks for embedding."""
    return _splitter.split_text(text)
