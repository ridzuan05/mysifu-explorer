from langchain.agents import initialize_agent, AgentType
from langchain.callbacks import StreamlitCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.tools import DuckDuckGoSearchRun

import streamlit as st
import requests

st.set_page_config(
    page_title='MySifu: Asisten AI',
    page_icon='🔎',
    layout='wide',
    initial_sidebar_state='expanded',
    menu_items={
        'Get Help': 'https://mysifu.net/help',
        'Report a bug': None,  # this will hide the 'Report a bug' menu item
        'About': "MySifu is an AI app developed by Ridzuan Daud Tech."
    }
)

# Define a dynamic meta description for your page
meta_description = "MySifu.Net - Maklumat terkini sepantas kilat!"

# Display the meta description in your Streamlit app
# st.write(meta_description)

# Use columns to create a layout. The empty columns act as space on the sides.
col1, col2, col3 = st.columns([1,2,1])

# With the image in the center column
with col2:
    # st.image('img//mysifu_bg_logo.png', use_column_width=True)
    st.image('img//mysifu_app.png', use_column_width=True, output_format="auto")

st.title("🔎 MySifu AI")

with st.expander('Apakah itu MySifu?'):
    st.write('''
    Selamat datang ke MySifu, chatbot serbaguna anda yang direka khas untuk memenuhi keperluan pengguna di Malaysia.\n
    Dengan kebolehan berkomunikasi dalam pelbagai bahasa termasuk Bahasa Melayu, Mandarin, Tamil, Manglish, dan banyak lagi, MySifu memastikan perbualan yang lancar dan mesra. \n
    Apa pun bahasa yang anda gunakan, MySifu akan merespons dalam bahasa yang sama, menjamin komunikasi yang sempurna. \n
    Dilengkapi dengan pengetahuan luas mengenai Malaysia, MySifu sentiasa menyediakan jawapan dalam konteks Malaysia, memastikan setiap interaksi anda berkualiti dan relevan.

    Kelebihan MySifu:\n
    • Kemampuan berbilang bahasa - Melayu, Mandarin, Tamil, Manglish dll.\n
    • Respons yang disesuaikan dengan konteks Malaysia - budaya, citarasa, lokaliti dll.\n
    • Maklumat terkini - gabungan teknologi GPT OpenAI dan enjin carian.\n
    ''')

# Your API keys (should be kept secret, using placeholders here)
OPENAI_API_KEY = ''
SERPAPI_API_KEY = ''

with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"

# cache 6 hour
@st.cache_data(ttl=21600)
def get_latest_news():
    url = "https://newsapi.org/v2/top-headlines?country=my&apiKey=140626560d734e2e873e4021a7ca4de0"
    response = requests.get(url)
    return response.json()['articles']

# cache 6 hour
@st.cache_data(ttl=21600)
def get_latest_trends():
    url = "https://serpapi.com/search.json?engine=google_trends_trending_now&frequency=realtime&geo=MY&hl=en&api_key=bc887f0a4ad542651b2f9a523035ce0e34aba17fe29e782f0a3c48c02744cc7f"
    response = requests.get(url)
    return response.json()['realtime_searches']

with st.expander('📈 Trending Search'):
    try:
        trends_items = get_latest_trends()
        for trends_item in trends_items:
            st.write(trends_item['title'])
    except Exception as e:
        st.error(f"Error fetching latest news: {e}")

with st.expander('🗃 Trending News'):
    try:
        news_items = get_latest_news()
        for news_item in news_items:
            st.write(news_item['title'])
    except Exception as e:
        st.error(f"Error fetching latest trends: {e}")

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Apakah informasi terkini yang anda ingin cari?"}
    ]

# for msg in st.session_state.messages:
#    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input(placeholder="Siapa menang F1 race tahun lepas?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    llm = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=openai_api_key, streaming=True)
    search = DuckDuckGoSearchRun(name="Search")
    search_agent = initialize_agent([search], llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, handle_parsing_errors=True)
    with st.chat_message("assistant"):
        try:
            st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
            response = search_agent.run(st.session_state.messages, callbacks=[st_cb])
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.write(response)
        except Exception as e:
            st.error(f"Error getting the latest info: {e}")
