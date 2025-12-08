import pandas as pd
from neo4j_conn import run_cypher

# ----------------------
# Q1 & Q2: TABLE QUERIES
# ----------------------

def q1_games_by_tag(tag_name: str) -> pd.DataFrame:
    query = """
    MATCH (g:Game)-[:HAS_TAG]->(t:Tag {name: $tagName})
    RETURN
        g.name AS title,
        substring(g.releaseDate, 0, 4) AS releaseYear,
        g.price AS price,
        g.rating AS rating,
        g.recommendations AS recommendations
    ORDER BY g.rating DESC, g.recommendations DESC
    LIMIT 50;
    """
    records = run_cypher(query, {"tagName": tag_name})
    return pd.DataFrame([r.data() for r in records])


def q2_games_by_publisher(publisher_name: str) -> pd.DataFrame:
    query = """
    MATCH (p:Publisher {name: $publisherName})<-[:PUBLISHED_BY]-(g:Game)
    RETURN
        g.name AS title,
        substring(g.releaseDate, 0, 4) AS releaseYear,
        g.price AS price,
        g.rating AS rating,
        g.recommendations AS recommendations,
        count { (g)-[:HAS_TAG]->(:Tag) } AS tagCount
    ORDER BY g.rating DESC, g.recommendations DESC
    LIMIT 50;
    """
    records = run_cypher(query, {"publisherName": publisher_name})
    return pd.DataFrame([r.data() for r in records])

# ----------------------
# Q3–Q5: CHART QUERIES
# ----------------------

def q3_genre_distribution() -> pd.DataFrame:
    query = """
    MATCH (g:Game)-[:HAS_GENRE]->(ge:Genre)
    WITH ge.name AS genre, count(DISTINCT g) AS gameCount
    RETURN genre, gameCount
    ORDER BY gameCount DESC
    LIMIT 15;
    """
    return pd.DataFrame([r.data() for r in run_cypher(query)])


def q4_avg_price_rating_per_tag(min_games: int = 20) -> pd.DataFrame:
    query = """
    MATCH (g:Game)-[:HAS_TAG]->(t:Tag)
    WHERE g.price IS NOT NULL AND g.rating IS NOT NULL
    WITH
        t.name AS tag,
        count(DISTINCT g) AS gameCount,
        avg(g.price) AS avgPrice,
        avg(g.rating) AS avgRating
    WHERE gameCount >= $minGames
    RETURN tag, gameCount, avgPrice, avgRating
    ORDER BY gameCount DESC
    LIMIT 20;
    """
    return pd.DataFrame([r.data() for r in run_cypher(query, {"minGames": min_games})])


def q5_games_per_year(min_year: int, max_year: int) -> pd.DataFrame:
    """
    Aggregate games per release year using pandas.

    The releaseDate is stored as strings like '01-Nov-00'.
    We:
      - fetch raw dates and prices from Neo4j
      - parse them with pandas.to_datetime (format '%d-%b-%y')
      - extract the year
      - group by year (count, avg price)
      - filter by [min_year, max_year]
    """

    query = """
    MATCH (g:Game)
    WHERE g.releaseDate IS NOT NULL
    RETURN
        g.releaseDate AS releaseDate,
        g.price       AS price;
    """

    records = run_cypher(query)
    rows = [r.data() for r in records]
    df = pd.DataFrame(rows)

    if df.empty:
        return df

    # Parse the date strings like '01-Nov-00'
    df["date"] = pd.to_datetime(df["releaseDate"], format="%d-%b-%y", errors="coerce")

    # Drop rows we couldn't parse
    df = df.dropna(subset=["date"])

    # Extract year
    df["year"] = df["date"].dt.year

    # Group by year
    grouped = (
        df.groupby("year", as_index=False)
        .agg(
            gameCount=("year", "size"),
            avgPrice=("price", "mean"),
        )
        .sort_values("year")
    )

    # Filter by selected range
    grouped = grouped[(grouped["year"] >= min_year) & (grouped["year"] <= max_year)]

    return grouped


# ----------------------
# Q6–Q8: GRAPH QUERIES
# ----------------------

def q6_game_neighborhood(game_name: str):
    query = """
    MATCH (g:Game {name: $gameName})
    OPTIONAL MATCH (g)-[r1:PUBLISHED_BY]->(p:Publisher)
    OPTIONAL MATCH (g)-[r2:DEVELOPED_BY]->(d:Developer)
    OPTIONAL MATCH (g)-[r3:HAS_GENRE]->(ge:Genre)
    OPTIONAL MATCH (g)-[r4:HAS_TAG]->(t:Tag)
    OPTIONAL MATCH (g)-[r5:SUPPORTS_LANGUAGE]->(l:Language)
    RETURN g, p, d, ge, t, l, r1, r2, r3, r4, r5;
    """
    return run_cypher(query, {"gameName": game_name})


def q7_similar_games_shared_tags(game_name: str):
    query = """
    MATCH (g:Game {name: $gameName})-[:HAS_TAG]->(t:Tag)<-[:HAS_TAG]-(other:Game)
    WHERE g <> other
    WITH g, other, collect(DISTINCT t) AS sharedTags, count(DISTINCT t) AS commonTagCount
    WHERE commonTagCount >= 2
    ORDER BY commonTagCount DESC, other.rating DESC
    LIMIT 10
    UNWIND sharedTags AS tag
    MATCH (g)-[r1:HAS_TAG]->(tag)
    MATCH (other)-[r2:HAS_TAG]->(tag)
    RETURN g, other, tag, r1, r2;
    """
    return run_cypher(query, {"gameName": game_name})


def q8_publisher_genre_subgraph(publisher_name: str):
    query = """
    MATCH (p:Publisher {name: $publisherName})<-[:PUBLISHED_BY]-(g:Game)-[:HAS_GENRE]->(ge:Genre)
    WITH p, ge, g
    ORDER BY ge.name, g.rating DESC
    WITH p, ge, collect(g)[0..5] AS topGamesPerGenre
    UNWIND topGamesPerGenre AS g
    MATCH (p)<-[pubRel:PUBLISHED_BY]-(g)-[genRel:HAS_GENRE]->(ge)
    RETURN p, g, ge, pubRel, genRel;
    """
    return run_cypher(query, {"publisherName": publisher_name})

