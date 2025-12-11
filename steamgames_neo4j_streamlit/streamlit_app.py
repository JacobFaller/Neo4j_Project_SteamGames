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
    q9_n_est_games_from_source_graph,
    q0_tag_based_recommendations_graph,
)

st.set_page_config(
    page_title="Steam Games Graph Explorer",
    layout="wide",
)

OPTIONS = [
    "Home",
    "Q1 – Games by Tag (table)",
    "Q2 – Games by Publisher (table)",
    "Q3 – Genre Distribution (chart)",
    "Q4 – Avg Price & Rating per Tag (chart)",
    "Q5 – Games per Release Year (chart)",
    "Q6 – Game Neighborhood (graph)",
    "Q7 – Similar Games via Shared Tags (graph)",
    "Q8 – Publisher–Genre Subgraph (graph)",
    "Q9 – N-est Games from Source (graph)",
    "Q0 – Tag-based Recommendations (graph)",
]


# ---------- get current view from URL ----------
params = st.query_params
current_view = params.get("view", "Home")  # <- no list, no [0]

if current_view not in OPTIONS:
    current_view = "Home"


# ---------- sidebar ----------
st.sidebar.markdown(
    "<h2 style='font-weight:700; font-size:22px; margin-bottom: 0.5rem;'>📌 Navigation</h2>",
    unsafe_allow_html=True,
)

st.markdown(
    """
    <style>
    div[data-testid="stSidebar"] div[role="radiogroup"] > label {
        display: flex;
        align-items: center;
        height: 48px;
        padding: 4px 0;
        margin-bottom: 4px;
        line-height: 1.2rem !important;
        white-space: normal !important;
    }
    div[data-testid="stSidebar"] div[role="radiogroup"] > label p {
        margin: 0 !important;
        padding: 0 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

sidebar_choice = st.sidebar.radio(
    "",
    OPTIONS,
    index=OPTIONS.index(current_view),
)

if sidebar_choice != current_view:
    current_view = sidebar_choice
    st.query_params["view"] = current_view

# ---------- HOME PAGE ----------
if current_view == "Home":
    st.title("Steam Games Graph Explorer")

    st.write(
        """
        This application demonstrates the use of a Neo4j AuraDB graph database to analyze and visualize 
        structural patterns in the Steam games ecosystem.  
        
        It exposes **eight predefined Cypher queries** that highlight:
        - table-based analytics
        - statistical charts
        - interactive graph visualizations (neighborhoods, similarity clusters, publisher–genre subgraphs)  

        Use the sidebar to select a query, or choose one of the tiles below.
        """
    )

    st.markdown("---")
    st.subheader("Available Queries")

    # style card-like buttons
    # style card-like buttons (title + description inside)
    st.markdown(
        """
        <style>
        /* Outer wrapper for each tile */
        div.tile-button {
            height: 80px !important;           /* tile height */
            margin-bottom: 8px !important;     /* small row gap */
        }

        /* Style the Streamlit button as a compact card */
        div.tile-button > button {
            background-color: #1f1f1f !important;
            border-radius: 16px !important;
            border: 1px solid #333 !important;
            padding: 8px 12px !important;

            width: 100% !important;
            height: 100% !important;

            text-align: center !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;

            cursor: pointer !important;
            font-size: 0.95rem !important;
            font-weight: 600 !important;

            transition: background-color 0.15s ease, transform 0.15s ease !important;
        }

        div.tile-button > button:hover {
            background-color: #262626 !important;
            transform: translateY(-2px) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


    cols = st.columns(3)

    tiles = [
    "Q1 – Games by Tag (table)",
    "Q2 – Games by Publisher (table)",
    "Q3 – Genre Distribution (chart)",
    "Q4 – Avg Price & Rating per Tag (chart)",
    "Q5 – Games per Release Year (chart)",
    "Q6 – Game Neighborhood (graph)",
    "Q7 – Similar Games via Shared Tags (graph)",
    "Q8 – Publisher–Genre Subgraph (graph)",
    "Q9 – N-est Games from Source (graph)",
    "Q0 – Tag-based Recommendations (graph)",
    ]



    for i, label in enumerate(tiles):
        col = cols[i % 3]
        with col:
            st.markdown('<div class="tile-button">', unsafe_allow_html=True)

            # show a short, clean title on the tile
            short_title = label.split("(", 1)[0].strip()  # e.g. "Q1 – Games by Tag"

            if st.button(short_title, key=f"tile_{i}", use_container_width=True):
                st.query_params["view"] = label
                st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

    st.stop()
# ---------------- TABLE QUERIES ----------------

if current_view.startswith("Q1"):
    st.header("Q1 – Games by Tag")
    st.write("Displays a ranked list of games associated with a selected tag, including their release year, price, rating, and popularity.")
    tag = st.text_input("Tag name", "Adventure")
    if st.button("Run"):
        df = q1_games_by_tag(tag)
        st.dataframe(df, use_container_width=True)

elif current_view.startswith("Q2"):
    st.header("Q2 – Games by Publisher")
    st.write("Retrieves all games published by a chosen publisher and summarizes their pricing, ratings, and tagging breadth.")
    pub = st.text_input("Publisher", "Valve")
    if st.button("Run"):
        df = q2_games_by_publisher(pub)
        st.dataframe(df, use_container_width=True)

# ---------------- CHART QUERIES ----------------

elif current_view.startswith("Q3"):
    st.header("Q3 – Genre Distribution")
    st.write("Visualizes the distribution of games across genres to highlight which genres are most prevalent in the dataset.")
    if st.button("Run"):
        df = q3_genre_distribution()
        st.dataframe(df, use_container_width=True)

        fig = px.bar(df, x="genre", y="gameCount", title="Games Per Genre")
        st.plotly_chart(fig, use_container_width=True)

elif current_view.startswith("Q4"):
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

elif current_view.startswith("Q5"):
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

elif current_view.startswith("Q6"):
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
                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    config={
                        "scrollZoom": True,   # enables wheel & pinch zoom
                        "displayModeBar": True,
                        "dragmode": "pan"     # ← makes dragging move the graph
                    }
                )


elif current_view.startswith("Q7"):
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
                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    config={
                        "scrollZoom": True,   # enables wheel & pinch zoom
                        "displayModeBar": True,
                        "dragmode": "pan"     # ← makes dragging move the graph
                    }
                )


elif current_view.startswith("Q8"):
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
                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    config={
                        "scrollZoom": True,   # enables wheel & pinch zoom
                        "displayModeBar": True,
                        "dragmode": "pan"     # ← makes dragging move the graph
                    }
                )


elif current_view.startswith("Q9"):
    st.header("Q9 – The N-est Path (graph)")
    st.write(
        "The 'N-est'-Path instead of the shortest path, because sometimes life is about the journey, not the destination. You get to decide! \n\n" \
        "From a selected game, finds and visualizes up to five other games that are "
        "exactly **n thematic relationships (tag/genre)** away."
    )

    col1, col2 = st.columns(2)
    with col1:
        source_game = st.text_input("Source game", "Portal 2")
    with col2:
        n = st.selectbox("Distance n", [2, 4, 6], index=0)

    if st.button("Run Q9"):
        try:
            records = q9_n_est_games_from_source_graph(source_game, int(n))
        except ValueError as e:
            st.error(str(e))
            records = []

        if not records:
            st.warning(
                f"No games found at exactly {int(n)} thematic hops "
                f"from '{source_game}'."
            )
        else:
            fig = build_network_figure(
                records,
                node_keys=["sourceGame", "node"],
                rel_keys=["rel"],
                title=f"Thematic games at distance n = {int(n)} from {source_game}",
                layout_mode="spring",
            )
            if fig is None:
                st.warning("Graph is empty.")
            else:
                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    config={
                        "scrollZoom": True,
                        "displayModeBar": True,
                        "dragmode": "pan",
                    },
                )


elif current_view.startswith("Q0"):
    st.header("Q0 – Tag-based Recommendations (graph)")
    st.write(
        "Recommends up to five games based on **shared tags** with the selected title, "
        "and visualizes the source game, recommended games, and connecting tags."
    )

    game_name = st.text_input("Game name", "Portal 2")

    col1, col2, col3 = st.columns(3)
    with col1:
        tag1 = st.text_input("Tag 1 (optional)", "")
    with col2:
        tag2 = st.text_input("Tag 2 (optional)", "")
    with col3:
        tag3 = st.text_input("Tag 3 (optional)", "")

    if st.button("Run Q0"):
        tags = [t for t in [tag1, tag2, tag3] if t.strip()]

        records = q0_tag_based_recommendations_graph(game_name, tags)

        if not records:
            st.warning(
                "No recommendations found. "
                "Check the game name and/or try different tags."
            )
        else:
            fig = build_network_figure(
                records,
                node_keys=["sourceGame", "recommendedGame", "tag"],
                rel_keys=["srcTagRel", "recTagRel"],
                title=f"Tag-based recommendations for {game_name}",
                layout_mode="q7_radial",   # radial layout: center game, ring of tags, outer ring of games
            )
            if fig is None:
                st.warning("Graph is empty.")
            else:
                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    config={
                        "scrollZoom": True,
                        "displayModeBar": True,
                        "dragmode": "pan",
                    },
                )
