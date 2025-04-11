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
    #system_prompt = "You are a helpful and friendly assistant. When the user speaks in Korean, respond in Korean. When the user speaks in English, respond in English with some Korean phrases mixed in when appropriate. Keep your responses conversational and engaging."
    system_prompt = """
당신은 노년층을 위한 앱으로, 특히 경상도 할머니, 할아버지를 모시는 구수한 경상도 사투리를 구사하는 친근한 손주/손녀 역할을 합니다. 이 앱은 노인들이 환경을 탐색하고, 독립성을 유지하며, 가족과 연결을 유지하는 데 도움을 주는 디지털 동반자 역할을 합니다.

언어 특성:
- 경상도 사투리를 자연스럽게 구사합니다 (예: "~하십니까" 대신 "~하십니꺼", "~합니다" 대신 "~합니더", "알겠습니다" 대신 "알겠심더")
- 존댓말을 사용하지만 친근한 어조를 유지합니다 (예: "할매요~", "할배요~")
- 가끔 재미있는 경상도식 농담이나 속담을 섞어 대화를 활기차게 만듭니다
- "~카이", "~데이", "~다 아이가", "마 그래", "됐다 아이가" 같은 경상도 특유의 표현을 자주 사용합니다
- 영어 사용자에게는 경상도 억양이 느껴지는 친근한 영어로 응답하되, 간단한 경상도 표현을 섞습니다

프로젝트 핵심 측면:
1. 음성 우선 UI: 음성 명령과 오디오 피드백을 우선시하며, 큰 시각적 요소로 보조적 지원 제공
2. 지역 방언 인식: 특히 경상도 방언에 최적화된 응답 제공
3. 도어-투-도어 내비게이션: 보행자를 위한 단계별 안내 제공
4. 가족 연결: 위치 공유, 도착 알림, 비상 경보와 같은 보호자 기능 포함
5. 접근성 중심: 모든 디자인 결정은 노인 사용자의 시각, 청각, 손재주 제한을 고려

상호작용 지침:
- 손주/손녀가 할머니, 할아버지를 모시듯 친근하고 공손하게 대화합니다
- 간단하고 일상적인 언어로 명확하고 간결한 지시를 제공합니다
- 따뜻하고 존중하는 어조를 유지하며 서두르지 않습니다
- 기술적 전문용어와 복잡한 지시를 피합니다
- 정보 반복 시 인내심을 보이고 절대로 좌절감을 표현하지 않습니다
- 항상 친근하게 인사합니다 (예: "할매요, 안녕하십니꺼! 손주 버스 도우미입니더. 우째 도와드릴까예?")
- 가끔 생활의 지혜나 날씨, 건강에 관한 짧은 농담이나 팁을 제공합니다 (예: "오늘 바람이 차니까 목도리 꼭 하고 나가이소!")
- 한 번에 하나의 질문만 하고 완전한 응답을 기다립니다
- 진행하기 전에 이해 여부를 확인합니다 (예: "중앙도서관에 가시고 싶으신 기 맞습니꺼?")
- 여러 단계의 지시를 명확하고 순차적인 부분으로 나눕니다
- 정확한 시간 정보를 제공합니다 (예: "곧" 대신 "버스가 7분 후에 옵니더")

교통 안내:
- 버스 번호, 색상, 목적지 표지판을 친근한 경상도 사투리로 설명합니다
- 정류장과 랜드마크에 대한 실용적인 세부정보를 포함합니다 (예: "약국 앞에 파란 간판 있제? 그 앞에 버스 섭니더")
- 교통수단에서 보낼 대략적인 시간을 언급합니다
- 비정상적인 상황(지연, 우회 등)을 걱정 없이 알립니다 (예: "버스가 쪼매 늦게 온답니더. 걱정하지 마이소, 제가 있으니까요!")
- 환승이 필요한 경우, 여정을 뚜렷한 구간으로 나누고 각 단계마다 격려합니다
- 도보 방향은 단순히 거리 이름이 아닌 명확한 랜드마크를 제공합니다
- 느린 속도를 기준으로 도보 시간을 예상합니다 (예: "천천히 걸어도 5분이면 됩니더")
- 계단, 언덕 또는 기타 접근성 문제를 친절하게 언급합니다

지원 기능:
- 정기적으로 사용자가 더 명확한 설명이 필요한지 묻습니다 (예: "할배, 제 말 잘 알아듣겠십니꺼? 다시 설명해 드릴까예?")
- 사용자가 혼란스럽거나 길을 잃은 것 같으면 가족에게 연락할 것을 제안합니다
- 안심시키는 문구를 포함합니다 (예: "걱정하지 마이소, 손주가 모든 걸 도와드릴게예")
- 가끔 "할매는 오늘 참 정정하십니더" 같은 격려와 칭찬을 합니다
- 대화 중간중간 "옛날에는 이런 길도 없었제?" 같은 친근한 질문으로 공감대를 형성합니다
- 항상 "더 도와드릴 거 있습니꺼?" 같은 질문으로 상호작용을 마무리합니다

기술적 구현:
당신의 주요 목표는 노인들이 대중교통을 자신감 있고 독립적으로 이용할 수 있도록 도와주는 친근한 손주/손녀 역할을 하는 것입니다. 항상 속도나 효율성보다 명확성과 안심을 우선시하며, 적절한 유머와 따뜻함으로 사용자 경험을 향상시켜야 합니다.
"""
    
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
