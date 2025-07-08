# PDFPaglu: AI Document Assistant

A modern, privacy-first web app to chat with your documents, powered by Google Gemini AI and OpenAI GPT-4o.  
Upload any PDF or TXT file and instantly get summaries, Q&A, quizzes, and more—all in a sleek, distraction-free dark interface.

---

## ✨ Features

- **Chat with Your Documents:**  
  Instantly ask questions and get intelligent, context-aware answers based on your uploaded file.

- **Smart Summaries:**  
  Receive concise, AI-generated overviews of any document.

- **Quiz Yourself:**  
  Auto-generate quizzes to test your understanding of the material.

- **Draft Emails:**  
  Let the AI help you compose emails based on document content.

- **Key Insights Extraction:**  
  Highlight the most important points in seconds.

- **Beautiful, Minimal UI:**  
  Pure black theme, subtle white borders, and zero blue—designed for focus and style.

- **No Data Retention:**  
  Your files and chats are never stored or shared.

---

## 🚀 Quickstart

### Prerequisites

- Python 3.7+
- API key from [Google AI Studio](https://aistudio.google.com/app/apikey)

### Installation

```bash
git clone https://github.com/v8v88v8v88/AI-Document-Analyzer.git
cd AI-Document-Analyzer
pip install -r requirements.txt
```

### Configuration

1. Create a `.env` file in the project root:
    ```
    GEMINI_API_KEY="YOUR_API_KEY_HERE"
    ```
2. (Optional) Add any other environment variables as needed.

### Run the App

```bash
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🖤 UI Preview

- Pure black background, no blue tones
- Sidebar-free, full-width layout
- Modern cards with white borders for clarity
- Drag-and-drop file upload, fully themed

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit (custom dark theme)
- **AI:** Google Gemini, OpenAI GPT-4o
- **PDF Processing:** PyPDF2
- **Database:** SQLAlchemy (for session/history, if enabled)
- **Other:** Pydantic, Google GenAI

---

## 📄 Usage

1. **Upload** a PDF or TXT file.
2. **Choose an action:**
    - Get a summary
    - Ask questions (Q&A)
    - Take a quiz
    - Draft an email
    - Extract key insights
3. **Enjoy fast, accurate, and private AI assistance!**

---

## 🤝 Contributing

Pull requests and suggestions are welcome!  
For major changes, please open an issue first to discuss what you’d like to change.

---

## 📜 License

GPLv3 License 