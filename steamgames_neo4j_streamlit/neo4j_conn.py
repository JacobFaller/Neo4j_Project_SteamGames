# neo4j_conn.py
import os
from pathlib import Path
from neo4j import GraphDatabase
from dotenv import load_dotenv

ENV_PATH = Path(__file__).with_name(".env")
load_dotenv(dotenv_path=ENV_PATH)

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USER")
PASSWORD = os.getenv("NEO4J_PASSWORD")
DATABASE = os.getenv("NEO4J_DATABASE")

# Create ONE driver when the module is imported
_driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))


def get_driver():
    """Return the global Neo4j driver instance."""
    return _driver


def run_cypher(query: str, parameters: dict | None = None):
    """Run a Cypher query and return a list of neo4j.Record objects."""
    driver = get_driver()
    with driver.session(database=DATABASE, default_access_mode="READ") as session:
        result = session.run(query, parameters or {})
        return list(result)
