"""
Task 3 — Chuẩn hóa dữ liệu sang Markdown.

Hướng dẫn:
    1. Đọc JSON từ landing/legal/ và landing/news/.
    2. Giữ metadata ở đầu file Markdown.
    3. Giữ cấu trúc thư mục legal/ và news/.
    4. Không tạo file rỗng hoặc file trùng khi chạy lại.

JSON format trong landing:
    {
        "url": str,
        "title": str,
        "date_crawled": str,
        "content_markdown": str
    }
"""

import json
from pathlib import Path


LANDING_DIR = Path(__file__).parent.parent / "data" / "landing"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "standardized"


def _convert_json_to_markdown(
    input_path: Path,
    output_dir: Path,
    doc_type: str,
) -> int:
    """Convert JSON file sang Markdown.

    Args:
        input_path: Path đến file JSON.
        output_dir: Thư mục output.
        doc_type: "legal" hoặc "news".

    Returns:
        1 nếu thành công, 0 nếu thất bại hoặc skip.
    """
    output_path = output_dir / f"{input_path.stem}.md"

    # Skip nếu đã tồn tại (tránh trùng)
    if output_path.exists():
        print(f"Skip (exists): {output_path.name}")
        return 0

    try:
        data = json.loads(input_path.read_text(encoding="utf-8"))

        # Validate required fields
        url = data.get("url", "")
        title = data.get("title", "Untitled")
        date_crawled = data.get("date_crawled", "")
        content = data.get("content_markdown", "").strip()

        # Không tạo file rỗng
        if not content:
            print(f"Skip (empty): {input_path.name}")
            return 0

        # Build header với metadata
        header = (
            f"# {title}\n\n"
            f"**URL:** {url}\n\n"
            f"**Type:** {doc_type}\n\n"
            f"**Crawled:** {date_crawled}\n\n"
            f"---\n\n"
        )

        output_path.write_text(header + content, encoding="utf-8")
        print(f"Converted: {input_path.name} -> {output_path.name}")
        return 1

    except json.JSONDecodeError as e:
        print(f"Error (JSON): {input_path.name}: {e}")
        return 0
    except Exception as e:
        print(f"Error: {input_path.name}: {e}")
        return 0


def convert_legal_docs() -> int:
    """Convert JSON trong landing/legal -> standardized/legal.

    Returns:
        Số file đã convert thành công.
    """
    legal_input = LANDING_DIR / "legal"
    legal_output = OUTPUT_DIR / "legal"
    legal_output.mkdir(parents=True, exist_ok=True)

    count = 0
    for path in legal_input.iterdir():
        if path.suffix.lower() != ".json":
            continue
        count += _convert_json_to_markdown(path, legal_output, "legal")

    return count


def convert_news_articles() -> int:
    """Convert JSON trong landing/news -> standardized/news.

    Returns:
        Số file đã convert thành công.
    """
    news_input = LANDING_DIR / "news"
    news_output = OUTPUT_DIR / "news"
    news_output.mkdir(parents=True, exist_ok=True)

    count = 0
    for path in news_input.glob("*.json"):
        count += _convert_json_to_markdown(path, news_output, "news")

    return count


def convert_all() -> dict:
    """Convert toàn bộ dữ liệu landing.

    Returns:
        Dict với số file đã convert của mỗi loại.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=== Converting Legal Documents ===")
    legal_count = convert_legal_docs()

    print("\n=== Converting News Articles ===")
    news_count = convert_news_articles()

    result = {
        "legal": legal_count,
        "news": news_count,
        "total": legal_count + news_count,
    }

    print(f"\nDone! Converted {result['total']} files "
          f"(legal: {legal_count}, news: {news_count})")
    print(f"Output: {OUTPUT_DIR}")

    return result


if __name__ == "__main__":
    convert_all()
