# -*- coding: utf-8 -*-
"""
Created on Tue Jun  9 21:21:58 2026

@author: hetvi
"""

import streamlit as st
import google.generativeai as genai

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# ---- PIXEL STYLING ----
st.set_page_config(page_title="Fact or Cap?", page_icon="🎮", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

* {
    image-rendering: pixelated;
}

html, body, [class*="css"]  {
    font-family: 'Press Start 2P', monospace !important;
}

.stApp {
    background-color: #5C94FC;
    background-image: linear-gradient(#5C94FC, #5C94FC 85%, #E8A860 85%, #E8A860 100%);
}

h1, h2, h3 {
    color: white !important;
    text-shadow: 3px 3px 0px #000000;
    text-align: center;
    line-height: 1.6 !important;
}

p, label, .stMarkdown, span {
    color: white !important;
}

.stButton > button {
    font-family: 'Press Start 2P', monospace !important;
    background-color: #4a9a3a;
    color: white !important;
    border: 4px solid #2d6a20;
    box-shadow: 4px 4px 0px #1a4010;
    border-radius: 0px;
    padding: 12px 20px;
    font-size: 12px !important;
    text-shadow: 2px 2px 0px #000;
    transition: transform 0.1s;
}

.stButton > button:hover {
    background-color: #5ab04a;
    color: white !important;
    border-color: #2d6a20;
}

.stButton > button:active {
    transform: translate(4px, 4px);
    box-shadow: 0px 0px 0px #1a4010;
}

.stTextArea textarea, .stTextInput input {
    font-family: 'Press Start 2P', monospace !important;
    background-color: #9090b0 !important;
    color: white !important;
    border: 4px solid #606080 !important;
    border-radius: 0px !important;
    font-size: 11px !important;
}

.stTextArea textarea::placeholder, .stTextInput input::placeholder {
    color: #e0d0ff !important;
    opacity: 0.8;
}

.stCheckbox label p {
    font-family: 'Press Start 2P', monospace !important;
    color: white !important;
    font-size: 11px !important;
}

.block-container {
    background-color: #5a8a3a;
    border: 6px solid #2d5c1e;
    outline: 3px solid #2d5c1e;
    outline-offset: 4px;
    box-shadow: 6px 6px 0px #1a3010;
    border-radius: 0px;
    padding: 40px 32px !important;
    max-width: 750px;
    margin: 40px auto;
}

div[data-testid="stAlert"] {
    font-family: 'Press Start 2P', monospace !important;
    border-radius: 0px;
    font-size: 11px !important;
    border-width: 3px !important;
}

.stSpinner > div {
    font-family: 'Press Start 2P', monospace !important;
    color: white !important;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# This controls which screen the user is on
if "screen" not in st.session_state:
    st.session_state.screen = 0

# ---- SCREEN 0: HOME ----
if st.session_state.screen == 0:
    st.title("FACT OR CAP? 🎮")
    st.write("Before you trust what AI has said, let's do a quick reality check!")
    
    if st.button("START"):
        st.session_state.screen = 1
        st.rerun()
        
        # ---- SCREEN 1: SPILL THE TEA ----
elif st.session_state.screen == 1:
    st.title("☕ Spill the Tea")
    st.write("What issue are you facing, and what did AI tell you?")
    
    # Text box for the user to type in
    user_input = st.text_area(
        label="Type here:",
        placeholder="eg. AI said my headache is due to stress...",
        height=150
    )
    
    # Save what they typed, then move to next screen
    if st.button("NEXT ▶"):
        if user_input.strip() == "":
            st.warning("Please type something first!")
        else:
            st.session_state.user_input = user_input  # save it for later
            st.session_state.screen = 2
            st.rerun()
            
            
          # ---- SCREEN 2: HOLD UP - QUESTIONS ----
elif st.session_state.screen == 2:
    st.title("🛑 Hold Up... Let's Get Into This")
    st.write("Help us understand your situation better before we check the AI's advice.")
    st.write("Tick all the ones that you can answer yes to")
    st.write("---")

    # Q1 - duration
    q1 = st.checkbox("Do you know how long this has been going on?")
    duration = ""
    if q1:
        duration = st.text_input("How long? (eg. 3 days, 2 weeks)")

    st.write("---")

    # Q2 - symptoms list
    q2 = st.checkbox("Do you want to list your symptoms?")
    symptoms = ""
    if q2:
        symptoms = st.text_area("List them out here:", height=100)

    st.write("---")

    # Q3 to Q6 - yes/no
    q3 = st.checkbox("Is it getting worse?")
    q4 = st.checkbox("Are you experiencing severe symptoms?")
    q5 = st.checkbox("Is it affecting school or daily activities?")
    q6 = st.checkbox("Have you consulted a medical professional before?")

    st.write("---")
    extra = st.text_area("Anything else to add? (optional)", height=80)

    if st.button("CHECK IT ▶"):
        selected = []
        if q1 and duration: selected.append(f"Going on for: {duration}")
        if q2 and symptoms: selected.append(f"Symptoms: {symptoms}")
        if q3: selected.append("Getting worse")
        if q4: selected.append("Severe symptoms")
        if q5: selected.append("Affecting school or daily life")
        if q6: selected.append("Has consulted a doctor before")

        st.session_state.selected_questions = selected
        st.session_state.extra_details = extra
        st.session_state.screen = 3
        st.rerun()

    # ---- SCREEN 3: FACT OR CAP VERDICT ----
elif st.session_state.screen == 3:
    st.title("🎮 Fact or Cap?")
    st.write("Let's check what the AI told you...")

    # Only run the AI check once, then save the result
    if "ai_verdict_text" not in st.session_state:
        with st.spinner("Checking the facts..."):
            
            # Gather everything the user told us
            user_input = st.session_state.get("user_input", "")
            extra_info = st.session_state.get("selected_questions", [])
            extra_details = st.session_state.get("extra_details", "")

            prompt = f"""
            You are a friendly health-literacy helper for teenagers.
            A user got this advice from an AI chatbot: "{user_input}"
            
            Extra context they shared: {extra_info}
            Additional details: {extra_details}

            In 3-4 short, simple sentences:
            1. Give a clear verdict: FACT (reasonable), SALT (take with a pinch of salt), or CAP (don't trust this).
            2. Briefly explain why in plain language.
            3. Always remind them to see a real doctor for anything serious.
            
            Start your response with exactly one of these words: FACT, SALT, or CAP
            """

            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(prompt)
            st.session_state.ai_verdict_text = response.text

    # Show the result
    ai_text = st.session_state.ai_verdict_text
    
    if ai_text.strip().upper().startswith("FACT"):
        st.success("✅ Seems reasonable")
        st.session_state.verdict = "✅ Seems reasonable"
    elif ai_text.strip().upper().startswith("CAP"):
        st.error("🚫 Don't trust AI for this")
        st.session_state.verdict = "🚫 Don't trust AI for this"
    else:
        st.warning("🧂 Take this with a pinch of salt")
        st.session_state.verdict = "🧂 Take this with a pinch of salt"

    st.write(ai_text)

    st.write("---")
    if st.button("NEXT ▶"):
        st.session_state.screen = 4
        st.rerun()
        
        # ---- SCREEN 4: YOUR NEXT MOVE ----
elif st.session_state.screen == 4:
    st.title("👉 Your Next Move")
    st.write("Based on everything so far, here's what we suggest:")
    st.write("---")

    verdict = st.session_state.get("verdict", "")

    if "Don't trust" in verdict:
        st.error("🩺 Consult a healthcare professional — soon")
        st.write("👨‍👩‍👧 Talk to a parent or guardian")
    elif "pinch of salt" in verdict:
        st.warning("🩺 Consider checking with a healthcare professional")
        st.write("👨‍👩‍👧 Talk to a parent or guardian")
        st.write("📋 Monitor your symptoms")
    else:
        st.success("📋 Monitor your symptoms")
        st.write("🩺 Still worth a check-up if anything changes")

    st.write("---")
    if st.button("NEXT ▶"):
        st.session_state.screen = 5
        st.rerun()

# ---- SCREEN 5: PLOT TWIST ----
elif st.session_state.screen == 5:
    st.title("🔄 Plot Twist")
    st.write("**Did you know...**")
    st.write("---")

    col1, col2 = st.columns(2)
    with col1:
        st.info("🤖 AI can make mistakes")
        st.info("🔬 AI can't perform physical examinations")
    with col2:
        st.info("📋 AI does not know your medical history")
        st.info("👩‍⚕️ It's always safest to consult a medical professional")

    st.write("---")
    if st.button("FINISH ▶"):
        st.session_state.screen = 6
        st.rerun()

# ---- SCREEN 6: THE END ----
elif st.session_state.screen == 6:
    st.title("🎉 Thank You for Playing!")
    st.write("When in doubt, seek professional help.")
    st.write("---")
    st.write("*The End*")
    if st.button("PLAY AGAIN"):
        # Reset everything and go back to screen 0
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()