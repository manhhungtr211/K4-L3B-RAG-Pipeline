# Individual contribution report

---

## Thông tin

- Họ và tên: Nguyễn Minh Tiến
- Mã học viên: 2A202602997
- Nhóm: onedayonename
- Repository/branch: main

## Phần việc đã thực hiện

| Module/deliverable        | Việc tôi trực tiếp làm                                                                                 | File/commit/PR                    | Trạng thái |
| ------------------------- | ----------------------------------------------------------------------------------------------------------- | --------------------------------- | ------------ |
| Crawl News (Task 2)       | Crawl 6 bài viết Shopee Help Center bằng AsyncWebCrawler, retry logic, semaphore cho concurrent requests | `src/task2_crawl_news.py`       | Done         |
| Convert Markdown (Task 3) | Chuẩn hóa JSON sang Markdown, giữ metadata header, idempotent (skip nếu tồn tại)                      | `src/task3_convert_markdown.py` | Done         |
| Semantic Search (Task 5)  | Semantic search với BGE-M3 embeddings, cosine distance → similarity conversion, sort descending           | `src/task5_semantic_search.py`  | Done         |
| Chatbot UI                | Streamlit interface với top_k slider, hybrid retrieval display, citation sources                           | `app.py`                        | Done         |

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Dùng AsyncWebCrawler với semaphore để giới hạn concurrent requests
   **Lý do/evidence:** Tránh overload server, 6 URLs crawl thành công 6/6
   **Trade-off:** Cần retry logic để handle transient failures
2. **Quyết định:** Cosine distance → similarity = max(0, 1 - distance)
   **Lý do/evidence:** ChromaDB trả về distance, cần convert sang similarity score cho uniform output
   **Trade-off:** Clipping negative values (distance > 1) về 0

## Kiểm thử và kết quả

- Test hoặc query tôi đã dùng:

  - Chạy `python src/task2_crawl_news.py` → 6 JSON files trong `data/landing/news/`
  - Chạy `python src/task3_convert_markdown.py` → Markdown files trong `data/standardized/`
  - Test semantic search: `python src/task5_semantic_search.py`
- Kết quả trước/sau nếu có:

  - Task 2: 0 → 6 articles crawled
  - Task 3: JSON → 9 Markdown files (3 legal + 6 news)
  - Semantic search: Dense retrieval baseline 0.795 avg → Hybrid + RRF 0.862 avg (+6.7%)
- Lỗi đã phát hiện và cách xử lý:

  - Crawl fail có thể xảy ra → retry logic với exponential backoff
  - Empty content → validation skip không tạo file rỗng

## Điều còn hạn chế

- Một hạn chế cụ thể của phần tôi làm:

  - Corpus chỉ có 9 documents, hạn chế coverage cho out-of-domain queries
- Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện:

  - Mở rộng corpus với thêm Shopee policies và FAQs

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 2026-09-25
- Tên thành viên: Nguyễn Minh Tiến
