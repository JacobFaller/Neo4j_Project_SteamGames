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

<ins>Source:</ins> Kaggle - Steam Games Dataset (Author: Martin Bustos)

Due to file size constraints, the original CSV was split into two UTF-8 encoded parts before import. 
*NOTE: Only a subset of the "SteamGames_part_1_UTF8.csv" file contents is used. After the import of this, the Aura Free constraints had been reached already, preventin the use of the second file ("SteamGames_part_2.csv").*

<ins>Retained columns (graph-relevant features):</ins>

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

Several other columns were *deliberately* removed because they primarily featured cumulative, non-relational values that added little to graph reasoning and increased storage and processing overhead.

**🗂️ Graph Data Model**

<ins>Node Labels</ins>

Game

Publisher

Developer

Genre

Category

Language

Tag

Platform (Windows/Mac/Linux)

<ins>Relationship Types</ins>

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
| Name (Primary Entity) | AppID | Release date | Price | Discount | Rating | Achievements | Recommendations | Supported languages | Windows | Mac | Linux | Developers | Publishers | Categories | Genres | Tags |

**⚙️ Import Pipeline (High-Level)**

Because of the dataset size and Neo4j AuraDB free-tier relationship limits, the import was performed in several stages:

Primary Game nodes

Import (:Game) nodes with basic attributes (ID, release date, price, discount, rating, achievements, recommendations).

Dataset reduction

Remove games with zero recommendations (and, in an earlier step, games with both zero recommendations and zero rating).

This reduced the graph from ~60k games and far more than ~400k relationships to roughly:

~13k Game nodes

~400k relationships

<ins>Relationship rebuilds</ins>

For each relationship type (e.g. Publisher, Developer, Genre, Category, Language, Tag), run a dedicated LOAD CSV + SPLIT + UNWIND import.

Arrays such as Supported languages required additional cleaning (e.g. stripping brackets and quotes) before splitting.

<ins>Tag relationships and AuraDB limit</ins>

Tag relationships were imported last, as they generate a large number of edges.

The free-tier limit of 400k relationships was essentially reached; only a small remainder of tag relationships exceeded the limit, which is acceptable for the project’s learning-oriented scope.

**STILL IN PROGRESS --> 🌐 Web Application Architecture**

The web application is intentionally minimal:

<u>Backend</u>

Language: Python

Framework: Flask

Database driver: Official neo4j Python driver

<ins>Responsibilities:</ins>

Manage a shared Neo4j driver/session.

Expose HTTP endpoints such as /api/games-by-tag, /api/games-by-publisher, etc.

Return JSON suitable for both table and graph visualizations.

<ins>Frontend</ins>

Stack: Plain HTML, CSS, and vanilla JavaScript (Fetch API).

<ins>UI concept:</ins>

Single-page layout with ~5 “query cards” (pre-selected query statements).

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


**STILL IN PROGRESS --> 🚀 Quick Start**


**STILL IN PROGRESS --> 📊 Graph Visualization (via WebApp)**


**📖 Full Documentation**

Detailed planning, import scripts, intermediate statistics, and design rationales are documented in Notion:

**👉 Neo4j Steam Games Graph Project Plan (Notion)**
https://www.notion.so/Neo4j-Steam-Games-Graph-Project-Plan-2af149f538b4809eb4f8d69c3e24a766?showMoveTo=true&saveParent=true
