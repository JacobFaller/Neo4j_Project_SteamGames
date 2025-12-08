import streamlit as st
import plotly.express as px
import streamlit.components.v1 as components

from graph_utils import build_network
from neo4j_queries import (
    q1_games_by_tag,
    q2_games_by_publisher,
    q3_genre_distribution,
    q4_avg_price_rating_per_tag,
    q5_games_per_year,
    q6_game_neighborhood,
    q7_similar_games_shared_tags,
    q8_publisher_genre_subgraph,
)

st.set_page_config(page_title="Steam Games Graph Explorer", layout="wide")
st.title("Steam Games Graph Explorer")

query = st.sidebar.radio(
    "Select a query",
    [
        "Q1 – Games by Tag (table)",
        "Q2 – Games by Publisher (table)",
        "Q3 – Genre Distribution (chart)",
        "Q4 – Avg Price & Rating per Tag (chart)",
        "Q5 – Games per Release Year (chart)",
        "Q6 – Game Neighborhood (graph)",
        "Q7 – Similar Games via Shared Tags (graph)",
        "Q8 – Publisher–Genre Subgraph (graph)",
    ],
)

# ---------------- TABLE QUERIES ----------------

if query.startswith("Q1"):
    st.header("Q1 – Games by Tag")
    tag = st.text_input("Tag name", "RPG")
    if st.button("Run"):
        df = q1_games_by_tag(tag)
        st.dataframe(df, use_container_width=True)

elif query.startswith("Q2"):
    st.header("Q2 – Games by Publisher")
    pub = st.text_input("Publisher", "Valve")
    if st.button("Run"):
        df = q2_games_by_publisher(pub)
        st.dataframe(df, use_container_width=True)

# ---------------- CHART QUERIES ----------------

elif query.startswith("Q3"):
    st.header("Q3 – Genre Distribution")
    if st.button("Run"):
        df = q3_genre_distribution()
        st.dataframe(df, use_container_width=True)

        fig = px.bar(df, x="genre", y="gameCount", title="Games Per Genre")
        st.plotly_chart(fig, use_container_width=True)

elif query.startswith("Q4"):
    st.header("Q4 – Avg Price & Rating per Tag")
    min_games = st.slider("Minimum games", 5, 100, 20)
    if st.button("Run"):
        df = q4_avg_price_rating_per_tag(min_games=min_games)
        st.dataframe(df, use_container_width=True)

        fig = px.scatter(
            df,
            x="avgPrice",
            y="avgRating",
            size="gameCount",
            hover_name="tag",
            title="Avg Price vs Rating per Tag",
        )
        st.plotly_chart(fig, use_container_width=True)

elif query.startswith("Q5"):
    st.header("Q5 – Games per Release Year")
    col1, col2 = st.columns(2)
    with col1: min_year = st.number_input("Min year", value=2000)
    with col2: max_year = st.number_input("Max year", value=2025)

    if st.button("Run"):
        df = q5_games_per_year(int(min_year), int(max_year))
        st.dataframe(df, use_container_width=True)

        fig = px.line(df, x="year", y="gameCount", title="Games per Year")
        st.plotly_chart(fig, use_container_width=True)

# ---------------- GRAPH QUERIES ----------------

elif query.startswith("Q6"):
    st.header("Q6 – Game Neighborhood")
    game = st.text_input("Game", "Portal 2")
    if st.button("Run"):
        records = q6_game_neighborhood(game)
        net = build_network(records, ["g", "p", "d", "ge", "t", "l"], ["r1", "r2", "r3", "r4", "r5"])
        net.show("q6.html")
        components.html(open("q6.html").read(), height=600, width=1000)

elif query.startswith("Q7"):
    st.header("Q7 – Similar Games via Shared Tags")
    game = st.text_input("Game", "Portal 2")
    if st.button("Run"):
        records = q7_similar_games_shared_tags(game)
        net = build_network(records, ["g", "other", "tag"], ["r1", "r2"])
        net.show("q7.html")
        components.html(open("q7.html").read(), height=600, width=1000)

elif query.startswith("Q8"):
    st.header("Q8 – Publisher–Genre Subgraph")
    pub = st.text_input("Publisher", "Valve")
    if st.button("Run"):
        records = q8_publisher_genre_subgraph(pub)
        net = build_network(records, ["p", "g", "ge"], ["pubRel", "genRel"])
        net.show("q8.html")
        components.html(open("q8.html").read(), height=600, width=1000)
