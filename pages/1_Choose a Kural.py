import streamlit as st
import sqlite3
import re
from streamlit.components.v1 import components
main_page = __import__("HomePage")


def get_chapters():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    chapters = cursor.execute("SELECT * FROM chapter").fetchall()
    chapter_list = []
    for chapter in chapters:
        chapter_list.append(str(chapter[0]) + '.  ' + chapter[1])
    return chapter_list

def get_kural(chapter):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    chapters = cursor.execute(f"SELECT * FROM kural WHERE chapter='{chapter}'").fetchall()
    return chapters
   

with st.sidebar:
        kural_num = st.number_input(label="Explore a குறள் quickly", min_value=1, max_value=1330, step=1)
        if st.button("Explore this kural using the chatbot", key="quick"):
            st.session_state["kural"] = kural_num
            if "messages" in st.session_state.keys():
                del st.session_state.messages
            st.switch_page("pages/2_Explore a Kural.py")

st.title("Choose a Kural to explore more")
col1,col2 = st.columns(2)
divisions = ["அறத்துப்பால் (Moralities Division)","பொருள் பால் (Economics Division)","இன்பத்துப்பால் (Love-making Division)"]
selected_division = col1.selectbox("Choose a division", divisions, index=None, placeholder="Select பால் (Division)")
if selected_division:
    if selected_division == divisions[0]:
        chapters = get_chapters()[:39]
    if selected_division == divisions[1]:
        chapters = get_chapters()[39:109]
    if selected_division == divisions[2]:
        chapters = get_chapters()[109:]
    selected_chapter = col2.selectbox("Choose a chapter", chapters, index=None, placeholder="Select பால் (Division)")
    if selected_chapter:
        chapter_name = re.findall(r"[\d]+. +([^\n]*)", selected_chapter)
        kural_list = get_kural(chapter_name[0].strip())
        if selected_division == divisions[1] and chapter_name[0].strip()=='குறிப்பறிதல்':
            kural_list = kural_list[:10]
        if selected_division == divisions[2] and chapter_name[0].strip()=='குறிப்பறிதல்':
            kural_list = kural_list[10:]
        for kural_now in kural_list:
            kural = kural_now[2].split()
            with st.expander(f"{' '.join(kural[:4])}\n\n{' '.join(kural[4:])}"):
                col1, col2 = st.columns(2)
                col1.write(f"குறள்: {kural_now[0]} <br>அதிகாரம்: {kural_now[1]}", unsafe_allow_html=True)
                col2.write(f"<b>Meaning in English:</b> {kural_now[3]}", unsafe_allow_html=True)
                if col2.button("Explore this kural using the chatbot", key=kural_now[0], ):
                    st.session_state["kural"] = kural_now[0]
                    if "messages" in st.session_state.keys():
                        del st.session_state.messages
                    st.switch_page("pages/2_Explore a Kural.py")



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