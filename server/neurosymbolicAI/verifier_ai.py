import os
import json
from langchain_community.chat_models import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.agents import AgentExecutor, create_react_agent
from kor import create_extraction_chain, Object, Text
from .symbolicAI import Symbolic
from config import get_secret
try:  # pragma: no cover
    from ..prompts import (
        VERIFIER_JSON_PROMPT,
        VERIFIER_FIX_PROMPT,
        POSITION_SCHEMA_DESCRIPTION,
        RELATION_SCHEMA_DESCRIPTION,
        MOVE_FEATURE_SCHEMA_DESCRIPTION,
    )
except ImportError:  # pragma: no cover
    from prompts import (
        VERIFIER_JSON_PROMPT,
        VERIFIER_FIX_PROMPT,
        POSITION_SCHEMA_DESCRIPTION,
        RELATION_SCHEMA_DESCRIPTION,
        MOVE_FEATURE_SCHEMA_DESCRIPTION,
    )

os.environ["URI"] = get_secret("NEO4J_URI")
os.environ["NEO_USER"] = get_secret("NEO4J_USERNAME")
os.environ["PASSWORD"] = get_secret("NEO4J_PASSWORD")
os.environ["KB_PATH"] = get_secret("KB_PATH")

class Verifier():  
    
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
        self.sym.consult(os.getenv('KB_PATH'))
        
        self.agent_prompt = PromptTemplate.from_template(VERIFIER_JSON_PROMPT)
        
        self.agent = create_react_agent(self.llm, [], self.agent_prompt)
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=[],
            verbose=True
        )
        
        self.fix_agent_prompt =  PromptTemplate.from_template(VERIFIER_FIX_PROMPT)
        
        self.fix_agent = create_react_agent(self.llm, [], self.fix_agent_prompt)
        self.fix_agent_executor = AgentExecutor(
            agent=self.fix_agent,
            tools=[],
            verbose=True,
        )
        
    def parse_fen(self, fen_string: str):
        self.sym.parse_fen(fen_string)

    def verify_piece_position(self, response) -> list:
        '''
        Checks whether the position of the piece specified in the commentary is valid.
        
        :param: :response: response propagated from the chess solver
        :return: a list of dict
        '''
        
        # Create a schema
        schema = Object(
                    id="position schema",
                    description=(
                        "A generated chess commentary."
                    ),
                    attributes=[
                        Text(
                            id="piece",
                            description=POSITION_SCHEMA_DESCRIPTION,
                            examples=[
                                ("The position of black queen is a2.", "{'piece': 'queen', 'color': 'black', 'position': 'a2'}"),
                                ("The position of king is a2.", "{'piece': 'king', 'color': 'N/A', 'position': 'a2'}"),
                                ("The position of black bishop.", "{'piece': 'bishop', 'color': 'black', 'position': 'N/A'}"),
                            ],
                            many=True
                        ),
                    ],
                    many=False,
                )
        
        chain = create_extraction_chain(self.llm, schema, encoder_or_encoder_class='json')
        
        list_of_statements = []
            
        structured_response = self.agent_executor.invoke({'input': response})
        print("before structured_response:", structured_response['output'])
        structured_response = json.loads(str(structured_response['output']).replace("\'", "\""))
        print("after structured_response:", structured_response)
        
        for index, statement_key in enumerate(structured_response['statements']):
            try:
                print("statement_key:", statement_key) 
                statement = structured_response['statements'][statement_key]
                print(f"statement_{index + 1}:", statement)
            
                structured_filtered_response = chain.invoke(statement)['text']['raw']
                structured_filtered_response = structured_filtered_response.replace("<json>", "")
                structured_filtered_response = structured_filtered_response.replace("</json>", "")
                json_response = json.loads(structured_filtered_response)

                piece_info = json.loads(json_response["position schema"]["piece"][0].replace("\'", "\""))
                print("piece_info:", piece_info)
                
                piece = piece_info['piece']
                color = piece_info['color']
                position = piece_info['position']
                
                print("piece name:", piece)
                print("color:", color)
                print("position:", position)
                
                # Use Symbolic class to verfiy the statement
                response = self.sym.verify_position(piece, color, position)
                print("response:", response)
                
                if piece == "N/A"or len(response) == 0:
                    list_of_statements.append({"statement": statement, "condition": False})
                elif color == "N/A" or position == "N/A":
                    if color == "N/A":
                        color = response[0]['Color']

                    if position == "N/A":
                        position = response[0]['Position']
                        
                    fix_agent_input = {"statement": statement, "piece": piece, "color": color, "position": position}
                    print("fix_agent_input:", f"""{fix_agent_input}""")
                    fixed_statement = self.fix_agent_executor.invoke({"input": f"""{fix_agent_input}"""})['output']
                    print("fixed_statement:", fixed_statement)      
                    list_of_statements.append({"statement": fixed_statement, "condition": True})              
                else:
                    if not(len(response) == 0):
                        list_of_statements.append({"statement": statement, "condition": True}) 
            except:
                pass

        return list_of_statements
        
    def verify_piece_relation(self, response):
        '''
        Checks whether the move of a piece is legal.
        
        :param: :response: response propagated from the chess solver

        :return: a list of dict

        '''
        
        # Create a schema
        schema = Object(
                    id="relation schema",
                    description=(
                        "what is the relation between chess pieces?"
                    ),
                    attributes=[
                        Text(
                            id="relations",
                            description=RELATION_SCHEMA_DESCRIPTION,
                            examples=[
                                ("The black queen at c6 defend the black pawn at f3", "{'piece': 'queen', 'color': 'black', 'position': 'c6', 'ally_piece': 'pawn', 'ally_color': 'black', 'ally_position': 'f3', 'relation': 'defend'}"),
                                ("Black pawn at h5 is threated by the white rook at h8", "{'piece': 'rook', 'color': 'white', 'position': 'h8', 'opponent_piece': 'pawn', 'opponent_color': 'black', 'opponent_position': 'h5', 'relation': 'threat'}"),
                            ],
                            many=True
                        ),
                    ],
                    many=False,
                )
        
        chain = create_extraction_chain(self.llm, schema, encoder_or_encoder_class='json') 
        
        list_of_statements = []
            
        structured_response = self.agent_executor.invoke({'input': response})
        print("before structured_response:", structured_response['output'])
        structured_response = json.loads(structured_response['output'].replace("\'", "\""))
        print("after structured_response:", structured_response)

        for index, statement_key in enumerate(structured_response['statements']):
            try:
                statement = structured_response['statements'][statement_key]
                print(f"statement_{index + 1}:", statement)
            
                json_response = chain.invoke(statement)['text']['data']['relation schema']['relations'][0]
                print("JSON Response:", json_response)
            
                json_response = json_response.replace("<json>", "")
                json_response = json_response.replace("</json>", "").replace("\'","\"")
                print("before json_response:", json_response)
        
                relation_info = json.loads(json_response)
                print("relation_info:", relation_info)
                    
                piece1 = relation_info['piece']
                color1 = relation_info['color']
                position1 = relation_info['position']
                
                relation = relation_info['relation']
                    
                if relation == "defend":                    
                    piece2 = relation_info['ally_piece']
                    color2 = relation_info['ally_color']
                    position2 = relation_info['ally_position']
                elif relation == "threat":
                    piece2 = relation_info['opponent_piece']
                    color2 = relation_info['opponent_color']
                    position2 = relation_info['opponent_position']
                    
                print("piece1:", piece1)
                print("color1:", color1)
                print("position1:", position1)
                    
                print("piece2:", piece2)
                print("color2:", color2)
                print("position2:", position2)
                    
                print("relation:", relation)
                    
                # Use Symbolic class to verfiy the statement
                response = self.sym.verify_relation(piece1, color1, position1, piece2, color2, position2, relation)
                print(response)
                
                if piece1 == "N/A" or relation == "N/A" or len(response) == 0:
                    list_of_statements.append({"statement": statement, "condition": False})
                elif color1 == "N/A" or position1 == "N/A" or color2 == "N/A" or position2 == "N/A" or piece2 == "N/A":
                    if color1 == "N/A":
                        color1 = response[0]['Color1']

                    if position1 == "N/A":
                        position1 = response[0]['Position1']
                        
                    if piece2 == "N/A":
                        piece2 = response[0]['Piece2']
                    
                    if color2 == "N/A":
                        color2 = response[0]['Color2']
                        
                    if position2 == "N/A":
                        position2 = response[0]['Position2']
                        
                    fix_agent_input = {"statement": statement, "piece1": piece1, "color1": color1, "position1": position1, "piece2": piece2, "color2": color2, "position2": position2, "relation": relation}
                    print("fix_agent_input:", f"""{fix_agent_input}""")
                    fixed_statement = self.fix_agent_executor.invoke({"input": f"""{fix_agent_input}"""})['output']
                    print("fixed_statement:", fixed_statement)      
                    list_of_statements.append({"statement": fixed_statement, "condition": True})              
                else:
                    if not(len(response) == 0):
                        list_of_statements.append({"statement": statement, "condition": True})
            except:
                pass
                        
        return list_of_statements

    def verify_piece_move_feature(self, response):
        '''
        Checks whether piece have certain move relation.
        
        :param: :response: response propagated from the chess solver.
        :return: a list of dict
        '''
        
        # Create a schema
        schema = Object(
            id="move feature schema",
            description=(
                "what is the move feature between chess pieces?"
            ),
            attributes=[
            Text(
                    id="move feature",
                    description=MOVE_FEATURE_SCHEMA_DESCRIPTION,
                    examples=[
                        ("white rook at d1 is attacked by black rook at d8 for the move e1", "{'piece': 'rook', 'color': 'white', 'position': 'd1', 'opponent_piece': 'rook', 'opponent_color': 'black', 'opponent_position': 'd8', 'move': 'e1', 'feature': 'move_is_attacked'}"),
                        ("The black rook move to d8 is threatened by a white knight at f7.", "{'piece': 'rook', 'color': 'black', 'position': 'N/A', 'opponent_piece': 'knight', 'opponent_color': 'white', 'opponent_position': 'f7', 'move': 'd8', 'feature': 'move_is_attacked'}")
                    ],
                    many=True
                ),
            ],
            many=False,
        )
        
        chain = create_extraction_chain(self.llm, schema, encoder_or_encoder_class='json')
        
        list_of_statements = []
            
        structured_response = self.agent_executor.invoke({'input': response})
        print("before structured_response:", structured_response['output'])
        structured_response = json.loads(structured_response['output'].replace("\'", "\""))
        print("after structured_response:", structured_response)

    
        for index, statement_key in enumerate(structured_response['statements']): 
            try:
                statement = structured_response['statements'][statement_key]
                print(f"statement_{index + 1}:", statement)
            
                json_response = chain.invoke(statement)['text']['data']['move feature schema']['move feature'][0]
                print("JSON Response:", json_response)
            
                json_response = json_response.replace("<json>", "")
                json_response = json_response.replace("</json>", "").replace("\'","\"")
                print("before json_response:", json_response)
        
                move_info = json.loads(json_response)
                print("move_info:", move_info)
                 
                piece1 = move_info['piece']
                color1 = move_info['color']
                position1 = move_info['position']
                
                feature = move_info['feature']
                
                move = move_info['move']
                print("move:", move)
                 
                if feature == "move_defend" or feature == "move_is_protected":                    
                    piece2 = move_info['ally_piece']
                    color2 = move_info['ally_color']
                    position2 = move_info['ally_position']
                elif feature == "move_threat" or feature == "move_is_attacked":
                    piece2 = move_info['opponent_piece']
                    color2 = move_info['opponent_color']
                    position2 = move_info['opponent_position']
                
                print("piece1:", piece1)
                print("color1:", color1)
                print("position1:", position1)
                
                print("piece2:", piece2)
                print("color2:", color2)
                print("position2:", position2)
                
                print("feature:", feature)
                
                if color1 == "N/A" and not(color2 == "N/A"):
                    if feature == "move_defend" or feature == "move_is_protected":
                        color1 = "white" if color2 == "white" else "black"
                    elif feature == "move_threat" or feature == "move_is_attacked":
                        color1 = "white" if color2 == "black" else "black"
                
                if color2 == "N/A" and not(color1 == "N/A"):
                    if feature == "move_defend" or feature == "move_is_protected":
                        color2 = "white" if color1 == "white" else "black"
                    elif feature == "move_threat" or feature == "move_is_attacked":
                        color1 = "black" if color1 == "white" else "white"
                
                # Use Symbolic class to verfiy the statement
                if piece1 == "N/A" or feature == "N/A" or color1 == "N/A" or color2 == "N/A":
                    list_of_statements.append({"statement": statement, "condition": False})
                elif piece1 == "N/A" or position1 == "N/A" or piece2 == "N/A" or position2 == "N/A":
                    responses = self.sym.graph.verify_move_feature_missing_param(feature)
                    # print("responses:", responses)
                    
                    list_of_true_elem = []
                    list_of_false_elem = []
                   
                    if not(piece2 == "N/A"):
                        if not(position2 == "N/A"):
                            if not(position1 == "N/A"):
                                for response in responses:
                                    try:
                                        if piece1 == response['piece1'] and piece2 == response['piece2'] and color1 == response['color1'] and color2 == response['color2'] and position1 == response['position1'] and position2 == response["position2"] and ((not(move == "N/A") and move == response["to"]) or move == "N/A"):
                                            list_of_true_elem.append({"statement": statement, "piece1": piece1, "color1": color1, "position1": position1, "from_position": position1, "to_position": response["to"] if move == "N/A" else move, "piece2": piece2, "color2": color2, "position2": position2})
                                        else:
                                            list_of_false_elem.append({"statement": statement})
                                    except:
                                        pass
                            else:
                                for response in responses:
                                    try:
                                        if piece1 == response['piece1'] and piece2 == response['piece2'] and color1 == response['color1'] and color2 == response['color2'] and position2 == response['position2'] and ((not(move == "N/A") and move == response["to"]) or move == "N/A"):
                                            list_of_true_elem.append({"statement": statement, "piece1": piece1, "color1": color1, "position1": response['position1'], "from_position": response['position1'], "to_position": response["to"] if move == "N/A" else move, "piece2": piece2, "color2": color2, "position2": position2})
                                        else:
                                            list_of_false_elem.append({"statement": statement})
                                    except:
                                        pass
                        else:
                            if (position1 == "N/A"):
                                for response in responses:
                                    try:
                                        if piece1 == response['piece1'] and piece2 == response['piece2'] and color1 == response['color1'] and color2 == response['color2'] and position1 == response['position1'] and ((not(move == "N/A") and move == response["to"]) or move == "N/A"):
                                            list_of_true_elem.append({"statement": statement, "piece1": piece1, "color1": color1, "position1": position1, "from_position": position1, "to_position": response["to"] if move == "N/A" else move, "piece2": piece2, "color2": color2, "position2": response['position2']})
                                        else:
                                            list_of_false_elem.append({"statement": statement})
                                    except:
                                        pass
                            else:
                                for response in responses:
                                    try:
                                        if piece1 == response['piece1'] and piece2 == response['piece2'] and color1 == response['color1'] and color2 == response['color2'] and ((not(move == "N/A") and move == response["to"]) or move == "N/A"):
                                            list_of_true_elem.append({"statement": statement, "piece1": piece1, "color1": color1, "position1": response['position1'], "from_position": response['position1'], "to_position": response["to"] if move == "N/A" else move, "piece2": piece2, "color2": color2, "position2": response['position2']})
                                        else:
                                            list_of_false_elem.append({"statement": statement})
                                    except:
                                        pass
                    else:
                        if not(position2 == "N/A"):
                            if not(position1 == "N/A"):
                                for response in responses:
                                    try:
                                        if piece1 == response['piece1'] and color1 == response['color1'] and color2 == response['color2'] and position1 == response['position1'] and position2 == response["position2"] and ((not(move == "N/A") and move == response["to"]) or move == "N/A"):
                                            list_of_true_elem.append({"statement": statement, "piece1": piece1, "color1": color1, "position1": position1, "from_position": position1, "to_position": response["to"] if move == "N/A" else move, "piece2": response['piece2'], "color2": color2, "position2": position2})
                                        else:
                                            list_of_false_elem.append({"statement": statement})
                                    except:
                                        pass
                            else:
                                for response in responses:
                                    try:
                                        if piece1 == response['piece1'] and color1 == response['color1'] and color2 == response['color2'] and position2 == response['position2'] and ((not(move == "N/A") and move == response["to"]) or move == "N/A"):
                                            list_of_true_elem.append({"statement": statement, "piece1": piece1, "color1": color1, "position1": response['position1'], "from_position": response['position1'], "to_position": response["to"] if move == "N/A" else move, "piece2": response['piece2'], "color2": color2, "position2": position2})
                                        else:
                                            list_of_false_elem.append({"statement": statement})
                                    except:
                                        pass
                        else:
                            if (position1 == "N/A"):
                                for response in responses:
                                    try:
                                        if piece1 == response['piece1'] and color1 == response['color1'] and color2 == response['color2'] and position1 == response['position1'] and ((not(move == "N/A") and move == response["to"]) or move == "N/A"):
                                            list_of_true_elem.append({"statement": statement, "piece1": piece1, "color1": color1, "position1": position1, "from_position": position1, "to_position": response["to"] if move == "N/A" else move, "piece2": response['piece2'], "color2": color2, "position2": response['position2']})
                                        else:
                                            list_of_false_elem.append({"statement": statement})
                                    except:
                                        pass
                            else:
                                for response in responses:
                                    try:
                                        if piece1 == response['piece1'] and color1 == response['color1'] and color2 == response['color2'] and ((not(move == "N/A") and move == response["to"]) or move == "N/A"):
                                            list_of_true_elem.append({"statement": statement, "piece1": piece1, "color1": color1, "position1": response['position1'], "from_position": response['position1'], "to_position": response["to"] if move == "N/A" else move, "piece2": response['piece2'], "color2": color2, "position2": response['position2']})
                                        else:
                                            list_of_false_elem.append({"statement": statement})
                                    except:
                                        pass
                                                        
                    for correct_statement in list_of_true_elem:
                        try:
                            print("correct_statement:", f"""{correct_statement}""")
                            fixed_statement = self.fix_agent_executor.invoke({"input": f"""{correct_statement}"""})['output']
                            print("fixed_statement:", fixed_statement)      
                            list_of_statements.append({"statement": fixed_statement, "condition": True})  
                        except:
                            pass
                        
                    if len(correct_statement) == 0:
                        list_of_statements.append({"statement": statement, "condition": False}) 

                else:
                    response = self.sym.graph.verify_move_feature(piece1, color1, position1, piece2, color2, position2, move, feature)
                    print("response:", response[0]['piece'])
                    
                    if response == None or response[0] == None: # Incorrect
                        list_of_statements.append({"statement": statement, "condition": False})
                    elif response[0]['piece'] == piece1: # Correct
                        list_of_statements.append({"statement": statement, "condition": True})    
            except:
                pass
                
        return list_of_statements
