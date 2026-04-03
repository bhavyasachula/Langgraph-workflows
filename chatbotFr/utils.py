import uuid
import streamlit as st
from chatbotbackend import chatbot
def generatethread_id():
    thread_id = uuid.uuid4()
    return thread_id

def resetchat():
    thread_id = generatethread_id();
    st.session_state['thread_id'] = thread_id
    addthreadid(st.session_state['thread_id'])
    st.session_state['message_history'] = []

def addthreadid(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def loadConversations(thread_id):
    return chatbot.get_state(config={'configurable':{'thread_id':thread_id}}).values['messages'] 