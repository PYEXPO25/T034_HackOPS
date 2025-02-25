import speech_recognition as sr
import pyttsx3
from fuzzywuzzy import fuzz
import google.generativeai as genai
import os

# Initialize Text-to-Speech Engine
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen():
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True  # Improve noise adaptation

    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source, timeout=5)  # Timeout to prevent long waits

    try:
        return recognizer.recognize_google(audio).lower()
    except sr.UnknownValueError:
        return None
    except sr.RequestError:
        return "Error in voice processing."

# Load API Key Securely
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("API key not found. Set GEMINI_API_KEY in environment variables.")

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-pro")

def generate_question(board, subject, difficulty="medium"):
    prompt = f"Generate a {difficulty} difficulty {subject} question for a {board} board student."
    response = model.generate_content(prompt)
    return response.text.strip() if response else "Error generating question."

def generate_correct_answer(question):
    prompt = f"Provide the correct answer for this question: {question}"
    response = model.generate_content(prompt)
    return response.text.strip() if response else "Error generating answer."

def check_answer(user_answer, correct_answer):
    if not user_answer:
        return {"score": 0, "message": "No input detected."}

    accuracy = fuzz.ratio(user_answer.lower().strip(), correct_answer.lower().strip())

    if accuracy >= 90:
        return {"score": 10, "message": "Perfect! You earned 10 points."}
    elif accuracy >= 70:
        return {"score": 7, "message": f"Almost! Correct answer: {correct_answer}."}
    elif accuracy >= 50:
        return {"score": 5, "message": f"Partially correct. Correct answer: {correct_answer}."}
    else:
        return {"score": 0, "message": f"Incorrect. Correct answer: {correct_answer}."}

def play_game(board, subject):
    score = 0
    for _ in range(5):
        question = generate_question(board, subject)
        speak(question)  # Ask question
        user_answer = listen()  # Take user's voice input

        if user_answer == "Error in voice processing.":
            return {"final_score": score, "message": "Voice recognition error. Please try again."}

        correct_answer = generate_correct_answer(question)
        result = check_answer(user_answer, correct_answer)
        score += result["score"]

        speak(result["message"])  # Give spoken feedback
        print(result["message"])

    return {"final_score": score, "message": f"Game over! Your score is {score}."}
