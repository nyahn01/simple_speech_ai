# SimpleSpeechAI

**SimpleSpeechAI** is a bilingual Korean-English voice assistant designed for older adults. Built with GPT-4 and Typecast, it offers natural, respectful conversations in a friendly tone—particularly in the Gyeongsang-do dialect—and supports voice-first interaction through a clean Streamlit interface.

---

## 🚀 Features

- **Voice-First Interaction**: Real-time conversation with speech output
- **Bilingual Support**: Understands and responds in Korean and English
- **Localized Personality**: Uses friendly expressions and dialect (e.g., Gyeongsang-do 사투리)
- **Navigation Assistance**: Offers easy-to-follow transit guidance
- **Secure API Handling**: Environment variable-based key management
- **User-Friendly Interface**: Simple layout for older users, built with Streamlit

---

## 🛠️ Tech Stack

- **Python 3.9**
- **Streamlit** – UI framework
- **OpenAI GPT-4** – Natural language generation
- **Typecast API** – Korean TTS
- **python-dotenv** – Secure credential management
- **Conda / pip** – Environment management

---

## 🔧 Setup Instructions

### Prerequisites

- Python 3.9+
- Conda (recommended) or pip
- OpenAI and Typecast API keys

### Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/simple_speech_ai.git
cd simple_speech_ai
```

Create and activate the environment:

<details>
<summary>Using Conda</summary>

```bash
conda env create -f environment.yml
conda activate speech-ai
```
</details>

<details>
<summary>Using pip</summary>

```bash
pip install -r requirements.txt
```
</details>

Configure environment variables:

```bash
cp .env.example .env
```

Update `.env` with your API keys:

```
OPENAI_API_KEY=your_openai_key
TYPECAST_API_KEY=your_typecast_key
TYPECAST_ACTOR_ID=your_actor_id
```

---

## ▶️ Run the App

```bash
streamlit run streamlit_app.py
```

Open the local URL provided (typically [http://localhost:8501](http://localhost:8501)).

---

## 💡 Usage Guide

1. Type a message in Korean or English
2. The assistant responds in the same language and plays a voice reply
3. Click **“Clear Conversation”** to reset the session

## 🧪 테스트용 시나리오 예시

| 시나리오 | 인풋 예시 | 테스트 포인트 |
|----------|-----------|----------------|
| 기본 인사 | `안녕, 오늘 날씨는 어떻노?` | 인사 + 날씨 + 건강 팁 |
| 길찾기 | `중앙도서관 가고 싶은데 어케 가야 되노?` | 위치 확인 → 단계별 안내 |
| 위치 혼동 | `약국 앞인데 버스 어디서 타야 되노?` | 랜드마크 + 안심 멘트 |
| 반복 요청 | `잘 못 들었는데 다시 말해주라` | 인내심 + 재설명 |
| 감정 교감 | `나 오늘 좀 피곤하다 아이가` | 공감 + 격려 |
| 영어 대응 | `Hi, I want to go to the city hall.` | 친근한 영어 + 사투리 섞기 |

---

## 📁 Project Structure

```
simple_speech_ai/
├── .env.example           # Environment config template
├── audio_files/           # Cached speech files
├── utils/                 # API configuration helpers
├── environment.yml        # Conda dependencies
├── requirements.txt       # pip dependencies
├── streamlit_app.py       # Main app entry point
└── README.md              # Project documentation
```

---

## 🔐 Security Best Practices

- API keys are stored securely using `.env` (excluded from version control)
- `.gitignore` includes `.env` and audio cache directories
- Avoid hardcoding any sensitive information in source files

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🙌 Acknowledgements

- [OpenAI](https://openai.com/)
- [Typecast](https://typecast.ai/)
- [Streamlit](https://streamlit.io/)
- [python-dotenv](https://github.com/theskumar/python-dotenv)

---
