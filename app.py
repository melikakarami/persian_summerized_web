import gradio as gr

from config import Config
from main import run


def generate(topic, num_sites):

    if topic.strip() == "":
        return "موضوع را وارد کنید.", ""

    cfg = Config(
        topic=topic,
        num_sites=num_sites,
    )

    result = run(cfg)

    summary = result["summary"]

    sources = ""

    for s in result["sources"]:
        sources += f"• {s['title']}\n{s['url']}\n\n"

    return summary, sources


css = """
footer{
display:none;
}

.gradio-container{
max-width:1100px !important;
margin:auto;
}

textarea{
font-size:18px !important;
}
"""


with gr.Blocks(
    theme=gr.themes.Soft(),
    css=css,
    title="Persian News Summarizer"
) as demo:

    gr.Markdown(
        """
# 📰 Persian News Summarizer

جستجو، استخراج و خلاصه‌سازی اخبار فارسی با هوش مصنوعی
"""
    )

    with gr.Row():

        topic = gr.Textbox(
            label="موضوع",
            placeholder="مثلاً: هوش مصنوعی در پزشکی",
            scale=5
        )

        num_sites = gr.Slider(
            minimum=2,
            maximum=10,
            step=1,
            value=5,
            label="تعداد منابع",
            scale=1
        )

    button = gr.Button(
        "🔍 شروع",
        variant="primary",
        size="lg"
    )

    with gr.Row():

        summary = gr.Textbox(
            label="خلاصه نهایی",
            lines=18
        )

        sources = gr.Textbox(
            label="منابع",
            lines=18
        )

    button.click(
        fn=generate,
        inputs=[
            topic,
            num_sites
        ],
        outputs=[
            summary,
            sources
        ]
    )

demo.launch(share=True)