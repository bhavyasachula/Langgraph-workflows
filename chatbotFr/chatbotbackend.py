from langgraph.graph import START,END
from langgraph.graph import StateGraph,START,END
from langgraph.graph.message import add_messages
from typing import TypedDict,Annotated,Literal
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage,HumanMessage,SystemMessage,AIMessage
from langgraph.checkpoint.memory import MemorySaver # Using this for Persistence
load_dotenv()

class Chatbotstate(TypedDict):
    messages:Annotated[list[BaseMessage],add_messages]

checkpointer = MemorySaver() # call the function memorysaver() 

graph = StateGraph(Chatbotstate)

llm = ChatGroq(model="openai/gpt-oss-120b")

def chatbot(state:Chatbotstate):
    messages = state['messages']
    res =llm.invoke(messages)
    return {'messages': [AIMessage(content=res.content)]}

graph.add_node("Chatbot",chatbot)
graph.add_edge(START,"Chatbot")
graph.add_edge("Chatbot",END)
chatbot = graph.compile(checkpointer=checkpointer) 