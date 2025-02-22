import streamlit as st
import re
import datetime
import sqlite3
import random
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import HuggingFaceEndpoint
import warnings
import torch
from PIL import Image

warnings.filterwarnings("ignore")

api_key = st.secrets["HUGGINGFACEHUB_API_TOKEN"]
torch.classes.__path__ = []

repo_id = "mistralai/Mistral-7B-Instruct-v0.2"
llm = HuggingFaceEndpoint(
    repo_id=repo_id, max_length=128, temperature=0.4, task='text-generation'
)

st.set_page_config(page_title="Thirukkural.AI", layout="wide")

def get_kural(id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    kural = cursor.execute(f"SELECT * FROM kural WHERE id={id}").fetchall()
    return kural[0]

def kural_for_the_day():
    date_now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    dates = cursor.execute("SELECT * FROM day").fetchall()
    empty_ids = []
    for i in range(len(dates)):
        if dates[i][1] == date_now:
            return get_kural(dates[i][0])
        if dates[i][1] == None:
            empty_ids.append(i+1)
    if empty_ids != []:
        choice = random.choice(empty_ids)
        cursor.execute(f"UPDATE day SET date='{date_now}' WHERE id={choice}")
        conn.commit()
        return kural_for_the_day()
    else:
        cursor.execute("DROP TABLE day")
        conn.commit()
        cursor.execute("CREATE TABLE day(id INTEGER, date TEXT)")
        conn.commit()
        for i in range(len(dates)):
            cursor.execute(f"INSERT INTO day(id) VALUES({i+1})")
        conn.commit()
        return kural_for_the_day()

def kural_search(user_question):
    embeddings = HuggingFaceEmbeddings()
    knowledge_base = FAISS.load_local("kural_faiss_index", embeddings, allow_dangerous_deserialization=True)

    with open("thirukkural.txt","r", encoding="utf8")as f:
        text_tamil = f.readlines()
    for i in range(len(text_tamil)):
        text_tamil[i] = re.sub(r" +", " ", text_tamil[i])
        text_tamil[i] = re.sub(r"[\\n|$]", " ", text_tamil[i]).strip()[:-1]
    with open("thirukkural_eng.txt","r", encoding="utf8")as f:
        text = f.readlines()
    for i in range(len(text)):
        text[i] = re.sub(r"[\n|$]", " ", text[i]).strip()
        text[i] = re.sub(r" +", " ", text[i])
    
    search_results = []
    docs = knowledge_base.similarity_search(user_question, k=3)
    for line in docs:
        search_results.append([text.index(line.page_content)+1, text_tamil[text.index(line.page_content)], text[text.index(line.page_content)]])
    
    chain = load_qa_chain(llm, chain_type="stuff")
    response = chain.run(input_documents=docs, question="In a simple and detailed manner, what is given in the text about "+user_question+"? Refer to the text as 'Thirukkural' only and no other nouns like text or document. The name of the author or speaker of the text is called 'Thiruvalluvar' and refer to him only by his name with the correct spelling and no other terms like author or speaker. Do not make up any numbers for chapters")
    return search_results, response

def main():
    with st.sidebar:
        kural_num = st.number_input(label="Explore a குறள் quickly", min_value=1, max_value=1330, step=1)
        if st.button("Explore this kural using the chatbot", key="quick"):
            st.session_state["kural"] = kural_num
            if "messages" in st.session_state.keys():
                del st.session_state.messages
            st.switch_page("pages/2_Explore a Kural.py")

    head_1, head_2 = st.columns([0.8,0.2])
    head_1.title("Thirukkural.AI")
    head_1.write("#### Explore Thirukkural with the help of AI")
    head_1.write("")
    image = Image.open("thiruvalluvar.jpg")
    head_2.image(image)
    kural_t = kural_for_the_day()
    kural_today = kural_t[2].split()
    
    with st.container(border=True):
        col1, col2, col3 = st.columns([0.55, 0.35, 0.1])
        col1.write("<h3>What does the Thirukkural say about</h3> ", unsafe_allow_html=True)
        user_question = col2.text_input("Enter a topic", label_visibility='collapsed').capitalize()
        if col3.button("Search") or user_question:
            col2.write("<br>", unsafe_allow_html=True)
            if '?' in user_question:
                user_question = user_question.replace('?','')
            response = kural_search(user_question)
            col3_1, col3_2 = st.columns([0.5, 0.5], gap="large")
            col3_1.write(response[1])
            col3_2.write("This explanation was based on the following")
            for kural_now in response[0]:
                with col3_2.expander("குறள் "+str(kural_now[0])):
                    kural = kural_now[1].split()
                    st.write(f"{' '.join(kural[:4])}<br>{' '.join(kural[4:])}", unsafe_allow_html=True)
                    st.write(kural_now[2])
                    if st.button("Explore", key=kural_now[0]):
                        st.session_state["kural"] = kural_now[0]
                        if "messages" in st.session_state.keys():
                            del st.session_state.messages
                        st.switch_page("pages/2_Explore a Kural.py")
        else:
            st.caption("Suggested queries: family, love, education, marriage, respecting elders, qualities of a man, qualities of a woman, relationship between husband and wife")

    with st.container():
        st.write()
        col1, col2 = st.columns(spec=[0.6,0.4], gap="large")
        col1.subheader("Featured குறள் of the day:")
        col1.write(f"{' '.join(kural_today[:4])}<br>{' '.join(kural_today[4:])}", unsafe_allow_html=True)
        col1.write(f"<b>English Meaning:</b> {kural_t[3]}", unsafe_allow_html=True)
        col2.metric("குறள்",kural_t[0])
        col2.write(f"அதிகாரம் <br><h5>{kural_t[1]}</h5>", unsafe_allow_html=True)
        if col2.button("Explore this kural using the chatbot", key="kural_for_the_day"):
            st.session_state["kural"] = int(kural_for_the_day()[0])
            if "messages" in st.session_state.keys():
                del st.session_state.messages
            st.switch_page("pages/2_Explore a Kural.py")

if __name__ == "__main__":
    main()

hide_st_style = """
        <style>
        #MainMenu {visibility:hidden;}
        #footer {visibility:hidden;}
        #header {visibility:hidden;}
        .stDeployButton {
            visibility: hidden;
        }
        </style>
"""

css='''
[data-testid="stSidebarNav"] {
  min-height: 50vh
}
'''

st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)
st.markdown(hide_st_style, unsafe_allow_html=True)
