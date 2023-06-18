import json
import os
import pickle

import requests
from dotenv import load_dotenv, find_dotenv
from langchain.document_loaders import UnstructuredHTMLLoader
from langchain.document_loaders import UnstructuredPDFLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS

INDEX_FILE = 'fowler.pkl'


class Ingestor:
    def __init__(self, article_links: list[str], force=False):
        self.articles: list[Article] = [Article(link) for link in article_links]
        self.force = force

    def ingest_and_store(self):
        raw_documents = self.ingest()
        self.store(raw_documents)

    @staticmethod
    def store(raw_documents):
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000,
                                                  chunk_overlap=200)
        chunked_documents = splitter.split_documents(raw_documents)
        embeddings = OpenAIEmbeddings()
        store = FAISS.from_documents(chunked_documents, embeddings)
        with open(INDEX_FILE, 'wb') as f:
            pickle.dump(store, f)

    def ingest(self):
        os.makedirs('./raw', exist_ok=True)
        with requests.Session() as session:
            return sum([article.load(session, self.force) for article in self.articles], [])


class Article:
    def __init__(self, url: str):
        self.url = url
        self.filename = f'./raw/{self.cleanse(url)}'
        self.readable = os.access(self.filename, os.R_OK)

    @staticmethod
    def cleanse(url):
        raw_name = os.path.basename(url)
        name = raw_name[:-1] if raw_name.endswith('/') else raw_name
        return name if name.endswith('pdf') or name.endswith('html') else name + '.html'

    def load(self, session: requests.Session, force=False):
        if force or not os.access(self.filename, os.R_OK):
            self.write(self.fetch(session))
        loader = UnstructuredPDFLoader(self.filename) if self.is_pdf() else UnstructuredHTMLLoader(self.filename)
        return loader.load()

    def is_pdf(self):
        return self.url.endswith('pdf')

    def fetch(self, session: requests.Session):
        print(f'Fetching article from {self.url}')
        return session.get(self.url)

    def write(self, response):
        print(f'Writing file to {self.filename}')
        if self.is_pdf():
            with open(self.filename, 'wb') as f:
                f.write(response.content)
        else:
            with open(self.filename, 'w') as f:
                f.write(response.text)


if __name__ == '__main__':
    _ = load_dotenv(find_dotenv())
    with open('./article_details.json') as file:
        articles = [article['link'] for article in json.load(file)]

    ingestor = Ingestor(articles, force=True)
    ingestor.ingest_and_store()
