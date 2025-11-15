from typing import Optional

from langchain_community.graphs.neo4j_graph import Neo4jGraph

try:  # pragma: no cover
    from .config import get_secret
except ImportError:  # pragma: no cover
    from config import get_secret

graph = None
GRAPH_ERROR: Optional[Exception] = None

try:  # pragma: no cover
    graph = Neo4jGraph(
        url=get_secret("NEO4J_URI"),
        username=get_secret("NEO4J_USERNAME"),
        password=get_secret("NEO4J_PASSWORD"),
    )
except Exception as exc:  # pragma: no cover
    GRAPH_ERROR = exc
