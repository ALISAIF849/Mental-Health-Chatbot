from groq import Groq
import os
from dotenv import load_dotenv
from rag_engine import retrieve_context

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_ai_response(user_input, emotion, history):

    context = retrieve_context(user_input)

    prompt = f"""You are a compassionate mental health assistant.

Detected emotion: {emotion}

Relevant knowledge:
{context}

Conversation history:
{history}

User message:
{user_input}

Respond empathetically. Do not give medical diagnosis.
Encourage professional help if needed."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a compassionate mental health support assistant. Be empathetic, supportive, and encouraging. Never provide medical diagnoses."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Groq API Error: {e}")
        return f"I'm here for you. It sounds like you're going through a difficult time. Please know that your feelings are valid. Consider reaching out to a counselor or trusted friend. You're not alone. 💜"
