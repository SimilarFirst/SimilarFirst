"""
Animation Engine for Akira Character
2D sprite-based animation system
"""

import tkinter as tk
from PIL import Image, ImageDraw, ImageTk
import threading
import time
import math
import random

class AnimationEngine:
    """2D Animation engine for Akira character"""
    
    def __init__(self, canvas):
        self.canvas = canvas
        self.current_emotion = "neutral"
        self.is_running = False
        self.animation_thread = None
        
        # Animation properties
        self.frame_count = 0
        self.animation_speed = 0.1  # seconds per frame
        
        # Character properties (Akira)
        self.character = {
            'x': 150,
            'y': 200,
            'width': 120,
            'height': 160,
            'hair_color': '#FF6B4A',  # Orange-red hair
            'skin_color': '#FFDBAA',  # Light skin
            'shirt_color': '#FFFFFF',  # White shirt
            'skirt_color': '#000000',  # Black skirt
            'tie_color': '#4A90E2',   # Blue tie
        }
        
        # Animation states
        self.animations = {
            'neutral': self.draw_neutral,
            'happy': self.draw_happy,
            'sad': self.draw_sad,
            'thinking': self.draw_thinking,
            'talking': self.draw_talking,
            'surprised': self.draw_surprised,
            'excited': self.draw_excited,
            'sleepy': self.draw_sleepy
        }
        
        # Eyes and mouth positions for different emotions
        self.expressions = {
            'neutral': {'eye_size': 8, 'mouth_curve': 0, 'eyebrow_y': -2},
            'happy': {'eye_size': 6, 'mouth_curve': 5, 'eyebrow_y': -1},
            'sad': {'eye_size': 6, 'mouth_curve': -5, 'eyebrow_y': -4},
            'thinking': {'eye_size': 7, 'mouth_curve': 1, 'eyebrow_y': -3},
            'talking': {'eye_size': 8, 'mouth_curve': 2, 'eyebrow_y': -1},
            'surprised': {'eye_size': 12, 'mouth_curve': 0, 'eyebrow_y': 2},
            'excited': {'eye_size': 10, 'mouth_curve': 8, 'eyebrow_y': 1},
            'sleepy': {'eye_size': 3, 'mouth_curve': -1, 'eyebrow_y': -5}
        }
    
    def start_animation_loop(self):
        """Start the animation loop"""
        if not self.is_running:
            self.is_running = True
            self.animation_thread = threading.Thread(target=self._animation_loop, daemon=True)
            self.animation_thread.start()
    
    def stop_animation_loop(self):
        """Stop the animation loop"""
        self.is_running = False
    
    def set_emotion(self, emotion):
        """Set character emotion"""
        if emotion in self.animations:
            self.current_emotion = emotion
    
    def _animation_loop(self):
        """Main animation loop"""
        while self.is_running:
            try:
                self.canvas.after(0, self._draw_frame)
                time.sleep(self.animation_speed)
                self.frame_count += 1
            except Exception as e:
                print(f"Animation error: {e}")
                time.sleep(0.1)
    
    def _draw_frame(self):
        """Draw current animation frame"""
        try:
            # Clear canvas
            self.canvas.delete("all")
            
            # Draw current animation
            if self.current_emotion in self.animations:
                self.animations[self.current_emotion]()
            else:
                self.draw_neutral()
                
        except Exception as e:
            print(f"Draw frame error: {e}")
    
    def draw_neutral(self):
        """Draw neutral expression"""
        self._draw_character_base()
        self._draw_expression('neutral')
    
    def draw_happy(self):
        """Draw happy expression with slight bounce"""
        bounce_offset = math.sin(self.frame_count * 0.3) * 2
        self._draw_character_base(y_offset=bounce_offset)
        self._draw_expression('happy')
        
        # Add sparkles around character
        for i in range(3):
            x = self.character['x'] + random.randint(-50, 50)
            y = self.character['y'] + random.randint(-50, 50)
            self.canvas.create_text(x, y, text="✨", font=("Arial", 12))
    
    def draw_sad(self):
        """Draw sad expression"""
        self._draw_character_base(y_offset=5)  # Slight droop
        self._draw_expression('sad')
        
        # Add tear drops
        tear_x = self.character['x'] - 15
        tear_y = self.character['y'] - 30
        self.canvas.create_oval(tear_x, tear_y, tear_x+4, tear_y+8, fill='lightblue', outline='blue')
    
    def draw_thinking(self):
        """Draw thinking expression with thought bubble"""
        self._draw_character_base()
        self._draw_expression('thinking')
        
        # Thought bubble
        bubble_x = self.character['x'] + 60
        bubble_y = self.character['y'] - 80
        self.canvas.create_oval(bubble_x, bubble_y, bubble_x+40, bubble_y+30, fill='white', outline='gray')
        self.canvas.create_text(bubble_x+20, bubble_y+15, text="?", font=("Arial", 16, "bold"))
        
        # Small thought bubbles
        for i, (dx, dy) in enumerate([(30, -20), (20, -10), (10, -5)]):
            size = 6 - i * 2
            x, y = self.character['x'] + dx, self.character['y'] + dy
            self.canvas.create_oval(x, y, x+size, y+size, fill='white', outline='gray')
    
    def draw_talking(self):
        """Draw talking expression with mouth animation"""
        mouth_animation = math.sin(self.frame_count * 0.8) * 2
        self._draw_character_base()
        self._draw_expression('talking', mouth_offset=mouth_animation)
        
        # Sound waves
        for i in range(3):
            radius = 30 + i * 15
            alpha = (self.frame_count * 0.5 + i * 0.5) % (2 * math.pi)
            wave_x = self.character['x'] + 50 + math.cos(alpha) * 10
            wave_y = self.character['y'] - 40 + math.sin(alpha) * 5
            self.canvas.create_text(wave_y, wave_x, text="~", font=("Arial", 8), fill='lightblue')
    
    def draw_surprised(self):
        """Draw surprised expression"""
        self._draw_character_base(y_offset=-3)  # Slight jump
        self._draw_expression('surprised')
        
        # Exclamation mark
        excl_x = self.character['x'] + 40
        excl_y = self.character['y'] - 60
        self.canvas.create_text(excl_x, excl_y, text="!", font=("Arial", 20, "bold"), fill='red')
    
    def draw_excited(self):
        """Draw excited expression with energetic movement"""
        shake_x = math.sin(self.frame_count * 0.8) * 2
        shake_y = math.cos(self.frame_count * 0.8) * 2
        self._draw_character_base(x_offset=shake_x, y_offset=shake_y)
        self._draw_expression('excited')
        
        # Energy sparkles
        for i in range(5):
            angle = (self.frame_count * 0.2 + i * 0.4) % (2 * math.pi)
            radius = 40 + math.sin(self.frame_count * 0.1) * 10
            spark_x = self.character['x'] + math.cos(angle) * radius
            spark_y = self.character['y'] + math.sin(angle) * radius
            self.canvas.create_text(spark_x, spark_y, text="⭐", font=("Arial", 10))
    
    def draw_sleepy(self):
        """Draw sleepy expression"""
        sway = math.sin(self.frame_count * 0.2) * 3
        self._draw_character_base(x_offset=sway, y_offset=2)
        self._draw_expression('sleepy')
        
        # Zzz above head
        for i, (dx, dy) in enumerate([(5, -80), (15, -90), (25, -100)]):
            x, y = self.character['x'] + dx, self.character['y'] + dy
            size = 10 + i * 2
            self.canvas.create_text(x, y, text="Z", font=("Arial", size), fill='gray')
    
    def _draw_character_base(self, x_offset=0, y_offset=0):
        """Draw the base character (Akira's body)"""
        x = self.character['x'] + x_offset
        y = self.character['y'] + y_offset
        
        # Head (circle)
        head_size = 40
        self.canvas.create_oval(
            x - head_size, y - 80,
            x + head_size, y - 20,
            fill=self.character['skin_color'],
            outline='black',
            width=2
        )
        
        # Hair (long and flowing)
        # Back hair
        hair_points = [
            x - 45, y - 85,  # Top left
            x + 45, y - 85,  # Top right
            x + 30, y + 20,  # Bottom right
            x - 30, y + 20   # Bottom left
        ]
        self.canvas.create_polygon(hair_points, fill=self.character['hair_color'], outline='darkred')
        
        # Front hair bangs
        for i in range(-2, 3):
            bang_x = x + i * 15
            bang_points = [
                bang_x - 8, y - 85,
                bang_x + 8, y - 85,
                bang_x, y - 65
            ]
            self.canvas.create_polygon(bang_points, fill=self.character['hair_color'], outline='darkred')
        
        # Body - White shirt
        self.canvas.create_rectangle(
            x - 30, y - 20,
            x + 30, y + 40,
            fill=self.character['shirt_color'],
            outline='black',
            width=2
        )
        
        # Blue tie with number 38
        tie_points = [x - 8, y - 15, x + 8, y - 15, x, y + 25]
        self.canvas.create_polygon(tie_points, fill=self.character['tie_color'], outline='darkblue')
        self.canvas.create_text(x, y + 5, text="38", font=("Arial", 8, "bold"), fill='yellow')
        
        # Black skirt
        skirt_points = [
            x - 35, y + 40,
            x + 35, y + 40,
            x + 40, y + 80,
            x - 40, y + 80
        ]
        self.canvas.create_polygon(skirt_points, fill=self.character['skirt_color'], outline='black')
        
        # Arms
        self.canvas.create_rectangle(x - 45, y - 10, x - 30, y + 30, fill=self.character['skin_color'], outline='black')
        self.canvas.create_rectangle(x + 30, y - 10, x + 45, y + 30, fill=self.character['skin_color'], outline='black')
        
        # Legs
        self.canvas.create_rectangle(x - 25, y + 80, x - 10, y + 120, fill=self.character['skin_color'], outline='black')
        self.canvas.create_rectangle(x + 10, y + 80, x + 25, y + 120, fill=self.character['skin_color'], outline='black')
        
        # Shoes
        self.canvas.create_oval(x - 30, y + 115, x - 5, y + 125, fill='black')
        self.canvas.create_oval(x + 5, y + 115, x + 30, y + 125, fill='black')
    
    def _draw_expression(self, emotion, mouth_offset=0):
        """Draw facial expression"""
        expr = self.expressions.get(emotion, self.expressions['neutral'])
        x = self.character['x']
        y = self.character['y']
        
        # Eyes
        eye_size = expr['eye_size']
        left_eye_x, right_eye_x = x - 15, x + 15
        eye_y = y - 50
        
        # Draw eyes based on emotion
        if emotion == 'sleepy':
            # Sleepy eyes (lines)
            self.canvas.create_line(left_eye_x - 5, eye_y, left_eye_x + 5, eye_y, width=3)
            self.canvas.create_line(right_eye_x - 5, eye_y, right_eye_x + 5, eye_y, width=3)
        else:
            # Normal eyes (ovals)
            self.canvas.create_oval(
                left_eye_x - eye_size//2, eye_y - eye_size//2,
                left_eye_x + eye_size//2, eye_y + eye_size//2,
                fill='white', outline='black', width=2
            )
            self.canvas.create_oval(
                right_eye_x - eye_size//2, eye_y - eye_size//2,
                right_eye_x + eye_size//2, eye_y + eye_size//2,
                fill='white', outline='black', width=2
            )
            
            # Pupils
            pupil_size = 3
            self.canvas.create_oval(
                left_eye_x - pupil_size, eye_y - pupil_size,
                left_eye_x + pupil_size, eye_y + pupil_size,
                fill='black'
            )
            self.canvas.create_oval(
                right_eye_x - pupil_size, eye_y - pupil_size,
                right_eye_x + pupil_size, eye_y + pupil_size,
                fill='black'
            )
        
        # Eyebrows
        eyebrow_y = eye_y + expr['eyebrow_y'] - 10
        self.canvas.create_line(left_eye_x - 8, eyebrow_y, left_eye_x + 8, eyebrow_y, width=3)
        self.canvas.create_line(right_eye_x - 8, eyebrow_y, right_eye_x + 8, eyebrow_y, width=3)
        
        # Mouth
        mouth_y = y - 30
        mouth_curve = expr['mouth_curve'] + mouth_offset
        
        if mouth_curve > 3:
            # Happy mouth (smile)
            self.canvas.create_arc(
                x - 15, mouth_y - 5,
                x + 15, mouth_y + 10,
                start=0, extent=180,
                outline='black', width=2, style='arc'
            )
        elif mouth_curve < -3:
            # Sad mouth (frown)
            self.canvas.create_arc(
                x - 15, mouth_y - 10,
                x + 15, mouth_y + 5,
                start=180, extent=180,
                outline='black', width=2, style='arc'
            )
        else:
            # Neutral/small mouth
            self.canvas.create_line(x - 5, mouth_y, x + 5, mouth_y, width=2)
        
        # Nose (small dot)
        self.canvas.create_oval(x - 1, y - 40, x + 1, y - 38, fill='black')