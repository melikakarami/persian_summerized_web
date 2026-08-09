# Persian Web Content Search & Summarization 🇮🇷

An intelligent NLP system for **searching, extracting, and summarizing Persian web content**.

The user enters a topic or question, and the system automatically searches relevant Persian web pages, extracts their main content, and generates a concise Persian summary with the original sources.

## ✨ Features

* 🔎 Persian web search
* 🌐 Web content extraction
* 🧹 Text cleaning and preprocessing
* 🤖 AI-based Persian text summarization
* 🔗 Source display
* 🧩 Modular architecture
* 🖥️ Gradio web interface

## 🛠️ Technologies

* **Python**
* **Gradio**
* **Qwen2.5-1.5B-Instruct**
* **Transformers**
* **NLP libraries**
* **Web scraping & search libraries**

## 🔄 Workflow

```text
User Query
    ↓
Web Search
    ↓
Content Extraction
    ↓
Text Processing
    ↓
AI Summarization
    ↓
Summary + Sources
```

## 📁 Project Structure

```text
├── app.py
├── main.py
├── config.py
├── searcher.py
├── scraper.py
├── summarizer.py
├── logger.py
├── outputs/
└── logs/
```

## 🚀 Installation

```bash
git clone https://github.com/melikakarami/persian_summerized_web.git
cd persian_summerized_web
pip install -r requirements.txt
```

Run the application:

```bash
python app.py
```

## 🎯 Goal

The goal of this project is to **reduce the time required to read multiple Persian web sources** by automatically searching, extracting, and summarizing their most important information.

