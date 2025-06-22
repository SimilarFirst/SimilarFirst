#!/usr/bin/env python3
"""
Akira - AI Voice Assistant with Animated Anime Character
Web interface version for container environment
"""

from flask import Flask, render_template, request, jsonify, send_file
import threading
import json
import os
import tempfile
from deepseek_client import DeepSeekClient
from silero_tts import SileroTTSEngine

app = Flask(__name__)

# Global components
deepseek_client = None
tts_engine = None
conversation_history = []

def initialize_components():
    """Initialize AI and TTS components"""
    global deepseek_client, tts_engine
    
    try:
        print("🔄 Initializing DeepSeek client...")
        deepseek_client = DeepSeekClient()
        
        if deepseek_client.test_connection():
            print("✅ DeepSeek connected successfully")
        else:
            print("❌ DeepSeek connection failed")
            return False
        
        print("🔄 Loading Silero TTS...")
        tts_engine = SileroTTSEngine()
        
        if tts_engine.is_loaded:
            print("✅ TTS engine loaded")
        else:
            print("⚠️ TTS engine failed to load")
        
        print("🎉 Akira is ready!")
        return True
        
    except Exception as e:
        print(f"❌ Initialization error: {e}")
        return False

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat with AI"""
    global conversation_history
    
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message or not deepseek_client:
            return jsonify({'error': 'Invalid message or AI not ready'}), 400
        
        # Get AI response
        result = deepseek_client.chat_completion(message, conversation_history)
        
        if result["status"] == "success":
            response = result["response"]
            emotion = deepseek_client.detect_emotion(response)
            
            # Update conversation history
            conversation_history.append({"role": "user", "content": message})
            conversation_history.append({"role": "assistant", "content": response})
            
            return jsonify({
                'response': response,
                'emotion': emotion,
                'status': 'success'
            })
        else:
            return jsonify({
                'error': result['response'],
                'status': 'error'
            }), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/speak', methods=['POST'])
def speak():
    """Generate speech from text"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text or not tts_engine or not tts_engine.is_loaded:
            return jsonify({'error': 'Invalid text or TTS not ready'}), 400
        
        # Generate audio
        audio_file = tts_engine.create_temp_audio(text)
        if audio_file:
            return send_file(audio_file, as_attachment=True, mimetype='audio/wav')
        else:
            return jsonify({'error': 'Failed to generate audio'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clear', methods=['POST'])
def clear_history():
    """Clear conversation history"""
    global conversation_history
    conversation_history.clear()
    return jsonify({'status': 'cleared'})

@app.route('/api/status')
def status():
    """Get system status"""
    return jsonify({
        'deepseek_ready': deepseek_client is not None,
        'tts_ready': tts_engine is not None and tts_engine.is_loaded,
        'conversation_length': len(conversation_history)
    })

if __name__ == '__main__':
    print("🚀 Starting Akira Assistant...")
    
    # Initialize components in background
    init_thread = threading.Thread(target=initialize_components)
    init_thread.start()
    
    # Start Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)