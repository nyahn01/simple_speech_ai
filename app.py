import streamlit as st
import requests
import json
import time
import os
import io
import tempfile
from openai import OpenAI
from dotenv import load_dotenv
from audiorecorder import audiorecorder

# Load environment variables from .env file
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Voice-First AI Conversation",
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
if 'auto_play' not in st.session_state:
    st.session_state.auto_play = True
if 'is_listening' not in st.session_state:
    st.session_state.is_listening = False

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
st.title("Voice-First AI Conversation")
st.markdown("🎙️ Speak or type to interact with the AI assistant.")

# Function to get language selection
def speech_language_code():
    language_mapping = {
        "Korean": "ko",
        "English": "en"
    }
    
    selected = st.session_state.get('speech_language', "Auto-detect")
    return language_mapping.get(selected, None)  # None is for auto-detect

# Function to transcribe audio using OpenAI Whisper API
def transcribe_audio(audio_data):
    with st.spinner("Transcribing your speech..."):
        try:
            # Export audio to a temporary WAV file
            temp_filename = f"temp_recording_{int(time.time())}.wav"
            audio_data.export(temp_filename, format="wav")
            
            # Use OpenAI's Whisper API to transcribe the audio
            with open(temp_filename, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=speech_language_code()
                )
            
            # Clean up the temporary file
            os.remove(temp_filename)
            
            return transcript.text
        except Exception as e:
            st.error(f"Error transcribing audio: {e}")
            return None

# Function to generate response using OpenAI
def generate_response(user_input):
    # Simple system prompt
    system_prompt = "You are a helpful AI assistant. Respond concisely and conversationally."
    
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
    
    with st.spinner("Generating response..."):
        try:
            response = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=250  # Keeping responses shorter for voice interaction
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
    with st.spinner("Generating voice response..."):
        payload = {
            'text': text,
            'lang': 'auto',
            'actor_id': api_keys["typecast_actor_id"],
            'xapi_hd': True,
            'model_version': 'latest',
            'tempo': 1.1,  # Slightly faster for better flow
            'volume': 100,
            'pitch': 0
        }
        
        try:
            r = requests.post('https://typecast.ai/api/speak', headers=headers, json=payload)
            r.raise_for_status()
            response_data = r.json()
            
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
            poll_interval = 1  # Seconds between polls
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for attempt in range(max_attempts):
                progress_value = attempt / max_attempts
                progress_bar.progress(progress_value)
                status_text.text(f"Creating voice response... ({attempt+1}/{max_attempts})")
                
                poll_response = requests.get(speak_url, headers=headers)
                poll_response.raise_for_status()
                poll_data = poll_response.json()
                
                # Check if we have status in the poll data
                if ('status' in poll_data and poll_data['status'] == 'done') or \
                   ('result' in poll_data and 'status' in poll_data['result'] and poll_data['result']['status'] == 'done'):
                    progress_bar.progress(1.0)
                    status_text.text("Voice ready!")
                    
                    # Get the audio download URL
                    audio_url = None
                    if 'result' in poll_data and 'audio_download_url' in poll_data['result']:
                        audio_url = poll_data['result']['audio_download_url']
                    elif 'audio_download_url' in poll_data:
                        audio_url = poll_data['audio_download_url']
                    
                    if audio_url:
                        # Download the audio file
                        audio_response = requests.get(audio_url)
                        audio_response.raise_for_status()
                        
                        filename = f"./audio_files/speech_{int(time.time())}.wav"
                        with open(filename, 'wb') as f:
                            f.write(audio_response.content)
                        
                        return filename
                    else:
                        st.error("Could not find audio_download_url in response")
                        return None
                else:
                    time.sleep(poll_interval)
            
            progress_bar.progress(1.0)
            status_text.text("Time limit reached")
            st.error(f"Exceeded maximum polling attempts ({max_attempts})")
            return None
            
        except Exception as e:
            st.error(f"Error in generate_speech: {e}")
            return None

# Function to process user input and generate response
def process_message(user_input):
    if not user_input.strip():
        return
    
    # Add user message to conversation
    with st.chat_message("user"):
        st.write(user_input)
        
        # If coming from voice, indicate it was spoken
        if st.session_state.is_listening:
            st.caption("🎤 via speech")
            st.session_state.is_listening = False
    
    # Generate AI response
    ai_response = generate_response(user_input)
    
    # Add AI response to conversation
    with st.chat_message("assistant"):
        st.write(ai_response)
        
        # Generate speech for the response
        audio_file = generate_speech(ai_response)
        
        if audio_file:
            # Store the audio file
            st.session_state.audio_file = audio_file
            
            # Auto-play the audio if enabled
            if st.session_state.auto_play:
                audio_placeholder = st.empty()
                with audio_placeholder:
                    st.audio(audio_file, format="audio/wav", start_time=0)
        else:
            st.warning("Voice synthesis failed")

# Clear conversation
def clear_conversation():
    st.session_state.conversation_history = []
    st.session_state.audio_file = None
    st.experimental_rerun()

# Toggle auto-play setting
def toggle_auto_play():
    st.session_state.auto_play = not st.session_state.auto_play

# Function to process audio recording
def process_audio_recording(audio_data):
    if audio_data is None or len(audio_data) == 0:
        return
    
    # Set listening flag
    st.session_state.is_listening = True
    
    # Display recording info
    st.sidebar.write(f"Recording length: {audio_data.duration_seconds:.2f} seconds")
    
    # Transcribe the audio
    transcript = transcribe_audio(audio_data)
    
    if transcript:
        st.sidebar.success(f"Transcribed: {transcript}")
        # Process the transcribed text as user input
        process_message(transcript)
    else:
        st.sidebar.error("Failed to transcribe audio. Please try again.")

# Create two columns - main content and sidebar
col_main, col_sidebar = st.columns([3, 1])

# Sidebar settings and controls
with st.sidebar:
    st.title("Voice Settings")
    
    # Speech recognition language
    if 'speech_language' not in st.session_state:
        st.session_state.speech_language = "Auto-detect"
        
    st.session_state.speech_language = st.selectbox(
        "Recognition Language",
        ["Auto-detect", "Korean", "English"],
        index=["Auto-detect", "Korean", "English"].index(st.session_state.speech_language)
    )
    
    # Auto-play toggle
    auto_play = st.checkbox("Auto-play responses", value=st.session_state.auto_play, on_change=toggle_auto_play)
    
    # Clear conversation button
    if st.button("Clear Conversation"):
        clear_conversation()
    
    # Voice recording section
    st.markdown("### 🎤 Voice Input")
    
    # Initialize audio recorder with proper parameters
    audio_data = audiorecorder("Click to record", "Click to stop recording")
    
    # Help text
    st.caption("Click once to start recording, click again to stop.")
    
    # Process audio when new recording is available
    if len(audio_data) > 0:
        process_audio_recording(audio_data)

# Main area
# Display conversation history
if not st.session_state.conversation_history:
    st.info("💬 Start a conversation by speaking or typing below.")

for i, message in enumerate(st.session_state.conversation_history):
    st.chat_message("user").write(message["user"])
    if "assistant" in message:
        with st.chat_message("assistant"):
            st.write(message["assistant"])

# Input area at the bottom
st.write("---")
user_input = st.chat_input("Type your message or use the voice input button...")

if user_input:
    process_message(user_input)