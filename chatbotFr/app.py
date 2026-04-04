# with st.chat_message("user",avatar="😎"):
#     st.text("hi baapo ke baaap bhavya")

# with st.chat_message("Ghostt",avatar="👻"):
#     st.text("hi how can i help u baapo ke baap")
import streamlit as st
from chatbotbackend import chatbot
from langchain_core.messages import HumanMessage ,AIMessage
import time
import uuid
from utils import generatethread_id,resetchat,addthreadid,loadConversations


# """ Session----------------------------------Setup """
if "message_history" not in st.session_state:
    st.session_state["message_history"]=[] 
    
if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generatethread_id()

if "chat_threads" not in st.session_state:
     st.session_state["chat_threads"] = []

addthreadid(st.session_state['thread_id'])
#Streamlit setup 
st.header("lolopoloGPT")


st.sidebar.title("lolopoloGPT")
if  st.sidebar.button("New chat"):
    resetchat()

st.sidebar.header("My Conversations")
    #displays the uuid for new chat
for threadid in st.session_state['chat_threads']:
    if st.sidebar.button(str(threadid)): # variable of for loop    
        st.session_state['thread_id'] = threadid
        messages = loadConversations(threadid)

        temp_msg = []
        for msg in messages:
            if isinstance(msg,HumanMessage):
                role="user"
            elif isinstance(msg,AIMessage):
                role="assistant"
            else:
                continue
            temp_msg.append({"role":role,"content":msg.content})
        
        st.session_state['message_history'] = temp_msg  
    
# loading the conversation history
for message in st.session_state["message_history"]:
    with st.chat_message(message['role']):
        st.text(message['content'])
CONFIG = {'configurable':{
    'thread_id':st.session_state['thread_id']}} 
#Check:if replace with the generatethread_id function 

userinput = st.chat_input("Ask anthing...")

if userinput:

    st.session_state['message_history'].append({
        'role':'user',
        "content":userinput
        })
    with st.chat_message("user"):
        st.text(userinput)

    with st.chat_message("assistant"):
            aimsg = st.write_stream(
            message_chunk.content for  message_chunk, metadata in chatbot.stream(
            {'messages':[HumanMessage(content=userinput)]},
            config=CONFIG,stream_mode="messages")
    )
              
    st.session_state['message_history'].append({'role':'assistant','content':aimsg})
