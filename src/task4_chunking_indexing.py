"""
Task 4 — Chunking, embedding và indexing.

Hướng dẫn:
    1. Đọc toàn bộ Markdown trong data/standardized/.
    2. Chia văn bản bằng strategy đã chọn.
    3. Embed chunks bằng một provider duy nhất.
    4. Upsert vào ChromaDB với cosine distance.

Mỗi document/chunk phải theo docs/MODULE_CONTRACTS.md. ID cần ổn định để
chạy lại pipeline không tạo dữ liệu trùng. Task 5 phải dùng chung embed_texts().
"""

import os
import re
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"

# Giải thích lựa chọn tham số trong báo cáo nhóm.
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
CHUNKING_METHOD = "recursive"

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "sentence_transformers")
EMBEDDING_DIM = 1024

COLLECTION_NAME = "rag_documents"


def embed_texts(texts: list[str]) -> list[list[float]]:

    if not texts:
        return []

    provider = os.getenv("EMBEDDING_PROVIDER", EMBEDDING_PROVIDER).lower()

    from google import genai
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    model_name = os.getenv("EMBEDDING_MODEL", "text-embedding-004")
    embeddings = []
    for text in texts:
        result = client.models.embed_content(
            model=model_name,
            contents=text,
        )
        embeddings.append(result.embedding.values)
    return embeddings


def get_collection():
    """Mở Chroma collection dùng cosine distance."""
    import chromadb

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def _extract_url_from_markdown(content: str) -> str | None:
    """Trích xuất URL từ header metadata nếu có dạng **Source:** <url>."""
    match = re.search(r"\*\*Source:\*\*\s*(https?://[^\s\n]+)", content)
    if match:
        return match.group(1).strip()
    return None


def load_documents() -> list[dict]:
    """Đọc Markdown và trả về danh sách Document theo contract."""
    documents = []
    if not STANDARDIZED_DIR.exists():
        return documents

    for path in sorted(STANDARDIZED_DIR.rglob("*.md")):
        if path.name.startswith("."):
            continue
        doc_type = "legal" if "legal" in path.parts else "news"
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            continue

        url = _extract_url_from_markdown(content)
        doc_id = path.relative_to(STANDARDIZED_DIR).as_posix()

        documents.append({
            "id": doc_id,
            "content": content,
            "metadata": {
                "source": path.name,
                "title": path.stem.replace("_", " ").title(),
                "doc_type": doc_type,
                "url": url,
            },
        })
    return documents


def chunk_documents(documents: list[dict]) -> list[dict]:
    """Chia Document thành chunks có id và chunk_index theo contract."""
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = []
    for document in documents:
        split_texts = splitter.split_text(document["content"])
        for index, text in enumerate(split_texts):
            clean_text = text.strip()
            if not clean_text:
                continue
            chunks.append({
                "id": f"{document['id']}::chunk-{index}",
                "content": clean_text,
                "metadata": {
                    **document["metadata"],
                    "chunk_index": index,
                },
            })
    return chunks


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """Thêm embedding vào từng chunk."""
    if not chunks:
        return chunks

    contents = [chunk["content"] for chunk in chunks]
    vectors = embed_texts(contents)

    for chunk, vector in zip(chunks, vectors):
        chunk["embedding"] = vector
    return chunks


def index_to_vectorstore(chunks: list[dict]) -> None:
    """Upsert chunks vào ChromaDB."""
    if not chunks:
        return

    collection = get_collection()
    collection.upsert(
        ids=[chunk["id"] for chunk in chunks],
        documents=[chunk["content"] for chunk in chunks],
        embeddings=[chunk["embedding"] for chunk in chunks],
        metadatas=[chunk["metadata"] for chunk in chunks],
    )


def run_pipeline() -> None:
    """Chạy load, chunk, embed và index."""
    documents = load_documents()
    print(f"Loaded {len(documents)} documents from {STANDARDIZED_DIR}")
    chunks = chunk_documents(documents)
    print(f"Split into {len(chunks)} chunks")
    embedded_chunks = embed_chunks(chunks)
    print("Embedded chunks successfully")
    index_to_vectorstore(embedded_chunks)
    print(f"Indexed {len(embedded_chunks)} chunks to ChromaDB collection '{COLLECTION_NAME}'")


if __name__ == "__main__":
    run_pipeline()
