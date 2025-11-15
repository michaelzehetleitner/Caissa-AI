import os
import sys
import types


def _install_module(name: str) -> types.ModuleType:
    """
    Creates a lightweight stub module for missing third-party packages so the
    server code can be imported inside tests without installing heavy deps.
    """
    module = sys.modules.get(name)
    if module is None:
        module = types.ModuleType(name)
        sys.modules[name] = module
        parent_name, _, child_name = name.rpartition(".")
        if parent_name:
            parent = _install_module(parent_name)
            setattr(parent, child_name, module)
        else:
            module.__path__ = []  # Treat as a package for nested imports.
    return module


# Provide default secrets so get_secret lookups succeed during imports.
for key, value in {
    "OPENAI_API_KEY": "test-openai-key",
    "NEO4J_URI": "bolt://stub",
    "NEO4J_USERNAME": "stub-user",
    "NEO4J_PASSWORD": "stub-pass",
    "KB_PATH": "/tmp/caissa_kb.pl",
    "GEMINI_API_KEY": "stub-gemini-key",
}.items():
    os.environ.setdefault(key, value)

os.environ.setdefault("CAISSA_SKIP_LLM", "1")

# streamlit
streamlit = _install_module("streamlit")
if not hasattr(streamlit, "secrets"):
    streamlit.secrets = {}

# python-dotenv
dotenv = _install_module("dotenv")


def load_dotenv(*args, **kwargs):
    return {}


dotenv.load_dotenv = load_dotenv

# flask + flask_cors
flask = _install_module("flask")


class _Flask:
    def __init__(self, *args, **kwargs):
        self.routes = {}

    def route(self, *args, **kwargs):
        def decorator(func):
            self.routes[func.__name__] = (args, kwargs)
            return func

        return decorator


def _jsonify(*args, **kwargs):
    return {"args": args, "kwargs": kwargs}


flask.Flask = _Flask
flask.jsonify = _jsonify
flask.request = types.SimpleNamespace()

flask_cors = _install_module("flask_cors")
flask_cors.CORS = lambda *args, **kwargs: None

# torch
torch = _install_module("torch")
torch.float16 = "float16"
torch.float32 = "float32"


class _Cuda:
    @staticmethod
    def is_available():
        return False


class _MPS:
    @staticmethod
    def is_available():
        return False


class _Backends:
    mps = _MPS()


torch.cuda = _Cuda()
torch.backends = _Backends()

# transformers
transformers = _install_module("transformers")
transformers.__version__ = "5.0.0"


class _AutoTokenizer:
    @classmethod
    def from_pretrained(cls, model_id):
        return cls()

    def __call__(self, *args, **kwargs):
        return types.SimpleNamespace(
            input_ids=[[0]],
            to=lambda device: types.SimpleNamespace(input_ids=[[0]]),
        )

    @property
    def eos_token_id(self):
        return 0

    def decode(self, token):
        return "uci"


class _AutoModel:
    @classmethod
    def from_pretrained(cls, model_id, **kwargs):
        return cls()

    def to(self, device):
        return self

    def generate(self, **kwargs):
        return types.SimpleNamespace(sequences=[[0]])


def _pipeline(*args, **kwargs):
    def _runner(prompt):
        return [{"generated_text": ""}]

    return _runner


transformers.AutoTokenizer = _AutoTokenizer
transformers.AutoModelForCausalLM = _AutoModel
transformers.pipeline = _pipeline

# kor
kor = _install_module("kor")


class _KorObject:
    def __init__(self, *args, **kwargs):
        pass


class _KorText:
    def __init__(self, *args, **kwargs):
        pass


def _create_extraction_chain(*args, **kwargs):
    class _Chain:
        def invoke(self, inputs):
            return {}

    return _Chain()


kor.Object = _KorObject
kor.Text = _KorText
kor.create_extraction_chain = _create_extraction_chain

# pydantic
pydantic = _install_module("pydantic")


class BaseModel:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


def Field(default=None, **kwargs):
    return default


pydantic.BaseModel = BaseModel
pydantic.Field = Field

# pyswip
pyswip = _install_module("pyswip")


class _Query(list):
    def close(self):
        pass


class Prolog:
    def consult(self, filepath):
        self.filepath = filepath

    def query(self, *args, **kwargs):
        return _Query()


pyswip.Prolog = Prolog

# neo4j
neo4j = _install_module("neo4j")


class _Session:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute_write(self, *args, **kwargs):
        return None

    def execute_read(self, *args, **kwargs):
        return []


class _Driver:
    def session(self):
        return _Session()

    def close(self):
        pass


class GraphDatabase:
    @staticmethod
    def driver(uri, auth=None):
        return _Driver()


neo4j.GraphDatabase = GraphDatabase

# chess
chess = _install_module("chess")


class Board:
    pass


chess.Board = Board

# langchain.prompts
langchain_prompts = _install_module("langchain.prompts")


class PromptTemplate:
    def __init__(self, template):
        self.template = template

    @classmethod
    def from_template(cls, template):
        return cls(template)


langchain_prompts.PromptTemplate = PromptTemplate

# langchain.agents
langchain_agents = _install_module("langchain.agents")


class Tool:
    def __init__(self, name, func, description=""):
        self.name = name
        self.func = func
        self.description = description

    @classmethod
    def from_function(cls, name, func, description="", return_direct=False):
        return cls(name=name, func=func, description=description)


class AgentExecutor:
    def __init__(self, agent, tools, **kwargs):
        self.agent = agent
        self.tools = tools

    def invoke(self, inputs):
        if callable(self.agent):
            return self.agent(inputs)
        return {"output": ""}


def create_react_agent(llm, tools, prompt):
    def _agent(inputs):
        return {"output": inputs.get("input", "")}

    return _agent


langchain_agents.Tool = Tool
langchain_agents.AgentExecutor = AgentExecutor
langchain_agents.create_react_agent = create_react_agent

# langchain.tools
langchain_tools = _install_module("langchain.tools")
langchain_tools.Tool = Tool

# langchain.chains.conversation.memory
conversation_memory = _install_module("langchain.chains.conversation.memory")


class ConversationBufferWindowMemory:
    def __init__(self, *args, **kwargs):
        pass


conversation_memory.ConversationBufferWindowMemory = ConversationBufferWindowMemory

# langchain_core.agents
langchain_core_agents = _install_module("langchain_core.agents")


class AgentAction:
    def __init__(self, tool: str = "", tool_input=None, log: str = ""):
        self.tool = tool
        self.tool_input = tool_input
        self.log = log


class AgentFinish:
    def __init__(self, return_values=None, log: str = ""):
        self.return_values = return_values or {}
        self.log = log


langchain_core_agents.AgentAction = AgentAction
langchain_core_agents.AgentFinish = AgentFinish

# langchain_core.output_parsers
langchain_output_parsers = _install_module("langchain_core.output_parsers")


class JsonOutputParser:
    def __init__(self, *args, **kwargs):
        pass

    def parse(self, text):
        raise NotImplementedError


langchain_output_parsers.JsonOutputParser = JsonOutputParser

# langchain_community.chat_models
langchain_chat = _install_module("langchain_community.chat_models")


class ChatOpenAI:
    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs

    def invoke(self, inputs):
        return {"output": inputs.get("input", "")}


langchain_chat.ChatOpenAI = ChatOpenAI

# langchain_google_genai
langchain_genai = _install_module("langchain_google_genai")


class ChatGoogleGenerativeAI:
    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs


langchain_genai.ChatGoogleGenerativeAI = ChatGoogleGenerativeAI

# langgraph.graph
langgraph_graph = _install_module("langgraph.graph")


class _CompiledGraph:
    def stream(self, inputs):
        return iter([])


class StateGraph:
    def __init__(self, state_type):
        self.state_type = state_type
        self.nodes = {}

    def add_node(self, name, func):
        self.nodes[name] = func

    def set_entry_point(self, name):
        self.entry_point = name

    def add_edge(self, *args, **kwargs):
        pass

    def add_conditional_edges(self, *args, **kwargs):
        pass

    def compile(self):
        return _CompiledGraph()


langgraph_graph.StateGraph = StateGraph
langgraph_graph.END = object()
