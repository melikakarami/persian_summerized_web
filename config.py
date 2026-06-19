"""
config.py
---------
تمام تنظیمات سامانه به صورت متمرکز اینجا تعریف شده‌اند.
هر مقدار هم می‌تواند از طریق آرگومان خط فرمان (main.py) و هم برنامه‌نویسی
(import کردن Config) تغییر کند. این فایل مرکز "پویا بودن" پروژه است.
"""

from dataclasses import dataclass, field
from datetime import datetime
import os


@dataclass
class Config:
    # ---------------- جستجو ----------------
    topic: str = ""                      # موضوعی که کاربر می‌دهد
    num_sites: int = 5                   # تعداد صفحاتی که باید جستجو/استخراج شوند (آرگومان پویا)
    search_region: str = "ir-fa"         # ناحیه جستجو در DuckDuckGo برای نتایج فارسی
    search_safesearch: str = "moderate"
    extra_search_retries: int = 2        # اگر تعداد نتایج کافی نبود، چند بار دیگر تلاش شود

    # ---------------- استخراج محتوا ----------------
    max_chars_per_page: int = 6000       # حداکثر کاراکتر خام نگه‌داشته‌شده از هر صفحه
    request_timeout: int = 15            # ثانیه
    min_valid_text_len: int = 200        # صفحاتی با متن کمتر از این، نامعتبر در نظر گرفته می‌شوند

    # ---------------- خلاصه‌سازی (LLM) ----------------
    model_name: str = "Qwen/Qwen2.5-1.5B-Instruct"   # مدل سبک پیش‌فرض
    use_4bit: bool = False               # کوانتیزیشن 4-بیتی (در صورت نیاز به کاهش مصرف VRAM)
    device: str = "auto"                 # "auto" | "cuda" | "cpu"
    per_page_summary_max_new_tokens: int = 220
    final_summary_max_new_tokens: int = 450
    temperature: float = 0.4

    # ---------------- خروجی و لاگ ----------------
    output_dir: str = "outputs"
    log_dir: str = "logs"
    run_id: str = field(default_factory=lambda: datetime.now().strftime("%Y%m%d_%H%M%S"))
    save_intermediate_json: bool = True  # ذخیره نتایج میانی (جستجو، متن خام، خلاصه هر صفحه)

    def run_log_dir(self) -> str:
        path = os.path.join(self.log_dir, f"run_{self.run_id}")
        os.makedirs(path, exist_ok=True)
        return path

    def run_output_dir(self) -> str:
        path = os.path.join(self.output_dir, f"run_{self.run_id}")
        os.makedirs(path, exist_ok=True)
        return path
