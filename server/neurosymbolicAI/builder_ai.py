import os
import json
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from .symbolicAI import Symbolic
from server.config import get_secret
try:  # pragma: no cover
    from ..prompts import BUILDER_AGENT_PROMPT
except ImportError:  # pragma: no cover
    from prompts import BUILDER_AGENT_PROMPT

os.environ["URI"] = get_secret("NEO4J_URI")
os.environ["NEO_USER"] = get_secret("NEO4J_USERNAME")
os.environ["PASSWORD"] = get_secret("NEO4J_PASSWORD")
os.environ["KB_PATH"] = get_secret("KB_PATH")


class Relation(BaseModel):
    name: str = Field(description="the name of the new relation")
    type: str = Field(description="type of the new relation")
    relationships: dict = Field(description="relations in the new relaton description")


class Builder:
    def __init__(self):
        # Gemini LLM
        # self.llm = ChatGoogleGenerativeAI(
        #     model="gemini-1.5-flash-8b",
        #     google_api_key=get_secret("GEMINI_API_KEY"),
        #     temperature=0,
        # )

        # OpenAI LLM
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=get_secret("OPENAI_API_KEY"),
        )

        self.sym = Symbolic()
        self.sym.consult(os.getenv("KB_PATH"))

        self.parser = JsonOutputParser(pydantic_object=Relation)
        self.agent_prompt = PromptTemplate.from_template(BUILDER_AGENT_PROMPT)
        self.agent = create_react_agent(self.llm, [], self.agent_prompt)
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=[],
            verbose=True,
            handle_parsing_errors="MUST return first Final Answer",
        )

    def parse_fen(self, fen_string: str) -> None:
        self.sym.parse_fen(fen_string)

    def extract_relations(self, description: str) -> dict:
        return self.agent_executor.invoke({"input": description})

    def _load_structured_response(self, agent_output: str) -> dict:
        """
        Normalize single quotes from the prompt template and turn the output into JSON.
        """
        structured_response = agent_output.replace("'", '"')
        return json.loads(structured_response)

    def build_relations(self, input_text: str) -> None:
        """
        Extract a new relation description from the LLM and materialize it inside the symbolic graph.
        """

        agent_response = self.extract_relations(input_text)
        structured_text = agent_response.get("output", "")
        try:
            parsed = self.parser.parse(structured_text)
            if hasattr(parsed, "dict"):
                json_response = parsed.dict()
            else:
                json_response = parsed
        except Exception:
            json_response = self._load_structured_response(structured_text)
        print("json_response:", json_response)

        relationships = json_response.get("relationships", "N/A")
        if relationships == "N/A":
            raise Exception("Could not build the relationship")

        feature_name = json_response["name"]
        feature_relationships = json_response["relationships"]
        print("feature_relationships:", feature_relationships)
        print("type(feature_relationships):", type(feature_relationships))

        list_of_moves = []
        initial_flag = True

        for index in range(len(feature_relationships)):
            relation_name = feature_relationships[f"relation_{index + 1}"]
            print("relation_name:", relation_name)

            records = self.sym.graph.find_moves(relation_name)
            print("records:", records)

            relation_list = []
            for record in records:
                piece = record["piece"]
                color = record["color"]
                from_position = record["from"]
                to_position = record["to"]

                move_tuple = (piece, color, from_position, to_position)
                relation_list.append(move_tuple)

                print("piece:", record["piece"])
                print("color:", record["color"])
                print("from:", record["from"])
                print("to:", record["to"])

            if initial_flag:
                list_of_moves = relation_list
                initial_flag = False
            else:
                common_list = [piece for piece in relation_list if piece in list_of_moves]
                list_of_moves = common_list

        print("list_of_moves:", list_of_moves)
        for elem in list_of_moves:
            piece, color, from_position, to_position = elem
            self.sym.graph.build_feature(piece, color, from_position, to_position, feature_name)
