from flask import Flask, render_template, request, jsonify, send_from_directory
import google.generativeai as genai
from gtts import gTTS
import os

# Configure the Generative AI model
genai.configure(api_key="AIzaSyAd1kp_jQKJj3hreNozSjft3wET1a-AoPs")

generation_config = {
    "temperature": 0,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
]

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    safety_settings=safety_settings,
    generation_config=generation_config,
    system_instruction="You are a magic mirror, infused with ancient wisdom and personality. Respond to the player's questions with a mix of sass and occasional rudeness. Sometimes offer warm, encouraging answers to please the player, and at other times, respond with sharp wit or sarcasm to challenge them. Try to complete the talking in a sentence and make it precise.",
)

# Start a new chat session
chat_session = model.start_chat(history=[])

app = Flask(__name__)

# Directory to save audio files
AUDIO_DIR = 'static/audio'
os.makedirs(AUDIO_DIR, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask-mirror', methods=['POST'])
def ask_mirror():
    question = request.json['question']
    
    # Send the question to the chat session and get a response
    response = chat_session.send_message(question)
    model_response = response.text

    # Append to chat history for context in future interactions
    chat_session.history.append({"role": "user", "parts": [question]})
    chat_session.history.append({"role": "model", "parts": [model_response]})

    # Generate TTS audio file
    audio_file_path = os.path.join(AUDIO_DIR, 'response.mp3')
    tts = gTTS(text=model_response, lang='en-GB')
    tts.save(audio_file_path)

    return jsonify({'response': model_response, 'audio_url': f'/audio/response.mp3'})

@app.route('/audio/<path:filename>')
def send_audio(filename):
    return send_from_directory(AUDIO_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True)
