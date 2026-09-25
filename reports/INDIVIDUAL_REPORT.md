# Báo cáo đóng góp cá nhân

## Thông tin

- Họ và tên: Phạm Anh Minh
- Mã học viên: 2A202603009
- Nhóm: onedayonename
- Repository/branch: `K4-L3B-RAG-Pipeline` / `minh`

## Phần việc đã thực hiện

| Module | Phần việc trực tiếp thực hiện | File | Trạng thái |
|---|---|---|---|
| Task 7 - RRF reranking | Triển khai Reciprocal Rank Fusion, loại kết quả trùng theo ID, sắp xếp điểm, giới hạn `top_k` và gắn nhãn kết quả `hybrid`. | `src/task7_reranking.py` | Hoàn thành |
| Task 8 - PageIndex fallback | Bổ sung lớp tích hợp PageIndex an toàn, cơ chế cache tài liệu và xử lý an toàn khi provider hoặc API key không khả dụng. | `src/task8_pageindex_vectorless.py` | Hoàn thành |
| Task 9 - Retrieval pipeline | Kết nối dense search, lexical search, RRF và PageIndex fallback. Fallback sử dụng điểm dense gốc và lỗi provider không làm pipeline bị crash. | `src/task9_retrieval_pipeline.py` | Hoàn thành |
| Task 10 - Generation | Triển khai sắp xếp context, định dạng context có citation, gọi Gemini với model `gemini-3.8-flash` và cơ chế từ chối an toàn. | `src/task10_generation.py` | Hoàn thành |
| Xử lý merge conflict | Xử lý conflict của Task 9 và push kết quả cuối lên `origin/main`. | `src/task9_retrieval_pipeline.py` | Hoàn thành |

## Các quyết định kỹ thuật quan trọng

1. **Dùng RRF thay vì cộng trực tiếp điểm dense và lexical.** Mỗi tài liệu nhận điểm `1 / (k + rank)` từ từng bảng xếp hạng. Cách này giữ nguyên sự khác biệt giữa các thang điểm và tạo kết quả duy nhất theo ID ổn định.

2. **Dùng điểm dense gốc để quyết định fallback.** Task 9 so sánh điểm dense cao nhất với `SCORE_THRESHOLD`, không so sánh với điểm RRF vì hai loại điểm có ý nghĩa và thang đo khác nhau.

## Kiểm thử và kết quả

- Đã kiểm tra cú pháp các module đã sửa bằng `python -m py_compile`.
- Đã đối chiếu interface của Task 7–10 với module contracts của repository.
- Đã kiểm tra các trường hợp RRF loại trùng, fallback theo điểm dense và xử lý lỗi provider.
- Đã cấu hình Task 10 sử dụng `GEMINI_API_KEY`, provider `gemini` và model `gemini-3.8-flash`.
- Không commit API key hoặc response từ provider bên ngoài vào repository.

## Điều còn hạn chế và hướng phát triển

- Chức năng upload và query PageIndex cần được kiểm tra thêm với tài khoản provider thật đã cấu hình.
- Gemini yêu cầu `GEMINI_API_KEY` hợp lệ và dependency `google-genai`.
- Các chỉ số đánh giá đầy đủ trong `reports/RESULT.md` chưa được điền vì chưa chạy golden-dataset evaluation.

## Xác nhận đóng góp

Tôi xác nhận báo cáo này phản ánh đúng các phần việc trực tiếp đã thực hiện và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 25/09/2026
- Tên thành viên: Phạm Anh Minh
