"""
DeepSeek R1 API Client for Akira Assistant
"""

import os
import requests
import json
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

class DeepSeekClient:
    """Client for DeepSeek R1 API integration"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DeepSeek API key not found. Please set DEEPSEEK_API_KEY environment variable.")
        
        self.base_url = "https://api.deepseek.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # System prompt for Akira personality
        self.system_prompt = """Ты - Акира, умная и дружелюбная голосовая помощница в виде аниме-девушки. 
        Твои характеристики:
        - Ты говоришь на русском языке
        - Ты веселая, но профессиональная
        - Ты помогаешь с различными задачами: заметки, напоминания, поиск информации
        - Ты можешь управлять приложениями и работать с браузером
        - Твои ответы должны быть краткими но информативными
        - Ты проявляешь эмоции через свои ответы (радость, задумчивость, удивление)
        
        Отвечай естественно и дружелюбно, как настоящий помощник."""
    
    def chat_completion(self, message: str, conversation_history: List[Dict] = None) -> Dict:
        """
        Send a chat completion request to DeepSeek R1
        
        Args:
            message: User message
            conversation_history: Previous conversation messages
            
        Returns:
            Dict with response and metadata
        """
        try:
            # Prepare messages
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Add conversation history
            if conversation_history:
                messages.extend(conversation_history)
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # API request payload
            payload = {
                "model": "deepseek-reasoner",  # DeepSeek R1 model
                "messages": messages,
                "max_tokens": 1000,
                "temperature": 0.7,
                "stream": False
            }
            
            # Make API request
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Extract response
            ai_response = result["choices"][0]["message"]["content"]
            
            return {
                "response": ai_response,
                "status": "success",
                "usage": result.get("usage", {}),
                "model": result.get("model", "deepseek-reasoner")
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "response": f"Извините, произошла ошибка подключения: {str(e)}",
                "status": "error",
                "error_type": "connection_error"
            }
        except Exception as e:
            return {
                "response": f"Произошла неожиданная ошибка: {str(e)}",
                "status": "error", 
                "error_type": "general_error"
            }
    
    def detect_emotion(self, text: str) -> str:
        """
        Detect emotion from AI response for animation selection
        
        Returns:
            Emotion string: happy, sad, thinking, neutral, surprised
        """
        text_lower = text.lower()
        
        # Happy indicators
        if any(word in text_lower for word in ["отлично", "здорово", "замечательно", "прекрасно", "хорошо", "😊", "рад"]):
            return "happy"
        
        # Sad indicators  
        if any(word in text_lower for word in ["сожалению", "грустно", "плохо", "ошибка", "проблема", "😢"]):
            return "sad"
        
        # Thinking indicators
        if any(word in text_lower for word in ["подумаю", "размышляю", "анализирую", "рассмотрю", "хм", "интересно"]):
            return "thinking"
        
        # Surprised indicators
        if any(word in text_lower for word in ["удивительно", "невероятно", "вау", "ого", "неожиданно"]):
            return "surprised"
        
        return "neutral"
    
    def test_connection(self) -> bool:
        """Test API connection"""
        try:
            # Try a simple API call
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json={
                    "model": "deepseek-reasoner",
                    "messages": [{"role": "user", "content": "Hi"}],
                    "max_tokens": 10
                },
                timeout=10
            )
            
            print(f"Test response status: {response.status_code}")
            print(f"Test response: {response.text}")
            
            if response.status_code == 200:
                return True
            elif "insufficient balance" in response.text.lower():
                print("❌ API key has insufficient balance")
                return False
            else:
                print(f"❌ API test failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False