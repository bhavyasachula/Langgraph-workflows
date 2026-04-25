from langgraph.graph import START,END
from langgraph.graph import StateGraph,START,END
from langgraph.graph.message import add_messages
from typing import TypedDict,Annotated,Literal
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage,HumanMessage,SystemMessage,AIMessage
from langgraph.checkpoint.sqlite import SqliteSaver # Using this for Persistence
from langgraph.prebuilt import ToolNode , tools_condition
from langchain_core.tools import tool 
from langchain_community.tools import DuckDuckGoSearchRun
import sqlite3
import os
import requests

os.environ['LANGCHAIN_PROJECT'] = "LANGGRAPH-LANGSMITH" # Set the LANGCHAIN_PROJECT environment variable

load_dotenv()

llm = ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct")

@tool
def getstockprice_for_America_tool(symbol:str):
    """Fetch a latest stock price of America(US) for a given stock symbol eg(AAPL, MSFT,TSLA)
        using alpha vantage api. 
    """
    url =f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={os.getenv('ALPHAVANTAGE_API_KEY')}"
    r = requests.get(url)
    return r.json()


search_tool= DuckDuckGoSearchRun(region="us-en")

tools = [getstockprice_for_America_tool,search_tool]

llm_tools = llm.bind_tools(tools) # Bind the tools to the llm so that it can use them when needed.

tool = ToolNode(tools) # Create a ToolNode with the bound tools.

conn = sqlite3.connect(database="chatbot.db",check_same_thread=False)

class Chatbotstate(TypedDict):
    messages:Annotated[list[BaseMessage],add_messages]

checkpointer = SqliteSaver(conn=conn) 

graph = StateGraph(Chatbotstate)


def chatbot(state:Chatbotstate):
    messages = state['messages']
    res =llm_tools.invoke(messages)
    return {'messages': [res]}

graph.add_node("Chatbot",chatbot)
graph.add_node("tools",tool) # Add the tool node to the graph
graph.add_edge(START,"Chatbot")
graph.add_conditional_edges("Chatbot",tools_condition)
graph.add_edge("tools", "Chatbot") 
graph.add_edge("Chatbot",END)

config = {
    "configurable": {
        "thread_id": "1"
    }
}
chatbot = graph.compile(checkpointer=checkpointer) 

response=chatbot.invoke({"messages":[HumanMessage(content="What is the status of iran and usa war and tell the latest stock price of in america?")]},config=config) # Example invocation to test the chatbot with a human message.
print(response["messages"][-1].content) 

# def retrieval_of_threads():
#     allthreads = {
#     checkpoint.config['configurable']['thread_id']
#     for checkpoint in checkpointer.list(None) 
#     }
#     return list(allthreads)
