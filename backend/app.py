from flask import Flask, request, jsonify
from flask_login import login_required, current_user
from flask_cors import CORS
from db import init_db, db
from models import Conversation
from auth import init_auth, register_user, login_user_route, logout_user_route
from emotion_model import detect_emotion
from gemini_service import generate_ai_response
from crisis_detection import crisis_detection

app = Flask(__name__)
app.secret_key = "supersecretkey"
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False
CORS(app, supports_credentials=True)

# Initialize DB & Auth
init_db(app)
init_auth(app)

with app.app_context():
    db.create_all()

conversation_history = {}

# =====================
# AUTH ROUTES
# =====================

@app.route("/register", methods=["POST"])
def register():
    return register_user()


@app.route("/login", methods=["POST"])
def login():
    return login_user_route()


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    return logout_user_route()


# =====================
# CHAT ROUTE (PROTECTED)
# =====================

@app.route("/chat", methods=["POST"])
def chat():

    user_input = request.json["message"]
    user_id = request.json.get("user_id")

    if not user_id:
        return jsonify({"error": "User ID required"}), 401

    # Crisis detection
    if crisis_detection(user_input):
        return jsonify({
            "emotion": "critical",
            "reply": "I'm really concerned. Please contact a trusted person or local helpline immediately."
        })

    # Detect emotion
    emotion = detect_emotion(user_input)

    if user_id not in conversation_history:
        conversation_history[user_id] = []

    user_history = conversation_history[user_id]

    # Generate response
    response = generate_ai_response(user_input, emotion, user_history)

    # Update memory
    user_history.append(f"User: {user_input}")
    user_history.append(f"Bot: {response}")

    # Save to database
    convo = Conversation(
        user_id=user_id,
        message=user_input,
        response=response,
        emotion=emotion
    )

    db.session.add(convo)
    db.session.commit()

    return jsonify({
        "emotion": emotion,
        "reply": response
    })


# =====================
# GET CHAT HISTORY
# =====================

@app.route("/history", methods=["POST"])
def get_history():
    user_id = request.json.get("user_id")

    if not user_id:
        return jsonify({"error": "User ID required"}), 401

    conversations = Conversation.query.filter_by(
        user_id=user_id
    ).all()

    history = [
        {
            "message": c.message,
            "response": c.response,
            "emotion": c.emotion
        }
        for c in conversations
    ]

    return jsonify(history)


if __name__ == "__main__":
    app.run(debug=True)
