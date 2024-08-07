import streamlit as st
import openai
from openai import OpenAI
import anthropic
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define options for the dropdowns
options = {
    'OpenAI': ['gpt-4o-mini', 'gpt-4o', 'gpt-4', 'gpt-3.5-turbo'],
    'Anthropic': ['claude-3-opus-20240229', 'claude-3-sonnet-20240229', 'claude-3-haiku-20240307', 'claude-3-5-sonnet-20240620'],
}

# Initialize session state
if 'chat_log' not in st.session_state:
    st.session_state.chat_log = []
if 'category' not in st.session_state:
    st.session_state.category = None
if 'selected_item' not in st.session_state:
    st.session_state.selected_item = None
if 'api_key' not in st.session_state:
    st.session_state.api_key = None

# Define the function to get a response
def get_response(category, model_name, user_message, api_key1):
    try:
        if category == 'OpenAI':
            chat_log = st.session_state.chat_log
            client = OpenAI(api_key=api_key1)
            logging.info("OpenAI client initialized.")
            
            chat_log.append({"role": "user", "content": user_message})
            logging.info(f"User message added to chat log: {user_message}")
            logging.info(model_name)

            response = client.chat.completions.create(
                model=model_name,
                messages=chat_log,
                max_tokens=3500
            )

            assistant_response = response.choices[0].message.content.strip('\n').strip()
            chat_log.append({"role": "assistant", "content": assistant_response})
            st.session_state.chat_log = chat_log
            return assistant_response
                
        elif category == 'Anthropic':
            client = anthropic.Client(api_key=api_key1)
            message = client.messages.create(
                model=model_name,
                max_tokens=1000,
                temperature=0,
                system="You are a helpful assistant.",
                messages=[{
                    "role": "user",
                    "content": [{
                        "type": "text",
                        "text": user_message
                    }]
                }]
            )
            return message.content
        
        else:
            return "Unsupported model provider"
    
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return f"Error: {e}"

# Main interface
st.title("Chatbot Interface")

# Category selection
category = st.selectbox('Select a category', list(options.keys()))
if category:
    model_select = st.selectbox('Select a model', options.get(category, []))
    api_key_input = st.text_input('Enter your API key', type='password')

    if st.button("Submit"):
        st.session_state.category = category
        st.session_state.selected_item = model_select
        st.session_state.api_key = api_key_input

# Display chatbot interface if form has been submitted
if st.session_state.api_key:
    st.subheader("Chat Interface")

    # Display chat log
    for entry in st.session_state.chat_log:
        role = entry['role']
        content = entry['content']
        st.write(f"*{role.capitalize()}*: {content}")

    # Input fields for the chat
    user_message = st.text_input('You:', '', key='user_message')
    if st.button('Send'):
        if user_message:
            st.session_state.chat_log.append({"role": "user", "content": user_message})

            # Get the response from the model
            response = get_response(
                st.session_state.category,
                st.session_state.selected_item,
                user_message,
                st.session_state.api_key
            )

            # Append assistant response to chat log
            st.session_state.chat_log.append({"role": "assistant", "content": response})
        else:
            st.error("Please enter a message.")

    # Reset Chat Button
    if st.button('Reset Chat'):
        st.session_state.chat_log = []
        st.session_state.api_key = None  # Clear API key to reset the interface
else:
    st.write('Please select a category and model, enter your API key, and click "Submit" to start chatting.')