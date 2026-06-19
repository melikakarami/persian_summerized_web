"""
modules/logger.py
------------------
لاگ‌گیری متمرکز. برای هر اجرا (run) یک پوشه جدا ساخته می‌شود و هر مرحله
(search / scrape / summarize / main) فایل لاگ مخصوص به خودش را دارد.
هر لاگر هم‌زمان روی کنسول و فایل می‌نویسد.
"""

import logging
import os
import sys


_LOGGERS = {}


def get_logger(name: str, run_log_dir: str) -> logging.Logger:
    """
    یک لاگر برای مرحله مشخص (name) برمی‌گرداند که در پوشه run_log_dir
    فایل <name>.log می‌سازد. اگر قبلا ساخته شده باشد همان را برمی‌گرداند.
    """
    cache_key = f"{run_log_dir}:{name}"
    if cache_key in _LOGGERS:
        return _LOGGERS[cache_key]

    os.makedirs(run_log_dir, exist_ok=True)
    log_path = os.path.join(run_log_dir, f"{name}.log")

    logger = logging.getLogger(cache_key)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(fmt)
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(fmt)
    console_handler.setLevel(logging.INFO)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    _LOGGERS[cache_key] = logger
    return logger
