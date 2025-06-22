"""
DeepSeek/LLM Client for Akira Assistant using EmergentIntegrations
"""

import os
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Try emergentintegrations first, fall back to direct API calls
try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    EMERGENT_AVAILABLE = True
    print("✅ EmergentIntegrations available")
except ImportError:
    EMERGENT_AVAILABLE = False
    print("⚠️ EmergentIntegrations not available, using direct API")
    import requests
    import json

load_dotenv()

class DeepSeekClient:
    """Client for LLM integration with multiple fallback options"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        
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
        
        # Initialize LLM client
        self.llm_client = None
        self.session_id = "akira_session_001"
        self.mode = "mock"  # mock, emergent, direct
        
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the appropriate LLM client"""
        
        if EMERGENT_AVAILABLE and self.api_key:
            try:
                # Try EmergentIntegrations with multiple providers
                print("🔄 Trying EmergentIntegrations...")
                
                # Try different providers in order of preference
                providers_to_try = [
                    ("gemini", "gemini-2.0-flash"),
                    ("openai", "gpt-4o-mini"), 
                    ("anthropic", "claude-3-5-haiku-20241022")
                ]
                
                for provider, model in providers_to_try:
                    try:
                        print(f"   Trying {provider} with {model}...")
                        
                        self.llm_client = LlmChat(
                            api_key=self.api_key,
                            session_id=self.session_id,
                            system_message=self.system_prompt
                        ).with_model(provider, model)
                        
                        # Test the connection
                        test_msg = UserMessage(text="Привет!")
                        response = self.llm_client.send_message(test_msg)
                        
                        if response and len(response) > 0:
                            self.mode = "emergent"
                            print(f"✅ Connected using {provider} - {model}")
                            return
                            
                    except Exception as e:
                        print(f"   Failed {provider}: {e}")
                        continue
                        
            except Exception as e:
                print(f"⚠️ EmergentIntegrations failed: {e}")
        
        # Try direct DeepSeek API
        if self.api_key:
            try:
                print("🔄 Trying direct DeepSeek API...")
                if self._test_deepseek_direct():
                    self.mode = "direct"
                    print("✅ Connected to DeepSeek directly")
                    return
            except Exception as e:
                print(f"⚠️ Direct DeepSeek failed: {e}")
        
        # Fall back to mock mode
        print("⚠️ Falling back to mock mode")
        self.mode = "mock"
    
    def _test_deepseek_direct(self) -> bool:
        """Test direct DeepSeek API connection"""
        if not self.api_key:
            return False
            
        try:
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-reasoner",
                    "messages": [{"role": "user", "content": "Hi"}],
                    "max_tokens": 10
                },
                timeout=10
            )
            
            return response.status_code == 200
        except:
            return False
    
    def chat_completion(self, message: str, conversation_history: List[Dict] = None) -> Dict:
        """
        Send a chat completion request
        
        Args:
            message: User message
            conversation_history: Previous conversation messages
            
        Returns:
            Dict with response and metadata
        """
        
        if self.mode == "emergent" and self.llm_client:
            return self._chat_emergent(message)
        elif self.mode == "direct":
            return self._chat_direct(message, conversation_history)
        else:
            return self._chat_mock(message)
    
    def _chat_emergent(self, message: str) -> Dict:
        """Chat using EmergentIntegrations"""
        try:
            user_message = UserMessage(text=message)
            response = self.llm_client.send_message(user_message)
            
            return {
                "response": response,
                "status": "success",
                "model": "emergent_llm"
            }
        except Exception as e:
            return {
                "response": f"Извините, произошла ошибка: {str(e)}",
                "status": "error",
                "error_type": "emergent_error"
            }
    
    def _chat_direct(self, message: str, conversation_history: List[Dict] = None) -> Dict:
        """Chat using direct DeepSeek API"""
        try:
            messages = [{"role": "system", "content": self.system_prompt}]
            
            if conversation_history:
                messages.extend(conversation_history)
            
            messages.append({"role": "user", "content": message})
            
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-reasoner",
                    "messages": messages,
                    "max_tokens": 1000,
                    "temperature": 0.7
                },
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            ai_response = result["choices"][0]["message"]["content"]
            
            return {
                "response": ai_response,
                "status": "success",
                "usage": result.get("usage", {}),
                "model": "deepseek-reasoner"
            }
            
        except Exception as e:
            return {
                "response": f"Извините, произошла ошибка: {str(e)}",
                "status": "error",
                "error_type": "direct_error"
            }
    
    def _chat_mock(self, message: str) -> Dict:
        """Mock chat responses for demonstration"""
        
        mock_responses = {
            "привет": "Привет! Я Акира, твоя голосовая помощница! Как дела? 😊",
            "как дела": "У меня всё отлично! Готова помочь тебе с любыми задачами. Что тебя интересует?",
            "что ты умеешь": "Я могу помочь с заметками, напоминаниями, поиском информации, управлением приложениями и многим другим! Спроси меня о чём угодно!",
            "расскажи о себе": "Я Акира - твоя умная помощница! У меня рыжие волосы, я ношу белую рубашку, чёрную юбку и синий галстук с числом 38. Люблю помогать и изучать новое! 🎀",
            "спасибо": "Пожалуйста! Всегда рада помочь! 😊",
            "пока": "До свидания! Было приятно пообщаться! Обращайся, если что-то понадобится! 👋"
        }
        
        message_lower = message.lower().strip()
        
        # Check for exact matches first
        for key, response in mock_responses.items():
            if key in message_lower:
                return {
                    "response": response,
                    "status": "success",
                    "model": "mock_akira"
                }
        
        # Default responses based on message type
        if "?" in message:
            response = "Это очень интересный вопрос! К сожалению, сейчас я работаю в демо-режиме. Для полноценной работы нужен рабочий API ключ с балансом. Но я всё равно рада пообщаться! 🤔"
        elif any(word in message_lower for word in ["помоги", "сделай", "создай", "найди"]):
            response = "Конечно, я бы с радостью помогла! В демо-режиме мои возможности ограничены, но когда появится рабочий API ключ, смогу делать гораздо больше! 💪"
        elif any(word in message_lower for word in ["грустно", "плохо", "проблема"]):
            response = "Не расстраивайся! Всё обязательно наладится. Я здесь, чтобы поддержать тебя! 🤗"
        elif any(word in message_lower for word in ["здорово", "отлично", "классно"]):
            response = "Как же здорово! Я очень рада за тебя! 🎉"
        else:
            response = f"Понимаю, ты говоришь про '{message}'. В демо-режиме я могу только поддержать беседу. Для полной функциональности нужен рабочий API ключ! 😊"
        
        return {
            "response": response,
            "status": "success",
            "model": "mock_akira"
        }
    
    def detect_emotion(self, text: str) -> str:
        """
        Detect emotion from AI response for animation selection
        
        Returns:
            Emotion string: happy, sad, thinking, neutral, surprised
        """
        text_lower = text.lower()
        
        # Happy indicators
        if any(word in text_lower for word in ["отлично", "здорово", "замечательно", "прекрасно", "хорошо", "😊", "рад", "🎉", "классно"]):
            return "happy"
        
        # Sad indicators  
        if any(word in text_lower for word in ["сожалению", "грустно", "плохо", "ошибка", "проблема", "😢", "извините"]):
            return "sad"
        
        # Thinking indicators
        if any(word in text_lower for word in ["подумаю", "размышляю", "анализирую", "рассмотрю", "хм", "интересно", "🤔", "демо-режим"]):
            return "thinking"
        
        # Surprised indicators
        if any(word in text_lower for word in ["удивительно", "невероятно", "вау", "ого", "неожиданно"]):
            return "surprised"
        
        return "neutral"
    
    def test_connection(self) -> bool:
        """Test connection"""
        if self.mode == "mock":
            print("⚠️ Running in mock mode - no real API connection")
            return True
        
        try:
            result = self.chat_completion("Hi")
            return result["status"] == "success"
        except:
            return False
    
    def get_status(self) -> str:
        """Get current client status"""
        if self.mode == "emergent":
            return "🌟 Connected via EmergentIntegrations"
        elif self.mode == "direct":
            return "🔗 Connected directly to DeepSeek"
        else:
            return "🎭 Demo mode (no API key or insufficient balance)"