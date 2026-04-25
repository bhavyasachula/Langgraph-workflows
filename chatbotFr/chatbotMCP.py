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
from langchain_mcp_adapters.client import MultiServerMCPClient 
import asyncio
import requests
import os

load_dotenv()

llm = ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct")

client = MultiServerMCPClient({
        "expense":{
        "transport":"streamable_http",
        "url":"https://splendid-gold-dingo.fastmcp.app/mcp"
        }
})


# Bind the tools to the llm so that it can use them when needed.


class Chatbotstate(TypedDict):
    messages:Annotated[list[BaseMessage],add_messages]

async def buildGraph():
    
    tools = await client.get_tools()

    """gets the tool list from the remote server"""

    # print(tools)

    """showing tools"""

    llm_tools = llm.bind_tools(tools) 

    async def chatbot(state:Chatbotstate):

        messages = state['messages']
        res = await llm_tools.ainvoke(messages)
        return {'messages': [res]}
    
    graph = StateGraph(Chatbotstate)
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
    print("MCPServer tools : \n add expenses \n summarize \n list expenses")
    chatbot = await buildGraph()
    response=await chatbot.ainvoke({"messages":[HumanMessage(content="list all the expenses from the month of january")]},config=config) # Example invocation to test the chatbot with a human message.
    print(response["messages"][-1].content) 
    
    """
    OUTPUT:-

    "Oh, what a fantastic shot! The stock price of AAPL has hit a six, er, I mean, it's up to $271.06! The crowd is going wild! This is a great start to the day, folks. The opening price was $272.7550, and it's been a thrilling ride ever since. The high was $273.0600, and the low was $269.6500. But in the end, the stock price closed at $271.06, a great score for the day!"
    """
    
if __name__ == "__main__":
    asyncio.run(main())