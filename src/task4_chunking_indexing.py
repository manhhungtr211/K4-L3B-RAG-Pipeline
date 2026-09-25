"""
Task 4 — Chunking, embedding và indexing.

Hướng dẫn:
    1. Đọc toàn bộ Markdown trong data/standardized/.
    2. Chia văn bản bằng RecursiveCharacterTextSplitter.
    3. Embed chunks bằng SentenceTransformer.
    4. Upsert vào ChromaDB với cosine distance.

Document/Chunk schema theo docs/MODULE_CONTRACTS.md:
    Document: {id, content, metadata: {source, title, doc_type, url}}
    Chunk: {id, content, metadata: {source, title, doc_type, url, chunk_index}}

Quy tắc:
    - ID ổn định (dùng path tương đối từ standardized/)
    - Chunk có chunk_index
    - Không tạo chunk trùng khi chạy lại
    - embed_texts() dùng chung cho Task 4 và Task 5
"""

import os
import re
from pathlib import Path
from dotenv import load_dotenv

from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

from .contracts import Chunk, Document, EmbeddedChunk

load_dotenv()

# === Config ===
STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"

# Chunking parameters
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
CHUNKING_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

# Embedding model
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "sentence_transformers")
EMBEDDING_DIM = 1024

# ChromaDB
COLLECTION_NAME = "rag_documents"


# === Document Loading ===
def _extract_url_from_markdown(content: str) -> str | None:
    """Trích xuất URL từ header metadata nếu có dạng **URL:** hoặc **Source:** <url>."""
    match = re.search(r"\*\*(?:URL|Source):\*\*\s*(https?://[^\s\n\)]+)", content)
    if match:
        return match.group(1).strip()
    return None


def load_documents() -> list[Document]:
    """Đọc Markdown từ standardized/ và trả về list[Document].

    Returns:
        List of Document dicts theo contract.
    """
    documents: list[Document] = []
    if not STANDARDIZED_DIR.exists():
        return documents

    for path in sorted(STANDARDIZED_DIR.rglob("*.md")):
        if path.name.startswith("."):
            continue

        # Xác định doc_type từ thư mục
        parts = path.relative_to(STANDARDIZED_DIR).parts
        doc_type = "legal" if "legal" in parts else "news"

        # Đọc nội dung
        content = path.read_text(encoding="utf-8")
        if not content.strip():
            continue

        # Trích xuất title từ dòng đầu tiên nếu có heading
        title = path.stem.replace("_", " ").title()
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("# "):
                title = line[2:].strip()
                break

        url = _extract_url_from_markdown(content)
        doc_id = path.relative_to(STANDARDIZED_DIR).as_posix()

        documents.append({
            "id": doc_id,
            "content": content,
            "metadata": {
                "source": path.name,
                "title": title,
                "doc_type": doc_type,
                "url": url,
            },
        })

    return documents


# === Chunking ===
def chunk_documents(documents: list[Document]) -> list[Chunk]:
    """Chia Document thành list[Chunk] có chunk_index.

    Args:
        documents: List of Document dicts.

    Returns:
        List of Chunk dicts theo contract.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=CHUNKING_SEPARATORS,
    )

    chunks: list[Chunk] = []

    for document in documents:
        texts = splitter.split_text(document["content"])

        for index, text in enumerate(texts):
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


# === Embedding ===
def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed list of texts thành vectors.

    Args:
        texts: List of text strings.

    Returns:
        List of embedding vectors (list[float]).
    """
    if not texts:
        return []

    provider = os.getenv("EMBEDDING_PROVIDER", EMBEDDING_PROVIDER).lower()

    if provider == "gemini":
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

    elif provider == "openai":
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        model_name = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
        response = client.embeddings.create(input=texts, model=model_name)
        return [item.embedding for item in response.data]

    else:
        # Cache model để không load lại nhiều lần
        if not hasattr(embed_texts, "_model") or embed_texts._model is None:
            embed_texts._model = SentenceTransformer(EMBEDDING_MODEL)

        model = embed_texts._model
        embeddings = model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()


def embed_chunks(chunks: list[Chunk]) -> list[EmbeddedChunk]:
    """Thêm embedding vào từng chunk.

    Args:
        chunks: List of Chunk dicts.

    Returns:
        List of EmbeddedChunk dicts.
    """
    if not chunks:
        return []

    texts = [chunk["content"] for chunk in chunks]
    embeddings = embed_texts(texts)

    result: list[EmbeddedChunk] = []
    for chunk, embedding in zip(chunks, embeddings):
        result.append({
            **chunk,
            "embedding": embedding,
        })

    return result


# === ChromaDB ===
def get_collection():
    """Mở hoặc tạo ChromaDB collection với cosine distance.

    Returns:
        ChromaDB collection object.
    """
    import chromadb

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def index_to_vectorstore(chunks: list[EmbeddedChunk]) -> None:
    """Upsert chunks vào ChromaDB.

    Args:
        chunks: List of EmbeddedChunk dicts.
    """
    if not chunks:
        print("No chunks to index.")
        return

    collection = get_collection()

    collection.upsert(
        ids=[chunk["id"] for chunk in chunks],
        documents=[chunk["content"] for chunk in chunks],
        embeddings=[chunk["embedding"] for chunk in chunks],
        metadatas=[chunk["metadata"] for chunk in chunks],
    )

    print(f"Indexed {len(chunks)} chunks to ChromaDB collection '{COLLECTION_NAME}'")


# === Pipeline ===
def run_pipeline() -> dict:
    """Chạy load -> chunk -> embed -> index.

    Returns:
        Summary dict với số lượng documents và chunks.
    """
    print("=== Loading documents ===")
    documents = load_documents()
    print(f"Loaded {len(documents)} documents")

    print("\n=== Chunking ===")
    chunks = chunk_documents(documents)
    print(f"Created {len(chunks)} chunks")

    print("\n=== Embedding ===")
    embedded_chunks = embed_chunks(chunks)
    print(f"Embedded {len(embedded_chunks)} chunks")

    print("\n=== Indexing ===")
    index_to_vectorstore(embedded_chunks)

    return {
        "documents": len(documents),
        "chunks": len(chunks),
    }


if __name__ == "__main__":
    result = run_pipeline()
    print(f"\nPipeline complete: {result}")
