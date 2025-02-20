import streamlit as st
import sqlite3
import time
from sentence_transformers import SentenceTransformer, util
from langchain_community.llms import HuggingFaceEndpoint
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
import warnings
warnings.filterwarnings("ignore")
main_page = __import__("HomePage")

api_key = st.secrets["HUGGINGFACEHUB_API_TOKEN"]

repo_id = "mistralai/Mistral-7B-Instruct-v0.2"
llm = HuggingFaceEndpoint(
    repo_id=repo_id, max_length=128, temperature=0.6, token=api_key, task='text-generation'
)
template = """Prompt: Don't be too verbose. Always answer with respect to the given kural. Try not to repeat the given words and use simple and easy-to-understand words. The given kural is from Thirukkural written by Thiruvalluvar. You may refer it as kural only. Don't produce unwanted words and answer like a human without any ai bullshit. Avoid answering if the given question is not related to the given kural.
Question: {question}
kural:  {kural}
Answer:"""
prompt = PromptTemplate.from_template(template)
llm_chain = LLMChain(prompt=prompt, llm=llm)


def similar_kural(chapter):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    kural = cursor.execute(f"SELECT * FROM kural WHERE chapter='{chapter}'").fetchall()
    tamil_kural_list, kural_list, similarity = [], [], []
    for line in kural:
        kural_list.append(line[3])
        tamil_kural_list.append(line[2])
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(kural_list)
    for embedding in embeddings:
        similarity.append(float(util.cos_sim(model.encode(main_page.get_kural(st.session_state["kural"])[3]), embedding)[0][0]))
    return get_kural_list(enumerate(similarity), tamil_kural_list)

def get_kural_list(similarity, kural_list):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    sorted_similarity = sorted(similarity, key=lambda x:x[1], reverse=True)[1:4]
    return_kural = []
    for i in range(len(kural_list)):
        for j in range(len(sorted_similarity)):
            if i == sorted_similarity[j][0]:
                kural = cursor.execute(f"SELECT id FROM kural WHERE tamil='{kural_list[i]}'").fetchall()
                return_kural.append([kural[0][0],kural_list[i]])
    return return_kural


def response_generator(message, kural):
    kural_full = main_page.get_kural(kural)
    response = llm_chain.run(question=message, kural=kural_full[3])
    for word in response.split():
        yield word + " "
        time.sleep(0.05)

if "kural" in st.session_state:
    kural_full = main_page.get_kural(st.session_state["kural"])
    kural = kural_full[2].split()
        
    with st.sidebar:
        kural_num = st.number_input(label="Explore a குறள் quickly", min_value=1, max_value=1330, step=1)
        if st.button("Explore this kural using the chatbot", key="quick"):
            st.session_state["kural"] = kural_num
            if "messages" in st.session_state.keys():
                del st.session_state.messages
            st.switch_page("pages/2_Explore a Kural.py")
    
    col1, col2 = st.columns(2)
    with col1:
        col1.subheader("Explore this Kural with Mistral 7B")
        col1.write(f"<br>{' '.join(kural[:4])}<br>{' '.join(kural[4:])}", unsafe_allow_html=True)
        col1.write(f"<br>குறள்: {kural_full[0]} <br>அதிகாரம்: {kural_full[1]}", unsafe_allow_html=True)
        col1.write(f"<br><b>Meaning in English:</b> {kural_full[3]}<br><br>", unsafe_allow_html=True)  
        
        col1.write("<h4>Explore similar குறள்</h4>", unsafe_allow_html=True)
        similar_kural_list = similar_kural(kural_full[1])
        for kural in similar_kural_list:
            with st.container(border=True):
                kural_line = kural[1].split()
                st.write(f"{' '.join(kural_line[:4])}<br>{' '.join(kural_line[4:])}", unsafe_allow_html=True)
                col1_1, col1_2 = st.columns([0.8,0.2])
                col1_1.write(f"அதிகாரம்: {kural_full[1]}<br>குறள்: {kural[0]}", unsafe_allow_html=True)
                if col1_2.button("Explore", key=kural[0]):
                    st.session_state["kural"] = kural[0]
                    if "messages" in st.session_state.keys():
                        del st.session_state.messages
                    st.switch_page("pages/2_Explore a Kural.py")
    
    with col2.container():
        history = st.container(height=500)
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with history.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Chat with Mistral 7B about the குறள்"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with history.chat_message("user"):
                st.markdown(prompt)

            with history.chat_message("assistant"):
                response = st.write_stream(response_generator(prompt, kural_full[0]))

            st.session_state.messages.append({"role": "assistant", "content": response})
        
        with col2.expander("Suggested Prompts"):
            st.code("Explain this", language=None)
            st.code("Explain this like I am 5", language=None)
            st.code("Write a haiku for this", language=None)
            st.code("What is the moral of this", language=None)

else:
    st.switch_page("pages/1_Choose a Kural.py")



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