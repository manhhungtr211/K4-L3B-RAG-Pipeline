"""
Task 5 — Semantic search.

Embed query bằng chính hàm của Task 4, query ChromaDB và đổi cosine distance
thành similarity. Output phải theo SearchResult, sort giảm dần và không quá top_k.

Contract:
    - Dùng chung embed_texts() từ Task 4
    - Trả về list[SearchResult] với đúng schema
    - Score: 1.0 - distance (cosine distance -> similarity)
    - Sort giảm dần theo score
    - Không trùng ID, không vượt top_k
"""

from typing import Annotated

from .contracts import ChunkMetadata, SearchResult
from .task4_chunking_indexing import embed_texts, get_collection


def semantic_search(
    query: str,
    top_k: int = 10,
) -> Annotated[list[SearchResult], "Sorted by score descending, max top_k results"]:
    """Tìm kiếm semantic bằng dense retrieval.

    Args:
        query: Query string để tìm kiếm.
        top_k: Số lượng kết quả tối đa trả về.

    Returns:
        Danh sách SearchResult đã sort giảm dần theo score.
        Mỗi result có:
        - id: str (duy nhất)
        - content: str
        - score: float (0.0-1.0, similarity)
        - metadata: ChunkMetadata (có chunk_index)
        - retrieval_method: "dense"
    """
    if top_k <= 0:
        return []

    # Embed query bằng model từ Task 4
    query_vector = embed_texts([query])[0]

    # Query ChromaDB với cosine distance
    collection = get_collection()
    response = collection.query(
        query_embeddings=[query_vector],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    # Build results từ response
    results: list[SearchResult] = []
    seen_ids: set[str] = set()

    ids = response.get("ids", [[]])[0]
    documents = response.get("documents", [[]])[0]
    metadatas = response.get("metadatas", [[]])[0]
    distances = response.get("distances", [[]])[0]

    for item_id, content, metadata, distance in zip(
        ids,
        documents,
        metadatas,
        distances,
    ):
        # Skip duplicates
        if item_id in seen_ids:
            continue
        seen_ids.add(item_id)

        # Chuyển cosine distance -> similarity (0-1)
        score = max(0.0, 1.0 - distance)

        results.append({
            "id": item_id,
            "content": content,
            "score": score,
            "metadata": metadata,
            "retrieval_method": "dense",
        })

    # Sort giảm dần theo score
    results.sort(key=lambda x: x["score"], reverse=True)

    # Giới hạn top_k
    return results[:top_k]


if __name__ == "__main__":
    # Demo
    test_query = "hướng dẫn sử dụng shopee"
    results = semantic_search(test_query, top_k=3)
    print(f"Query: {test_query}")
    print(f"Results: {len(results)}")
    for r in results:
        print(f"  - [{r['score']:.3f}] {r['id']}")
