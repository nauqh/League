from utils import *
from graph import *
import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

key = os.getenv('KEY')


st.set_page_config(
    page_title="League of Legends",
    page_icon="🌨️",
    layout="wide")

# TODO: Sidebar
with st.sidebar:
    st.info(
        "📌 **NOTE**: A rate limit is set to 100 requests every 2 minutes! [Details](https://developer.riotgames.com/docs/portal)")
    st.write("## About the project")
    st.markdown(
        "A rating system that measures users performance within a game by combining stats related to role, laning phase, kills / deaths / damage / wards / damage to objectives etc")
    st.markdown(
        "Status: `Beta`")
    st.markdown(
        "Sever shutdown on: Mon, Jan 30th, 2023 @ 1:25am (PT)")
    st.markdown("##")

# TODO: Main
st.markdown("""<h1 style='
                font-family: Recoleta-Regular; font-weight: 400; color: #c89b3c;
                font-size: 3.5rem'>How Bad Is Your League Profile</h1>""",
            unsafe_allow_html=True)

st.markdown("""<h3 style='
                font-family: Recoleta-Regular; font-weight: 400;
                font-size: 1.55rem'>Our sophisticated A.I. judges your awful style of play</h3>""",
            unsafe_allow_html=True)

"""
![Python](https://img.shields.io/badge/Made%20With-Python%203.8-blue.svg?style=for-the-badge&logo=Python)
![Plotly](https://img.shields.io/badge/plotly%20-%2300416A.svg?&style=for-the-badge&logo=plotly&logoColor=white)
"""
st.markdown("##")
st.image("img/wallpaper.jpg")


regions = {
    "EUW": "EUW1",
    "NA": "NA1",
    "OCE": "OC1",
    "KR": "KR",
    "VN": "VN2"
}

mass = {
    "EUW": "EUROPE",
    "NA": "AMERICAS",
    "OCE": "SEA",
    "VN": "SEA",
    "KR": "ASIA"
}

modes = {
    "Normal Draft": 400,
    "Ranked Solo": 420,
    "Ranked Flex": 440,
    "ARAM": 450
}

st.write("##")
with st.container():
    col1, col2, col3 = st.columns([1, 1, 2])

    inputs = {}
    with col1:
        region = st.selectbox("Choose your region", list(regions.keys()))
        inputs['region'] = regions[region]
        inputs['mass_region'] = mass[region]

    with col2:
        mode = st.selectbox("Choose game mode", list(modes.keys()))
        inputs['mode'] = modes[mode]

    with col3:
        summoner = st.text_input("Search a summoner")
        inputs['summoner'] = summoner
    run = st.button("Search")

if run:
    df = master_function(inputs['summoner'], inputs['region'],
                         inputs['mass_region'], 50, inputs['mode'], key)

    df = pd.read_csv("df.csv")

    # TODO: Winrate
    st.write("##")
    with st.container():
        l, r = st.columns([1, 1])
        with l:
            k, d, a, kda, p_kill = basic(df)
            st.header("Overview")
            st.markdown(f"""<h1 style='
                    font-weight: 400; color: #999999;
                    font-size: 3rem'>{k} / <span style='color:#E84057'>{d}</span> / {a}</h1>""",
                        unsafe_allow_html=True)
            st.markdown(f"""<h1 style='
                    font-weight: 600; color: #E84057;
                    font-size: 5rem'>{kda} : 1</h1>""",
                        unsafe_allow_html=True)
            st.markdown(f"""<h1 style='
                    font-weight: 400; color: #fafafa;
                    font-size: 3rem'>P/Kill : {p_kill}%</h1>""",
                        unsafe_allow_html=True)
        with r:
            graph = winrate(df)
            st.plotly_chart(graph, use_container_width=True)

    # TODO: General stats
    stats = overview(df)
    headers = ['Winrate', 'KDA', 'DMG/min', 'Gold/min']
    stats2 = statistics(df)
    lowers = ['Avg Game', 'Vision Score', 'CS per Minute', 'First Blood Rate']

    st.write("##")
    with st.container():
        st.header("Statistics")
        cols = st.columns([1, 1, 1, 1])
        for i in range(len(cols)):
            with cols[i]:
                st.subheader(stats[i])
                st.write(headers[i])

        cols = st.columns([1, 1, 1, 1])
        for i in range(len(cols)):
            with cols[i]:
                st.subheader(stats2[i])
                st.write(lowers[i])

    # TODO: Champ pool
    champDf = champ_df(df)
    champs = get_champ_pool(champDf)

    st.write("##")
    with st.container():
        st.header("Champion pool")
        cols = st.columns([1, 1, 1, 1, 1])
        for i in range(len(cols)):
            url = "icons/" + champs[i] + "_0.jpg"
            with cols[i]:
                st.image(url)

    # TODO: Mastery timeline of most played champion
    st.write("##")
    with st.container():
        st.header("Most played champion")
        graph = champexp_graph(champDf, df)
        st.plotly_chart(graph, use_container_width=True)
