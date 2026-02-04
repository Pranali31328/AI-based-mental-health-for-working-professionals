import streamlit as st
import sqlite3
import pandas as pd
from transformers import pipeline
from datetime import datetime

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Workplace Mental Health Intelligence Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- CUSTOM LIGHT STYLING ----------------
st.markdown("""
    <style>
        body {background-color: #f5f7fa;}
        .stApp {background-color: #f5f7fa;}
        h1, h2, h3 {color: #1f2d3d;}
        .stMetric {background-color: white; padding: 10px; border-radius: 8px;}
    </style>
""", unsafe_allow_html=True)

# ---------------- DATABASE ----------------
conn = sqlite3.connect("mental_health.db", check_same_thread=False)
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS logs (
    time TEXT,
    emotion TEXT,
    confidence REAL,
    stress INTEGER
)
""")
conn.commit()

# ---------------- AI MODEL ----------------
@st.cache_resource
def load_emotion_model():
    return pipeline("text-classification",
                    model="bhadresh-savani/distilbert-base-uncased-emotion")

emotion_model = load_emotion_model()

# ---------------- LOGIC ----------------
def calculate_stress(emotion):
    stress_map = {
        "sadness": 75,
        "anger": 85,
        "fear": 80,
        "joy": 20,
        "love": 25,
        "surprise": 40
    }
    return stress_map.get(emotion.lower(), 50)

def detect_work_pressure(text):
    text = text.lower()
    if any(word in text for word in ["deadline", "target", "urgent"]):
        return "Deadline Pressure"
    if any(word in text for word in ["meeting", "call", "discussion"]):
        return "Meeting Fatigue"
    if any(word in text for word in ["busy", "workload", "tasks"]):
        return "Workload Overload"
    return "No Major Work Pressure"

def burnout_prediction():
    recent_data = pd.read_sql("SELECT stress FROM logs ORDER BY time DESC LIMIT 5", conn)
    if len(recent_data) < 3:
        return "Low"
    avg_stress = recent_data["stress"].mean()
    if avg_stress > 70:
        return "High"
    elif avg_stress > 50:
        return "Moderate"
    return "Low"

# ---------------- SIDEBAR ----------------
st.sidebar.title("Mental Health Intelligence System")
page = st.sidebar.radio("Navigation", ["Home", "AI Assessment", "Analytics Dashboard", "About"])

# =====================================================
# HOME PAGE
# =====================================================
if page == "Home":
    st.title("Workplace Mental Health Intelligence Platform")
    st.write("""
    This platform uses Natural Language Processing to assess workplace emotional states,
    quantify stress levels, and provide predictive mental wellness insights.
    """)

    st.subheader("System Capabilities")
    st.markdown("""
    - Emotion Detection using AI  
    - Professional Stress Quantification  
    - Burnout Risk Prediction  
    - Workplace Pressure Analysis  
    - Emotional Trend Analytics  
    """)

# =====================================================
# AI ASSESSMENT PAGE
# =====================================================
elif page == "AI Assessment":
    st.title("AI-Based Emotional Assessment")

    user_input = st.text_input("Describe how you are feeling about your work today:")

    if user_input:
        result = emotion_model(user_input)[0]
        emotion = result["label"]
        confidence = round(result["score"] * 100, 2)
        stress = calculate_stress(emotion)
        pressure = detect_work_pressure(user_input)
        burnout = burnout_prediction()

        st.subheader("Analysis Result")

        col1, col2, col3 = st.columns(3)
        col1.metric("Detected Emotion", emotion)
        col2.metric("AI Confidence (%)", confidence)
        col3.metric("Stress Score", f"{stress}/100")

        st.write("Burnout Risk Level:", burnout)
        st.write("Workplace Pressure Insight:", pressure)

        c.execute("INSERT INTO logs VALUES (?,?,?,?)",
                  (datetime.now(), emotion, confidence, stress))
        conn.commit()

# =====================================================
# ANALYTICS DASHBOARD
# =====================================================
elif page == "Analytics Dashboard":
    st.title("Emotional Analytics Dashboard")
    data = pd.read_sql("SELECT * FROM logs", conn)

    if not data.empty:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Stress Trend Over Time")
            st.line_chart(data["stress"])

        with col2:
            st.subheader("Emotion Distribution")
            st.bar_chart(data["emotion"].value_counts())
    else:
        st.info("No data available. Complete assessments to generate analytics.")

# =====================================================
# ABOUT PAGE
# =====================================================
elif page == "About":
    st.title("About This Project")
    st.write("""
    This system is an AI-driven workplace mental health analytics platform designed to:
    
    - Monitor emotional patterns  
    - Quantify stress levels  
    - Predict burnout risk  
    - Provide workplace-related mental insights  
    
    The platform integrates Natural Language Processing, predictive analytics,
    and visualization tools for mental wellness intelligence.
    """)
