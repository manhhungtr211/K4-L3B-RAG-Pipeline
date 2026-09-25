# Báo cáo đóng góp cá nhân

## Thông tin

- Họ và tên: Trần Vũ Gia Huy
- Mã học viên: 2A202602705
- Nhóm: Chưa cung cấp
- Repository/branch: `K4-L3B-RAG-Pipeline` / `main`

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Task 6 - Lexical search | Xây dựng tokenizer Unicode, BM25 index và hàm tìm kiếm theo từ khóa bằng `BM25Okapi` | `src/task6_lexical_search.py`, commit `9b44b8a` | Done |
| Tích hợp Task 4 và Task 6 | Nạp 700 chunks do Task 4 index trong ChromaDB để BM25 và dense retrieval dùng cùng corpus, ID và metadata | `src/task6_lexical_search.py`, commit `9b44b8a` | Done |
| Golden dataset | Xây dựng 20 câu hỏi, câu trả lời và context bám corpus, gồm dữ liệu bài viết và chính sách | `group_project/evaluation/golden_dataset.json`, commit `09eff5d` | Done |

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Nạp corpus BM25 từ collection ChromaDB do Task 4 tạo thay vì duy trì một bản corpus riêng.
   **Lý do/evidence:** Collection `rag_documents` chứa 700 chunks. Cách này bảo đảm Task 5 và Task 6 tham chiếu cùng ID, nội dung và metadata theo `MODULE_CONTRACTS.md`.
   **Trade-off:** Lần tìm kiếm đầu tiên phải đọc toàn bộ chunks; corpus được cache nên cần nạp lại nếu index thay đổi trong cùng tiến trình.

2. **Quyết định:** Tokenize bằng `casefold()` và regex Unicode, dùng số token trùng để phá hòa nhưng giữ nguyên BM25 score.
   **Lý do/evidence:** Cách này xử lý chữ hoa/thường và tiếng Việt nhất quán; tiêu chí phụ giúp xếp hạng ổn định khi `BM25Okapi` trả cùng điểm trên corpus nhỏ.
   **Trade-off:** Tokenizer chưa thực hiện tách từ tiếng Việt chuyên sâu.

## Kiểm thử và kết quả

- Test/query đã dùng: contract test của Task 6; ba test liên quan Task 4, Task 6 và chữ ký hàm; query `sản phẩm chính hãng` với `top_k=3`; acceptance test của golden dataset.
- Kết quả: các test được chọn đều pass; query thật trả 3 kết quả hợp lệ; golden dataset có 20 câu duy nhất, không có trường rỗng và vượt acceptance test.
- Lỗi đã phát hiện và cách xử lý: ChromaDB có thể lược bỏ `url` khi giá trị là `None`; Task 6 khôi phục `url: None` để đáp ứng schema.

## Điều còn hạn chế

- BM25 index vẫn được dựng lại ở mỗi lần gọi `lexical_search()`, dù corpus đã được cache.
- Nếu có thêm thời gian, tôi sẽ cache BM25 index và bổ sung cơ chế refresh khi collection Task 4 thay đổi.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 25/09/2026
- Tên thành viên: Trần Vũ Gia Huy
