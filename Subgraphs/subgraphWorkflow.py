from typing_extensions import TypedDict
from langgraph.graph import StateGraph ,START , END
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

class ParentState(TypedDict):
    question:str
    answer_eng:str
    answer_hindi:str

