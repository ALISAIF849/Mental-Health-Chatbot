import streamlit as st
import os
import sys

# Show Python version for debugging
print(f"Python version: {sys.version}", flush=True)

try:
    from groq import Groq
    print("Groq imported successfully", flush=True)
except Exception as e:
    print(f"Error importing Groq: {e}", flush=True)

try:
    from transformers import pipeline
    print("Transformers imported successfully", flush=True)
except Exception as e:
    print(f"Error importing transformers: {e}", flush=True)

try:
    from sentence_transformers import SentenceTransformer
    print("SentenceTransformers imported successfully", flush=True)
except Exception as e:
    print(f"Error importing sentence_transformers: {e}", flush=True)

try:
    import faiss
    print("FAISS imported successfully", flush=True)
except Exception as e:
    print(f"Error importing faiss: {e}", flush=True)

try:
    import numpy as np
    print("NumPy imported successfully", flush=True)
except Exception as e:
    print(f"Error importing numpy: {e}", flush=True)

# ==========================================
# CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="MindCare AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# LOAD MODELS (cached)
# ==========================================

@st.cache_resource
def load_emotion_model():
    return pipeline(
        "text-classification",
        model="j-hartmann/emotion-english-distilroberta-base"
    )

@st.cache_resource
def load_rag_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

@st.cache_resource
def load_knowledge_base():
    knowledge = [
        "Anxiety can cause rapid heartbeat and excessive worry.",
        "Depression includes persistent sadness and low energy.",
        "Breathing exercises help reduce panic attacks.",
        "Cognitive Behavioral Therapy is effective for anxiety disorders.",
        "Talking to a trusted person can improve emotional well-being.",
        "Regular exercise can significantly improve mental health.",
        "Sleep hygiene is crucial for emotional regulation.",
        "Mindfulness meditation can reduce stress and anxiety.",
        "Social connections are vital for mental wellness.",
        "Professional help is important for persistent mental health issues."
    ]
    
    model = load_rag_model()
    embeddings = model.encode(knowledge)
    
    if len(embeddings.shape) == 1:
        embeddings = np.expand_dims(embeddings, axis=0)
    
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))
    
    return knowledge, index

# Load models
emotion_classifier = load_emotion_model()
rag_model = load_rag_model()
knowledge, faiss_index = load_knowledge_base()

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def detect_emotion(text):
    result = emotion_classifier(text)[0]
    return result["label"]

def crisis_detection(text):
    keywords = ["suicide", "kill myself", "end my life", "hopeless", "don't want to live", "want to die"]
    return any(word in text.lower() for word in keywords)

def retrieve_context(query):
    query_vector = rag_model.encode([query])
    D, I = faiss_index.search(np.array(query_vector), k=min(2, len(knowledge)))
    return " ".join([knowledge[i] for i in I[0]])

def generate_ai_response(user_input, emotion, history):
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        return "I'm here to listen. Please share what's on your mind, and I'll do my best to support you. 💜"
    
    context = retrieve_context(user_input)
    
    prompt = f"""You are a compassionate mental health assistant.

Detected emotion: {emotion}

Relevant knowledge:
{context}

Conversation history:
{history}

User message:
{user_input}

Respond empathetically. Do not give medical diagnosis. Encourage professional help if needed."""

    try:
        client = Groq(api_key=api_key)
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
        return f"I'm here for you. It sounds like you're going through a difficult time. Please know that your feelings are valid. Consider reaching out to a counselor or trusted friend. You're not alone. 💜"

# ==========================================
# CSS STYLING
# ==========================================

st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main background */
    .stApp {
        background-color: #343541;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #202123;
        border-right: 1px solid #4d4d4f;
    }
    
    [data-testid="stSidebar"] .stButton > button {
        background-color: transparent;
        border: 1px solid #565869;
        color: white;
        border-radius: 8px;
        padding: 12px 16px;
        width: 100%;
        text-align: left;
        margin: 4px 0;
        transition: all 0.2s;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: #2a2b32;
    }
    
    /* Message container */
    .message-container {
        padding: 24px 48px;
        border-bottom: 1px solid #444654;
    }
    
    .message-container.user {
        background-color: #343541;
    }
    
    .message-container.assistant {
        background-color: #444654;
    }
    
    /* Message content */
    .message-content {
        display: flex;
        max-width: 800px;
        margin: 0 auto;
        gap: 20px;
        align-items: flex-start;
    }
    
    /* Avatar */
    .avatar {
        width: 40px;
        height: 40px;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        flex-shrink: 0;
    }
    
    .avatar.user {
        background: linear-gradient(135deg, #5436DA 0%, #7B68EE 100%);
    }
    
    .avatar.assistant {
        background: linear-gradient(135deg, #10a37f 0%, #1a7f64 100%);
    }
    
    /* Message text */
    .message-text {
        color: #ececf1;
        font-size: 16px;
        line-height: 1.75;
        flex-grow: 1;
        padding-top: 4px;
    }
    
    /* Emotion badge */
    .emotion-badge {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 14px;
        font-size: 12px;
        font-weight: 600;
        margin-top: 12px;
        color: white;
        letter-spacing: 0.3px;
    }
    
    .emotion-joy { background: linear-gradient(135deg, #10a37f, #1a7f64); }
    .emotion-sadness { background: linear-gradient(135deg, #3b82f6, #1d4ed8); }
    .emotion-anger { background: linear-gradient(135deg, #ef4444, #dc2626); }
    .emotion-fear { background: linear-gradient(135deg, #a855f7, #7c3aed); }
    .emotion-surprise { background: linear-gradient(135deg, #f59e0b, #d97706); }
    .emotion-disgust { background: linear-gradient(135deg, #84cc16, #65a30d); }
    .emotion-neutral { background: linear-gradient(135deg, #6b7280, #4b5563); }
    
    /* Title styling */
    .main-title {
        text-align: center;
        font-size: 2.8rem;
        font-weight: 700;
        color: #ececf1;
        margin-bottom: 8px;
    }
    
    .subtitle {
        text-align: center;
        color: #8e8ea0;
        font-size: 1.1rem;
        margin-bottom: 40px;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #10a37f 0%, #1a7f64 100%);
        color: white;
        border: none;
        padding: 14px 28px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 15px;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(16, 163, 127, 0.4);
    }
    
    /* Feature cards */
    .feature-card {
        background: #40414f;
        border: 1px solid #565869;
        border-radius: 14px;
        padding: 28px 20px;
        text-align: center;
        transition: all 0.3s;
        height: 100%;
    }
    
    .feature-card:hover {
        border-color: #10a37f;
        transform: translateY(-6px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.3);
    }
    
    .feature-icon {
        font-size: 36px;
        margin-bottom: 14px;
    }
    
    .feature-title {
        color: #ececf1;
        font-weight: 600;
        font-size: 17px;
        margin-bottom: 10px;
    }
    
    .feature-desc {
        color: #8e8ea0;
        font-size: 14px;
        line-height: 1.5;
    }
    
    /* Chat area padding */
    .chat-messages {
        padding-bottom: 120px;
    }
    
    /* Crisis resources */
    .crisis-box {
        background: linear-gradient(135deg, #ef444422, #dc262622);
        border: 1px solid #ef4444;
        border-radius: 10px;
        padding: 16px;
        margin-top: 20px;
    }
    
    .crisis-title {
        color: #ef4444;
        font-weight: 600;
        margin-bottom: 10px;
    }
    
    .crisis-text {
        color: #fca5a5;
        font-size: 13px;
        line-height: 1.6;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #2a2b32;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #565869;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# SESSION STATE
# ==========================================

if "messages" not in st.session_state:
    st.session_state.messages = []
if "history" not in st.session_state:
    st.session_state.history = []

# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:
    st.markdown("### 🧠 MindCare AI")
    st.markdown("---")
    
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.history = []
        st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Crisis resources
    st.markdown("""
    <div class="crisis-box">
        <div class="crisis-title">🆘 Crisis Resources</div>
        <div class="crisis-text">
            <strong>Emergency:</strong> 911<br>
            <strong>Suicide Hotline:</strong> 988<br>
            <strong>Crisis Text:</strong> HOME to 741741
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    st.caption("Built with ❤️ for mental health awareness")

# ==========================================
# MAIN CHAT AREA
# ==========================================

st.markdown('<div class="chat-messages">', unsafe_allow_html=True)

# Welcome message
if not st.session_state.messages:
    st.markdown('<h1 class="main-title">🧠 MindCare AI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Your compassionate AI companion for mental wellness</p>', unsafe_allow_html=True)
    
    # Feature cards
    f1, f2, f3, f4 = st.columns(4)
    
    with f1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🎯</div>
            <div class="feature-title">Emotion Detection</div>
            <div class="feature-desc">AI analyzes your emotional state</div>
        </div>
        """, unsafe_allow_html=True)
    
    with f2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">💬</div>
            <div class="feature-title">Empathetic Chat</div>
            <div class="feature-desc">Responses tailored to you</div>
        </div>
        """, unsafe_allow_html=True)
    
    with f3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📚</div>
            <div class="feature-title">Knowledge Base</div>
            <div class="feature-desc">Mental health expertise</div>
        </div>
        """, unsafe_allow_html=True)
    
    with f4:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🔒</div>
            <div class="feature-title">Private & Secure</div>
            <div class="feature-desc">Your privacy matters</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Quick suggestions
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("😔 I'm feeling down today", use_container_width=True):
            st.session_state.pending = "I'm feeling down today"
            st.rerun()
        if st.button("😤 I need to vent", use_container_width=True):
            st.session_state.pending = "I need to vent about something"
            st.rerun()
    
    with col2:
        if st.button("😰 I'm feeling anxious", use_container_width=True):
            st.session_state.pending = "I'm feeling anxious"
            st.rerun()
        if st.button("🤔 I need some advice", use_container_width=True):
            st.session_state.pending = "I need some advice"
            st.rerun()

# Display messages
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"""
        <div class="message-container user">
            <div class="message-content">
                <div class="avatar user">👤</div>
                <div class="message-text">{msg["content"]}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        emotion = msg.get("emotion", "neutral").lower()
        emotion_class = f"emotion-{emotion}" if emotion in ['joy', 'sadness', 'anger', 'fear', 'surprise', 'disgust'] else 'emotion-neutral'
        st.markdown(f"""
        <div class="message-container assistant">
            <div class="message-content">
                <div class="avatar assistant">🧠</div>
                <div class="message-text">
                    {msg["content"]}
                    <br><span class="emotion-badge {emotion_class}">Detected: {emotion.capitalize()}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Handle pending message
if "pending" in st.session_state:
    pending = st.session_state.pending
    del st.session_state.pending
    
    st.session_state.messages.append({"role": "user", "content": pending})
    
    # Check for crisis
    if crisis_detection(pending):
        response = "I'm really concerned about what you've shared. Please know that you matter and help is available. Please contact a crisis helpline immediately: Call 988 (Suicide & Crisis Lifeline) or text HOME to 741741. You don't have to face this alone. 💜"
        emotion = "critical"
    else:
        emotion = detect_emotion(pending)
        history_text = "\n".join(st.session_state.history[-6:])
        response = generate_ai_response(pending, emotion, history_text)
    
    st.session_state.messages.append({"role": "assistant", "content": response, "emotion": emotion})
    st.session_state.history.append(f"User: {pending}")
    st.session_state.history.append(f"Assistant: {response}")
    st.rerun()

# Chat input
if prompt := st.chat_input("Message MindCare AI..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Check for crisis
    if crisis_detection(prompt):
        response = "I'm really concerned about what you've shared. Please know that you matter and help is available. Please contact a crisis helpline immediately: Call 988 (Suicide & Crisis Lifeline) or text HOME to 741741. You don't have to face this alone. 💜"
        emotion = "critical"
    else:
        emotion = detect_emotion(prompt)
        history_text = "\n".join(st.session_state.history[-6:])
        
        with st.spinner(""):
            response = generate_ai_response(prompt, emotion, history_text)
    
    st.session_state.messages.append({"role": "assistant", "content": response, "emotion": emotion})
    st.session_state.history.append(f"User: {prompt}")
    st.session_state.history.append(f"Assistant: {response}")
    st.rerun()
