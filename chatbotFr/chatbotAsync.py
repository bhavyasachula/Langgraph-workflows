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
import asyncio
import requests
import os
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



tools = [getstockprice_for_America_tool]

llm_tools = llm.bind_tools(tools) # Bind the tools to the llm so that it can use them when needed.


class Chatbotstate(TypedDict):
    messages:Annotated[list[BaseMessage],add_messages]

def buildGraph():
    graph = StateGraph(Chatbotstate)

    # Create a ToolNode with the bound tools.

    async def chatbot(state:Chatbotstate):

        messages = state['messages']
        res = await llm_tools.ainvoke(messages)
        return {'messages': [res]}
    
    tool = ToolNode(tools)
    graph.add_node("Chatbot",chatbot)
    graph.add_node("tools",tool) # Add the tool node to the graph
    graph.add_edge(START,"Chatbot")
    graph.add_conditional_edges("Chatbot",tools_condition)
    graph.add_edge("tools", "Chatbot") 
    graph.add_edge("Chatbot",END)

    chatbot = graph.compile() 
    return chatbot

config={
    "configurable":{"thread":"1"}
}

async def main():
    chatbot = buildGraph()
    response=await chatbot.ainvoke({"messages":[HumanMessage(content=" tell stock price of Apple in cricket commentators way?")]},config=config) # Example invocation to test the chatbot with a human message.
    print(response["messages"][-1].content) 
    
    """
    OUTPUT:-

    "Oh, what a fantastic shot! The stock price of AAPL has hit a six, er, I mean, it's up to $271.06! The crowd is going wild! This is a great start to the day, folks. The opening price was $272.7550, and it's been a thrilling ride ever since. The high was $273.0600, and the low was $269.6500. But in the end, the stock price closed at $271.06, a great score for the day!"
    """
    
if __name__ == "__main__":
    asyncio.run(main())