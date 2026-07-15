import gradio as gr

from config import Config
from main import run


# -----------------------
# Backend
# -----------------------

def generate(topic, num_sites):

    if not topic.strip():
        return (
            "⚠️ لطفاً موضوع را وارد کنید.",
            ""
        )

    try:

        cfg = Config(
            topic=topic,
            num_sites=num_sites,
        )

        result = run(cfg)

        summary = result["summary"]

        sources = ""

        for s in result["sources"]:
            sources += (
                f"### {s['title']}\n"
                f"{s['url']}\n\n"
            )

        return summary, sources

    except Exception as e:
        return f"❌ خطا:\n{e}", ""


# -----------------------
# CSS مدرن، شیک و مینیمال (تم خاکستری-کرم و سرچ‌باکس شبه‌گوگل)
# -----------------------

css = """
/* حذف فوتر پیش‌فرض گرادیو */
footer {
    display: none !important;
}

/* رنگ پس‌زمینه نرم خاکستری-کرم کل صفحه */
body {
    background: #f4f3ef !important; /* کرم-خاکستری بسیار ملایم */
    font-family: 'Vazirmatn', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* استایل کانتینر اصلی */
.gradio-container {
    max-width: 900px !important; /* جمع‌وجورتر برای شباهت به ساختار گوگل */
    margin: 50px auto !important;
    padding: 0 !important;
    background: transparent !important;
}

/* کارت‌های شیشه‌ای با تم کرم روشن */
.gr-group, .block {
    border-radius: 28px !important;
    border: 1px solid #e9e8e3 !important;
    background: #faf9f5 !important; /* کرم بسیار روشن و گرم */
    box-shadow: 0 10px 30px -10px rgba(112, 108, 97, 0.1) !important;
    padding: 24px !important;
    transition: all 0.3s ease;
}

/* استایل سرچ‌باکس شبه‌گوگل (پهن و گرد) */
textarea, input[type="text"] {
    background-color: #ffffff !important;
    border: 1.5px solid #dcdad2 !important;
    color: #3c3a36 !important; /* متن خاکستری تیره گرم */
    border-radius: 30px !important; /* لبه‌های کاملاً گرد مانند گوگل */
    
    /* ایجاد پدینگ در سمت راست برای قرارگیری آیکون ذره‌بین */
    padding: 14px 50px 14px 20px !important; 
    
    /* قراردادن آیکون ذره‌بین در سمت راست (RTL) */
    background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%238a877f' width='20' height='20'><path stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z'/></svg>") !important;
    background-repeat: no-repeat !important;
    background-position: right 20px center !important;
    background-size: 20px !important;
    
    box-shadow: 0 2px 8px rgba(112, 108, 97, 0.05) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    font-size: 16px !important;
}

/* رنگ متن راهنما (Placeholder) هماهنگ با تم کرم-خاکستری */
textarea::placeholder, input[type="text"]::placeholder {
    color: #a6a39a !important;
}

/* افکت فوکوس هوشمند سرچ‌باکس */
textarea:focus, input[type="text"]:focus {
    border-color: #8a877f !important; /* تیره شدن حاشیه */
    background-color: #ffffff !important;
    box-shadow: 0 4px 15px rgba(112, 108, 97, 0.12) !important; /* سایه عمیق‌تر و نرم‌تر */
    outline: none !important;
}

/* استایل دکمه با تم خاکستری تیره گرم */
#submit-btn {
    background: #4a4741 !important; /* خاکستری تیره گرم */
    color: #fcfbf9 !important;
    border: none !important;
    height: 50px !important;
    font-size: 16px !important;
    font-weight: 700 !important;
    border-radius: 30px !important; /* هماهنگ با گردی سرچ‌باکس */
    cursor: pointer !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 12px rgba(74, 71, 65, 0.15) !important;
}

#submit-btn:hover {
    background: #383530 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 18px rgba(74, 71, 65, 0.25) !important;
}

/* زیباسازی بخش نمونه‌ها (Examples) */
.gr-samples-item {
    border-radius: 20px !important;
    background: #f0eee7 !important;
    border: 1px solid #e1ded5 !important;
    color: #5c5952 !important;
    transition: all 0.2s !important;
}

.gr-samples-item:hover {
    background: #e5e2d8 !important;
    transform: translateY(-1px);
}

/* زیباسازی تب‌های خروجی */
.tabs {
    border-bottom: 2px solid #e2e1da !important;
}

.tab-nav button.selected {
    color: #4a4741 !important;
    border-bottom-color: #4a4741 !important;
    font-weight: bold !important;
}
"""


# -----------------------
# UI
# -----------------------

# استفاده از رنگ‌های خنثی و خاکستری گرم در تم پیش‌فرض گرادیو
custom_theme = gr.themes.Soft(
    primary_hue="stone",
    secondary_hue="stone",
    neutral_hue="stone",
)

with gr.Blocks(
    title="Persian News Summarizer"
) as demo:

    # هدر مینی‌مالیستی و شیک کرم-خاکستری
    gr.HTML("""
    <div style="
        padding: 30px 20px;
        border-radius: 24px;
        background: #faf9f5;
        border: 1px solid #e9e8e3;
        color: #4a4741;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 10px 25px -10px rgba(112, 108, 97, 0.08);
    ">
        <h1 style="font-size: 32px; font-weight: 800; margin: 0; color: #3c3a36;">
            📰 Persian News Summarizer
        </h1>
        <p style="font-size: 16px; opacity: 0.8; margin-top: 10px; font-weight: 400; color: #706c61;">
            جستجو، استخراج و خلاصه‌سازی هوشمند اخبار فارسی
        </p>
    </div>
    """)

    # بخش جستجو به سبک گوگل (کشیده و فاقد ستون‌های دراز عمودی)
    with gr.Group():
        with gr.Row():
            with gr.Column(scale=4):
                topic = gr.Textbox(
                    label="", # حذف عنوان بالای فیلد برای شباهت بیشتر به گوگل
                    placeholder="چیزی تایپ کنید یا جستجو کنید...",
                    lines=1, # حتماً تک‌خطی برای جلوگیری از فرم مستطیلی بزرگ
                    autofocus=True
                )
            with gr.Column(scale=1):
                num_sites = gr.Slider(
                    minimum=2,
                    maximum=10,
                    value=5,
                    step=1,
                    label="تعداد منابع"
                )
        
        button = gr.Button(
            "جستجو و خلاصه‌سازی",
            variant="primary",
            elem_id="submit-btn"
        )

    status = gr.Markdown(
        "<p style='text-align: center; color: #8a877f; font-size: 14px; margin-top: 10px;'>🟢 آماده دریافت موضوع جدید</p>"
    )

    # -----------------------
    # Outputs (خروجی‌ها)
    # -----------------------
    gr.HTML("<div style='margin-top: 25px;'></div>")
    
    with gr.Tabs():
        with gr.Tab("📝 خلاصه نهایی"):
            summary = gr.Textbox(
                lines=15,
                placeholder="نتیجه خلاصه‌سازی اینجا نمایش داده می‌شود...",
                interactive=False
            )

        with gr.Tab("🔗 منابع استخراج‌شده"):
            sources = gr.Markdown(
                value="*منابع پس از پایان فرآیند جستجو در این بخش لیست خواهند شد.*"
            )

    # -----------------------
    # Examples (نمونه‌ها)
    # -----------------------
    gr.HTML("<div style='margin-top: 30px;'></div>")
    
    gr.Examples(
        examples=[
            ["هوش مصنوعی در پزشکی", 5],
            ["اقتصاد ایران", 5],
            ["بازار خودرو", 5],
            ["فوتبال ایران", 4],
            ["ارز دیجیتال", 5],
            ["بورس تهران", 5]
        ],
        inputs=[
            topic,
            num_sites
        ]
    )

    # -----------------------
    # Events (رویدادها)
    # -----------------------
    button.click(
        fn=generate,
        inputs=[
            topic,
            num_sites
        ],
        outputs=[
            summary,
            sources
        ],
        show_progress="full"
    )

    topic.submit(
        fn=generate,
        inputs=[
            topic,
            num_sites
        ],
        outputs=[
            summary,
            sources
        ],
        show_progress="full"
    )

# -----------------------
# Launch
# -----------------------
if __name__ == "__main__":
    demo.launch(
        css=css,
        theme=custom_theme,
        share=True
    )