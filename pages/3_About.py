import streamlit as st

with st.sidebar:
        kural_num = st.number_input(label="Explore a குறள் quickly", min_value=1, max_value=1330, step=1)
        if st.button("Explore this kural using the chatbot", key="quick"):
            st.session_state["kural"] = kural_num
            if "messages" in st.session_state.keys():
                del st.session_state.messages
            st.switch_page("pages/2_Explore a Kural.py")

col1, col2 = st.columns(2, gap="large")
with col1:
     st.subheader("About Thirukkural")
     st.write("""
    The Thirukkural (திருக்குறள்) is a classic Tamil language text consisting of 1,330 short couplets, or kurals, of seven words each. The text is divided into three books with aphoristic teachings on virtue (aram), wealth (porul) and love (inbam), respectively. Thirukkural is structured into 133 chapters, each containing 10 couplets (or kurals), for a total of 1,330 couplets. It is widely acknowledged for its universality and secular nature. Its authorship is traditionally attributed to Valluvar, also known in full as Thiruvalluvar. The text has been dated variously from 300 BCE to 5th century CE.
<br><br>
    Written on the ideas of ahimsa, it emphasizes non-violence and moral vegetarianism as virtues for an individual. In addition, it highlights virtues such as truthfulness, self-restraint, gratitude, hospitality, kindness, goodness of wife, duty, giving, and so forth, besides covering a wide range of social and political topics such as king, ministers, taxes, justice, forts, war, greatness of army and soldier's honor, death sentence for the wicked, agriculture, education, abstinence from alcohol and intoxicants.
""", unsafe_allow_html=True)


with col2:
    st.subheader("About Thirukkural.AI")
    st.write("""
Welcome to Thirukkural.AI, your gateway to the timeless wisdom of Thiruvalluvar powered by cutting-edge AI technology and deployed using Streamlit. This is a chatbot designed to help you delve into the profound teachings of Thiruvalluvar.
<br><br>
With Thirukkural.AI, you can easily find what Thiruvalluvar has said about any topic using RAG (Retrieval-Augmented Generation) model made specifically using the vectors of each kural. Simply enter a keyword, and let Thirukkural.AI uncover the relevant kural for you.
<br><br>
But that's not all... Thirukkural.AI goes beyond mere exploration. It allows you to delve deeper into a specific kural, providing insights and interpretations using Mistral 7B powered chat bot. Want more? Explore similar kural suggestions based on advanced sentence transformers, expanding your understanding and appreciation of Thiruvalluvar's timeless wisdom.
""", unsafe_allow_html=True)

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