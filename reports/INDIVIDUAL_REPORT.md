# Báo cáo đóng góp cá nhân

## Thông tin

- Họ và tên: Trần Vũ Gia Huy
- Mã học viên: 2A202602705
- Nhóm: Chưa cung cấp
- Repository/branch: `K4-L3B-RAG-Pipeline` / `main`

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Task 6 - Lexical search | Xây dựng tokenizer Unicode, BM25 index và hàm tìm kiếm theo từ khóa bằng `BM25Okapi` | `src/task6_lexical_search.py` (commit cùng báo cáo) | Done |
| Tích hợp Task 4 và Task 6 | Nạp trực tiếp 700 chunks đã được Task 4 index trong ChromaDB để BM25 và dense retrieval dùng cùng corpus, ID và metadata | `src/task6_lexical_search.py` | Done |
| Tuân thủ module contract | Trả `SearchResult` với `retrieval_method="bm25"`, score kiểu `float`, thứ tự giảm dần, không trùng ID và không vượt `top_k` | `src/task6_lexical_search.py`, `tests/test_contracts.py` | Done |

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Nạp corpus BM25 từ collection ChromaDB do Task 4 tạo thay vì duy trì một bản corpus riêng.
   **Lý do/evidence:** Collection `rag_documents` hiện chứa 700 chunks. Dùng cùng dữ liệu đã index bảo đảm Task 5 và Task 6 tham chiếu cùng ID, nội dung và metadata, đúng yêu cầu trong `MODULE_CONTRACTS.md`.
   **Trade-off:** Lần tìm kiếm đầu tiên phải đọc toàn bộ chunks từ ChromaDB; corpus sau đó được cache trong biến `CORPUS`, vì vậy nếu index thay đổi trong cùng tiến trình thì cần nạp lại corpus.

2. **Quyết định:** Tokenize bằng `casefold()` và regex Unicode, đồng thời dùng số token trùng làm tiêu chí phá hòa nhưng vẫn giữ nguyên BM25 score.
   **Lý do/evidence:** Cách này xử lý chữ hoa/thường và văn bản tiếng Việt nhất quán. Với corpus rất nhỏ, `BM25Okapi` có thể cho cùng điểm, kể cả điểm 0, giữa tài liệu khớp và không khớp; tiêu chí phụ giúp thứ tự ổn định.
   **Trade-off:** Tokenizer đơn giản chưa thực hiện tách từ tiếng Việt chuyên sâu; cụm từ nhiều âm tiết vẫn được xem là các token riêng.

## Kiểm thử và kết quả

- Test hoặc query đã dùng:
  - `pytest tests/test_contracts.py::test_lexical_search_returns_bm25_contract -q`
  - Ba test liên quan đến Task 4, Task 6 và chữ ký public function trong `tests/test_contracts.py`.
  - Query thực tế: `sản phẩm chính hãng`, `top_k=3` trên collection ChromaDB.
- Kết quả: 3/3 test được chọn đều pass; query thật trả 3 kết quả và vượt qua `validate_search_results(..., expected_method="bm25")`.
- Lỗi đã phát hiện và cách xử lý: ChromaDB có thể lược bỏ metadata `url` khi giá trị ban đầu là `None`. Khi nạp corpus, tôi khôi phục trường thành `url: None` để kết quả đáp ứng đầy đủ schema.

## Điều còn hạn chế

- Một hạn chế cụ thể: BM25 index đang được dựng lại ở mỗi lần gọi `lexical_search()`, dù corpus đã được cache.
- Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện: cache cả BM25 index và tokenized corpus, đồng thời bổ sung cơ chế refresh khi collection Task 4 thay đổi.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 25/09/2026
- Tên thành viên: Trần Vũ Gia Huy
