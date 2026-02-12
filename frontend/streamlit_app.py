import streamlit as st
import requests
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000"

# Page config
st.set_page_config(
    page_title="MindCare AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ChatGPT-style CSS
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main background - ChatGPT dark theme */
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
    
    /* Auth tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
        justify-content: center;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #40414f;
        border-radius: 8px;
        color: #8e8ea0;
        padding: 14px 32px;
        border: 1px solid #565869;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #10a37f, #1a7f64) !important;
        color: white !important;
        border: none !important;
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
    
    /* Input fields */
    .stTextInput > div > div > input {
        background-color: #40414f !important;
        border: 1px solid #565869 !important;
        border-radius: 8px !important;
        color: #ececf1 !important;
        font-size: 15px !important;
        padding: 14px 16px !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #10a37f !important;
        box-shadow: 0 0 0 1px #10a37f !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #8e8ea0 !important;
    }
    
    /* Chat area padding */
    .chat-messages {
        padding-bottom: 120px;
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
    
    /* Suggestion buttons */
    .suggestion-btn {
        background: #40414f !important;
        border: 1px solid #565869 !important;
        color: #ececf1 !important;
        padding: 16px 20px !important;
        border-radius: 12px !important;
        text-align: left !important;
        font-size: 14px !important;
        transition: all 0.2s !important;
    }
    
    .suggestion-btn:hover {
        border-color: #10a37f !important;
        background: #4a4b59 !important;
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
    
    ::-webkit-scrollbar-thumb:hover {
        background: #6b6c7b;
    }
    
    /* Chat input container */
    [data-testid="stChatInput"] {
        background-color: #40414f;
        border: 1px solid #565869;
        border-radius: 12px;
    }
    
    [data-testid="stChatInput"] textarea {
        color: #ececf1 !important;
    }
    
    /* Success/Error styling */
    .stSuccess {
        background-color: rgba(16, 163, 127, 0.1);
        border: 1px solid #10a37f;
        color: #10a37f;
    }
    
    .stError {
        background-color: rgba(239, 68, 68, 0.1);
        border: 1px solid #ef4444;
    }
    
    /* Sidebar user info */
    .user-info {
        background: linear-gradient(135deg, #10a37f22, #1a7f6422);
        border: 1px solid #10a37f44;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 20px;
    }
    
    .user-name {
        color: #ececf1;
        font-weight: 600;
        font-size: 16px;
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
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

# ==========================================
# LOGIN / REGISTER PAGE
# ==========================================

if not st.session_state.logged_in:
    st.markdown('<h1 class="main-title">🧠 MindCare AI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Your compassionate AI companion for mental wellness</p>', unsafe_allow_html=True)
    
    # Center the auth form
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        tab1, tab2 = st.tabs(["🔐 Sign In", "✨ Create Account"])
        
        with tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            login_user = st.text_input("Username", key="login_user", placeholder="Enter your username")
            login_pass = st.text_input("Password", type="password", key="login_pass", placeholder="Enter your password")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("Sign In", key="login_btn", use_container_width=True):
                if login_user and login_pass:
                    try:
                        res = requests.post(
                            f"{BASE_URL}/login",
                            json={"username": login_user, "password": login_pass},
                            timeout=10
                        )
                        if res.status_code == 200:
                            data = res.json()
                            st.session_state.logged_in = True
                            st.session_state.user_id = data.get("user_id")
                            st.session_state.username = login_user
                            st.rerun()
                        else:
                            st.error("❌ Invalid username or password")
                    except requests.exceptions.ConnectionError:
                        st.error("❌ Cannot connect to server. Is the backend running?")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                else:
                    st.warning("⚠️ Please enter both username and password")
        
        with tab2:
            st.markdown("<br>", unsafe_allow_html=True)
            reg_user = st.text_input("Username", key="reg_user", placeholder="Choose a username")
            reg_pass = st.text_input("Password", type="password", key="reg_pass", placeholder="Create a password")
            reg_pass2 = st.text_input("Confirm Password", type="password", key="reg_pass2", placeholder="Confirm your password")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("Create Account", key="reg_btn", use_container_width=True):
                if reg_user and reg_pass and reg_pass2:
                    if reg_pass != reg_pass2:
                        st.error("❌ Passwords don't match")
                    elif len(reg_pass) < 4:
                        st.error("❌ Password must be at least 4 characters")
                    else:
                        try:
                            res = requests.post(
                                f"{BASE_URL}/register",
                                json={"username": reg_user, "password": reg_pass},
                                timeout=10
                            )
                            if res.status_code == 201:
                                st.success("✅ Account created successfully! Please sign in.")
                            elif res.status_code == 400:
                                st.error("❌ Username already exists")
                            else:
                                st.error("❌ Registration failed")
                        except requests.exceptions.ConnectionError:
                            st.error("❌ Cannot connect to server. Is the backend running?")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                else:
                    st.warning("⚠️ Please fill in all fields")
    
    # Features section
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    f1, f2, f3, f4 = st.columns(4)
    
    with f1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🎯</div>
            <div class="feature-title">Emotion Detection</div>
            <div class="feature-desc">AI analyzes your emotional state in real-time</div>
        </div>
        """, unsafe_allow_html=True)
    
    with f2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">💬</div>
            <div class="feature-title">Empathetic Chat</div>
            <div class="feature-desc">Responses tailored to how you're feeling</div>
        </div>
        """, unsafe_allow_html=True)
    
    with f3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📚</div>
            <div class="feature-title">Knowledge Base</div>
            <div class="feature-desc">Powered by mental health expertise</div>
        </div>
        """, unsafe_allow_html=True)
    
    with f4:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🔒</div>
            <div class="feature-title">Private & Secure</div>
            <div class="feature-desc">Your conversations stay confidential</div>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# MAIN CHAT INTERFACE
# ==========================================

else:
    # Sidebar
    with st.sidebar:
        st.markdown(f"""
        <div class="user-info">
            <div class="user-name">👋 Hello, {st.session_state.username or 'User'}!</div>
        </div>
        """, unsafe_allow_html=True)
        
        # New Chat button
        if st.button("➕ New Chat", key="new_chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # View History
        with st.expander("📜 Chat History"):
            try:
                res = requests.post(
                    f"{BASE_URL}/history",
                    json={"user_id": st.session_state.user_id},
                    timeout=10
                )
                if res.status_code == 200:
                    history = res.json()
                    if history:
                        for item in history[-8:]:
                            st.markdown(f"**You:** {item['message'][:50]}...")
                            st.caption(f"Emotion: {item['emotion']}")
                            st.markdown("---")
                    else:
                        st.caption("No history yet")
            except:
                st.caption("Could not load history")
        
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
        
        # Logout
        if st.button("🚪 Logout", key="logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.session_state.username = ""
            st.session_state.messages = []
            st.rerun()
    
    # Main chat area
    st.markdown('<div class="chat-messages">', unsafe_allow_html=True)
    
    # Welcome message if no messages
    if not st.session_state.messages:
        st.markdown('<h1 class="main-title">🧠 MindCare AI</h1>', unsafe_allow_html=True)
        st.markdown('<p class="subtitle">How can I support you today?</p>', unsafe_allow_html=True)
        
        # Suggestion buttons
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("😔 I'm feeling down today", key="sug1", use_container_width=True):
                st.session_state.pending_message = "I'm feeling down today"
                st.rerun()
            if st.button("😤 I need to vent about something", key="sug3", use_container_width=True):
                st.session_state.pending_message = "I need to vent about something"
                st.rerun()
        
        with col2:
            if st.button("😰 I'm feeling anxious", key="sug2", use_container_width=True):
                st.session_state.pending_message = "I'm feeling anxious"
                st.rerun()
            if st.button("🤔 I need some advice", key="sug4", use_container_width=True):
                st.session_state.pending_message = "I need some advice"
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
    
    # Handle pending message from suggestion buttons
    if "pending_message" in st.session_state:
        pending = st.session_state.pending_message
        del st.session_state.pending_message
        
        # Add user message
        st.session_state.messages.append({"role": "user", "content": pending})
        
        # Get AI response
        try:
            res = requests.post(
                f"{BASE_URL}/chat",
                json={"message": pending, "user_id": st.session_state.user_id},
                timeout=60
            )
            if res.status_code == 200:
                data = res.json()
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": data["reply"],
                    "emotion": data["emotion"]
                })
        except:
            st.session_state.messages.append({
                "role": "assistant",
                "content": "I'm having trouble connecting right now. Please try again.",
                "emotion": "neutral"
            })
        st.rerun()
    
    # Chat input - this automatically clears after sending
    if prompt := st.chat_input("Message MindCare AI..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Get AI response
        with st.spinner(""):
            try:
                res = requests.post(
                    f"{BASE_URL}/chat",
                    json={"message": prompt, "user_id": st.session_state.user_id},
                    timeout=60
                )
                if res.status_code == 200:
                    data = res.json()
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": data["reply"],
                        "emotion": data["emotion"]
                    })
                else:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "Sorry, something went wrong. Please try again.",
                        "emotion": "neutral"
                    })
            except Exception as e:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "I'm having trouble connecting to the server. Please ensure the backend is running.",
                    "emotion": "neutral"
                })
        
        st.rerun()
