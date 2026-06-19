"""
main.py
-------
نقطه ورود سامانه. مراحل:
  1) جستجوی موضوعی فارسی در وب (DuckDuckGo)
  2) استخراج متن صفحات یافت‌شده
  3) خلاصه‌سازی دو مرحله‌ای با LLM سبک (Qwen2.5 یا هر مدل دیگر)
  4) ذخیره و نمایش خروجی نهایی

استفاده:
    python main.py --topic "هوش مصنوعی در پزشکی" --num-sites 5
"""

import argparse
import json
import os
import sys
import time

from config import Config
from modules.logger import get_logger
from modules.searcher import search_persian_pages
from modules.scraper import extract_all
from modules.summarizer import Summarizer


def parse_args() -> Config:
    parser = argparse.ArgumentParser(
        description="سامانه جستجو، استخراج و خلاصه‌سازی موضوعی محتوای وب فارسی"
    )
    parser.add_argument("--topic", required=True, help="موضوع مورد جستجو")
    parser.add_argument("--num-sites", type=int, default=5, help="تعداد صفحات هدف (پویا)")
    parser.add_argument("--model", default="Qwen/Qwen2.5-1.5B-Instruct", help="نام مدل HuggingFace")
    parser.add_argument("--max-chars", type=int, default=6000, help="حداکثر کاراکتر خام هر صفحه")
    parser.add_argument("--use-4bit", action="store_true", help="فعال‌سازی کوانتیزیشن 4-بیتی")
    parser.add_argument("--device", default="auto", help="auto | cuda | cpu")
    parser.add_argument("--output-dir", default="outputs")
    parser.add_argument("--log-dir", default="logs")

    args = parser.parse_args()

    cfg = Config(
        topic=args.topic,
        num_sites=args.num_sites,
        model_name=args.model,
        max_chars_per_page=args.max_chars,
        use_4bit=args.use_4bit,
        device=args.device,
        output_dir=args.output_dir,
        log_dir=args.log_dir,
    )
    return cfg


def run(cfg: Config):
    logger = get_logger("main", cfg.run_log_dir())
    t0 = time.time()
    logger.info("=" * 60)
    logger.info(f"شروع اجرا | موضوع: '{cfg.topic}' | تعداد صفحات هدف: {cfg.num_sites}")
    logger.info("=" * 60)

    out_dir = cfg.run_output_dir()

    # ---------- مرحله ۱: جستجو ----------
    search_results = search_persian_pages(cfg)
    if not search_results:
        logger.error("هیچ نتیجه‌ای از جستجو یافت نشد. اجرا متوقف شد.")
        sys.exit(1)

    if cfg.save_intermediate_json:
        with open(os.path.join(out_dir, "1_search_results.json"), "w", encoding="utf-8") as f:
            json.dump(search_results, f, ensure_ascii=False, indent=2)

    # ---------- مرحله ۲: استخراج متن ----------
    pages = extract_all(search_results, cfg)
    if not pages:
        logger.error("هیچ صفحه‌ای محتوای قابل‌استخراج نداشت. اجرا متوقف شد.")
        sys.exit(1)

    if cfg.save_intermediate_json:
        dump = [{"title": p["title"], "url": p["url"], "text_preview": p["text"][:300]} for p in pages]
        with open(os.path.join(out_dir, "2_extracted_pages.json"), "w", encoding="utf-8") as f:
            json.dump(dump, f, ensure_ascii=False, indent=2)

    # ---------- مرحله ۳: خلاصه‌سازی ----------
    summarizer = Summarizer(cfg)
    page_summaries = summarizer.summarize_all_pages(pages, cfg.topic)

    if cfg.save_intermediate_json:
        dump = [{"title": p["title"], "url": p["url"], "page_summary": p["page_summary"]} for p in page_summaries]
        with open(os.path.join(out_dir, "3_page_summaries.json"), "w", encoding="utf-8") as f:
            json.dump(dump, f, ensure_ascii=False, indent=2)

    final_summary = summarizer.summarize_final(page_summaries, cfg.topic)

    # ---------- مرحله ۴: ذخیره و نمایش خروجی نهایی ----------
    sources_block = "\n".join(f"- {p['title']}: {p['url']}" for p in page_summaries)

    final_text = (
        f"موضوع: {cfg.topic}\n"
        f"تعداد منابع استفاده‌شده: {len(page_summaries)}\n\n"
        f"خلاصه نهایی:\n{final_summary}\n\n"
        f"منابع:\n{sources_block}\n"
    )

    final_path = os.path.join(out_dir, "final_summary.txt")
    with open(final_path, "w", encoding="utf-8") as f:
        f.write(final_text)

    json_path = os.path.join(out_dir, "final_summary.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "topic": cfg.topic,
                "summary": final_summary,
                "sources": [{"title": p["title"], "url": p["url"]} for p in page_summaries],
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    elapsed = time.time() - t0
    logger.info(f"اجرا با موفقیت پایان یافت در {elapsed:.1f} ثانیه.")
    logger.info(f"خروجی متنی: {final_path}")
    logger.info(f"خروجی JSON: {json_path}")

    print("\n" + "=" * 60)
    print(final_text)
    print("=" * 60)

    return final_text


if __name__ == "__main__":
    config = parse_args()
    run(config)
