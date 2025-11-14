from langchain_neo4j import Neo4jGraph
from config import get_secret

graph = Neo4jGraph(
    url=get_secret("NEO4J_URI"),
    username=get_secret("NEO4J_USERNAME"),
    password=get_secret("NEO4J_PASSWORD"),
)
