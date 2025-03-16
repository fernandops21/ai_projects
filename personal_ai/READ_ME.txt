Personal AI Project - By Fernando Santos

Project Structure:

personal_ai/
├── app.py               # Main application
├── memory/
│   ├── __init__.py
│   ├── working.py       # Working memory management
│   ├── episodic.py      # Episodic memory management
│   ├── semantic.py      # Semantic memory management
│   └── procedural.py    # Procedural memory management
├── utils/
│   ├── __init__.py
│   ├── embedding.py     # Embedding utilities
│   ├── extraction.py    # Information extraction utilities
│   └── prompting.py     # Prompt construction utilities
└── data/                # Where memories will be stored
    ├── episodic/
    ├── semantic/
    └── procedural/
