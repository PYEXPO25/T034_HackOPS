import speech_recognition as sr
import pyttsx3
import os
from fuzzywuzzy import fuzz
import google.generativeai as genai


# Initialize Text-to-Speech Engine
engine = pyttsx3.init()

def speak(text):
    """Convert text to speech."""
    engine.say(text)
    engine.runAndWait()

def listen():
    """Capture voice input and return text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio).lower()
        print(f"User said: {text}")
        return text
    except sr.UnknownValueError:
        speak("Sorry, I couldn't understand. Please repeat.")
        return None

def get_user_choices():
    """Get the board and subject from the user using voice commands."""
    speak("Which board are you studying? CBSE, ICSE, or State?")
    board = listen()

    speak("Which subject do you want to play? Science, Math, History, or English?")
    subject = listen()

    if board and subject:
        speak(f"You selected {board} board and {subject} subject.")
        return board, subject
    else:
        speak("Sorry, I didn't get that. Let's try again.")
        return get_user_choices()

# Load API Key from Environment Variable
API_KEY = "AIzaSyD5jEnmWtDsGqoSJPolXT6lKG8ROu6dc74"  # Directly setting API key for testing

if not API_KEY:
    raise ValueError("API key not found. Set GEMINI_API_KEY in environment variables.")


genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-pro") 

def generate_question(board, subject, difficulty="medium"):
    """Generate a question dynamically based on board and subject."""
    prompt = f"Generate a {difficulty} difficulty {subject} question for a {board} board student."
    response = model.generate_content(prompt)

    question = response.text.strip()
    speak(question)  # Read the question out loud
    return question

def generate_correct_answer(question):
    """Use AI to generate the correct answer for the question."""
    prompt = f"Provide the correct answer for this question: {question}"
    response = model.generate_content(prompt)

    return response.text.strip()

def get_user_answer():
    """Capture user's answer via voice."""
    speak("Please say your answer.")
    return listen()

def check_answer(user_answer, correct_answer):
    """Check the user's answer and reward points based on accuracy."""
    correct_answer = correct_answer.lower().strip()
    user_answer = user_answer.lower().strip()

    accuracy = fuzz.ratio(user_answer, correct_answer)  # Get similarity percentage

    if accuracy == 100:
        score = 10
        speak("Perfect! You earned 10 points.")
    elif accuracy >= 80:
        score = 7
        speak(f"Almost perfect! You earned 7 points. The correct answer was {correct_answer}.")
    elif accuracy >= 50:
        score = 5
        speak(f"Partially correct! You earned 5 points. The correct answer was {correct_answer}.")
    else:
        score = 0
        speak(f"Incorrect. The correct answer was {correct_answer}.")

    return score

def analyze_sentiment(user_response):
    """Analyze the sentiment of user's voice response."""
    sentiment_prompt = f"Analyze the sentiment in this response: '{user_response}'. Return only 'positive', 'neutral', or 'negative'."
    response = model.generate_content(sentiment_prompt)

    sentiment = response.text.strip().lower()

    if sentiment == "negative":
        speak("It seems you're having a tough time. Let's try an easier question.")
        return "easy"
    elif sentiment == "positive":
        speak("Great! Let's challenge you with a harder question.")
        return "hard"
    else:
        return "medium"

def play_game():
    """Main game loop where questions are asked and answers are checked."""
    board, subject = get_user_choices()

    score = 0
    difficulty = "medium"

    for _ in range(5):  # Ask 5 questions
        question = generate_question(board, subject, difficulty)
        correct_answer = generate_correct_answer(question)
        user_answer = get_user_answer()

        if user_answer:
            score += check_answer(user_answer, correct_answer)

        # Adjust difficulty based on sentiment
        difficulty = analyze_sentiment(user_answer)

    speak(f"Game over! Your final score is {score} points.")

if __name__ == "__main__":
    play_game()
