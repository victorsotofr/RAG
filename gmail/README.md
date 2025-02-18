## Email (Gmail) synthesis using RAG
## WIP

This project enables users to **create syntheses** of **emails** from his Gmail adresse. 

---

## How It Works

**Fetches last 24h emails from Gmail inbox**  
  - Uses **API** to extract the targeted emails.

**Text Embedding & Indexing**  
  - Embeds emails' information using **FAISS**.

**Structured Summary**  
  - Uses RAG.
  - Sends the Summary to the inbox every morning.

---

## Setup & Installation

### 1. Install Dependencies

Ensure Python is installed and install the required packages:

```bash
WIP
```

### 2. Set Your OpenAI API Key

Before running, set your OpenAI and Google API keys:

```python
WIP
```
-> you can copy/paste it in a chat-box style.

### 3. Choose the hour to get your Daily resume!

```
WIP
```

### 4. Run the Script

Execute the Python script to start the interactive Q&A:

```bash
python script.py
```

---

## Notes

- The FAISS index allows rapid retrieval of relevant text snippets.
Source: [FAISS LangChain](https://python.langchain.com/docs/integrations/vectorstores/faiss/)
- This system is designed for your Gmail inbox but can be adapted to other email inboxes.  

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

WIP

---

Victor

Worked with: ChatGPT, MistralAI
