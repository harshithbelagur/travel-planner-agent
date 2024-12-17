This repo is for the Course Project of COMS E6998 - Intro to Deep Learning and GenAI at Columbia University.

The goal of the code is to test the performance of ReAct and ReWOO using Commercial LLMs (for travel planning here).

Please make sure that you have set up your OPENAI_KEY and SERAPI_KEY environment variables correctly before proceeding.

To run the code, use the requirements.txt file. Then, set up the SQL and VectorDB using the v1.ipynb notebook.

To run the tests, run the appropriate notebooks, and here is the explanation of each notebook - </br>
1. rewoo-custom-5-tools.ipynb - ReWOO with all tools
2. rewoo-custom-5-tools-without-llm.ipynb - ReWOO with dictionary instead of LLM tool
3. rewoo-custom-4-tools.ipynb - ReWOO with 4 tools
4. rewoo-custom-3-tools.ipynb - ReWOO with 3 tools
5. rewoo-custom (missing user preference).ipynb - ReWOO with first tool failure
6. rewoo-custom (missing travel dates).ipynb - ReWOO with second tool failure
7. react-langgraph-5-tools.ipynb - ReAct with all tools
8. react-langgraph-4-tools.ipynb - ReAct with 4 tools
9. react-langgraph-3-tools.ipynb - ReAct with 3 tools
10. react-langgraph (missing user preference).ipynb - ReAct with first tool failure
11. react-langgraph (missing travel dates).ipynb - ReAct with second tool failure

All tools for ReAct are in the tools folder and those for ReWOO are in the rewoo-tools folder. We had to have a separate rewoo-tools folder as there are customizations done to handle string as inputs
