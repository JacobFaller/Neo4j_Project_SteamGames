# Neo4j Steam Games Graph Project

This project constructs and explores a graph database of Steam games using Neo4j AuraDB and a curated subset of a Kaggle dataset. A lightweight Streamlit web application exposes eight predefined Cypher queries, providing both tabular analytics and interactive graph visualizations.

The focus of this work is graph modelling, import strategy, Cypher query design, and visual reasoning — not the development of a large-scale production system.

# 📚 Table of Contents

Dataset Overview

Graph Data Model

Schema Diagram

Import Pipeline

Web Application

Implemented Queries

Graph Visualization Features

Project Structure

Quick Start

Full Documentation

# 📁 Dataset Overview

Source: Steam Games Dataset (Kaggle — Martin Bustos)

Due to AuraDB Free tier limitations (relationship cap ≈ 400k), only a subset of the original CSV was imported. The dataset was split into two UTF-8 parts, and a preliminary filtering stage removed games with zero recommendations (and earlier, those with both zero recommendations and zero rating).

Fields used for graph modelling

Name (primary identity)

AppID

Release date

Price

Discount

Rating (Wilson lower bound)

Achievements

Recommendations

Supported languages

Developers

Publishers

Categories

Genres

Tags

Purely cumulative or textual fields were removed to reduce noise and maximize graph-relevant structure.

# 🗂️ Graph Data Model
Node Labels

Game

Publisher

Developer

Genre

Category

Language

Tag

Platform (Windows, Mac, Linux)

Relationship Types
(:Game)-[:PUBLISHED_BY]->(:Publisher)

(:Game)-[:DEVELOPED_BY]->(:Developer)

(:Game)-[:HAS_GENRE]->(:Genre)

(:Game)-[:HAS_CATEGORY]->(:Category)

(:Game)-[:SUPPORTS_LANGUAGE]->(:Language)

(:Game)-[:SUPPORTS_PLATFORM]->(:Platform)

(:Game)-[:HAS_TAG]->(:Tag)


All array-like fields were expanded into atomic nodes and relationships, enabling meaningful graph traversal and similarity-based reasoning.

Here is a general overview:

| Game Node Title | Game Node Attribute | Game Node Attribute | Game Node Attribute | Game Node Attribute | Game Node Attribute | Game Node Attribute | Game Node Attribute | SUPPORTS LANGUAGE | SUPPORTS PLATFORM | SUPPORTS PLATFORM | SUPPORTS PLATFORM | DEVELOPED BY | PUBLISHED BY | HAS CATEGORY | HAS GENRE | HAS TAG |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Name (Primary Entity) | AppID | Release date | Price | Discount | Rating Score (Wilson score interval lower bound) | Achievements | Recommendations | Supported languages | Windows | Mac | Linux | Developers | Publishers | Categories | Genres | Tags |


# ⚙️ Import Pipeline (High-Level Overview)

Due to the volume of relationships generated (especially by tags and genres), the data import required a staged pipeline:

1. Creation of Game nodes

Imported core attributes for ~13k games (filtered down from the full dataset).

2. Dataset reduction

Games lacking activity (no recommendations or zero rating) were removed to remain within AuraDB Free limits.

3. Incremental relationship imports

Each relationship category was imported via a dedicated LOAD CSV:

Developers

Publishers

Genres

Categories

Platforms

Languages

Tags (imported last due to very high cardinality)

Each stage involved splitting and cleaning string arrays, removing artifacts such as brackets, quotes, and whitespace.

4. AuraDB Free-tier constraints

The resulting graph contains approximately:

13,000+ game nodes

399,000+ relationships

Tag relationships slightly exceeded the limit; the final import therefore includes “most” but not all tag edges — sufficient for valid analysis.

#🌐 Web Application

The final application is written entirely in Python + Streamlit, with:

a left-hand navigation panel

eight predefined queries

interactive Plotly and PyVis-based visualizations

a Neo4j-backed analytics layer

a modular architecture allowing easy extensibility

Backend

Official Neo4j Python driver

.env configuration (URI, credentials, DB name)

Frontend

Streamlit interface

Plotly for charts

Custom PyVis layout for graph visualization

Automatic full-window responsive layouts

All queries run live against the Neo4j AuraDB instance.

#🔎 Implemented Queries

The app provides eight curated queries that demonstrate different graph reasoning patterns.

Q1 – Games by Tag

Q2 – Games by Publisher

Q3 – Genre Distribution (bar/pie)

Q4 – Average Price & Rating per Tag

Q5 – Games per Release Year (line chart)

Q6 – Game Neighborhood

Q7 – Similar Games via Shared Tags

Q8 – Publisher–Genre Subgraph

All graphs scale to the browser window using Streamlit’s layout="wide" and explicit Plotly height control.

#📁 Project Structure
steamgames_neo4j_streamlit/
│
├── streamlit_app.py        # Main frontend application
├── neo4j_conn.py           # Driver, session management, .env loader
├── neo4j_queries.py        # All Cypher queries exposed to the UI
├── graph_utils.py          # Graph layouts, PyVis+Plotly rendering
├── requirements.txt        # Python dependencies
└── .env.example            # Example config (no credentials committed)

#🚀 Quick Start
1. Clone the repository
git clone https://github.com/JacobFaller/Neo4j_Project_SteamGames
cd Neo4j_Project_SteamGames/steamgames_neo4j_streamlit

2. Create a virtual environment & install dependencies
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

3. Add your Neo4j credentials

Create a file named .env:

NEO4J_URI=neo4j+s://xxxx.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password
NEO4J_DATABASE=neo4j

4. Run the app
streamlit run streamlit_app.py

#📖 Full Documentation

Detailed planning, reasoning, intermediate experiments, and data-cleaning notes are available in the accompanying Notion workspace:

#👉 Neo4j Steam Games Graph Project Plan
https://www.notion.so/Neo4j-Steam-Games-Graph-Project-Plan-2af149f538b4809eb4f8d69c3e24a766
