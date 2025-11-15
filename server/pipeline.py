from json import tool
import json
import os
import operator
from typing import TypedDict, Annotated, Union

# LangChain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain_core.agents import AgentAction, AgentFinish
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI

# LangGraph
from langgraph.graph import END, StateGraph

# Agents
from neurosymbolicAI import Verifier
from neurosymbolicAI import Builder
from reinforced_agent import generate_response
from config import get_secret

try:  # pragma: no cover
    from .prompts import PIPELINE_MAIN_PROMPT, PIPELINE_VERIFIER_PROMPT
except ImportError:  # pragma: no cover
    from prompts import PIPELINE_MAIN_PROMPT, PIPELINE_VERIFIER_PROMPT

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RED = '\033[31m'

# Prompts
main_prompt = PromptTemplate.from_template(PIPELINE_MAIN_PROMPT)

verifier_prompt = PromptTemplate.from_template(PIPELINE_VERIFIER_PROMPT)

# Gemini LLM
# llm = ChatGoogleGenerativeAI(
#     model = "gemini-1.5-flash-8b",
#     google_api_key = get_secret("GEMINI_API_KEY"),
#     convert_system_message_to_human = True,
#     verbose = True,
# )

# OpenAI LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=get_secret("OPENAI_API_KEY"),
)

# Agent State class
class AgentState(TypedDict):
    '''
    :param: :input: input content from the user
    :param: :fen: forsyth-edwards notation of a chessboard
    :param: :commentary_agent_outcome: output of commentary agent
    :param: :verifier_agent_outcome: output of verifier agent
    :param: :pipeline_history: conversation history before agent execution
    :param: :final_answer: final state
    '''
    input: str
    fen: str 
    commentary_agent_outcome: Union[AgentAction, AgentFinish, None]
    verifier_agent_outcome: Union[AgentAction, AgentFinish, None]
    pipeline_history: Annotated[list[tuple[AgentAction, str]], operator.add]
    status: Union[AgentAction, AgentFinish, None]
    final_answer: str

# Tools
def verify_piece_position(state) -> list:
    '''
    Verifies the position of a pieces in a chess commentary.
    
    :param: :state: graph's state. for more info visit: https://langchain-ai.github.io/langgraph/
    
    :return: list of statements and their condition.
    '''
    
    print(bcolors.OKCYAN + "verify_piece_position function" + bcolors.ENDC)
    print(bcolors.RED + "state:" + bcolors.ENDC, state)
    
    # forsyth–edwards notation of a chessboard
    fen_string = state['fen']
    print(bcolors.BOLD + "FEN:" + bcolors.ENDC, fen_string)
    
    # the response of the chess solver
    response = state['commentary_agent_outcome']
    print(bcolors.BOLD + "commentary:" + bcolors.ENDC, response)
    
    # instantiate a verifier object
    verifier = Verifier()
    
    verifier.parse_fen(fen_string)
    
    verifier_output = verifier.verify_piece_position(response)

    print("--------------------------------------------------------------------------------------------------------------------------------------------------------\n")
    
    return {"pipeline_history": [(state['verifier_agent_outcome'], verifier_output)]}

def verify_piece_relation(state) -> list:
    '''
    Verifies the relation between pieces in a chess commentary.
    
    :param: :state: graph's state. for more info visit: https://langchain-ai.github.io/langgraph/
    
    :return: list of statements and their condition.
    '''
    
    print(bcolors.OKCYAN + "verify_piece_relation function" + bcolors.ENDC)
    print(bcolors.RED + "state:" + bcolors.ENDC, state)
    
    # Forsyth–Edwards Notation (FEN) of a chessboard
    fen_string = state['fen']
    print("FEN:", fen_string)
    
    # the response of the chess solver
    response = state['commentary_agent_outcome']
    print("Commentary:", response)
    
    # Instantiate a Verifier object
    verifier = Verifier()
    
    verifier.parse_fen(fen_string)
    
    verifier_output = verifier.verify_piece_relation(response)
    
    print("Verifier Output:", verifier_output)
    print("--------------------------------------------------------------------------------------------------------------------------------------------------------\n")

    return {"pipeline_history": [(state['verifier_agent_outcome'], verifier_output)]}

def verify_move_relation(state) -> list:
    '''
    Verifies the move feature of a piece in a chess commentary.
    
    :param: :state: graph's state. for more info visit: https://langchain-ai.github.io/langgraph/
    
    :return: list of statements and their condition.
    '''
    
    print(bcolors.OKCYAN + "verify_move_relation function" + bcolors.ENDC)
    print(bcolors.RED + "state:" + bcolors.ENDC, state)
    
    # Forsyth–Edwards Notation (FEN) of a chessboard
    fen_string = state['fen']
    print("FEN:", fen_string)
    
    # the response of the chess solver
    response = state['commentary_agent_outcome']
    print("Commentary:", response)
    
    # Instantiate a Verifier object
    verifier = Verifier()
    
    verifier.parse_fen(fen_string)
    
    verifier_output = verifier.verify_piece_move_feature(response)
    
    print("Verifier Output:", verifier_output)
    print("--------------------------------------------------------------------------------------------------------------------------------------------------------\n")

    return {"pipeline_history": [(state['verifier_agent_outcome'], verifier_output)]}

def generate_commentary(state) -> dict:
    '''
    Calls the chess solver agent and retrive a commentary.
    
    :param: :state: graph's state. for more info visit: https://langchain-ai.github.io/langgraph/
    
    :return: a commentary generated from the chess solver agent.
    '''    
    
    print(bcolors.OKCYAN + "generate_commentary" + bcolors.ENDC, state)
    print(bcolors.RED + "state:" +bcolors.ENDC, state)
    
    input = state['input']
    status = state['status']

    try:
        if status == "Reinforced Agent":        
            agent_outcome = generate_response(prompt=input)
            return {"commentary_agent_outcome": agent_outcome}
        elif status == "Reflex":
            feedback = state["verifier_agent_outcome"]
            agent_outcome = generate_response(prompt=input, feedback=feedback)
            return {"commentary_agent_outcome": agent_outcome}
    except:
        return {"status": "N/A"}
    
def build_relation(state) -> None:
    '''
    Calls the build agent and construct a new relation from existing one.
    
    :param: :state: graph's state. for more info visit: https://langchain-ai.github.io/langgraph/
    
    :return: #### None
    '''
    
    print(bcolors.OKCYAN + "build_relation function" + bcolors.ENDC)
    print(bcolors.RED + "state:" + bcolors.ENDC, state)
    
    input = state['input']
    status = state['status']
    
    if not(status == "N/A"):
        try:
            builder = Builder()
            response = builder.build_relations(input)
            return {"status": "End", "final_answer": "Hurray, the relationship was built successfully."}
        except:
            return {"status": "N/A", "final_answer": "Sorry, I could not build the new relation."}
    else:
        return {"status": "N/A", "final_answer": "Sorry, I could not build the new relation."}
 
# Tools
main_tools = [
    Tool(
        name = "Reinforced Agent",
        func = lambda state: generate_commentary(state),
        description = "useful when you need to generate a chess commentary."
    ),
    Tool(
        name = "Builder Agent",
        func = lambda state: build_relation(state),
        description = "useful when you need to verify the position of a chess piece i"
    ) 
]

verifier_tools = [
    Tool(
        name = "Verify Piece Position",
        func = lambda state: verify_piece_position(state),
        description = "useful when you need to verify the position of a chess piece in commentary."
    ),
    Tool(
        name = "Verify Piece Relation",
        func = lambda state: verify_piece_relation(state),
        description = "useful when you need to verify the relation between chess pieces in commentary."
    ),
    Tool(
        name = "Verify Piece Move Feature",
        func = lambda state: verify_move_relation(state),
        description = "useful when you need to verify the move feature of a chess piece in a commentary."
    ),
]

main_agent = create_react_agent(llm, main_tools, main_prompt)
verifier_agent = create_react_agent(llm, verifier_tools, verifier_prompt)

main_agent_runnable = AgentExecutor(
    agent=main_agent,
    tools=main_tools,
    verbose=True
)

verifier_agent_runnable = AgentExecutor(
    agent=verifier_agent,
    tools=verifier_tools,
    verbose=True
)

def run_main(state) -> dict:
    '''
    Calls the main agent and retrive the path to take based on the user input.
    
    :param: :state: graph's state. for more info visit: https://langchain-ai.github.io/langgraph/
    
    :return: the name of the sub-agent to take based on the user.
    '''
    
    print(bcolors.OKCYAN + "run_main function" + bcolors.ENDC)
    print(bcolors.RED + "state:" + bcolors.ENDC, state)
    
    user_input = state['input']
    print("user_input:", user_input)
    print("--------------------------------------------------------------------------------------------------------------------------------------------------------\n")

    main_agent_result = main_agent_runnable.invoke({"input": user_input})
    main_agent_outcome = main_agent_result.get('output', "")
    print("main_agent_outcome:", main_agent_outcome)

    normalized_outcome = " ".join(main_agent_outcome.replace("`", " ").strip().split()).lower()
    agent_map = [
        ("builder agent", "Builder Agent"),
        ("reinforced agent", "Reinforced Agent"),
    ]

    for keyword, agent_name in agent_map:
        if keyword in normalized_outcome:
            return {"status": agent_name, "pipeline_history": [("Main Agent", agent_name)]}

    print(bcolors.WARNING + "Unrecognized agent selection, defaulting to N/A" + bcolors.ENDC)
    return {"status": "N/A", "pipeline_history": [("Main Agent", main_agent_outcome or "N/A")]}

def run_verifier(state) -> dict:
    '''
    Calls the verifier agent and retrive a verification based on the chess solver commentary.
    
    :param: :state: graph's state. for more info visit: https://langchain-ai.github.io/langgraph/
    
    :return: a verification generated for the commentary of the chess solver agent.
    '''
    
    print(bcolors.OKCYAN + "run_verifier function" + bcolors.ENDC)
    print(bcolors.RED + "state:" + bcolors.ENDC, state)

    commentary = state.get('commentary_agent_outcome')
    if commentary is None:
        print("run_verifier: missing commentary_agent_outcome, skipping verifier.")
        return {"verifier_agent_outcome": "N/A", "status": "N/A"}
    chess_solver_commentary = commentary
    print("chess solver commentary:", chess_solver_commentary)
    
    status = state['status']
    
    if status == "N/A":
        return {"verifier_agent_outcome": "N/A", "status": "N/A"}
    
    try:
        verifier_agent_outcome = verifier_agent_runnable.invoke({"input": chess_solver_commentary})
        
        print("verifier_agent_outcome:", verifier_agent_outcome)
        
        return {"verifier_agent_outcome": verifier_agent_outcome['output'], "status": verifier_agent_outcome['output'], "pipeline_history": [("Tiny Agent", verifier_agent_outcome['output'])]}
    except:
        return {"verifier_agent_outcome": "N/A", "status": "N/A"}

def execute_tools(state):
    '''
    Execute a verifier module.
    
    :param: :state: graph's state. for more info visit: https://langchain-ai.github.io/langgraph/
    
    :return:
    '''
    
    print(bcolors.OKCYAN + "execute_tools function" + bcolors.ENDC)
    print(bcolors.RED + "state:" + bcolors.ENDC, state)
    print("--------------------------------------------------------------------------------------------------------------------------------------------------------\n")
    
    status = state['status']

    if status == "Verify Piece Position":
        try:
            verification = verify_piece_position(state)
        except:
            return {"status": "N/A", "pipeline_history: ": [("Tiny Agent: N/A", "N/A")]}
    elif status == "Verify Piece Relation":
        try:
            verification = verify_piece_relation(state)
        except:
            return {"status": "N/A", "pipeline_history: ": [("Tiny Agent: N/A", "N/A")]}
    elif status == "Verify Piece Move Feature":
        try:
            verification = verify_move_relation(state)  
        except:
            return {"status": "N/A", "pipeline_history: ": [("Tiny Agent: N/A", "N/A")]}
    else:
        return {"status": "N/A", "pipeline_history: ": [("Tiny Agent: N/A", "N/A")]}

    print(bcolors.BOLD + "verification:" + bcolors.ENDC, verification)
    print("--------------------------------------------------------------------------------------------------------------------------------------------------------\n")
    
    return {"pipeline_history": [("Tiny Agent", verification)]}
    
def reflex_checkpoint(state):
    '''
    Acts as a checkpoint to determine whether to verbally reinforce the commentary agent.
    
    :param: :state: graph's state. for more info visit: https://langchain-ai.github.io/langgraph/
    
    :return:
    '''
    
    flag = False
    
    print(bcolors.OKCYAN + "reflex_checkpoint function" + bcolors.ENDC)
    print(bcolors.RED + "state:" + bcolors.ENDC, state)
    
    pipeline_history = state.get("pipeline_history", [])
    verification = pipeline_history[-1][1] if pipeline_history else "N/A"
    status = state.get('status')

    print(bcolors.BOLD + "reflex verification:" + bcolors.ENDC, verification)
    print("type(verification):", type(verification))
    
    if verification == "N/A" or status == "N/A":
        print("--------------------------------------------------------------------------------------------------------------------------------------------------------\n")
        return {
            "status": "End",
            "final_answer": state.get("commentary_agent_outcome", "Sorry, I do not know the answer!"),
        }
    if isinstance(verification, str):
        print("reflex_checkpoint: unexpected verification type, returning commentary directly.")
        return {
            "status": "End",
            "final_answer": state.get("commentary_agent_outcome", "Sorry, I do not know the answer!"),
        }
    
    print("verification['pipeline_history'][-1][1]", verification['pipeline_history'][-1][1])
    print("type(verification['pipeline_history'][-1][1])", type(verification['pipeline_history'][-1][1]))
    
    summary = ""
    commentary = ""
    json_verification = verification['pipeline_history'][-1][1]
    list_of_verified_statements = []
        
    for elem in json_verification:
        print("elem:", elem)
        statement = str(elem['statement']).replace(".", "")

        if elem['condition'] == False:
            summary = summary + f"The statement {statement} is {elem['condition']}. " 
        else:
            summary = summary + f"The statement {statement} is {elem['condition']}. "
            list_of_verified_statements.append(elem)
            
    if not(len(list_of_verified_statements) == 0):
        flag = True
            
    for index, elem in enumerate(list_of_verified_statements):
        print("elem:", elem)
        statement = str(elem['statement']).replace(".", "")
        
        if index == len(list_of_verified_statements) - 1:
            commentary = commentary + statement + "."
        elif index == len(list_of_verified_statements) - 2:
            commentary = commentary + statement + " and "
        else:
            commentary = commentary + statement + ", "
            
    print(bcolors.BOLD + "summary:" + bcolors.ENDC, summary)
    print("--------------------------------------------------------------------------------------------------------------------------------------------------------\n")

    if flag: # The commentary is correct
        return {"verifier_agent_outcome": verification, "status": "End", "final_answer": commentary}
    else: # The commentary is incorrect
        return {"verifier_agent_outcome": summary, "status": "Reflex"}
    
def selection_checkpoint(state):
    '''
    Acts as a checkpoint to determine whether to execute the Builder agent or the Reinforced agent.
    
    :param: :state: graph's state. for more info visit: https://langchain-ai.github.io/langgraph/
    
    :return: 
    '''
    
    print(bcolors.OKCYAN + "selection_checkpoint function" + bcolors.ENDC)
    print(bcolors.RED + "state:" + bcolors.ENDC, state)
    print("--------------------------------------------------------------------------------------------------------------------------------------------------------\n")
    
    try:
        (_, status) = state['pipeline_history'][-1]
     
        if status == "Builder Agent":
            return "build"
        elif status == "Reinforced Agent":
            return "comment"
        else:
            return "end"
    except:
        return "end"
      

def should_continue(state) -> str:
    '''
    Checks the content of the previous response and uses it to determine whether to terminate or verify and reflex Chess Solver agent commentary.
    
    :param: :state: graph's state. for more info visit: https://langchain-ai.github.io/langgraph/
    
    :return:
    '''
    
    print(bcolors.OKCYAN + "should_continue function" + bcolors.ENDC)
    print(bcolors.RED + "state:" + bcolors.ENDC, state)
    print("--------------------------------------------------------------------------------------------------------------------------------------------------------\n")
    
    status = state['status']
    
    if status == "End":
        return "end"
    else:
        if status == "Reflex":
            return "reflex"
        else:
            return "end"
        
workflow = StateGraph(AgentState)

# Nodes
workflow.add_node("main_agent", run_main)
workflow.add_node("build_agent", build_relation)
workflow.add_node("commentary_agent", generate_commentary)
workflow.add_node("verifier_agent", run_verifier)
workflow.add_node("tiny_agent", execute_tools)
workflow.add_node("reflex_checkpoint", reflex_checkpoint)

# Always call main agent first.
workflow.set_entry_point("main_agent")

# Edges
workflow.add_edge("build_agent", END)
workflow.add_edge("commentary_agent", "verifier_agent")
workflow.add_edge("verifier_agent", "tiny_agent")
workflow.add_edge("tiny_agent", "reflex_checkpoint")

# Conditional Edges
workflow.add_conditional_edges(
    "main_agent",
    selection_checkpoint,
    {
        "build": "build_agent",
        "comment": "commentary_agent",
        "end": END
    }
)

workflow.add_conditional_edges(
    "reflex_checkpoint",
    should_continue,
    {
        "reflex": "commentary_agent",
        "end": END
    }
)

# Graph
app = workflow.compile()

def chat(input, fen_string) -> str:
    '''
    Starts the pipeline for either generating chess commentary or building new relations.
    
    :param: :input: user query
    :param: :fen_string: current forsyth-edwards notation of a chessboard 
    
    :return: text generated from the chatbot
    '''
    
    inputs = {"input": input, "status": "Begin", "fen": fen_string, "pipeline_history": []}
    
    results = []
    
    try:   
        for s in app.stream(inputs):
            result = list(s.values())[0]
            results.append(result)
            print(bcolors.OKGREEN + "Result:" + bcolors.ENDC, result)
            print("--------------------------------------------------------------------------------------------------------------------------------------------------------\n") 
        
        for result in reversed(results):
            if 'final_answer' in result:
                return result['final_answer']

        return "Sorry, I do not know the answer!"
    except Exception as exc:
        print(f"Error while running chat pipeline: {exc}")
        return "Sorry, I do not know the answer!"
