import re
import logging
from elasticsearch import Elasticsearch, exceptions
from transformers import pipeline
from docx import Document
import pypandoc
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Elasticsearch client
es = Elasticsearch(hosts=["http://localhost:9200"])

def clean_text(text):
    try:
        text = re.sub(r'\s+', ' ', text)  # Remove extra whitespace
        text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
        return text.lower()  # Convert to lowercase
    except Exception as e:
        logger.error(f"Error cleaning text: {e}")
        return text

def index_article(article_id, article_text):
    try:
        es.index(index="financialtimes_articles", id=article_id, body={"text": article_text})
        logger.info(f"Indexed article {article_id}")
    except exceptions.ElasticsearchException as e:
        logger.error(f"Error indexing article {article_id}: {e}")

def retrieve_articles(query):
    try:
        response = es.search(index="financialtimes_articles", body={"query": {"match": {"text": query}}})
        return [hit["_source"]["text"] for hit in response["hits"]["hits"]]
    except exceptions.ElasticsearchException as e:
        logger.error(f"Error retrieving articles: {e}")
        return []

# Text generation pipeline
generator = pipeline('text-generation', model='t5-small')

def generate_response(query, retrieved_articles):
    try:
        context = " ".join(retrieved_articles)
        input_text = f"{query} Context: {context}"
        return generator(input_text, max_length=150, num_return_sequences=1)
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return []

def extract_text_from_rtfd(rtfd_path):
    # Ensure the RTFD path is correct
    if not os.path.isdir(rtfd_path):
        raise FileNotFoundError(f"The directory {rtfd_path} does not exist.")

    # Find the RTF file within the RTFD directory
    rtf_file = None
    for file_name in os.listdir(rtfd_path):
        if file_name.endswith('.rtf'):
            rtf_file = os.path.join(rtfd_path, file_name)
            break

    if rtf_file is None:
        raise FileNotFoundError(f"No RTF file found in the directory {rtfd_path}.")

    # Convert RTF to DOCX
    docx_path = rtf_file.replace('.rtf', '.docx')
    pypandoc.convert_file(rtf_file, 'docx', outputfile=docx_path)

    # Extract text from DOCX
    doc = Document(docx_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

def main():
    # Extract text from RTFD file
    rtfd_file_path = '/Users/victor/Documents/_Perso/FT_20250129.rtfd'
    try:
        article_text = extract_text_from_rtfd(rtfd_file_path)
    except FileNotFoundError as e:
        logger.error(e)
        return

    # Clean the extracted text
    cleaned_text = clean_text(article_text)

    # Index the article
    article_id = 1  # You can use a unique identifier for each article
    index_article(article_id, cleaned_text)

    # Retrieve articles based on a query
    query = "OpenAI DeepSeek"
    retrieved_articles = retrieve_articles(query)

    # Generate a response
    response = generate_response(query, retrieved_articles)
    print(response)

if __name__ == "__main__":
    main()