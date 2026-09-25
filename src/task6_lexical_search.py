"""
Task 6 — Lexical search bằng BM25.

Dùng cùng corpus chunks với Task 5. BM25 phù hợp với từ khóa chính xác, mã tài
liệu và tên riêng. Output phải theo SearchResult và sort score giảm dần.
"""

import re

from rank_bm25 import BM25Okapi

from .contracts import Chunk, SearchResult


CORPUS: list[Chunk] = []


def _tokenize(text: str) -> list[str]:
    """Tokenize consistently for both documents and queries."""
    return re.findall(r"\w+", text.casefold(), flags=re.UNICODE)


def build_bm25_index(corpus: list[dict]) -> BM25Okapi:
    """Tạo BM25 index từ cùng corpus chunks của Task 4."""
    tokenized_corpus = [_tokenize(item["content"]) for item in corpus]
    return BM25Okapi(tokenized_corpus)


def _load_corpus_from_vectorstore() -> list[Chunk]:
    """Nạp đúng corpus chunks đã được Task 4 index vào ChromaDB."""
    # Import lazily để unit test của Task 6 không phải load embedding model.
    from .task4_chunking_indexing import get_collection

    response = get_collection().get(include=["documents", "metadatas"])
    ids = response.get("ids") or []
    documents = response.get("documents") or []
    metadatas = response.get("metadatas") or []

    return [
        {
            "id": item_id,
            "content": content,
            # ChromaDB may omit metadata fields whose original value was None.
            "metadata": {**metadata, "url": metadata.get("url")},
        }
        for item_id, content, metadata in zip(ids, documents, metadatas)
        if item_id and content and metadata
    ]


def lexical_search(query: str, top_k: int = 10) -> list[SearchResult]:
    """Trả về BM25 SearchResult theo score giảm dần."""
    global CORPUS

    query_tokens = _tokenize(query)
    if top_k <= 0 or not query_tokens:
        return []

    if not CORPUS:
        CORPUS = _load_corpus_from_vectorstore()
    if not CORPUS:
        return []

    bm25 = build_bm25_index(CORPUS)
    scores = bm25.get_scores(query_tokens)
    query_token_set = set(query_tokens)

    token_overlaps = [
        sum(token in query_token_set for token in _tokenize(item["content"]))
        for item in CORPUS
    ]

    # BM25Okapi can assign the same score (including zero) to matching and
    # non-matching documents in very small corpora. Token overlap provides a
    # deterministic tie-break without changing the reported BM25 score.
    ranked_indices = sorted(
        range(len(CORPUS)),
        key=lambda index: (
            -float(scores[index]),
            -token_overlaps[index],
            index,
        ),
    )

    results: list[SearchResult] = []
    seen_ids: set[str] = set()
    for index in ranked_indices:
        item = CORPUS[index]
        if token_overlaps[index] == 0 or item["id"] in seen_ids:
            continue
        seen_ids.add(item["id"])
        results.append(
            {
                "id": item["id"],
                "content": item["content"],
                "score": float(scores[index]),
                "metadata": item["metadata"],
                "retrieval_method": "bm25",
            }
        )
        if len(results) == top_k:
            break

    return results


if __name__ == "__main__":
    for result in lexical_search("sản phẩm chính hãng", top_k=3):
        print(result)
