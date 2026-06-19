"""
modules/scraper.py
-------------------
استخراج متن اصلی هر صفحه وب.
اولویت با trafilatura است (دقیق‌تر برای جدا کردن متن مقاله از منو/تبلیغ/فوتر).
اگر trafilatura نتیجه نداد، به requests + BeautifulSoup سقوط می‌کنیم.
"""

from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup

from config import Config
from modules.logger import get_logger

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}


def _extract_with_trafilatura(url: str, timeout: int) -> Optional[str]:
    import trafilatura

    downloaded = trafilatura.fetch_url(url, no_ssl=True)
    if not downloaded:
        return None
    text = trafilatura.extract(
        downloaded,
        include_comments=False,
        include_tables=False,
        favor_recall=True,
    )
    return text


def _extract_with_bs4(url: str, timeout: int) -> Optional[str]:
    resp = requests.get(url, headers=HEADERS, timeout=timeout)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.content, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
        tag.decompose()

    paragraphs = soup.find_all("p")
    text = "\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
    return text if text else None


def extract_page_text(url: str, cfg: Config) -> Optional[str]:
    """
    متن یک URL را برمی‌گرداند یا None در صورت شکست.
    """
    logger = get_logger("scrape", cfg.run_log_dir())
    text = None

    try:
        text = _extract_with_trafilatura(url, cfg.request_timeout)
        if text:
            logger.info(f"[trafilatura] موفق: {url} ({len(text)} کاراکتر)")
    except Exception as e:
        logger.warning(f"[trafilatura] شکست برای {url}: {e}")

    if not text:
        try:
            text = _extract_with_bs4(url, cfg.request_timeout)
            if text:
                logger.info(f"[bs4-fallback] موفق: {url} ({len(text)} کاراکتر)")
        except Exception as e:
            logger.error(f"[bs4-fallback] شکست برای {url}: {e}")

    if not text or len(text) < cfg.min_valid_text_len:
        logger.warning(f"رد شد (متن ناکافی یا خالی): {url}")
        return None

    return text[: cfg.max_chars_per_page]


def extract_all(search_results: List[Dict], cfg: Config) -> List[Dict]:
    """
    روی همه نتایج جستجو حلقه می‌زند، متن هر کدام را استخراج می‌کند
    و فقط صفحاتی که متن معتبر داشته‌اند را برمی‌گرداند.
    خروجی: [{title, url, snippet, text}, ...]
    """
    logger = get_logger("scrape", cfg.run_log_dir())
    pages = []

    for item in search_results:
        url = item["url"]
        logger.info(f"در حال استخراج: {url}")
        text = extract_page_text(url, cfg)
        if text:
            pages.append({**item, "text": text})
        else:
            logger.info(f"حذف شد از لیست نهایی (بدون محتوای قابل‌استفاده): {url}")

    logger.info(f"استخراج پایان یافت. {len(pages)} از {len(search_results)} صفحه معتبر بودند.")
    return pages
