"""
Task 2 — Crawl bài viết/thông báo.

Hướng dẫn:
    1. Điền tối thiểu 5 URL công khai vào ARTICLE_URLS.
    2. Crawl từng URL bằng Crawl4AI.
    3. Lưu mỗi bài thành một JSON trong data/landing/news/.
    4. Giữ đủ url, title, date_crawled và content_markdown.

Cài browser trước khi chạy:
    python -m playwright install chromium
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from crawl4ai import AsyncWebCrawler


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"

# Danh sách URL cần crawl
BASE_SHOPEE = "https://help.shopee.vn/portal/4/article/"
ARTICLE_URLS = [
    BASE_SHOPEE + "79368",
    BASE_SHOPEE + "79550",
    BASE_SHOPEE + "125827",
    BASE_SHOPEE + "79476",
    BASE_SHOPEE + "134226",
    BASE_SHOPEE + "134509",
]


async def crawl_article(
    url: str,
    max_retries: int = 3,
    delay: float = 1.0,
) -> Optional[dict]:
    """Crawl a single article URL with retry logic.

    Args:
        url: URL to crawl.
        max_retries: Number of retry attempts on failure.
        delay: Delay between retries in seconds.

    Returns:
        Dict with url, title, date_crawled, content_markdown, or None on failure.
    """
    for attempt in range(max_retries):
        try:
            async with AsyncWebCrawler() as crawler:
                result = await crawler.arun(url=url)
                return {
                    "url": url,
                    "title": result.metadata.get("title", "Unknown"),
                    "date_crawled": datetime.now().isoformat(),
                    "content_markdown": result.markdown,
                }
        except Exception as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(delay * (attempt + 1))
            else:
                return None
    return None


async def crawl_all(max_concurrent: int = 3) -> dict:
    """Crawl all URLs concurrently and save to JSON files.

    Args:
        max_concurrent: Maximum number of concurrent crawl operations.

    Returns:
        Summary dict with success and failure counts.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    semaphore = asyncio.Semaphore(max_concurrent)
    results = {"success": 0, "failed": 0, "articles": []}

    async def crawl_with_semaphore(index: int, url: str) -> tuple[int, bool]:
        async with semaphore:
            article = await crawl_article(url)
            if article:
                output = DATA_DIR / f"article_{index:02d}.json"
                output.write_text(
                    json.dumps(article, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
                print(f"Saved: {output}")
                return index, True
            print(f"Failed: {url}")
            return index, False

    tasks = [
        crawl_with_semaphore(i, url)
        for i, url in enumerate(ARTICLE_URLS, 1)
    ]
    outcomes = await asyncio.gather(*tasks, return_exceptions=True)

    for outcome in outcomes:
        if isinstance(outcome, Exception):
            results["failed"] += 1
        elif outcome[1]:
            results["success"] += 1
        else:
            results["failed"] += 1

    return results


if __name__ == "__main__":
    results = asyncio.run(crawl_all())
    print(f"\nDone! Success: {results['success']}, Failed: {results['failed']}")
