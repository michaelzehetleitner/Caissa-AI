"""
Schema description text blocks shared by Kor extraction chains.
"""

POSITION_SCHEMA_DESCRIPTION = """
                                Chess piece from the following list of pieces: [king, queen, knight, bishop, rook, pawn]
                                Chess color of a chess piece from the following list: [black, white]
                                Chess position of a chess piece from the following list of positions: [
                                    a1, a2, a3, a4, a5, a6, a7, a8,
                                    b1, b2, b3, b4, b5, b6, b7, b8,
                                    c1, c2, c3, c4, c5, c6, c7, c8,
                                    d1, d2, d3, d4, d5, d6, d7, d8,
                                    e1, e2, e3, e4, e5, e6, e7, e8,
                                    f1, f2, f3, f4, f5, f6, f7, f8,
                                    g1, g2, g3, g4, g5, g6, g7, g8,
                                    h1, h2, h3, h4, h5, h6, h7, h8
                                ]
                                
                                # Note
                                - you must fill fields with 'N/A' if they are not stated in the input.
"""


RELATION_SCHEMA_DESCRIPTION = """
                                # Role
                                You are programmer expert in converting text to JSON
                            
                                # Context
                                Chess piece from the following list of pieces: [king, queen, knight, bishop, rook, pawn]
                                Chess color of a chess piece from the following list: [black, white]
                                Chess position of a chess piece from the following list of positions: [
                                    a1, a2, a3, a4, a5, a6, a7, a8,
                                    b1, b2, b3, b4, b5, b6, b7, b8,
                                    c1, c2, c3, c4, c5, c6, c7, c8,
                                    d1, d2, d3, d4, d5, d6, d7, d8,
                                    e1, e2, e3, e4, e5, e6, e7, e8,
                                    f1, f2, f3, f4, f5, f6, f7, f8,
                                    g1, g2, g3, g4, g5, g6, g7, g8,
                                    h1, h2, h3, h4, h5, h6, h7, h8
                                ]
                                Chess relation between two chess pieces is from the following list of relations: [defend, threat]
                                - The following is a description of the relations:
                                    1. {{tactic: "defend"}}: is a relationship between a piece and an ally piece such that piece can defend or protect the ally piece. this is DIFFERENT from "move_defend" and "move_is_protected".
                                    2. {{tactic: "threat"}}: is a relationship between a piece and an opponent piece such that piece can attack or threat the opponent. this is DIFFERENT from "move_threat" and "move_is_attacked".              
                                
                                # Note:
                                    - If piece color is "white" then opponent color is "black" and if piece color is "black" then its opponent color is "white".
                                    - Ally pieces have the same color.
                                    - you must fill fields with 'N/A' if they are not stated in the input.
"""


MOVE_FEATURE_SCHEMA_DESCRIPTION = """
                        # Role
                        You are programmer expert in converting text to JSON
                    
                        # Context
                        Chess piece from the following list of pieces: [king, queen, knight, bishop, rook, pawn]
                        Chess color of a chess piece from the following list: [black, white]
                        Chess position and move of a chess piece from the following list of positions: [
                            a1, a2, a3, a4, a5, a6, a7, a8,
                            b1, b2, b3, b4, b5, b6, b7, b8,
                            c1, c2, c3, c4, c5, c6, c7, c8,
                            d1, d2, d3, d4, d5, d6, d7, d8,
                            e1, e2, e3, e4, e5, e6, e7, e8,
                            f1, f2, f3, f4, f5, f6, f7, f8,
                            g1, g2, g3, g4, g5, g6, g7, g8,
                            h1, h2, h3, h4, h5, h6, h7, h8
                        ]
                        Chess move features between two chess pieces is from the following list of relations: [move_defend, move_threat, move_is_protected, move_is_attacked]
                        - The following is a description of the relations:
                            1. {{feature: "move_defend"}}: is a move made by a piece from its current position to new position to defend an ally piece on a third different position. Use when asked about a "move" that defend or protect a piece.
                            2. {{feature: "move_is_protected"}}: is a move made by a piece from its current position to new position and it is protected by an ally piece on a third different position. Use when asked about pieces that defend or protect a "move".
                            3. {{feature: "move_threat"}}: is a move made by a piece from its current position to new position to attack an opponent piece on a third different position. Use when asked about a "move" that attack or threat a piece.
                            4. {{feature: "move_is_attacked"}}: is a move made by a piece from its current position to new position and it is attacked by an opponent piece on a third different position. Use when asked about pieces that attack or threat a "move".
       
                        # Note:
                            - If piece color is "white" then opponent color is "black" and if piece color is "black" then its opponent color is "white".
                            - Ally pieces have the same color.
                            - The output must have 'piece', 'color', 'position', 'move' and 'feature'
                            - The output must include 'opponent_piece', 'opponent_color' and 'opponent_position' for 'move_is_attacked' or 'move_threat'
                            - The output must include 'ally_piece', 'ally_color' and 'ally_position' for 'move_is_protected' or 'move_defend'
                            - The 'move' can not be None or null!
                            - you must fill fields with 'N/A' if they are not stated in the input.
                            - The position of a piece MUST NOT be the SAME as the value of the move!
"""
