from typing_extensions import TypedDict
from langgraph.graph import StateGraph ,START , END
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()