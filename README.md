# SimpleSpeechAI

A Korean-English Voice Conversation Assistant powered by GPT-4 and Typecast text-to-speech.

## 🌟 Features

- Real-time conversation with an AI assistant
- Bilingual support for Korean and English
- High-quality Korean text-to-speech using Typecast API
- Clean Streamlit interface
- Persistent conversation history
- Secure API key management using environment variables

## 🛠️ Technologies

- **Python 3.9**
- **Streamlit** - Interactive web application framework
- **OpenAI GPT-4** - Natural language processing
- **Typecast API** - Korean text-to-speech synthesis
- **Conda** - Environment management
- **python-dotenv** - Environment variable management

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or later
- Conda (recommended for environment management) or pip
- OpenAI API key
- Typecast API key

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/simple_speech_ai.git
   cd simple_speech_ai
   ```

2. Create and activate environment:
   
   With Conda:
   ```bash
   conda env create -f environment.yml
   conda activate speech-ai
   ```
   
   With pip:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure your API keys:
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit the `.env` file and add your actual API keys:
     ```
     OPENAI_API_KEY=your_openai_api_key
     TYPECAST_API_KEY=your_typecast_api_key
     TYPECAST_ACTOR_ID=your_preferred_actor_id
     ```

### Running the Application

Start the Streamlit application:

```bash
streamlit run streamlit_app.py
```

Then open your browser and navigate to the URL shown in the terminal (usually http://localhost:8501).

## 💬 How to Use

1. Type a message in English or Korean into the chat input
2. The AI will respond in the same language (with some Korean phrases mixed in for English inputs)
3. The response will automatically be converted to speech and played

Use the "Clear Conversation" button in the sidebar to start a new conversation.

## 📝 Project Structure

```
simple_speech_ai/
├── .env                   # Environment variables (not in version control)
├── .env.example           # Example environment variables file
├── audio_files/           # Generated speech audio files
├── notebook/              # Jupyter notebooks for development
│   ├── audio_files/       # Audio files used during development
│   └── template_notebook.ipynb  # Template for using environment variables
├── utils/                 # Utility modules
│   ├── __init__.py        # Package initialization
│   └── api_config.py      # API configuration utilities
├── environment.yml        # Conda environment configuration
├── requirements.txt       # Pip requirements
├── streamlit_app.py       # Main application file
└── README.md              # Project documentation
```

## 🧪 Using Jupyter Notebooks

For development and testing, use the `template_notebook.ipynb` as a starting point. This template shows how to:

1. Import the utility functions from the `utils` package
2. Load API keys from environment variables
3. Make API calls to OpenAI and Typecast securely

Never hardcode API keys in your notebooks. The template demonstrates the proper way to access them from environment variables.

## ⚠️ Security Notes

- API keys are stored in the `.env` file which should never be committed to version control
- The `.gitignore` file is configured to exclude the `.env` file
- Generated audio files are saved in the `audio_files` directory
- Always use environment variables for sensitive information

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [OpenAI](https://openai.com/) for GPT-4
- [Typecast](https://typecast.ai/) for text-to-speech capabilities
- [Streamlit](https://streamlit.io/) for the web application framework
- [python-dotenv](https://github.com/theskumar/python-dotenv) for environment variable management
