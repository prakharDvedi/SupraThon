import streamlit as st
from model import predict_anomaly

# Set page config for a dark, modern look
st.set_page_config(page_title="Mental Health Anomaly Detector", page_icon="🧠", layout="centered")

# Custom CSS for dark mode with orange theme
st.markdown(
    """
    <style>
    body, .stApp, .main {
        background-color: #181818;
    }
    .title-style {
        font-family: 'Segoe UI', 'Roboto', sans-serif;
        color: #ffb347;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5em;
        letter-spacing: 1px;
    }
    .desc-style {
        font-family: 'Segoe UI', 'Roboto', sans-serif;
        color: #ffe5b4;
        font-size: 1.1rem;
        margin-bottom: 1.5em;
    }
    .stButton>button {
        background-color: #ffb347;
        color: #181818;
        border-radius: 8px;
        font-size: 1.1rem;
        padding: 0.5em 2em;
        border: none;
        font-weight: 600;
        transition: background 0.2s;
        box-shadow: 0 2px 8px rgba(255,179,71,0.08);
    }
    .stButton>button:hover {
        background-color: #ff8800;
        color: #fff;
    }
    .stTextInput>div>input, .stNumberInput>div>input {
        background-color: #232323;
        border-radius: 6px;
        border: 1px solid #ffb347;
        color: #fff;
    }
    .stNumberInput label, .stTextInput label {
        color: #ffb347 !important;
    }
    .stForm label {
        color: #ffb347 !important;
    }
    .stAlert {
        background-color: #232323 !important;
        color: #fff !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="title-style">🧠 Mental Health Anomaly Detector</div>', unsafe_allow_html=True)

st.markdown(
    '<div class="desc-style">'
    'Welcome to the Mental Health Anomaly Detector! This tool helps individuals and health & fitness companies assess the likelihood of mental health anomalies based on wearable sensor data.'
    '<br><br>'
    '<b>How it works:</b><br>'
    '- Enter your (or your users\') weekly average health metrics (sleep, steps, heart rate, etc.).<br>'
    '- Get a percentage likelihood of a mental health anomaly.<br>'
    '- If the likelihood is high, we recommend consulting a healthcare professional.'
    '<br><br>'
    '<b>Who is this for?</b><br>'
    '- Individuals: Track your own well-being using data from your smartwatch, fitness band, or phone.<br>'
    '- Companies: Assess your users\' health and provide timely recommendations.'
    '</div>',
    unsafe_allow_html=True
)

st.markdown("---")

if st.button("Start Assessment"):
    st.session_state["assessment_started"] = True

if st.session_state.get("assessment_started"):
    st.header(":orange[Enter Your Weekly Average Values]")
    with st.form("user_input_form"):
        col1, col2 = st.columns(2)
        with col1:
            sleep_duration = st.number_input("Sleep duration (hours)", min_value=0.0, max_value=24.0, step=0.1, value=7.5)
            step_count = st.number_input("Step count", min_value=0, max_value=100000, step=1, value=7000)
            resting_heart_rate = st.number_input("Resting heart rate", min_value=30, max_value=200, step=1, value=70)
            stress_level = st.number_input("Stress level (0 to 1)", min_value=0.0, max_value=1.0, step=0.01, value=0.3)
        with col2:
            sleep_onset_time = st.number_input("Sleep onset time (minutes from midnight)", min_value=0, max_value=1439, step=1, value=20)
            hr_day_avg = st.number_input("Daytime average heart rate", min_value=30, max_value=200, step=1, value=80)
            hr_sleep_min = st.number_input("Minimum sleep heart rate", min_value=30, max_value=200, step=1, value=55)
        submitted = st.form_submit_button("Submit")
        if submitted:
            user_input = [
                sleep_duration, step_count, resting_heart_rate, stress_level,
                sleep_onset_time, hr_day_avg, hr_sleep_min
            ]
            result = predict_anomaly(user_input)
            if result == 1:
                st.error("Anomaly detected! Please consult a doctor.")
            else:
                st.success("No anomaly detected.") 