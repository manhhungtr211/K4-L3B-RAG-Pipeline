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
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

from .contracts import Chunk, Document, EmbeddedChunk


# === Config ===
STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"

# Chunking parameters
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
CHUNKING_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

# Embedding model
EMBEDDING_MODEL = "BAAI/bge-m3"
EMBEDDING_DIM = 1024

# ChromaDB
COLLECTION_NAME = "rag_documents"


# === Document Loading ===
def load_documents() -> list[Document]:
    """Đọc Markdown từ standardized/ và trả về list[Document].

    Returns:
        List of Document dicts theo contract.
    """
    documents: list[Document] = []

    for path in STANDARDIZED_DIR.rglob("*.md"):
        # Xác định doc_type từ thư mục
        parts = path.relative_to(STANDARDIZED_DIR).parts
        doc_type = "legal" if "legal" in parts else "news"

        # Đọc nội dung
        content = path.read_text(encoding="utf-8")
        if not content.strip():
            continue

        # Trích xuất title từ dòng đầu tiên (markdown heading)
        lines = content.split("\n")
        title = "Untitled"
        for line in lines:
            line = line.strip()
            if line.startswith("# "):
                title = line[2:].strip()
                break

        documents.append({
            "id": path.relative_to(STANDARDIZED_DIR).as_posix(),
            "content": content,
            "metadata": {
                "source": path.name,
                "title": title,
                "doc_type": doc_type,
                "url": None,  # URL có trong content_markdown header
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
            if not text.strip():
                continue

            chunks.append({
                "id": f"{document['id']}::chunk-{index}",
                "content": text,
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
    # Cache model để không load lại nhiều lần
    if not hasattr(embed_texts, "_model"):
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
    collection = get_collection()

    # Kiểm tra chunks đã index chưa
    existing_ids = set(collection.get(include=[])["ids"])
    new_chunks = [c for c in chunks if c["id"] not in existing_ids]

    if not new_chunks:
        print(f"No new chunks to index (all {len(chunks)} already exist)")
        return

    collection.upsert(
        ids=[chunk["id"] for chunk in new_chunks],
        documents=[chunk["content"] for chunk in new_chunks],
        embeddings=[chunk["embedding"] for chunk in new_chunks],
        metadatas=[chunk["metadata"] for chunk in new_chunks],
    )

    print(f"Indexed {len(new_chunks)} new chunks (total in DB: {len(chunks)})")


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
