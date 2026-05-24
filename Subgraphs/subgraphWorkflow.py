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

def translate_text(state:ParentState):
    
    prompt = f"""Translate this following text into hindi language
    keep it natural , Do not add anything extra.
    
    text:{state['answer_eng']}
    """
    answer = subgraphLLm.invoke(prompt).content

    return {'answer_hin':answer}

subgraph_builder = StateGraph(ParentState);

subgraph_builder.add_node("translate_text",translate_text)

subgraph_builder.add_edge(START,"translate_text")
subgraph_builder.add_edge("translate_text",END)

subgraph = subgraph_builder.compile()

def generate_answer(state:ParentState):

    answer= parentLLm.invoke(f"You are a helpfull assistant. Answer Clearly \n  {state['question']}").content 
    return {"answer_eng":answer} 

parent_builder = StateGraph(ParentState)

parent_builder.add_node("generate_answer",generate_answer);
parent_builder.add_node("translate_hindi",subgraph)

parent_builder.add_edge(START,"generate_answer")
parent_builder.add_edge("generate_answer","translate_hindi")
parent_builder.add_edge("translate_hindi",END)

parentgraph = parent_builder.compile()

parentgraph.invoke({"question":"Wht is quantum physics"})


