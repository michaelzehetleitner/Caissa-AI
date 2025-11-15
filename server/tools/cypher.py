from langchain_community.chains.graph_qa.cypher import GraphCypherQAChain
from langchain.prompts.prompt import PromptTemplate
# from gemini_llm import llm

try:  # pragma: no cover
    from ..llama_llm import llm
except ImportError:  # pragma: no cover
    from llama_llm import llm

try:  # pragma: no cover
    from ..graph import graph, GRAPH_ERROR
except ImportError:  # pragma: no cover
    from graph import graph, GRAPH_ERROR

try:  # pragma: no cover
    from ..prompts import CYPHER_GENERATION_TEMPLATE
except ImportError:  # pragma: no cover
    from prompts import CYPHER_GENERATION_TEMPLATE

cypher_prompt = PromptTemplate.from_template(CYPHER_GENERATION_TEMPLATE)

if graph is not None:  # pragma: no branch
    _cypher_chain = GraphCypherQAChain.from_llm(
        llm,
        graph=graph,
        verbose=True,
        cypher_prompt=cypher_prompt,
        # return_intermediate_steps=True,
        return_direct=True,
        # validate_cypher=True,
        allow_dangerous_requests=True,
        handle_parsing_errors="ignore",
        handle_execution_errors="ignore",
    )
else:  # pragma: no cover
    _cypher_chain = None


def cypher_qa(question):
    """
    Thin wrapper around the GraphCypherQAChain that prints helpful diagnostics
    every time the tool is invoked. Whatever input LangChain passes through
    (string or dict) is forwarded unchanged to the underlying chain.
    """
    print("\n[CypherQA] Incoming question/input:", question)
    if _cypher_chain is None:  # pragma: no cover
        if GRAPH_ERROR is not None:
            raise RuntimeError(
                "GraphCypherQAChain is unavailable because the Neo4j graph "
                "connection failed."
            ) from GRAPH_ERROR
        raise RuntimeError("GraphCypherQAChain is unavailable: graph not initialized.")

    try:
        result = _cypher_chain.invoke(question)
    except Exception as exc:  # noqa: BLE001
        print("[CypherQA] Error while executing query:", exc)
        raise

    if isinstance(result, dict):
        context = result.get("context")
        if context is not None:
            print(f"[CypherQA] Context size: {len(context)}")
        print("[CypherQA] Raw result:", result)
    else:
        print("[CypherQA] Raw result:", result)

    return result
