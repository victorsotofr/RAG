# ==========================================
# TEACHING ASSISTANT - USES RAG PIPELINE TO LEVERAGE LESSONS' PDFs
# Student can either ask for MCQs or for open-answer questions.
# ==========================================
# SOURCES:
# MAIN GUIDE: https://python.langchain.com/docs/tutorials/rag/
# With the BIG HELP of this guy: https://www.youtube.com/watch?v=ZCSsIkyCZk4
# ==========================================

# SETUP
import logging
import getpass
import os
import tkinter as tk
from tkinter import scrolledtext, messagebox, Radiobutton, IntVar, StringVar, Checkbutton
from langchain_openai import OpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.vectorstores import VectorStoreRetriever
from langchain.chains import RetrievalQA

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ==========================================
# CLASSES FOR MODULARIZATION
# ==========================================

class PDFProcessor:
    def __init__(self, directory):
        self.directory = directory

    def load_pdfs(self):
        """Loads all Lessons' PDFs in a directory and extracts text."""
        documents = []
        for filename in os.listdir(self.directory):
            if filename.endswith(".pdf"):
                pdf_path = os.path.join(self.directory, filename)
                try:
                    loader = PyPDFLoader(pdf_path)
                    documents.extend(loader.load())
                    logging.info(f"Successfully loaded {filename}")
                except Exception as e:
                    logging.error(f"Error loading {filename}: {e}")
        return documents

    def process_documents(self, documents):
        """Splits documents into chunks."""
        try:
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
            chunks = text_splitter.split_documents(documents)
            logging.info(f"Processed {len(documents)} documents into {len(chunks)} chunks")
            return chunks
        except Exception as e:
            logging.error(f"Error processing documents: {e}")
            return []

class EmbeddingRetriever:
    def __init__(self, api_key):
        self.api_key = api_key

    def build_faiss_vectorstore(self, chunks):
        """Embeds text chunks and stores them in a FAISS index."""
        try:
            embeddings = OpenAIEmbeddings(openai_api_key=self.api_key)
            vectorstore = FAISS.from_documents(chunks, embeddings)
            retriever = VectorStoreRetriever(vectorstore=vectorstore)
            logging.info("Successfully built FAISS vector store")
            return retriever
        except Exception as e:
            logging.error(f"Error building FAISS vector store: {e}")
            return None

class QueryHandler:
    def __init__(self, api_key):
        self.api_key = api_key

    def generate_question(self, mode, retriever):
        """Generates a question based on the selected mode with a random topic."""
        try:
            if mode == "MCQ":
                instruction = "Generate a multiple-choice question with options based on a random topic from the information provided in the documents."
            elif mode == "Open-Answer":
                instruction = "Generate an open-ended question based on a random topic from the information provided in the documents."

            qa_chain = RetrievalQA.from_chain_type(
                llm=OpenAI(openai_api_key=self.api_key),
                retriever=retriever
            )

            response = qa_chain.invoke({"query": instruction})
            return response["result"] if isinstance(response, dict) and "result" in response else response
        except Exception as e:
            logging.error(f"Error generating question: {e}")
            return "Sorry, an error occurred while generating the question."

    def evaluate_answer(self, mode, question, user_answer, retriever):
        """Evaluates the user's answer based on the selected mode."""
        try:
            if mode == "MCQ":
                # Extract correct answer from the question
                parts = question.split(')')
                options = parts[1:]  # Extract options
                correct_answer = [option.strip().split('.')[1] for option in options if 'correct' in option.lower()]

                if not correct_answer:
                    return "Error: Correct answer not identified.", ""

                correct_answer = correct_answer[0]
                is_correct = correct_answer.lower() in [answer.lower() for answer in user_answer]

                if is_correct:
                    return "Correct!", f"Explanation: {question}"
                else:
                    return "Incorrect.", f"Correct Answer: {correct_answer}. Explanation: {question}"

            elif mode == "Open-Answer":
                # Simulate open-answer correction (this part can be enhanced with actual answer checking logic)
                instruction = f"Evaluate the following answer to the question '{question}': {user_answer}"
                qa_chain = RetrievalQA.from_chain_type(
                    llm=OpenAI(api_key=self.api_key),
                    retriever=retriever
                )
                response = qa_chain.invoke({"query": instruction})
                return response["result"] if isinstance(response, dict) and "result" in response else response
        except Exception as e:
            logging.error(f"Error evaluating answer: {e}")
            return "Sorry, an error occurred while evaluating your answer."

    def query_documents(self, query, retriever):
        """Handles open questions and generates responses using OpenAI."""
        try:
            instruction = "Answer based only on the information provided in the documents. If the information is not available, state that clearly."
            full_query = f"{instruction} Query: {query}"
            qa_chain = RetrievalQA.from_chain_type(
                llm=OpenAI(api_key=self.api_key),
                retriever=retriever
            )
            response = qa_chain.invoke({"query": full_query})
            return response["result"] if isinstance(response, dict) and "result" in response else response
        except Exception as e:
            logging.error(f"Error querying documents: {e}")
            return "Sorry, an error occurred while processing your request."

class TeachingAssistantApp:
    def __init__(self, root, api_key, pdf_processor, embedding_retriever, query_handler):
        self.root = root
        self.root.title("Teaching Assistant by Victor")
        self.api_key = api_key
        self.pdf_processor = pdf_processor
        self.embedding_retriever = embedding_retriever
        self.query_handler = query_handler

        self.current_question = ""
        self.mcq_options = []
        self.selected_options = []

        self.create_widgets()
        self.load_documents()

    def create_widgets(self):
        self.mode_var = StringVar(value="Open-Question")

        self.mode_label = tk.Label(self.root, text="Select Mode:")
        self.mode_label.pack(pady=5)

        self.mcq_radio = Radiobutton(self.root, text="MCQ", variable=self.mode_var, value="MCQ", command=self.generate_question)
        self.mcq_radio.pack()

        self.open_answer_radio = Radiobutton(self.root, text="Open-Answer", variable=self.mode_var, value="Open-Answer", command=self.generate_question)
        self.open_answer_radio.pack()

        self.open_question_radio = Radiobutton(self.root, text="Open-Question", variable=self.mode_var, value="Open-Question")
        self.open_question_radio.pack()

        self.question_label = tk.Label(self.root, text="Question:")
        self.question_label.pack(pady=5)

        self.question_text = tk.Label(self.root, text="", wraplength=400, justify="left")
        self.question_text.pack(pady=5)

        self.options_frame = tk.Frame(self.root)
        self.options_frame.pack(pady=5)

        self.answer_entry = tk.Entry(self.root, width=50)
        self.answer_entry.pack(pady=5)

        self.submit_button = tk.Button(self.root, text="Submit", command=self.handle_submission)
        self.submit_button.pack(pady=5)

        self.next_button = tk.Button(self.root, text="Next Question", command=self.generate_question, state=tk.DISABLED)
        self.next_button.pack(pady=5)

        self.answer_text = scrolledtext.ScrolledText(self.root, width=60, height=10)
        self.answer_text.pack(pady=5)

    def load_documents(self):
        pdf_documents = self.pdf_processor.load_pdfs()
        if not pdf_documents:
            messagebox.showwarning("Warning", "No PDFs found. Add PDFs to the 'lessons' directory and try again.")
            return

        chunks = self.pdf_processor.process_documents(pdf_documents)
        if not chunks:
            messagebox.showwarning("Warning", "No chunks processed. Check the PDFs and try again.")
            return

        self.retriever = self.embedding_retriever.build_faiss_vectorstore(chunks)
        if not self.retriever:
            messagebox.showwarning("Warning", "Failed to build FAISS vector store. Check the logs for errors.")

    def generate_question(self):
        mode = self.mode_var.get()
        self.current_question = self.query_handler.generate_question(mode, self.retriever)
        self.question_text.config(text=self.current_question.split(')')[0].strip() + ')')

        if mode == "MCQ":
            self.mcq_options = [option.strip() for option in self.current_question.split(')')[1:]]
            self.display_mcq_options()
        else:
            self.answer_entry.config(state=tk.NORMAL)
            self.clear_options()

        self.next_button.config(state=tk.NORMAL)

    def display_mcq_options(self):
        self.answer_entry.config(state=tk.DISABLED)
        self.clear_options()
        self.selected_options = []

        for index, option in enumerate(self.mcq_options):
            var = IntVar()
            checkbox = Checkbutton(self.options_frame, text=option, variable=var, command=lambda v=var: self.toggle_option(v))
            checkbox.pack(anchor="w")

    def toggle_option(self, var):
        if var.get() == 1:
            self.selected_options.append(var)
        else:
            self.selected_options.remove(var)

    def clear_options(self):
        for widget in self.options_frame.winfo_children():
            widget.destroy()

    def handle_submission(self):
        mode = self.mode_var.get()

        if mode == "MCQ":
            user_answer = [self.mcq_options[i] for i, var in enumerate(self.selected_options) if var.get() == 1]
        elif mode == "Open-Answer":
            user_answer = self.answer_entry.get().strip()

        if mode in ["MCQ", "Open-Answer"]:
            if not self.current_question:
                messagebox.showwarning("Warning", "Please generate a question first.")
                return
            feedback, explanation = self.query_handler.evaluate_answer(mode, self.current_question, user_answer, self.retriever)
            self.answer_text.delete(1.0, tk.END)
            self.answer_text.insert(tk.END, self.current_question + "\n\nYour Answer: " + ", ".join(user_answer) + "\n\nFeedback: " + feedback + "\n\nExplanation: " + explanation)

        elif mode == "Open-Question":
            if not user_answer:
                messagebox.showwarning("Warning", "Please enter a question.")
                return
            answer = self.query_handler.query_documents(user_answer, self.retriever)
            self.answer_text.delete(1.0, tk.END)
            self.answer_text.insert(tk.END, answer)

def main():
    api_key = os.environ.get("OPENAI_API_KEY") or getpass.getpass("Enter your API key here: ")
    os.environ["OPENAI_API_KEY"] = api_key

    PDF_DIR = "./lessons"
    os.makedirs(PDF_DIR, exist_ok=True)

    pdf_processor = PDFProcessor(PDF_DIR)
    embedding_retriever = EmbeddingRetriever(api_key)
    query_handler = QueryHandler(api_key)

    root = tk.Tk()
    app = TeachingAssistantApp(root, api_key, pdf_processor, embedding_retriever, query_handler)
    root.mainloop()

if __name__ == "__main__":
    main()
