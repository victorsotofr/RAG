## PDF Q&A System using OpenAI GPT-4 and FAISS

This project enables users to **ask questions** based on the content of **PDF documents**. 

By extracting text from PDFs, embedding it using **SentenceTransformers**, and indexing it with **FAISS**, the system retrieves relevant information and generates context-aware answers using **OpenAI's GPT-4**.

---

## How It Works

**PDF Text Extraction**  
  Utilizes **PyPDF2** to extract text from PDF files.

**Text Embedding & Indexing**  
  - Embeds text using **SentenceTransformers** (`all-MiniLM-L6-v2`).
  - Indexes embeddings with **FAISS** for efficient similarity search.

**Interactive Q&A**  
  - Users input questions.
  - Relevant document excerpts are retrieved.
  - GPT-4 generates answers based on retrieved content.

**Token Management**  
  - Uses **tiktoken** to manage token limits for GPT-4.

---

## Setup & Installation

### 1. Install Dependencies

Ensure Python is installed and install the required packages:

```bash
pip install openai faiss-cpu PyPDF2 sentence-transformers tiktoken
```

### 2. Set Your OpenAI API Key

Before running, set your OpenAI API key:

```python
import os
os.environ["OPENAI_API_KEY"] = "your-api-key-here"
```
-> you can copy/paste it in a chat-box style.

### 3. Prepare PDF Files

Place your PDF files in a folder named `pdfs` in the project directory:

```
/project-directory
│
├── script.py
└── pdfs/
    ├── document1.pdf
    ├── document2.pdf
    └── ...
```

### 4. Run the Script

Execute the Python script to start the interactive Q&A:

```bash
python script.py
```

---

## Usage Example

```bash
Ask a question (or type 'exit' to quit): What is embedding?
Answer:
 blabla
```

To exit, simply type **"exit"**.

---

## Notes

- If the context does not contain the answer, GPT-4 will respond:
  *"I don't know based on the provided documents."*  
- The FAISS index allows rapid retrieval of relevant text snippets.
Source: [FAISS LangChain](https://python.langchain.com/docs/integrations/vectorstores/faiss/)
- This system is designed for local PDF documents but can be adapted for other text sources.  

---

## Resources

The main basis for the work was:
- **LangChain RAG Guide**: [LangChain RAG Tutorial](https://python.langchain.com/docs/tutorials/rag/)

The useful resources were:
- **FAISS Documentation**: [FAISS LangChain](https://python.langchain.com/docs/integrations/vectorstores/faiss/)  
- **OpenAI GPT-4**: [OpenAI API Documentation](https://beta.openai.com/docs/api-reference/introduction)  
- **SentenceTransformers**: [SentenceTransformers Documentation](https://www.sbert.net/)  

---

## Future Improvements

- **Add support for other document types** (e.g., DOCX, TXT)  
- **Enable web-based interface** for remote access  
- **Optimize embedding model** for larger documents (the token limit is not practical)

---

Victor
Worked with: ChatGPT, MistralAI
