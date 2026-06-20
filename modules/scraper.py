"""
modules/scraper.py
-------------------
استخراج متن اصلی صفحات وب
اولویت با trafilatura است و در صورت شکست از BeautifulSoup استفاده می‌شود.
استخراج صفحات به صورت موازی انجام می‌شود.
"""

from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
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


# ================= Session =================

session = requests.Session()

retry_strategy = Retry(
    total=1,
    connect=0,
    read=0,
    backoff_factor=0,
    status_forcelist=[429, 500, 502, 503, 504],
)

adapter = HTTPAdapter(
    max_retries=retry_strategy,
    pool_connections=20,
    pool_maxsize=20,
)

session.mount("http://", adapter)
session.mount("https://", adapter)

session.headers.update(HEADERS)


# ===========================================


def _extract_with_trafilatura(url: str, timeout: int) -> Optional[str]:
    import trafilatura

    downloaded = trafilatura.fetch_url(
        url,
        no_ssl=True
    )

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

    resp = session.get(
        url,
        timeout=timeout
    )

    resp.raise_for_status()

    soup = BeautifulSoup(resp.content, "html.parser")

    for tag in soup(
            ["script", "style", "nav", "footer",
             "header", "noscript"]):
        tag.decompose()

    paragraphs = soup.find_all("p")

    text = "\n".join(
        p.get_text(strip=True)
        for p in paragraphs
        if p.get_text(strip=True)
    )

    return text if text else None


def extract_page_text(url: str, cfg: Config) -> Optional[str]:

    logger = get_logger("scrape", cfg.run_log_dir())

    text = None

    try:
        text = _extract_with_trafilatura(
            url,
            cfg.request_timeout
        )

        if text:
            logger.info(
                f"[trafilatura] موفق: {url} ({len(text)} کاراکتر)"
            )

    except Exception as e:

        logger.warning(
            f"[trafilatura] شکست برای {url}: {e}"
        )

    if not text:

        try:
            text = _extract_with_bs4(
                url,
                cfg.request_timeout
            )

            if text:
                logger.info(
                    f"[bs4] موفق: {url} ({len(text)} کاراکتر)"
                )

        except Exception as e:

            logger.error(
                f"[bs4] شکست برای {url}: {e}"
            )

    if not text or len(text) < cfg.min_valid_text_len:

        logger.warning(
            f"رد شد (متن ناکافی): {url}"
        )

        return None

    return text[:cfg.max_chars_per_page]


def extract_all(search_results: List[Dict],
                cfg: Config) -> List[Dict]:
    """
    استخراج موازی همه صفحات
    """

    logger = get_logger("scrape", cfg.run_log_dir())

    pages = []

    max_workers = min(10, len(search_results))

    logger.info(
        f"شروع استخراج موازی با {max_workers} Thread"
    )

    with ThreadPoolExecutor(
            max_workers=max_workers) as executor:

        future_to_item = {
            executor.submit(
                extract_page_text,
                item["url"],
                cfg
            ): item
            for item in search_results
        }

        for future in as_completed(future_to_item):

            item = future_to_item[future]

            url = item["url"]

            try:

                text = future.result()

                if text:

                    pages.append({
                        **item,
                        "text": text
                    })

                    logger.info(
                        f"استخراج موفق: {url}"
                    )

                else:

                    logger.info(
                        f"حذف شد: {url}"
                    )

            except Exception as e:

                logger.error(
                    f"خطا در {url}: {e}"
                )

    logger.info(
        f"پایان استخراج. "
        f"{len(pages)} از {len(search_results)} صفحه معتبر بودند."
    )

    return pages