# Báo cáo đóng góp cá nhân

## Thông tin

- Họ và tên: Trần Mạnh Hùng
- Mã học viên: 2A202602708
- Nhóm: onedayonename
- Repository/branch: `K4-L3B-RAG-Pipeline` / `main`

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Task 1 – Thu thập tài liệu pháp lý | Refactor toàn bộ crawler: chuyển sang `AsyncWebCrawler` (crawl4ai), cấu trúc lại `SOURCES` thành list-of-dict, bổ sung lưu JSON metadata (`url`, `title`, `date_crawled`, `content_markdown`) song song với PDF. | `src/task1_collect_legal_docs.py`, commits `6a4926c`, `4743f61`, `d4d21ec` | Hoàn thành |
| Task 1 – Crawl 3 tài liệu Shopee | Crawl thực tế 3 URL chính sách Shopee (điều kiện, quy trình, thời gian trả hàng & hoàn tiền), lưu JSON và PDF vào `data/landing/legal/`. | `data/landing/legal/shopee_*_{77243,77244,77245}.json/.pdf`, commits `4743f61`, `d4d21ec`, `61a6d7d` | Hoàn thành |
| Task 4 – Chunking & Indexing | Triển khai pipeline load → chunk (RecursiveCharacterTextSplitter, 500/50) → embed (BAAI/bge-m3, multi-provider: `sentence_transformers` / `gemini` / `openai`) → upsert ChromaDB (cosine, idempotent). Thêm `_extract_url_from_markdown` hỗ trợ cả `**URL:**` và `**Source:**`. | `src/task4_chunking_indexing.py`, commits `4743f61`, `8a1eb70`, `8b7f4aa` | Hoàn thành |
| Task 4 – Build vector index | Chạy embedding thực tế và upsert toàn bộ corpus vào ChromaDB, file `chroma.sqlite3` tăng từ ~700 KB → ~11 MB (≈ toàn bộ 9 documents). | `chroma_db/chroma.sqlite3`, `chroma_db/*/data_level0.bin`, commits `8a1eb70`, `8b7f4aa` | Hoàn thành |
| Task 9 – Patch retrieval pipeline | Sửa URL regex của `_extract_url_from_markdown` để không cắt mất ký tự cuối URL khi có ngoặc đơn; cập nhật logic retrieval pipeline đồng bộ với schema mới của Task 4. | `src/task9_retrieval_pipeline.py`, commit `8b7f4aa` | Hoàn thành |


## Quyết định kỹ thuật quan trọng

1. **Lưu song song JSON + PDF thay vì chỉ PDF.**
   **Lý do/evidence:** Task 3 (`task3_convert_markdown.py`) đọc JSON từ `landing/legal/` để convert sang Markdown. Nếu chỉ có PDF, pipeline Task 3 không chạy được. Lưu JSON với đầy đủ metadata (`url`, `title`, `date_crawled`, `content_markdown`) giúp chuỗi Task 1 → 3 → 4 chạy liền mạch.
   **Trade-off:** Tăng kích thước repo do lưu cả hai định dạng, nhưng đảm bảo acceptance test của Task 1 (yêu cầu PDF) và dependency của Task 3 (yêu cầu JSON) đều pass.

2. **Dùng regex `**(?:URL|Source):**` thay vì chỉ `**Source:**` trong `_extract_url_from_markdown`.**
   **Lý do/evidence:** Task 3 sinh Markdown header với `**URL:**`, nhưng code Task 4 cũ chỉ match `**Source:**` → `url` metadata bị `None` cho toàn bộ chunk. Sau khi sửa, URL được truyền đúng vào ChromaDB metadata.
   **Trade-off:** Không có trade-off đáng kể; thay đổi là pure fix.

## Kiểm thử và kết quả

- Crawl 3 URL Shopee Help Center thành công, mỗi URL sinh ra 1 file JSON và 1 file PDF trong `data/landing/legal/`.
- Chạy `run_pipeline()` trong `task4_chunking_indexing.py`: load 9 documents (3 legal + 6 news), tạo chunk, embed bằng BAAI/bge-m3, upsert vào ChromaDB; kích thước `chroma.sqlite3` tăng từ 6.5 MB → ~11 MB sau commit `8b7f4aa`.
- Kiểm tra `_extract_url_from_markdown` với string `**URL:** https://...` và `**Source:** https://...` → cả hai trả về URL đúng, không cắt mất ký tự cuối.

## Điều còn hạn chế

- Corpus pháp lý chỉ bao gồm 3 chính sách Shopee (trả hàng & hoàn tiền). Các truy vấn liên quan đến chính sách khác (bảo mật, điều khoản dịch vụ) sẽ không có kết quả liên quan trong dense retrieval.
- Nếu có thêm thời gian: mở rộng `SOURCES` trong Task 1 để crawl thêm các trang chính sách Shopee còn lại, sau đó chạy lại Task 4 để rebuild index, giúp tăng coverage cho downstream retrieval.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 25/09/2026
- Tên thành viên: Trần Mạnh Hùng
