from langgraph.graph import START,END
from langgraph.graph import StateGraph,START,END
from langgraph.graph.message import add_messages
from typing import TypedDict,Annotated,Literal
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import BaseMessage,HumanMessage,SystemMessage,AIMessage
from langgraph.checkpoint.sqlite import SqliteSaver # Using this for Persistence
from langgraph.prebuilt import ToolNode , tools_condition
from langchain_core.tools import tool 
from langgraph.types import interrupt,Command
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
@tool
def purchase_stock(symbol:str,quantity:str):
    """
    Simulate purchasing a given quantity of a stock symbol

    Simulate purchasing stock.
    IMPORTANT:
    - quantity must be an INTEGER (not string)
    Human-in-the-loop:
    Before confirming this tool will interrupt 
    and wait for the human decision ("yes / anything else").
    """
    quantity = int(quantity)
    decision = interrupt(f"Approve buying {quantity} shares of {symbol}? yes/no");

    if isinstance(decision,str) and decision.lower() == "yes":
        return{
            "status":"success",
            "message":f"Purchase order placed for {quantity} shares of {symbol}.",
            "symbol":symbol,
            "quantity":quantity
        }
    else:
        return{
            "status":"cancelled",
            "message":f"Purchase of {quantity} shares of {symbol} was declined by the human.",
            "symbol":symbol,
            "quantity":quantity
        }

search_tool= DuckDuckGoSearchRun(region="us-en")

tools = [getstockprice_for_America_tool,purchase_stock]

llm_tools = llm.bind_tools(tools) # Bind the tools to the llm so that it can use them when needed.

tool = ToolNode(tools) # Create a ToolNode with the bound tools.

memory = MemorySaver()

class Chatbotstate(TypedDict):
    messages:Annotated[list[BaseMessage],add_messages]

graph = StateGraph(Chatbotstate)


def chatbot(state:Chatbotstate):
    system_msg = SystemMessage(content="""
    You are a stock trading assistant.

    Rules:
    - If a tool is called, always use its result to respond.
    - Do NOT say you cannot perform the task.
    - If purchase_stock succeeds, confirm the purchase clearly.
    """)
    messages = state['messages']
     
    res =llm_tools.invoke([system_msg] + messages) # Pass the system message along with the conversation history to the llm with tools.
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

chatbot = graph.compile(checkpointer=memory) 

# Simulation for human-in-the-loop in (Cli with HITL)

if __name__ == "__main__":
    thread = "1"

while True:
    userinput = input("You :")
    if userinput.lower() =="exit" :
            break;
    
    state = {"messages":[HumanMessage(content=userinput)]}

    result =chatbot.invoke(
        state,
        config={"configurable":{
            "thread_id":thread
        }}
    )

    interrupt_data = result.get("__interrupt__",[])

    if interrupt_data:
            prompt_to_human = interrupt_data[0].value
            print(f"HITL:{prompt_to_human}")
            decision = input("Your decision :").lower()
            result = chatbot.invoke(
            Command(resume=decision),
            config={"configurable":{
            "thread_id":thread
        }}
    )
            
    messages = result["messages"]
    last_msg = messages[-1]
    print(f"Ai :{last_msg.content}\n");