

### A. Theoretical / scientific concepts and patterns (directly relevant)

LLM + engine / expert integration for chess explanations and evaluation:

* Kim et al., 2025 – “Bridging the Gap between Expert and Language Models: Concept-guided Chess Commentary Generation and Evaluation (CCC + GCC-Eval)” ([arXiv][1])
* Feng et al., 2023 – “ChessGPT: Bridging Policy Learning and Language Modeling” ([arXiv][2])
* Wen et al., 2025 – “ChessQA: Evaluating Large Language Models for Chess Understanding” ([arXiv][3])
* Jhamtani et al., 2018 – “Learning to Generate Move-by-Move Commentary for Chess Games from Large-Scale Social Forum Data” ([ACL Anthology][4])
* Lee & Wu, 2023 – “Improving Chess Commentaries by Combining Language Models and Chess Engines” ([Semantic Scholar][5])

Faithful explanations, verification, and reasoning patterns (general but complementary):

* Yao et al., 2023 – “ReAct: Synergizing Reasoning and Acting in Language Models”
* Madaan et al., 2023 – “Self-Refine / CRITIC” (draft–check–revise with tools)
* Shinn et al., 2023 – “Reflexion: Language Agents with Verbal Reinforcement Learning”
* Liu et al., 2023 – “Chain-of-Verification (CoVe)”
* Gao et al., 2024 – “Faithful Chain-of-Thought Reasoning”

Neural-symbolic / program-aided reasoning:

* Chen et al., 2022 – “Program-Aided Language Models (PAL)”
* Various works on differentiable logic / neurosymbolic reasoning applied to games (not chess-specific, but conceptually close to your Prolog + LLM setup).

Human-aligned explanations / player modeling:

* McIlroy-Young et al., 2020–2024 – “Maia Chess: A Human-Like Neural Network Chess Engine” and “Maia-2: A Unified Model for Human-AI Alignment in Chess” ([GitHub][6])

---

### B. Implementation-level tools, verification, and chess-focused systems

Chess commentary, explanation, and evaluation systems:

* ml-postech/concept-guided-chess-commentary (CCC + GCC-Eval official repo) ([GitHub][7])
* harsh19/ChessCommentaryGeneration (Jhamtani et al. commentary generation) ([GitHub][8])
* Lee & Wu implementation (if public; referenced in Semantic Scholar under “Improving Chess Commentaries by Combining Language Models and Chess Engines”) ([Semantic Scholar][5])

Datasets and benchmarks for explanation/understanding (not move choice):

* wieeii/ChessQA-Benchmark (ChessQA HF dataset) ([Hugging Face][9])
* kagisearch/llm-chess-puzzles (tactical correctness; useful for verifying facts about “this move wins/loses”) ([ACM Digital Library][10])
* jalpp/chess-llm-bench (Chess Context Protocol for structured board/context encoding) ([DBLP][11])

Chess-specialized models and engines you can wrap as tools:

* waterhorse1/ChessGPT (code + dataset + evaluation framework) ([GitHub][12])
* CSSLab/maia-chess (Maia and Maia-2 engines) ([GitHub][6])
* Stockfish, Leela Zero, and other standard engines (as evaluation oracles for your tools layer).

LLM + engine coaching / explanation projects:

* Leomconti/chess-ai-llm (Stockfish + GPT commentary) ([DBLP][13])
* chess.rich (Sunfish + LLM coaching system, closed source but live system)

---

### C. Closely related but complementary (for style, pedagogy, and alignment)

Human-like and level-specific evaluation:

* Maia Chess website and papers (human-level modeling, useful for tailoring explanations by Elo) ([Maia Chess][14])

General LLM game-commentary work:

* Su et al., 2025 – “A Study of LLMs in Game Commentary Generation” (covers non-chess games but techniques transfer)

Robustness and prompt-format sensitivity in chess:

* dpaleka/llm-chess-proofgame – “LLMs playing chess are sensitive to how the position came to be” ([CMU School of Computer Science][15])

---

### D. What else I would add (meta / methodology)

Methodology and evaluation patterns you can borrow, even if not chess-specific:

* Toolformer (Schick et al., 2023) – learning when to call tools.
* Self-Consistency for CoT (Wang et al., 2022) – ensembles of rationales.
* Benchmarks and techniques from faithful CoT / factuality in LLMs (surveys on hallucinations and faithfulness).

All of these are complementary to your project’s scope: fact-based, human-understandable evaluation and explanation of positions and moves, with move selection handled elsewhere.

[1]: https://arxiv.org/abs/2410.20811?utm_source=chatgpt.com "Bridging the Gap between Expert and Language Models ..."
[2]: https://arxiv.org/abs/2306.09200?utm_source=chatgpt.com "ChessGPT: Bridging Policy Learning and Language Modeling"
[3]: https://arxiv.org/abs/2510.23948?utm_source=chatgpt.com "ChessQA: Evaluating Large Language Models for Chess Understanding"
[4]: https://aclanthology.org/P18-1154/?utm_source=chatgpt.com "Learning to Generate Move-by-Move Commentary for ..."
[5]: https://www.semanticscholar.org/paper/Improving-Chess-Commentaries-by-Combining-Language-Lee-Wu/529548ce8485daac29dbead20c4c383d965ae1d6?utm_source=chatgpt.com "Improving Chess Commentaries by Combining Language ..."
[6]: https://github.com/CSSLab/maia-chess?utm_source=chatgpt.com "Maia is a human-like neural network chess engine trained ..."
[7]: https://github.com/ml-postech/concept-guided-chess-commentary?utm_source=chatgpt.com "ml-postech/concept-guided-chess-commentary"
[8]: https://github.com/harsh19/ChessCommentaryGeneration?utm_source=chatgpt.com "harsh19/ChessCommentaryGeneration"
[9]: https://huggingface.co/datasets/wieeii/ChessQA-Benchmark?utm_source=chatgpt.com "wieeii/ChessQA-Benchmark · Datasets at Hugging Face"
[10]: https://dl.acm.org/doi/10.5555/3666122.3666438?utm_source=chatgpt.com "ChessGPT: bridging policy learning and language modeling"
[11]: https://dblp.org/rec/conf/acl/HovyNBGJ18?utm_source=chatgpt.com "Learning to Generate Move-by-Move Commentary for ..."
[12]: https://github.com/waterhorse1/ChessGPT?utm_source=chatgpt.com "ChessGPT - Bridging Policy Learning and Language ..."
[13]: https://dblp.org/rec/conf/nips/FengLWTYSM0W23?utm_source=chatgpt.com "ChessGPT: Bridging Policy Learning and Language Modeling."
[14]: https://www.maiachess.com/?utm_source=chatgpt.com "Maia Chess"
[15]: https://www.cs.cmu.edu/~hovy/papers/18ACL-chess-commentary.pdf?utm_source=chatgpt.com "Learning to Generate Move-by-Move Commentary for ..."
