import streamlit as st
import plotly.express as px

from graph_utils import build_network_figure
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

st.set_page_config(
    page_title="Steam Games Graph Explorer",
    layout="wide",
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
    st.header("Q1 – Game Neighborhood (graph)")
    st.write("Displays a ranked list of games associated with a selected tag, including their release year, price, rating, and popularity.")
    tag = st.text_input("Tag name", "Adventure")
    if st.button("Run"):
        df = q1_games_by_tag(tag)
        st.dataframe(df, use_container_width=True)

elif query.startswith("Q2"):
    st.header("Q2 – Games by Publisher")
    st.write("Retrieves all games published by a chosen publisher and summarizes their pricing, ratings, and tagging breadth.")
    pub = st.text_input("Publisher", "Valve")
    if st.button("Run"):
        df = q2_games_by_publisher(pub)
        st.dataframe(df, use_container_width=True)

# ---------------- CHART QUERIES ----------------

elif query.startswith("Q3"):
    st.header("Q3 – Genre Distribution")
    st.write("Visualizes the distribution of games across genres to highlight which genres are most prevalent in the dataset.")
    if st.button("Run"):
        df = q3_genre_distribution()
        st.dataframe(df, use_container_width=True)

        fig = px.bar(df, x="genre", y="gameCount", title="Games Per Genre")
        st.plotly_chart(fig, use_container_width=True)

elif query.startswith("Q4"):
    st.header("Q4 – Avg Price & Rating per Tag")
    st.write("Aggregates games by tag to compare average prices, average ratings, and tag popularity.")
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
    st.write("Analyzes temporal trends by plotting the number of games released per year within a chosen time interval.")
    col1, col2 = st.columns(2)
    with col1:
        min_year = st.number_input("Min year", value=2000, step=1)
    with col2:
        max_year = st.number_input("Max year", value=2025, step=1)

    if st.button("Run Q5"):
        df = q5_games_per_year(int(min_year), int(max_year))

        # Debug visibility: show whatever came back
        st.subheader("Debug – Data after filtering")
        st.dataframe(df, use_container_width=True)

        if df.empty:
            st.warning("No data found for this year range.")
        else:
            st.subheader("Games per year")
            fig = px.line(df, x="year", y="gameCount", title="Games per Year")
            fig.update_layout(xaxis_title="Year", yaxis_title="Number of games")
            st.plotly_chart(fig, use_container_width=True)


# ---------------- GRAPH QUERIES ----------------

elif query.startswith("Q6"):
    st.header("Q6 – Game Neighborhood (graph)")
    st.write("Shows the immediate semantic neighborhood of a selected game, including its publishers, developers, genres, tags, and supported languages.")
    game_name = st.text_input("Game name", "Portal 2")
    if st.button("Run Q6"):
        records = q6_game_neighborhood(game_name)
        if not records:
            st.warning("No results found.")
        else:
            fig = build_network_figure(
                records,
                node_keys=["g", "p", "d", "ge", "t", "l"],
                rel_keys=["r1", "r2", "r3", "r4", "r5"],
                title=f"Neighborhood of {game_name}",
            )
            if fig is None:
                st.warning("Graph is empty.")
            else:
                st.plotly_chart(fig, use_container_width=True)


elif query.startswith("Q7"):
    st.header("Q7 – Similar Games via Shared Tags (graph)")
    st.write("Identifies and visualizes games that share multiple tags with the selected title, revealing clusters of related gameplay or thematic elements.")
    game_name = st.text_input("Game name", "Portal 2")
    if st.button("Run Q7"):
        records = q7_similar_games_shared_tags(game_name)
        if not records:
            st.warning("No results found.")
        else:
            fig = build_network_figure(
                records,
                node_keys=["g", "other", "tag"],
                rel_keys=["r1", "r2"],
                title=f"Games similar to {game_name} (shared tags)",
                layout_mode="q7_radial",
            )
            if fig is None:
                st.warning("Graph is empty.")
            else:
                st.plotly_chart(fig, use_container_width=True)


elif query.startswith("Q8"):
    st.header("Q8 – Publisher–Genre Subgraph (graph)")
    st.write("Illustrates how a publisher's catalog spans across genres by linking each genre to representative high-rated games.")
    pub_name = st.text_input("Publisher name", "Valve")
    if st.button("Run Q8"):
        records = q8_publisher_genre_subgraph(pub_name)
        if not records:
            st.warning("No results found.")
        else:
            fig = build_network_figure(
                records,
                node_keys=["p", "g", "ge"],
                rel_keys=["pubRel", "genRel"],
                title=f"Publisher–Genre subgraph for {pub_name}",
            )
            if fig is None:
                st.warning("Graph is empty.")
            else:
                st.plotly_chart(fig, use_container_width=True)


