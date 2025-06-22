"""
Akira Assistant Main UI
Tkinter-based user interface with animated character
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import os
from PIL import Image, ImageTk
from deepseek_client import DeepSeekClient
from silero_tts import SileroTTSEngine
from animation_engine import AnimationEngine
import pygame

class AkiraMainWindow:
    """Main window for Akira Assistant"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Akira - AI Assistant")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize components
        self.deepseek_client = None
        self.tts_engine = None
        self.animation_engine = None
        self.conversation_history = []
        self.current_emotion = "neutral"
        
        # Audio player (pygame mixer)
        pygame.mixer.init()
        
        # Setup UI
        self.setup_ui()
        self.setup_components()
        
        # Make window draggable and resizable
        self.setup_window_controls()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Character area (left side)
        self.character_frame = ttk.LabelFrame(main_frame, text="Акира", padding="10")
        self.character_frame.grid(row=0, column=0, rowspan=3, sticky=(tk.W, tk.N, tk.S), padx=(0, 10))
        
        # Character canvas for animation
        self.character_canvas = tk.Canvas(
            self.character_frame, 
            width=300, 
            height=400, 
            bg='white',
            relief='sunken',
            bd=2
        )
        self.character_canvas.pack(pady=10)
        
        # Character controls
        controls_frame = ttk.Frame(self.character_frame)
        controls_frame.pack(fill='x', pady=5)
        
        ttk.Button(controls_frame, text="🔄", command=self.reset_character, width=3).pack(side='left')
        ttk.Button(controls_frame, text="😊", command=lambda: self.set_emotion("happy"), width=3).pack(side='left', padx=2)
        ttk.Button(controls_frame, text="😢", command=lambda: self.set_emotion("sad"), width=3).pack(side='left', padx=2)
        ttk.Button(controls_frame, text="🤔", command=lambda: self.set_emotion("thinking"), width=3).pack(side='left', padx=2)
        
        # Chat area (right side)
        chat_frame = ttk.LabelFrame(main_frame, text="Чат с Акирой", padding="10")
        chat_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        chat_frame.columnconfigure(0, weight=1)
        chat_frame.rowconfigure(0, weight=1)
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            width=50,
            height=20,
            font=('Arial', 10),
            state='disabled'
        )
        self.chat_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Input area
        input_frame = ttk.Frame(chat_frame)
        input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        input_frame.columnconfigure(0, weight=1)
        
        self.text_input = tk.Text(input_frame, height=3, font=('Arial', 10))
        self.text_input.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        self.text_input.bind('<Return>', self.on_enter_key)
        self.text_input.bind('<Shift-Return>', self.on_shift_enter)
        
        # Send button
        self.send_button = ttk.Button(input_frame, text="Отправить", command=self.send_message)
        self.send_button.grid(row=0, column=1, sticky=(tk.N))
        
        # Control buttons (bottom)
        controls_main = ttk.Frame(main_frame)
        controls_main.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(controls_main, text="🗑️ Очистить историю", command=self.clear_history).pack(side='left')
        ttk.Button(controls_main, text="📝 Заметки", command=self.open_notes).pack(side='left', padx=5)
        ttk.Button(controls_main, text="⏰ Напоминания", command=self.open_reminders).pack(side='left', padx=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="🔄 Инициализация...")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief='sunken')
        status_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def setup_components(self):
        """Initialize AI and TTS components"""
        def init_components():
            try:
                # Initialize DeepSeek client
                self.status_var.set("🔄 Подключение к DeepSeek...")
                self.deepseek_client = DeepSeekClient()
                
                # Test connection
                if self.deepseek_client.test_connection():
                    self.status_var.set("✅ DeepSeek подключен")
                else:
                    self.status_var.set("❌ Ошибка подключения к DeepSeek")
                    return
                
                # Initialize TTS
                self.status_var.set("🔄 Загрузка голосового синтеза...")
                self.tts_engine = SileroTTSEngine()
                
                if self.tts_engine.is_loaded:
                    self.status_var.set("✅ Голосовой синтез готов")
                else:
                    self.status_var.set("⚠️ TTS недоступен, только текст")
                
                # Initialize animation engine
                self.animation_engine = AnimationEngine(self.character_canvas)
                self.animation_engine.start_animation_loop()
                
                self.status_var.set("🎉 Акира готова к работе!")
                self.add_chat_message("system", "Привет! Я Акира, твоя голосовая помощница. Как дела?")
                
            except Exception as e:
                self.status_var.set(f"❌ Ошибка инициализации: {str(e)}")
                messagebox.showerror("Ошибка", f"Не удалось инициализировать компоненты:\n{str(e)}")
        
        # Run initialization in background thread
        threading.Thread(target=init_components, daemon=True).start()
    
    def setup_window_controls(self):
        """Setup window dragging and resizing"""
        self.root.attributes('-topmost', True)  # Keep on top
        
        # Variables for dragging
        self._drag_start_x = 0
        self._drag_start_y = 0
        
        # Bind events for dragging
        self.root.bind('<Button-1>', self.start_drag)
        self.root.bind('<B1-Motion>', self.on_drag)
        
        # Add transparency control
        self.root.attributes('-alpha', 0.95)
    
    def start_drag(self, event):
        """Start dragging window"""
        self._drag_start_x = event.x
        self._drag_start_y = event.y
    
    def on_drag(self, event):
        """Handle window dragging"""
        x = self.root.winfo_x() + event.x - self._drag_start_x
        y = self.root.winfo_y() + event.y - self._drag_start_y
        self.root.geometry(f'+{x}+{y}')
    
    def on_enter_key(self, event):
        """Handle Enter key in text input"""
        if event.state & 0x1:  # Shift key
            return  # Allow newline
        else:
            self.send_message()
            return 'break'  # Prevent default behavior
    
    def on_shift_enter(self, event):
        """Handle Shift+Enter for newline"""
        return  # Allow default behavior
    
    def send_message(self):
        """Send message to AI"""
        message = self.text_input.get('1.0', tk.END).strip()
        if not message or not self.deepseek_client:
            return
        
        # Clear input
        self.text_input.delete('1.0', tk.END)
        
        # Add user message to chat
        self.add_chat_message("user", message)
        
        # Set thinking animation
        self.set_emotion("thinking")
        self.status_var.set("🤔 Акира думает...")
        
        # Process in background thread
        def process_message():
            try:
                # Get AI response
                result = self.deepseek_client.chat_completion(message, self.conversation_history)
                
                if result["status"] == "success":
                    response = result["response"]
                    
                    # Detect emotion from response
                    emotion = self.deepseek_client.detect_emotion(response)
                    self.set_emotion(emotion)
                    
                    # Add to chat
                    self.add_chat_message("assistant", response)
                    
                    # Update conversation history
                    self.conversation_history.append({"role": "user", "content": message})
                    self.conversation_history.append({"role": "assistant", "content": response})
                    
                    # Synthesize speech if available
                    if self.tts_engine and self.tts_engine.is_loaded:
                        self.speak_text(response)
                    
                    self.status_var.set("💬 Ответ получен")
                else:
                    self.add_chat_message("system", f"Ошибка: {result['response']}")
                    self.status_var.set("❌ Ошибка получения ответа")
                    
            except Exception as e:
                self.add_chat_message("system", f"Произошла ошибка: {str(e)}")
                self.status_var.set("❌ Ошибка обработки")
        
        threading.Thread(target=process_message, daemon=True).start()
    
    def add_chat_message(self, role, message):
        """Add message to chat display"""
        self.chat_display.config(state='normal')
        
        # Add timestamp and role
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M")
        
        if role == "user":
            prefix = f"[{timestamp}] Вы: "
            self.chat_display.insert(tk.END, prefix, 'user')
        elif role == "assistant":
            prefix = f"[{timestamp}] Акира: "
            self.chat_display.insert(tk.END, prefix, 'assistant')
        else:
            prefix = f"[{timestamp}] Система: "
            self.chat_display.insert(tk.END, prefix, 'system')
        
        self.chat_display.insert(tk.END, message + "\n\n")
        
        # Configure tags for styling
        self.chat_display.tag_config('user', foreground='blue')
        self.chat_display.tag_config('assistant', foreground='green')
        self.chat_display.tag_config('system', foreground='red')
        
        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)
    
    def speak_text(self, text):
        """Speak text using TTS"""
        def tts_worker():
            try:
                self.status_var.set("🔊 Акира говорит...")
                
                # Generate audio
                audio_file = self.tts_engine.create_temp_audio(text)
                if audio_file:
                    # Play audio
                    pygame.mixer.music.load(audio_file)
                    pygame.mixer.music.play()
                    
                    # Wait for playback to finish
                    while pygame.mixer.music.get_busy():
                        pygame.time.wait(100)
                    
                    # Clean up temp file
                    try:
                        os.unlink(audio_file)
                    except:
                        pass
                
                self.status_var.set("💬 Готова к разговору")
                self.set_emotion("neutral")
                
            except Exception as e:
                print(f"TTS Error: {e}")
                self.status_var.set("⚠️ Ошибка воспроизведения")
        
        threading.Thread(target=tts_worker, daemon=True).start()
    
    def set_emotion(self, emotion):
        """Set character emotion for animation"""
        self.current_emotion = emotion
        if self.animation_engine:
            self.animation_engine.set_emotion(emotion)
    
    def reset_character(self):
        """Reset character to neutral state"""
        self.set_emotion("neutral")
    
    def clear_history(self):
        """Clear conversation history"""
        if messagebox.askyesno("Подтверждение", "Очистить всю историю разговора?"):
            self.conversation_history.clear()
            self.chat_display.config(state='normal')
            self.chat_display.delete('1.0', tk.END)
            self.chat_display.config(state='disabled')
            self.add_chat_message("system", "История очищена")
    
    def open_notes(self):
        """Open notes window"""
        messagebox.showinfo("Заметки", "Функция заметок будет добавлена в следующей версии")
    
    def open_reminders(self):
        """Open reminders window"""
        messagebox.showinfo("Напоминания", "Функция напоминаний будет добавлена в следующей версии")