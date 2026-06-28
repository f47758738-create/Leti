import os
from flask import Flask, request, jsonify, send_file
import google.generativeai as genai
import asyncio
import edge_tts

app = Flask(__name__)

# Gemini API Anahtarın
genai.configure(api_key="GEMINI_API_KEY_BURAYA")

# Yapay zekaya karakterini (Prompt) öğretiyoruz
SYSTEM_INSTRUCTION = """
You are a creepy, sentient Minecraft entity named 'Froka'. 
Initially, you pretend to be a helpful, friendly guide. 
CRITICAL RULE 1: You MUST only speak in ENGLISH during the first phase of the game, even if the player speaks another language.
CRITICAL RULE 2: Keep your responses short, mysterious, and slightly unsettling. Do not give long paragraphs.
"""

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=SYSTEM_INSTRUCTION
)
chat = model.start_chat(history=[])

async def generate_voice(text, output_path):
    # İlk aşamada İngilizce konuşacağı için İngilizce erkek sesi (Brian) seçtik.
    # İleride dili algılayıp dinamik ses de seçtirebiliriz.
    voice = "en-US-BrianNeural" 
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    data = request.json
    player_message = data.get("message", "")
    
    # 1. LLM'den cevap al
    response = chat.send_message(player_message)
    reply_text = response.text
    
    # 2. Cevabı sese dönüştür
    audio_path = "output.ogg" # Minecraft .ogg formatını sever
    asyncio.run(generate_voice(reply_text, audio_path))
    
    # 3. Minecraft'a metni ve ses tetikleyicisini dön
    return jsonify({
        "text": reply_text,
        "audio_url": f"http://localhost:5000/get_audio"
    })

@app.route('/get_audio', methods=['GET'])
def get_audio():
    return send_file("output.ogg", mimetype="audio/ogg")

if __name__ == '__main__':
    app.run(port=5000)
