"""
modules/summarizer.py
----------------------
خلاصه‌سازی دو مرحله‌ای (map-reduce) با یک LLM سبک محلی (پیش‌فرض: Qwen2.5-1.5B-Instruct).

مرحله ۱ (map):   هر صفحه به‌تنهایی خلاصه می‌شود (برای کنترل طول ورودی مدل).
مرحله ۲ (reduce): خلاصه‌های مرحله ۱ با هم ترکیب و یک خلاصه نهایی کوتاه و
                   روان فارسی تولید می‌شود.

مدل فقط یک‌بار بارگذاری می‌شود (lazy singleton) تا روی Colab سریع‌تر اجرا شود.
"""

from typing import List, Dict
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from config import Config
from modules.logger import get_logger


class Summarizer:
    _model = None
    _tokenizer = None
    _loaded_model_name = None

    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.logger = get_logger("summarize", cfg.run_log_dir())
        self._load_model()

    def _load_model(self):
        if Summarizer._model is not None and Summarizer._loaded_model_name == self.cfg.model_name:
            self.logger.info(f"مدل از قبل بارگذاری شده، استفاده مجدد: {self.cfg.model_name}")
            return

        self.logger.info(f"در حال بارگذاری مدل: {self.cfg.model_name} ...")

        load_kwargs = {"torch_dtype": "auto", "device_map": self.cfg.device}

        if self.cfg.use_4bit:
            try:
                from transformers import BitsAndBytesConfig
                load_kwargs["quantization_config"] = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                )
                self.logger.info("کوانتیزیشن 4-بیتی فعال شد.")
            except Exception as e:
                self.logger.warning(f"بارگذاری 4-بیتی ممکن نشد، حالت عادی اجرا می‌شود: {e}")

        Summarizer._tokenizer = AutoTokenizer.from_pretrained(self.cfg.model_name)
        Summarizer._model = AutoModelForCausalLM.from_pretrained(
            self.cfg.model_name, **load_kwargs
        )
        Summarizer._loaded_model_name = self.cfg.model_name
        self.logger.info("مدل با موفقیت بارگذاری شد.")

    def _generate(self, system_prompt: str, user_prompt: str, max_new_tokens: int) -> str:
        tokenizer = Summarizer._tokenizer
        model = Summarizer._model

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        inputs = tokenizer([text], return_tensors="pt").to(model.device)

        output_ids = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=self.cfg.temperature,
            do_sample=self.cfg.temperature > 0,
            pad_token_id=tokenizer.eos_token_id,
        )
        generated = output_ids[0][inputs["input_ids"].shape[1]:]
        result = tokenizer.decode(generated, skip_special_tokens=True)
        return result.strip()

    def summarize_page(self, page: Dict, topic: str) -> str:
        """مرحله ۱: خلاصه کردن یک صفحه."""
        system_prompt = (
            "تو یک دستیار خلاصه‌سازی متن فارسی هستی. خلاصه‌ای دقیق، بی‌طرف و "
            "روان از متن داده‌شده بنویس و فقط به نکات مرتبط با موضوع کاربر بپرداز."
        )
        user_prompt = (
            f"موضوع مورد نظر کاربر: {topic}\n\n"
            f"منبع: {page['url']}\n"
            f"متن صفحه:\n{page['text']}\n\n"
            "این متن را در ۴ تا ۶ جمله، فقط به زبان فارسی خلاصه کن."
        )
        self.logger.info(f"خلاصه‌سازی مرحله ۱ برای: {page['url']}")
        summary = self._generate(
            system_prompt, user_prompt, self.cfg.per_page_summary_max_new_tokens
        )
        self.logger.debug(f"خلاصه صفحه ({page['url']}):\n{summary}")
        return summary

    def summarize_all_pages(self, pages: List[Dict], topic: str) -> List[Dict]:
        """مرحله ۱ برای همه صفحات."""
        results = []
        for page in pages:
            summary = self.summarize_page(page, topic)
            results.append({**page, "page_summary": summary})
        return results

    def summarize_final(self, page_summaries: List[Dict], topic: str) -> str:
        """مرحله ۲: ترکیب خلاصه‌های مرحله ۱ در یک خلاصه نهایی."""
        combined = "\n\n".join(
            f"- منبع {i+1} ({p['url']}):\n{p['page_summary']}"
            for i, p in enumerate(page_summaries)
        )
        system_prompt = (
            "تو یک دستیار حرفه‌ای تولید محتوای فارسی هستی. وظیفه‌ات ترکیب چند "
            "خلاصه از منابع مختلف وب در یک خلاصه نهایی واحد، کوتاه، کامل و "
            "قابل‌فهم برای خواننده عادی است. از تکرار خودداری کن و در صورت "
            "تناقض بین منابع، به آن اشاره کن."
        )
        user_prompt = (
            f"موضوع: {topic}\n\n"
            f"خلاصه‌های جمع‌آوری‌شده از {len(page_summaries)} منبع:\n{combined}\n\n"
            "یک خلاصه نهایی منسجم (حدود ۲۰۰ تا ۳۰۰ کلمه) فقط به زبان فارسی بنویس "
            "که نکات اصلی همه منابع را پوشش دهد."
        )
        self.logger.info("شروع خلاصه‌سازی نهایی (مرحله ۲) ...")
        final_summary = self._generate(
            system_prompt, user_prompt, self.cfg.final_summary_max_new_tokens
        )
        self.logger.info("خلاصه نهایی تولید شد.")
        self.logger.debug(f"خلاصه نهایی:\n{final_summary}")
        return final_summary
