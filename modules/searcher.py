"""
modules/searcher.py
--------------------
جستجوی موضوعی در وب با DuckDuckGo (بدون نیاز به API key).
خروجی: لیستی از دیکشنری {title, url, snippet}
"""

from typing import List, Dict
from config import Config
from modules.logger import get_logger


def _get_ddgs_client():
    """
    سازگاری با هر دو نام پکیج: ddgs (جدید) و duckduckgo_search (قدیمی).
    """
    try:
        from ddgs import DDGS
        return DDGS
    except ImportError:
        from duckduckgo_search import DDGS
        return DDGS


def search_persian_pages(cfg: Config) -> List[Dict]:
    """
    موضوع را در DuckDuckGo جستجو می‌کند و num_sites نتیجه معتبر برمی‌گرداند.
    اگر نتایج کافی نبود، چند بار دیگر با تعداد بیشتر تلاش می‌کند.
    """
    logger = get_logger("search", cfg.run_log_dir())
    DDGS = _get_ddgs_client()

    query = cfg.topic.strip()
    logger.info(f"شروع جستجو برای موضوع: '{query}' | تعداد هدف: {cfg.num_sites}")

    results: List[Dict] = []
    seen_urls = set()
    fetch_count = cfg.num_sites * 3  # کمی بیشتر می‌گیریم تا بعد از فیلتر، عدد num_sites کامل شود
    attempts = 0

    while len(results) < cfg.num_sites and attempts <= cfg.extra_search_retries:
        attempts += 1
        logger.debug(f"تلاش شماره {attempts} | درخواست {fetch_count} نتیجه از DuckDuckGo")
        try:
            with DDGS() as ddgs:
                raw_results = list(
                    ddgs.text(
                        query,
                        region=cfg.search_region,
                        safesearch=cfg.search_safesearch,
                        max_results=fetch_count,
                    )
                )
        except Exception as e:
            logger.error(f"خطا در جستجو (تلاش {attempts}): {e}")
            raw_results = []

        for r in raw_results:
            url = r.get("href") or r.get("url")
            title = r.get("title", "")
            snippet = r.get("body", "")
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)
            results.append({"title": title, "url": url, "snippet": snippet})
            logger.info(f"نتیجه یافت شد: {title} -> {url}")
            if len(results) >= cfg.num_sites:
                break

        fetch_count *= 2  # اگر کافی نبود، دفعه بعد بیشتر بخواه

    if len(results) < cfg.num_sites:
        logger.warning(
            f"فقط {len(results)} نتیجه از {cfg.num_sites} مورد درخواستی پیدا شد."
        )
    else:
        logger.info(f"جستجو کامل شد. {len(results)} نتیجه نهایی.")

    return results[: cfg.num_sites]
