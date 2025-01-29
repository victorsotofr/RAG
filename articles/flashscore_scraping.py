import requests
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
import sqlite3
import json

# Initialize the Elasticsearch client with the host
es = Elasticsearch(hosts=["http://localhost:9200"])

def scrape_articles(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    articles = []
    for article in soup.find_all('article'):
        title = article.find('h2').text
        content = article.find('p').text
        date = article.find('time').text
        articles.append({'title': title, 'content': content, 'date': date})

    return articles

def save_to_json(articles, filename='articles.json'):
    with open(filename, 'w') as f:
        json.dump(articles, f)

def save_to_db(articles, db_name='articles.db'):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS articles
                 (title text, content text, date text)''')

    for article in articles:
        c.execute("INSERT INTO articles VALUES (?,?,?)", (article['title'], article['content'], article['date']))

    conn.commit()
    conn.close()

def index_articles(articles):
    for article in articles:
        es.index(index='articles', document=article)

def retrieve_articles(query):
    response = es.search(index='articles', body={"query": {"match": {"content": query}}})
    return response['hits']['hits']

def main():
    url = "https://www.flashscore.fr/actualites/"
    articles = scrape_articles(url)

    # Save articles to JSON
    save_to_json(articles)

    # Save articles to SQLite database
    save_to_db(articles)

    # Index articles into Elasticsearch
    index_articles(articles)

    # Example query to retrieve articles
    query = "football"
    results = retrieve_articles(query)
    print(results)

if __name__ == "__main__":
    main()
