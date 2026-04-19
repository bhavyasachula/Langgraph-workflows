from langgraph.graph import START,END
from langgraph.graph import StateGraph,START,END
from langgraph.graph.message import add_messages
from typing import TypedDict,Annotated,Literal
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage,HumanMessage,SystemMessage,AIMessage
from langgraph.checkpoint.sqlite import SqliteSaver # Using this for Persistence
import sqlite3
load_dotenv()
conn = sqlite3.connect(database="chatbot.db",check_same_thread=False)
class Chatbotstate(TypedDict):
    messages:Annotated[list[BaseMessage],add_messages]

checkpointer = SqliteSaver(conn=conn) 

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

def retrieval_of_threads():
    allthreads = {
    checkpoint.config['configurable']['thread_id']
    for checkpoint in checkpointer.list(None) 
    }
     
    return list(allthreads)
