"""
Task 8 — PageIndex vectorless fallback.

Hướng dẫn:
    1. Đọc PAGEINDEX_API_KEY từ .env.
    2. Upload tài liệu ở định dạng PageIndex hỗ trợ.
    3. Cache document IDs để không upload lại.
    4. Parse kết quả thành SearchResult có method pageindex.

PageIndex là dịch vụ ngoài: cần timeout và xử lý lỗi để pipeline không crash.
"""

import os
import json
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY", "")
STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CACHE_PATH = STANDARDIZED_DIR.parent / "pageindex_documents.json"


def upload_documents() -> None:
    """Upload tài liệu và lưu document IDs để tái sử dụng."""
    # TODO: Upload documents và lưu mapping source -> document ID.
    #
    # Nếu SDK không nhận Markdown, convert sang PDF tạm trước khi upload.
    # Kiểm tra response thật của SDK thay vì đoán tên field.
    if not PAGEINDEX_API_KEY or not STANDARDIZED_DIR.exists():
        return
    cache = {}
    if CACHE_PATH.exists():
        try:
            cache = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    for path in STANDARDIZED_DIR.iterdir():
        if path.is_file():
            cache.setdefault(path.name, None)
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """Trả về pageindex SearchResult."""
    # TODO: Query các document IDs và parse retrieved nodes.
    #
    # Mỗi result cần: id, content, score, metadata, retrieval_method.
    # Nếu API không trả score, có thể gán score giảm dần theo rank.
    if not PAGEINDEX_API_KEY or top_k <= 0:
        return []
    return []


if __name__ == "__main__":
    upload_documents()
