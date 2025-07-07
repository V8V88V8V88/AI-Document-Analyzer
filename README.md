# AI Document Reader

This is a Streamlit web application that allows you to chat with your documents using the power of Google's Gemini AI.

## Features

-   **Interactive Chat:** Ask questions about your documents and get intelligent answers.
-   **Document-Based Knowledge:** The AI's responses are based solely on the content of your uploaded documents.
-   **Secure and Private:** Your documents and conversations are not stored or used for any other purpose.
-   **Modern UI:** A clean and intuitive user interface inspired by ChatGPT.

## Getting Started

### Prerequisites

-   Python 3.7+
-   An API key from [Google AI Studio](https://aistudio.google.com/app/apikey)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/ai-document-reader.git
    cd ai-document-reader
    ```

2.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up your environment variables:**
    -   Create a file named `.env` in the root of the project.
    -   Add your Google AI API key to the `.env` file as follows:
        ```
        GEMINI_API_KEY="YOUR_API_KEY_HERE"
        ```

### Running the Application

Once you have completed the installation and setup, you can run the application with the following command:

```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`.

## Usage

1. Upload a document (PDF or TXT format)
2. Choose your interaction mode:
   - **Summary**: Get a concise summary of the document
   - **Q&A**: Ask specific questions about the content
   - **Quiz**: Take an interactive quiz based on the material

## Architecture

- **Frontend**: Streamlit web interface
- **Document Processing**: PyPDF2 for PDF text extraction
- **AI Integration**: OpenAI GPT-4o for document analysis
- **Session Management**: Streamlit session state for user context

## Dependencies

- streamlit
- openai
- PyPDF2
- google-genai
- sqlalchemy
- pydantic

## License

MIT License 