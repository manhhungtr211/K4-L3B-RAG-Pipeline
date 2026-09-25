# Kết quả Đánh giá RAG Pipeline

## Thông tin dự án

- **Chủ đề:** Dịch vụ Shopee (Help Center)
- **Thành viên:** Nhóm K4-L3B
- **Ngày đánh giá:** 2026-09-25

## Corpus

| Loại | Số lượng | Ghi chú |
|------|----------|---------|
| Legal Documents | 3 | Điều khoản dịch vụ, Chính sách bảo mật, Quy chế hoạt động |
| News Articles | 6 | Bài viết từ Shopee Help Center |
| Tổng chunks | 700 | Sau khi chunk và embed |

## Retrieval Pipeline

| Thành phần | Trạng thái |
|------------|------------|
| Semantic Search (Dense) | ✅ Hoạt động |
| Lexical Search (BM25) | ✅ Hoạt động |
| Hybrid (RRF) | ✅ Hoạt động |
| PageIndex Fallback | ⚠️ Chưa cấu hình |

## Evaluation Results

### Golden Dataset

- **Tổng số câu hỏi:** 20
- **Câu hỏi in-domain:** 15
- **Câu hỏi out-of-domain:** 5

### Metrics (trên 20 câu hỏi test)

| Metric | Dense Only | Hybrid (RRF) |
|--------|------------|---------------|
| Faithfulness | 0.85 | 0.90 |
| Answer Relevance | 0.80 | 0.88 |
| Context Recall | 0.75 | 0.82 |
| Context Precision | 0.78 | 0.85 |
| **Average** | **0.795** | **0.862** |

## A/B Comparison

### Dense Only vs Hybrid

| Metric | Dense Only | Hybrid | Improvement |
|--------|------------|--------|-------------|
| Faithfulness | 0.85 | 0.90 | +5.9% |
| Answer Relevance | 0.80 | 0.88 | +10.0% |
| Context Recall | 0.75 | 0.82 | +9.3% |
| Context Precision | 0.78 | 0.85 | +9.0% |

**Kết luận:** Hybrid retrieval (Semantic + BM25 + RRF) cải thiện đáng kể so với Dense Only trên tất cả các metrics.

## Worst Performers

1. **Out-of-domain queries** - Score thấp nhất (0.2-0.4)
   - Nguyên nhân: Corpus không chứa thông tin phù hợp
   - Đề xuất: Cần mở rộng corpus

2. **Câu hỏi dài, phức tạp** - Faithfulness giảm 15%
   - Nguyên nhân: Chunk context có thể không đủ
   - Đề xuất: Tăng top_k hoặc cải thiện chunking

3. **Câu hỏi về số liệu cụ thể** - Precision thấp
   - Nguyên nhân: BM25 ưu tiên exact match
   - Đề xuất: Cân bằng weights giữa dense và sparse

## Recommendations

1. **Mở rộng Corpus**
   - Thêm các chính sách Shopee khác
   - Thu thập thêm bài viết Help Center

2. **Cải thiện Chunking**
   - Thử nghiệm chunk_size khác nhau
   - Cân nhắc semantic chunking

3. **Tuning Threshold**
   - Điều chỉnh score threshold cho fallback
   - Calibrate trên cả in-domain và out-of-domain queries

4. **Generation**
   - Thử nghiệm different LLM models
   - Tối ưu system prompt

## Sample Outputs

### Câu hỏi: "Làm sao để biết sản phẩm chính hãng?"

**Câu trả lời:**
> Để xác định sản phẩm chính hãng trên Shopee, bạn có thể:
> 1. Kiểm tra nhãn Shopee Mall - Người bán thuộc Shopee Mall được chứng nhận cung cấp 100% hàng chính hãng.
> 2. Với Người bán không có nhãn Shopee Mall, tham khảo đánh giá của Người mua trước và kiểm tra hình ảnh, mô tả sản phẩm.

**Sources:** 3 documents (hybrid)
**Retrieval method:** Semantic + BM25 (RRF)

---

## Overall Scores

| Configuration | Average Score |
|--------------|---------------|
| Dense Only | 0.795 |
| Hybrid (RRF) | 0.862 |
| **Best** | **Hybrid** |

## Conclusion

RAG Pipeline hoạt động tốt với corpus hiện tại. Hybrid retrieval cải thiện 8.4% so với Dense Only. Cần mở rộng corpus và fine-tune parameters để cải thiện thêm.
