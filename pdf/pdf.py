import os
import getpass
import faiss
import numpy as np
import PyPDF2
from sentence_transformers import SentenceTransformer
import openai
import tiktoken  # Tokenizer to estimate token count

# Ask for API key if not set in the environment
if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

openai.api_key = os.environ["OPENAI_API_KEY"]  # Set API key

# Initialize embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Directory to store PDFs
PDF_DIR = "./pdfs"
os.makedirs(PDF_DIR, exist_ok=True)

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    return text

# Function to embed text and store in FAISS index
def build_faiss_index(text_chunks):
    embeddings = embedding_model.encode(text_chunks, convert_to_numpy=True, show_progress_bar=True, batch_size=4)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index, text_chunks

# Function to retrieve relevant chunks
def retrieve_relevant_chunks(query, index, text_chunks, top_k=3):
    query_embedding = embedding_model.encode([query], convert_to_numpy=True)
    distances, indices = index.search(query_embedding, top_k)
    return [text_chunks[i] for i in indices[0] if i < len(text_chunks)]

# Function to trim context within token limit
def trim_context(relevant_chunks, max_tokens=4000):
    """Trims context to ensure it doesn't exceed the model's token limit."""
    encoding = tiktoken.encoding_for_model("gpt-4")
    token_count = 0
    trimmed_chunks = []

    for chunk in relevant_chunks:
        chunk_tokens = encoding.encode(chunk)
        if token_count + len(chunk_tokens) > max_tokens:
            break  # Stop adding if it exceeds limit
        trimmed_chunks.append(chunk)
        token_count += len(chunk_tokens)

    return "\n".join(trimmed_chunks)

# Function to generate an answer using OpenAI
def generate_answer(query, relevant_chunks):
    context = trim_context(relevant_chunks)  # Trim context dynamically
    prompt = f"""
    You are an AI assistant that answers questions based strictly on the provided document excerpts.
    If the context does not contain the answer, simply respond: "I don't know based on the provided documents."

    Context:
    {context}

    Question: {query}
    Answer:
    """

    client = openai.Client()
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content  # Extract answer

# Main function to load PDFs, index, and query
def main():
    pdf_files = [os.path.join(PDF_DIR, f) for f in os.listdir(PDF_DIR) if f.endswith(".pdf")]
    all_text = "\n".join([extract_text_from_pdf(pdf) for pdf in pdf_files])
    text_chunks = all_text.split("\n\n")  # Simple chunking by paragraphs
    # index, chunks = build_faiss_index(text_chunks)
    
    while True:
        query = input("Ask a question (or type 'exit' to quit): ")
        if query.lower() == "exit":
            break
        relevant_chunks = text_chunks[:3]
        answer = generate_answer(query, relevant_chunks)
        print("Answer:\n", answer)

if __name__ == "__main__":
    main()