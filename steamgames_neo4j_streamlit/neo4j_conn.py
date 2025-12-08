import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USER")
PASSWORD = os.getenv("NEO4J_PASSWORD")
DATABASE = os.getenv("NEO4J_DATABASE")


def get_driver():
    """Create a Neo4j driver instance."""
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    return driver


def run_cypher(query: str, parameters: dict | None = None):
    """Run a Cypher query on Aura and return records."""
    driver = get_driver()
    with driver.session(database=DATABASE) as session:
        result = session.run(query, parameters or {})
        return list(result)
