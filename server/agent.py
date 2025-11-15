from pydoc import describe
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
from langchain import hub
# from gemini_llm import llm

try:  # pragma: no cover - prefer package-relative import
    from .llama_llm import llm
except ImportError:  # pragma: no cover - fallback when running as script
    from llama_llm import llm

try:  # pragma: no cover
    from .neurosymbolicAI import NeuroSymbolic
except ImportError:  # pragma: no cover
    from neurosymbolicAI import NeuroSymbolic

try:  # pragma: no cover
    from .tools.cypher import cypher_qa
except ImportError:  # pragma: no cover
    from tools.cypher import cypher_qa

try:  # pragma: no cover - fallback when running as a script
    from .prompts import CLASSIC_AGENT_PROMPT
except ImportError:  # pragma: no cover
    from prompts import CLASSIC_AGENT_PROMPT

ns = NeuroSymbolic()

describtions = {
    "Chess Solver Chain": "use this tool when you need to suggest a chess move with a tactic.  given an FEN (Forsyth–Edwards Notation). to use the tool you must provide the following parameter ['fen_string'].",
    "Graph Cypher QA Chain": "use this tool to provide information about chess piece position, ally pieces that defends other pieces, opponent pieces that attack ally pieces , moves that cause threats opponent's pieces.",
}

tools = [
    Tool.from_function(
        name = "Chess Solver Chain",
        description = describtions["Chess Solver Chain"],
        func = ns.chat,
        return_direct = False
    ),
    Tool.from_function(
        name = "Graph Cypher QA Chain",
        description = describtions["Graph Cypher QA Chain"],
        func = cypher_qa,
        return_direct = False
    ),
]

# Prompt to LLM
agent_prompt = PromptTemplate.from_template(CLASSIC_AGENT_PROMPT)

agent = create_react_agent(llm, tools, agent_prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors="If the generate Cypher Query syntax is incorrect or invalid, you MUST use FULL CONTEXT If output list is NOT EMPTY OTHERWISE TRY AGAIN",
    request_timeout=600,
)

def generate_response(prompt):
    """
    Create a handler that calls the Conversational agent
    and returns a response to be rendered in the UI.
    """
    response = agent_executor.invoke({"input": prompt})
    
    return response['output']


    
