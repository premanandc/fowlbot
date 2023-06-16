import json
import os
import pickle

import streamlit as st
from dotenv import load_dotenv, find_dotenv
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.chat_models import ChatOpenAI

LOCAL_INDEX = './fowler.pkl'
SESSION_KEY = 'session_cache'


def build_toc():
    with open('article_details.json') as file:
        return {os.path.basename(article['link']): article for article in json.load(file)}


def as_markdown(article):
    if type(article) == str:
        return f'**:red[{article}]**'
    name = article['name'] or article['link']
    link = article['link']
    authors:list = article['authors'] or ['Martin Fowler']
    date = article['date']
    date_part = f' on {date}' if date else ''
    return f':white_check_mark: [{name}]({link}) by {", ".join(authors)}{date_part}.'


def lookup(source):
    raw_key = os.path.basename(source)
    stripped_key = os.path.splitext(raw_key)[0]
    toc = st.session_state.toc
    return as_markdown(toc.get(raw_key, toc.get(stripped_key, "No credible sources found :disappointed:")))


def is_ingested():
    return os.path.isfile(LOCAL_INDEX) and os.access(LOCAL_INDEX, os.R_OK)


def load_index():
    with open(LOCAL_INDEX, "rb") as f:
        return pickle.load(f)


st.title(':sunglasses: Welcome to Fowlbot!')

_ = load_dotenv(find_dotenv())
question = st.text_input(label='What does Martin say?', placeholder='Your question here and press Enter...')

if not is_ingested():
    st.write('Ask your administrator to ingest the contents of martinfowler.com to use this tool')
else:
    if SESSION_KEY not in st.session_state:
        st.session_state[SESSION_KEY] = load_index()
        st.session_state.toc = build_toc()

if SESSION_KEY in st.session_state:
    vector = st.session_state[SESSION_KEY]
    llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0.0, verbose=True)
    chain = RetrievalQAWithSourcesChain.from_chain_type(llm=llm, chain_type="stuff",
                                                        retriever=vector.as_retriever(),
                                                        return_source_documents=True,
                                                        verbose=True)

    if question:
        with st.spinner('Working... please wait...'):
            completion = chain({'question': question})
            st.subheader('Answer:')
            st.write(completion['answer'])
            with st.expander('Source(s):', expanded=True):
                for source in completion['sources'].split(','):
                    st.markdown(lookup(source.strip()))
