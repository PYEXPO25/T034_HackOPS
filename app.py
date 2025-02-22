from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
import pyttsx3
import random
import time
import threading
from playsound import playsound
import os

app = Flask(__name__)

# Initialize Text-to-Speech & Speech Recognition
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)  # Try changing to voices[1].id if needed
engine.setProperty('rate', 150)  # Adjust speech rate
recognizer = sr.Recognizer()

# Question Categories
CATEGORIES = {
    "general knowledge": [
        {"question": "What is the capital of France?", "answer": "paris"},
        {"question": "Who wrote Hamlet?", "answer": "shakespeare"},
    ],
    "science": [
        {"question": "What is the chemical symbol for water?", "answer": "h2o"},
        {"question": "What planet is known as the red planet?", "answer": "mars"},
    ],
}

selected_category = "general knowledge"
questions = []
current_question = 0
score = 0
streak = 0  # Streak Tracking

def speak(text):
    """Convert text to speech in a non-blocking way."""
    def run():
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"Error in TTS: {e}")
    threading.Thread(target=run).start()

def beep():
    """Play a beep sound before user input."""
    try:
        if os.path.exists("static/beep.wav"):
            playsound("static/beep.wav")
        else:
            print("Beep sound file not found!")
    except Exception as e:
        print(f"Error playing beep sound: {e}")

def delayed_speak(text, delay=0.5):
    """Delay before speaking."""
    time.sleep(delay)
    speak(text)

@app.route('/')
def index():
    """Load Game UI"""
    return render_template('index.html', title="Trivia Game")

@app.route('/start_game', methods=['POST'])
def start_game():
    """Start the game & select category based on user voice."""
    global selected_category, questions, current_question, score, streak

    category = request.json.get("category", "").lower()
    if category in CATEGORIES:
        selected_category = category
    else:
        selected_category = "general knowledge"  # Default

    questions = random.sample(CATEGORIES[selected_category], len(CATEGORIES[selected_category]))
    current_question, score, streak = 0, 0, 0

    delayed_speak(f"Starting {selected_category} trivia. First question:")
    return get_question()

@app.route('/get_question', methods=['GET'])
def get_question():
    """Send a question to the frontend."""
    global current_question

    if current_question >= len(questions):
        delayed_speak(f"Game over! Your final score is {score} out of {len(questions)}.")
        return jsonify({"question": None, "message": f"Game over! Score: {score}/{len(questions)}"})

    question_text = questions[current_question]["question"]
    delayed_speak(question_text)
    beep()
    return jsonify({"question": question_text, "score": score, "streak": streak})

@app.route('/check_answer', methods=['POST'])
def check_answer():
    """Receive answer from frontend, check correctness, and respond."""
    global current_question, score, streak
    data = request.json
    user_answer = data.get("answer", "").lower()

    correct_answer = questions[current_question]["answer"]
    if user_answer == correct_answer:
        delayed_speak("Correct! You're on fire!")
        score += 1
        streak += 1
        if streak == 3:
            delayed_speak("🔥 Triple streak! Keep it up!")
        elif streak == 5:
            delayed_speak("🚀 Five in a row! You're a genius!")
    else:
        delayed_speak(f"Wrong! The correct answer was {correct_answer}.")
        streak = 0  # Reset streak

    current_question += 1
    return get_question()

if __name__ == '__main__':
    app.run(debug=False, port=5000)  # Disable debug mode to prevent conflicts