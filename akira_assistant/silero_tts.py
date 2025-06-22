"""
Silero TTS Engine for Akira Assistant
Russian text-to-speech synthesis
"""

import torch
import torchaudio
import numpy as np
import tempfile
import os
from typing import Optional
import threading

class SileroTTSEngine:
    """Silero TTS engine for Russian speech synthesis"""
    
    def __init__(self):
        self.device = torch.device('cpu')
        self.model = None
        self.symbols = None
        self.sample_rate = None
        self.apply_tts = None
        self.speaker = 'baya'  # Default Russian female speaker
        self.is_loaded = False
        
        self.load_model()
    
    def load_model(self):
        """Load Silero TTS model"""
        try:
            # Download and load Russian TTS model
            model, symbols, sample_rate, example_text, apply_tts = torch.hub.load(
                repo_or_dir='snakers4/silero-models',
                model='silero_tts',
                language='ru',
                speaker='ru_v4'
            )
            
            self.model = model
            self.symbols = symbols
            self.sample_rate = sample_rate
            self.apply_tts = apply_tts
            self.is_loaded = True
            
            print("Silero TTS model loaded successfully")
            
        except Exception as e:
            print(f"Failed to load Silero TTS model: {e}")
            self.is_loaded = False
    
    def synthesize(self, text: str, speaker: Optional[str] = None) -> Optional[np.ndarray]:
        """
        Synthesize speech from text
        
        Args:
            text: Text to synthesize
            speaker: Speaker name (optional)
            
        Returns:
            Audio data as numpy array or None if failed
        """
        if not self.is_loaded:
            print("TTS model not loaded")
            return None
            
        if not text.strip():
            return None
        
        try:
            # Use specified speaker or default
            current_speaker = speaker or self.speaker
            
            # Generate audio
            audio = self.apply_tts(
                texts=[text],
                model=self.model,
                sample_rate=self.sample_rate,
                symbols=self.symbols,
                device=self.device
            )
            
            # Convert to numpy array
            audio_numpy = audio[0].cpu().numpy()
            return audio_numpy
            
        except Exception as e:
            print(f"TTS synthesis failed: {e}")
            return None
    
    def save_audio(self, audio_data: np.ndarray, filename: str) -> bool:
        """Save audio data to WAV file"""
        try:
            # Convert numpy array to tensor
            audio_tensor = torch.from_numpy(audio_data).unsqueeze(0)
            
            # Save as WAV file
            torchaudio.save(filename, audio_tensor, self.sample_rate)
            return True
            
        except Exception as e:
            print(f"Failed to save audio: {e}")
            return False
    
    def create_temp_audio(self, text: str) -> Optional[str]:
        """Create temporary audio file from text"""
        audio_data = self.synthesize(text)
        if audio_data is None:
            return None
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        temp_filename = temp_file.name
        temp_file.close()
        
        # Save audio
        if self.save_audio(audio_data, temp_filename):
            return temp_filename
        return None
    
    def get_available_speakers(self) -> list:
        """Get list of available Russian speakers"""
        return ['baya', 'kseniya', 'xenia', 'aidar', 'eugene']


class TTSWorker(threading.Thread):
    """Worker thread for TTS processing"""
    
    def __init__(self, tts_engine: SileroTTSEngine, text: str, speaker: str = None, callback=None, error_callback=None):
        super().__init__(daemon=True)
        self.tts_engine = tts_engine
        self.text = text
        self.speaker = speaker
        self.callback = callback
        self.error_callback = error_callback
    
    def run(self):
        """Run TTS processing in background thread"""
        try:
            audio_file = self.tts_engine.create_temp_audio(self.text)
            if audio_file and self.callback:
                self.callback(audio_file)
            elif not audio_file and self.error_callback:
                self.error_callback("Failed to generate audio")
        except Exception as e:
            if self.error_callback:
                self.error_callback(str(e))