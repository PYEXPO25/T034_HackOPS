from flask import Flask, render_template, request, jsonify
from game_logic import play_game
from flask_cors import CORS
from auth_routes import auth_bp  # Import the Blueprint

app = Flask(__name__)
app.secret_key = "1f82b6ec70366eace65a38a5d1b71735"
app.register_blueprint(auth_bp)  # Register the Blueprint
CORS(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/start_game", methods=["POST"])
def start_game():
    data = request.json
    board = data.get("board")
    subject = data.get("subject")

    if not board or not subject:
        return jsonify({"error": "Missing board or subject"}), 400

    result = play_game(board, subject)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
