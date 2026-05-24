from typing_extensions import TypedDict
from langgraph.graph import StateGraph ,START , END
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

class ParentState(TypedDict):
    question:str
    answer_eng:str
    answer_hin:str

parentLLm = ChatGroq(model="openai/gpt-oss-120b")
subgraphLLm = ChatGroq(model="openai/gpt-oss-120b")

def translate_text(state:StateGraph):
    
    prompt = f"""Translate this following text into hindi language
    keep it natural , Do not add anything extra.
    
    text:{state['answer_eng']}
    """
    answer = subgraphLLm.invoke(prompt).content

    return {'answer_hindi':answer}

subgraph_builder = StateGraph(ParentState);

subgraph_builder.add_node("translate_text",translate_text)

subgraph_builder.add_edge(START,"translate_text")
subgraph_builder.add_edge("translate_text",END)

subgraph = subgraph_builder.compile()

