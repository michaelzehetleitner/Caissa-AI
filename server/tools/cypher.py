from langchain_neo4j import GraphCypherQAChain
from langchain.prompts.prompt import PromptTemplate
# from gemini_llm import llm
from llama_llm import llm
from graph import graph

try:  # pragma: no cover
    from ..prompts import CYPHER_GENERATION_TEMPLATE
except ImportError:  # pragma: no cover
    from prompts import CYPHER_GENERATION_TEMPLATE

cypher_prompt = PromptTemplate.from_template(CYPHER_GENERATION_TEMPLATE)

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


def cypher_qa(question):
    """
    Thin wrapper around the GraphCypherQAChain that prints helpful diagnostics
    every time the tool is invoked. Whatever input LangChain passes through
    (string or dict) is forwarded unchanged to the underlying chain.
    """
    print("\n[CypherQA] Incoming question/input:", question)
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
