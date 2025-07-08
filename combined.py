import cv2
import numpy as np
import time
import base64
import requests
import json
from io import BytesIO
from PIL import Image
import os 
from dotenv import load_dotenv

import speech_recognition as sr
import pyaudio
import sys

import torch
import pyttsx3
import gradio as gr


load_dotenv()
device = "cuda" if torch.cuda.is_available() else "cpu"
class GeminiVisionDetector:
    def __init__(self, api_key):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
        
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

    def listen_once(self):
        """Listen for a single phrase and convert to text"""  # Method docstring explaining its purpose
        print("Say something...")  # Prompt user to speak
        
        try:  # Start error handling block
            with self.microphone as source:  # Open microphone as audio source
                audio = self.recognizer.listen(source, timeout=10)  # Listen for audio input with 10 second timeout
            
            print("Processing...")  # Indicate that speech is being processed
            text = self.recognizer.recognize_google(audio)  # Convert audio to text using Google's API
            print(f"You said: {text}")  # Display the recognized text
            return text  # Return the converted text
            
        except sr.UnknownValueError:
            print("Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"Error with speech recognition service: {e}")
            return None
        except sr.WaitTimeoutError:
            print("No speech detected within timeout")
            return None


    def encode_image_to_base64(self, frame):
        """Convert OpenCV frame to base64 string for API"""
        # Convert BGR to RGB (OpenCV uses BGR, PIL uses RGB)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Convert to PIL Image
        pil_image = Image.fromarray(rgb_frame)
        
        # Convert to base64
        buffer = BytesIO()
        pil_image.save(buffer, format="JPEG", quality=85)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return image_base64
    
    def query_gemini_with_image(self, frame, query):
        """Send frame and query to Gemini API"""
        try:
            # Encode image
            image_base64 = self.encode_image_to_base64(frame)
            
            # Prepare the request payload
            payload = {
                "contents": [{
                    "parts": [
                        {"text": query},
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": image_base64
                            }
                        }
                    ]
                }]
            }
            
            # Make API request
            headers = {
                'Content-Type': 'application/json',
            }
            
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    return result['candidates'][0]['content']['parts'][0]['text']
                else:
                    return "No response from Gemini"
            else:
                return f"API Error: {response.status_code} here- {response.text}"
                
        except Exception as e:
            return f"Error: {str(e)}"

def run_gemini_vision_detection():
    # Initialize Gemini detector with your API key
    API_KEY = os.getenv('GEMINI_API_KEY')  # Replace with your actual API key
    detector = GeminiVisionDetector(API_KEY)
    
    # Open the video capture
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open video source.")
        return
    
    # Set up variables
    prev_time = 0
    last_query_time = 0
    query_interval = 3  # Send query every 3 seconds
    current_response = "Press 'q' to query, 'c' to change query, 'x' to exit"
    
    # Default query - you can change this
    current_query = detector.listen_once()
    
    # Predefined queries you can cycle through
    # queries = [
    #     "What objects do you see in this image? Describe them briefly.",
    #     "Count the number of people in this image.",
    #     "Describe the colors and lighting in this scene.",
    #     "What activities or actions are happening in this image?",
    #     "Is this an indoor or outdoor scene? Describe the environment.",
    #     "What safety concerns, if any, do you notice in this image?"
    # ]
    query_index = 0
    
    print("Controls:")
    print("'q' - Send current frame to Gemini with query")
    print("'c' - Change to next predefined query")
    print("'a' - Toggle auto-query mode (every 3 seconds)")
    print("'x' - Exit")
    print(f"Current query: {current_query}")
    
    auto_query = False
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture image")
            break
        
        # Calculate FPS
        new_time = time.time()
        fps = 1 / (new_time - prev_time) if (new_time - prev_time) > 0 else 0
        prev_time = new_time
        
        # # Create a copy for display
        display_frame = frame.copy()
        
        # # Add FPS information
        # cv2.putText(display_frame, f'FPS: {int(fps)}', (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # # Add auto-query status
        # status_text = "AUTO-QUERY: ON" if auto_query else "AUTO-QUERY: OFF"
        # cv2.putText(display_frame, status_text, (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        # # Add current query (truncated if too long)
        # query_display = current_query[:60] + "..." if len(current_query) > 60 else current_query
        # #cv2.putText(display_frame, f'Query: {query_display}', (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        if auto_query and (new_time - last_query_time) > query_interval:
            print("Auto-querying Gemini...")
            # current_response = "Querying Gemini..."
            cv2.imshow("Gemini Vision Detection", display_frame)
            cv2.waitKey(1)
            
            response = detector.query_gemini_with_image(frame, current_query)
            current_response = response
            last_query_time = new_time
            print(f"Gemini Response: {response}")
            generare_audio(response)
        # Display the frame
        cv2.imshow("Gemini Vision Detection", display_frame)
        
        # Handle key presses
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('x'):
            break
        elif key == ord('q'):
            print("Querying Gemini...")
            # current_response = "Querying Gemini..."
            cv2.imshow("Gemini Vision Detection", display_frame)
            cv2.waitKey(1)
            
            response = detector.query_gemini_with_image(frame, current_query)
            # current_response = response
            print(f"Gemini Response: {response}")
            generare_audio(response)
        elif key == ord('c'):
            query_index = (query_index + 1) % len(queries)
            current_query = queries[query_index]
            print(f"Changed query to: {current_query}")
            
        elif key == ord('a'):
            auto_query = not auto_query
            status = "enabled" if auto_query else "disabled"
            print(f"Auto-query {status}")
            if auto_query:
                last_query_time = new_time
    
    cap.release()
    cv2.destroyAllWindows()







def generate_audio(text):
    # Initialize pyttsx3 engine
    engine = pyttsx3.init()
    
    # Set properties (optional)
    engine.setProperty('rate', 150)    # Speed of speech
    engine.setProperty('volume', 0.9)  # Volume level (0.0 to 1.0)
    
    # Save to file
    engine.save_to_file(text, "output.wav")
    engine.runAndWait()
    
    return "outputs/output.wav"





def detect_on_image_with_gemini(image_path, query=None):
    """Analyze a single image with Gemini"""
    API_KEY = os.getenv('GEMINI_API_KEY')  # Replace with your actual API key
    detector = GeminiVisionDetector(API_KEY)
    
    # Read the image
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not read image from {image_path}")
        return
    
    # Default query if none provided
    
    query = detector.listen_once() 
    
    print(f"Analyzing image with query: {query}")
    print("Please wait...")
    
    # Query Gemini
    response = detector.query_gemini_with_image(img, query)
    
    print(f"\nGemini Response:\n{response}")
    generate_audio(response)
    # Display the image
    cv2.imshow("Image Analysis", img)
    print("\nPress any key to close the image window...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Choose mode
    print("Choose mode:")
    print("1. Real-time webcam with Gemini Vision")
    print("2. Analyze single image with Gemini")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        run_gemini_vision_detection()
    elif choice == "2":
        image_path = "D:/jetson/Vocify/img1.jpg"
        if not image_path:
            image_path = "img2.png"
        
        query = input("Enter custom query (or press Enter for default): ").strip()
         
        
        detect_on_image_with_gemini(image_path, query)
    else:
        print("Invalid choice. Running webcam mode by default.")
        run_gemini_vision_detection()
