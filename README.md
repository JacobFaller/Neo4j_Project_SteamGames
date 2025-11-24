# Neo4j Steam Games Graph Project

This project constructs and explores a graph database of Steam games using Neo4j AuraDB and a curated Kaggle dataset.
A minimal web application (Python + Flask) exposes predefined Cypher queries and includes at least one graph visualization directly in the browser.

The focus is on graph modelling, query design, and visualization, not on building a feature-complete production system.

**📚 Table of Contents**

Dataset Overview

Graph Data Model

Import Pipeline

Web Application Architecture

Planned Cypher Queries

Project Structure

Quick Start

Graph Visualization

Full Documentation

**📁 Dataset Overview**

Source

Kaggle: Steam Games Dataset (Author: Martin Bustos)

Repository data: see data/ folder and links in this README.

Due to file size constraints, the original CSV was split into two UTF-8 encoded parts before import.

Retained columns (graph-relevant features):

Name (primary entity)

AppID

Release date

Price

Discount

Rating score (Wilson score interval lower bound)

Achievements

Recommendations

Supported languages

Windows / Mac / Linux

Developers

Publishers

Categories

Genres

Tags

Several other columns were deliberately removed because they primarily featured cumulative, non-relational values that added little to graph reasoning and increased storage and processing overhead.

**🗂️ Graph Data Model**
Node Labels

Game

Publisher

Developer

Genre

Category

Language

Tag

Platform (Windows/Mac/Linux)

Relationship Types

(:Game)-[:PUBLISHED_BY]->(:Publisher)

(:Game)-[:DEVELOPED_BY]->(:Developer)

(:Game)-[:HAS_GENRE]->(:Genre)

(:Game)-[:HAS_CATEGORY]->(:Category)

(:Game)-[:SUPPORTS_LANGUAGE]->(:Language)

(:Game)-[:SUPPORTS_PLATFORM]->(:Platform)

(:Game)-[:HAS_TAG]->(:Tag)

Array-like fields (e.g. languages, genres, categories, tags) are split into atomic nodes and relationships, so multiple games can share the same Language, Genre, etc., enabling genuine graph traversal and pattern discovery.

**🧬 Schema Diagram**

A high-level schema visualization is included in the repository:

![SteamGamesColumns.png](attachment:a6ed7859-cd0b-4547-b025-222f76cffce8:image.png)

| Game Node Title | Game Node Attribute | Game Node Attribute | Game Node Attribute | Game Node Attribute | Game Node Attribute | Game Node Attribute | Game Node Attribute | SUPPORTS LANGUAGE | SUPPORTS PLATFORM | SUPPORTS PLATFORM | SUPPORTS PLATFORM | DEVELOPED BY | PUBLISHED BY | HAS CATEGORY | HAS GENRE | HAS TAG |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Name (Primary Entity) | AppID | Release date | Price | Discount | Rating Score (Wilson score interval lower bound) | Achievements | Recommendations | Supported languages | Windows | Mac | Linux | Developers | Publishers | Categories | Genres | Tags |

**⚙️ Import Pipeline (High-Level)**

Because of the dataset size and Neo4j AuraDB free-tier relationship limits, the import was performed in several stages:

Primary Game nodes

Import (:Game) nodes with basic attributes (ID, release date, price, discount, rating, achievements, recommendations).

Dataset reduction

Remove games with zero recommendations (and, in an earlier step, games with both zero recommendations and zero rating).

This reduced the graph from ~60k games and ~400k relationships to roughly:

~13k Game nodes

~93k–230k relationships (depending on stage).

Relationship rebuilds

For each relationship type (e.g. Publisher, Developer, Genre, Category, Language, Tag), run a dedicated LOAD CSV + SPLIT + UNWIND import.

Arrays such as Supported languages required additional cleaning (e.g. stripping brackets and quotes) before splitting.

Tag relationships and AuraDB limit

Tag relationships were imported last, as they generate a large number of edges.

The free-tier limit of 400k relationships was almost reached; only a small remainder of tag relationships exceeded the limit, which is acceptable for the project’s learning-oriented scope.

**STILL IN PROGRESS --> 🌐 Web Application Architecture**

The web application is intentionally minimal:

Backend

Language: Python

Framework: Flask

Database driver: Official neo4j Python driver

Responsibilities:

Manage a shared Neo4j driver/session.

Expose HTTP endpoints such as /api/games-by-tag, /api/games-by-publisher, etc.

Return JSON suitable for both table and graph visualizations.

Frontend

Stack: Plain HTML, CSS, and vanilla JavaScript (Fetch API).

UI concept:

Single-page layout with ~5 “query cards”.

Each card includes:

Short explanation of the query.

Optional user input (e.g. tag, publisher, game name).

A “Run query” button.

Results rendered either as:

HTML tables (for lists), or

Embedded graph visualization for at least one query.

**STILL IN PROGRESS --> 🔎 Cypher Query Ideas**

The system will implement at least five queries drawn from the following candidates:

Games by Tag or Genre
Input: tag/genre name.
Output: list of games, with release date and price.

Games by Publisher / Developer
Input: publisher or developer name.
Output: associated games with basic metadata.

Similar / Related Games
Input: game title.
Output: games that share tags/genres or other structural similarities.

Most “Popular” Games
Input: none.
Output: top N games ordered by, e.g., number of relationships or recommendation count.

Co-occurring Tags or Dense Clusters
Input: optional minimum count.
Output: tag–tag or publisher–tag pairs with many games incident to them.

Genre-Based Recommendations
Input: game title.
Output: games with overlapping genres/tags and similar properties (e.g. price range, rating).

Publisher–Tag Statistics
Input: optional minimum number of games.
Output: publishers and their most characteristic tags.

Oldest vs. Newest per Genre
Input: none.
Output: earliest and latest game per genre by release date.

**STILL IN PROGRESS --> 📁 Project Structure**

A minimal, suggested project layout:

Neo4j_Project_SteamGames/
├─ data/
│  ├─ SteamGames_part_1_UTF8.csv
│  ├─ SteamGames_part_2_UTF8.csv
│  └─ (optional) raw/          # original files or backup
├─ docs/
│  └─ steam_games_graph_schema.png   # exported schema diagram
├─ backend/
│  ├─ app.py                         # Flask entrypoint
│  ├─ neo4j_client.py                # driver/session helper
│  ├─ queries.py                     # central Cypher query definitions
│  └─ config_example.py              # template for connection settings
├─ frontend/
│  ├─ index.html
│  ├─ styles.css
│  └─ main.js
├─ cypher/
│  ├─ import_games.cypher
│  ├─ import_relationships.cypher
│  └─ analysis_queries.cypher
├─ README.md
└─ requirements.txt


You can of course adapt filenames and folders to your preferred structure.

**STILL IN PROGRESS --> 🚀 Quick Start**

The exact steps depend on how you structure the code, but a typical setup looks like this:

Clone the repository

git clone https://github.com/JacobFaller/Neo4j_Project_SteamGames.git
cd Neo4j_Project_SteamGames


Create and activate a virtual environment

python -m venv .venv
source .venv/bin/activate      # on Windows: .venv\Scripts\activate


Install dependencies

pip install -r requirements.txt


requirements.txt will typically include:

Flask
neo4j


Configure Neo4j connection

Create backend/config.py (from config_example.py) with your AuraDB connection details:

NEO4J_URI = "neo4j+s://<your-instance-id>.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "<your-password>"
NEO4J_DATABASE = "neo4j"  # or your custom DB name


Run the Flask backend

cd backend
python app.py


Open the frontend

Option A: serve frontend/ via a simple static server, or

Option B: reference the Flask backend from frontend/main.js (e.g. fetch("http://localhost:5000/api/games-by-tag")), then open frontend/index.html in your browser.

**STILL IN PROGRESS --> 📊 Graph Visualization (via WebApp)**

For at least one query, the frontend will render a graph visualization of the result set.

Planned library: Neovis.js

Neo4j-focused wrapper around vis.js.

Accepts Cypher and renders nodes/edges with minimal configuration.

Ideal for quickly turning query results into an interactive network.

Alternative options (if needed):

Cytoscape.js (general-purpose, rich layouts)

D3.js force-directed graphs (very flexible but more verbose)

**📖 Full Documentation**

Detailed planning, import scripts, intermediate statistics, and design rationales are documented in Notion:

**👉 Neo4j Steam Games Graph Project Plan (Notion)**
https://www.notion.so/Neo4j-Steam-Games-Graph-Project-Plan-2af149f538b4809eb4f8d69c3e24a766?showMoveTo=true&saveParent=true
