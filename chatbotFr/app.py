import streamlit as st
from chatbotbackend import chatbot
from langchain_core.messages import HumanMessage
if "message_history" not in st.session_state:
    st.session_state["message_history"]=[] #session state is a dictionary that stores the values in this case
    # if message_history is not present then make the message_history in session state or make the message dict into 
    # session_state 
with st.chat_message("user",avatar="😎"):
    st.text("hi baapo ke baaap bhavya")

with st.chat_message("Ghostt",avatar="👻"):
    st.text("hi how can i help u baapo ke baap")

for message in st.session_state["message_history"]:
    with st.chat_message(message['role']):
        st.text(message['content'])
thread_id = 1
CONFIG = {'configurable':{
    'thread_id':thread_id}}
userinput = st.chat_input("Ask anthing...")

if userinput:

    st.session_state['message_history'].append({
        'role':'user',
        'avatar':'😎',
        "content":userinput
        })
    with st.chat_message("user"):
        st.text(userinput)

    
    with st.chat_message("ai"):
      aimsg = st.write_stream(
        message_chunk.content for  message_chunk, metadata in chatbot.stream({'messages':[HumanMessage(content=userinput)]},config=CONFIG,stream_mode="messages")
        )
      st.session_state['message_history'].append({'role':'ai','content':aimsg})