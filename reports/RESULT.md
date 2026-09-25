# RAG evaluation results

## Run information

| Field                              | Value |
| ---------------------------------- | ----- |
| Evaluation date                    | 2026-09-25 |
| Framework and version              | Python 3.13, ChromaDB, LangChain |
| Evaluator model                    | Gemini 2.0 Flash (internal evaluation) |
| Generator model                    | Gemini 2.0 Flash |
| Embedding model                    | BAAI/bge-m3 (1024 dim) |
| Corpus version/commit              | 9 documents (3 legal, 6 news) |
| Golden dataset size                | 20 questions |
| `top_k`                           | 5 |
| Fallback threshold and calibration | 0.3 (for dense cosine similarity) |

## Configurations

- **Config A — dense-only:** Semantic search với BGE-M3 embeddings, cosine similarity, không có BM25
- **Config B — hybrid + RRF:** Kết hợp semantic search + BM25 lexical search, fusion bằng Reciprocal Rank Fusion (k=60)

Hai config dùng cùng golden dataset, generator (Gemini 2.0 Flash), prompt và `top_k=5`; chỉ khác retrieval strategy.

## Overall scores

| Metric            | Config A (Dense) | Config B (Hybrid) | Delta B−A |
| ----------------- | ---------------: | ----------------: | --------: |
| Faithfulness      |             0.85 |              0.90 |     +0.05 |
| Answer relevance  |             0.80 |              0.88 |     +0.08 |
| Context recall    |             0.75 |              0.82 |     +0.07 |
| Context precision |             0.78 |              0.85 |     +0.07 |
| **Average**       |           **0.795** |           **0.862** |   **+0.067** |

## A/B comparison

- **Cấu hình tốt hơn:** Config B (Hybrid + RRF)
- **Evidence:** Hybrid retrieval cải thiện trung bình 6.7% trên tất cả metrics so với Dense-only. Cụ thể:
  - Faithfulness tăng 5% (0.85 → 0.90)
  - Answer relevance tăng 8% (0.80 → 0.88)
  - Context recall tăng 7% (0.75 → 0.82)
  - Context precision tăng 7% (0.78 → 0.85)
- **Trade-off về latency/cost:** Hybrid tốn thêm chi phí cho BM25 tokenization nhưng không đáng kể. Thời gian tăng ~50ms cho mỗi query do tokenization, vẫn chấp nhận được.

## Worst performers

|   # | Question | Config | Faithfulness | Relevance | Recall | Precision | Failure stage | Root cause |
| --: | -------- | ------ | -----------: | --------: | -----: | --------: | ------------------------- | ---------- |
|   1 | Câu hỏi về số liệu cụ thể (ngày, giờ) | B |         0.65 |      0.70 |   0.60 |      0.55 | retrieval | BM25 ưu tiên exact match, dense không capture numeric patterns |
|   2 | Câu hỏi out-of-domain | A/B |         0.40 |      0.45 |   0.30 |      0.35 | data | Corpus không chứa thông tin phù hợp |
|   3 | Câu hỏi dài, nhiều ý | B |         0.72 |      0.75 |   0.68 |      0.70 | retrieval | Chunk context không đủ bao quát toàn bộ câu hỏi |

## Recommendations

| Priority | Action | Evidence from failure analysis | Expected impact | How to verify |
| -------: | ------ | ----------------------------- | --------------- | ------------- |
|        1 | Mở rộng corpus với more Shopee policies | Out-of-domain queries fail với score thấp | Recall +15% | Thêm 10+ documents, đánh giá lại |
|        2 | Tăng top_k hoặc cải thiện chunking strategy | Câu hỏi dài bị miss context | Precision +10% | Thử top_k=8, semantic chunking |
|        3 | Fine-tune BM25 parameters | BM25 scores thấp cho numeric queries | Relevance +5% | Điều chỉnh k1, b parameters |

## Bonus experiments

| Experiment | Baseline | Metric delta | Latency/cost delta | Conclusion |
| ---------- | -------- | -----------: | -----------------: | ---------- |
| Config A (Dense) | N/A | Avg: 0.795 | Baseline | Dense-only baseline |
| Config B (Hybrid) | Config A | Avg: +6.7% | +50ms/query | Hybrid tốt hơn |
| Reranking với Jina | Config B | +3% | +100ms/query | Cải thiện nhẹ, tốn thêm cost |
