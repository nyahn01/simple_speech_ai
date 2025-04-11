import streamlit as st
import requests
import json
import time
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Korean AI Voice Conversation",
    page_icon="🎤",
    layout="centered"
)

# Create directory for audio files if it doesn't exist
os.makedirs("./audio_files", exist_ok=True)

# Initialize session state
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'audio_file' not in st.session_state:
    st.session_state.audio_file = None

# Get API Keys from environment variables or Streamlit secrets
def get_api_keys():
    # Try to get from environment variables first
    openai_api_key = os.getenv("OPENAI_API_KEY")
    typecast_api_key = os.getenv("TYPECAST_API_KEY")
    typecast_actor_id = os.getenv("TYPECAST_ACTOR_ID", "606c6b127b9f53b4cd1743f5")  # Default Korean voice
    
    # If not found, try to get from Streamlit secrets
    if not openai_api_key and hasattr(st, "secrets"):
        openai_api_key = st.secrets.get("OPENAI_API_KEY")
        typecast_api_key = st.secrets.get("TYPECAST_API_KEY")
        typecast_actor_id = st.secrets.get("TYPECAST_ACTOR_ID", "606c6b127b9f53b4cd1743f5")
    
    return {
        "openai_api_key": openai_api_key,
        "typecast_api_key": typecast_api_key,
        "typecast_actor_id": typecast_actor_id
    }

# Get API keys
api_keys = get_api_keys()

# Check if API keys are available
if not api_keys["openai_api_key"] or not api_keys["typecast_api_key"]:
    st.error("API keys are missing. Please set OPENAI_API_KEY and TYPECAST_API_KEY in your .env file or Streamlit secrets.")
    st.stop()

# Initialize OpenAI client
client = OpenAI(api_key=api_keys["openai_api_key"])

# App title
st.title("Korean AI Voice Conversation")
st.markdown("Speak or type in Korean or English and get an AI response with Korean TTS voice.")

# Function to generate response using OpenAI
def generate_response(user_input):
    # Set the system prompt
    system_prompt = "You are a helpful and friendly assistant. When the user speaks in Korean, respond in Korean. When the user speaks in English, respond in English with some Korean phrases mixed in when appropriate. Keep your responses conversational and engaging."
    
    # Format the messages for OpenAI API
    messages = [
        {"role": "system", "content": system_prompt}
    ]
    
    # Add conversation history
    for entry in st.session_state.conversation_history:
        messages.append({"role": "user", "content": entry["user"]})
        if "assistant" in entry:
            messages.append({"role": "assistant", "content": entry["assistant"]})
    
    # Add the current user input
    messages.append({"role": "user", "content": user_input})
    
    with st.spinner("Generating AI response..."):
        try:
            response = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            ai_response = response.choices[0].message.content
            
            # Update conversation history
            st.session_state.conversation_history.append({
                "user": user_input, 
                "assistant": ai_response
            })
            
            return ai_response
        except Exception as e:
            st.error(f"Error generating response: {e}")
            return f"Sorry, I couldn't generate a response: {str(e)}"

# Function to generate speech using Typecast AI
def generate_speech(text):
    # Set up the headers
    headers = {
        'Authorization': f'Bearer {api_keys["typecast_api_key"]}',
        'Content-Type': 'application/json'
    }
    
    # Step 1: Request speech synthesis
    with st.spinner("Initiating speech synthesis..."):
        payload = {
            'text': text,
            'lang': 'auto',
            'actor_id': api_keys["typecast_actor_id"],
            'xapi_hd': True,
            'model_version': 'latest',
            'tempo': 1,
            'volume': 100,
            'pitch': 0
        }
        
        try:
            r = requests.post('https://typecast.ai/api/speak', headers=headers, json=payload)
            r.raise_for_status()
            response_data = r.json()
            
            st.write("Speech synthesis initiated")
            
            # Get the speak URL from the response
            if 'result' in response_data and 'speak_v2_url' in response_data['result']:
                speak_url = response_data['result']['speak_v2_url']
            elif 'result' in response_data and 'speak_url' in response_data['result']:
                speak_url = response_data['result']['speak_url']
            else:
                st.error("Could not find speak URL in response")
                return None
            
            # Step 2: Poll for the speech synthesis result
            max_attempts = 30  # Maximum polling attempts
            poll_interval = 2  # Seconds between polls
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for attempt in range(max_attempts):
                progress_value = attempt / max_attempts
                progress_bar.progress(progress_value)
                status_text.text(f"Generating speech... ({attempt+1}/{max_attempts})")
                
                poll_response = requests.get(speak_url, headers=headers)
                poll_response.raise_for_status()
                poll_data = poll_response.json()
                
                # Check if we have status in the poll data
                if 'status' in poll_data and poll_data['status'] == 'done':
                    progress_bar.progress(1.0)
                    status_text.text("Speech synthesis complete!")
                    
                    # Check if there's an audio download URL in the response
                    if 'result' in poll_data and 'audio_download_url' in poll_data['result']:
                        audio_url = poll_data['result']['audio_download_url']
                        
                        # Download the audio file
                        audio_response = requests.get(audio_url)
                        audio_response.raise_for_status()
                        
                        filename = f"./audio_files/speech_{int(time.time())}.wav"
                        with open(filename, 'wb') as f:
                            f.write(audio_response.content)
                        
                        status_text.text("Audio ready to play")
                        return filename
                    else:
                        st.error("Could not find audio_download_url in response")
                        return None
                elif 'result' in poll_data and 'status' in poll_data['result'] and poll_data['result']['status'] == 'done':
                    progress_bar.progress(1.0)
                    status_text.text("Speech synthesis complete!")
                    
                    # Check if there's an audio download URL in the response
                    if 'audio_download_url' in poll_data['result']:
                        audio_url = poll_data['result']['audio_download_url']
                        
                        # Download the audio file
                        audio_response = requests.get(audio_url)
                        audio_response.raise_for_status()
                        
                        filename = f"./audio_files/speech_{int(time.time())}.wav"
                        with open(filename, 'wb') as f:
                            f.write(audio_response.content)
                        
                        status_text.text("Audio ready to play")
                        return filename
                    else:
                        st.error("Could not find audio_download_url in response")
                        return None
                else:
                    time.sleep(poll_interval)
            
            progress_bar.progress(1.0)
            status_text.text("Timed out waiting for speech synthesis")
            st.error(f"Exceeded maximum polling attempts ({max_attempts})")
            return None
            
        except Exception as e:
            st.error(f"Error in generate_speech: {e}")
            return None

# Function to process user input and generate response
def process_message(user_input):
    if not user_input.strip():
        st.warning("Please enter a message")
        return
    
    # Add user message to conversation
    st.chat_message("user").write(user_input)
    
    # Generate AI response
    ai_response = generate_response(user_input)
    
    # Add AI response to conversation
    with st.chat_message("assistant"):
        st.write(ai_response)
        
        # Generate speech for the response
        audio_file = generate_speech(ai_response)
        
        if audio_file:
            # Play the audio
            st.session_state.audio_file = audio_file
            st.audio(audio_file, format="audio/wav", start_time=0)
        else:
            st.warning("Speech generation failed")

# Clear conversation
def clear_conversation():
    st.session_state.conversation_history = []
    st.session_state.audio_file = None
    st.experimental_rerun()

# Create the sidebar
st.sidebar.title("Options")
if st.sidebar.button("Clear Conversation"):
    clear_conversation()

# Display conversation history
for i, message in enumerate(st.session_state.conversation_history):
    st.chat_message("user").write(message["user"])
    if "assistant" in message:
        st.chat_message("assistant").write(message["assistant"])

# Input area
with st.container():
    st.write("---")
    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        process_message(user_input)
