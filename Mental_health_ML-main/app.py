import streamlit as st
import pandas as pd
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
    '- If the likelihood is high, we recommend consulting a healthcare professional.'
    '<br><br>'
    '<b>Who is this for?</b><br>'
    '- Individuals: Track your own well-being using data from your smartwatch, fitness band, or phone.<br>'
    '- Companies: Assess your users\' health and provide timely recommendations.'
    '</div>',
    unsafe_allow_html=True
)

st.markdown("---")

# --- CSV Upload Section ---
st.markdown("""
<div style='background-color:#232323; border-radius:10px; padding:1em; margin-bottom:1em;'>
    <span style='font-size:1.2em; color:#ffb347; font-weight:bold;'>Batch Upload: Analyze Your Data from a File</span><br><br>
    <span style='color:#ffe5b4;'>
    Please upload a <b>CSV file</b> with the following columns in this exact order and with these exact names:<br>
    <b>sleep_duration, step_count, resting_heart_rate, stress_level, sleep_onset_time, HR_day_avg, HR_sleep_min</b><br>
    Each row should represent one day of data.<br>
    </span>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Upload your CSV file here:",
    type=["csv"],
    help="The file must have columns: sleep_duration, step_count, resting_heart_rate, stress_level, sleep_onset_time, HR_day_avg, HR_sleep_min."
)

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        required_cols = [
            "sleep_duration", "step_count", "resting_heart_rate", "stress_level",
            "sleep_onset_time", "HR_day_avg", "HR_sleep_min"
        ]
        if not all(col in df.columns for col in required_cols):
            st.error("CSV is missing one or more required columns. Please check the format and try again.")
        else:
            # Calculate averages
            averages = [df[col].mean() for col in required_cols]
            st.markdown(
                f"<div style='background-color:#232323; border-radius:10px; padding:1em; margin-bottom:1em;'>"
                f"<span style='color:#ffb347; font-weight:bold;'>Averages calculated from your file:</span><br>"
                + "<br>".join(f"<span style='color:#ffe5b4;'>{col}: <b>{avg:.2f}</b></span>" for col, avg in zip(required_cols, averages))
                + "</div>",
                unsafe_allow_html=True
            )
            # Use averages for prediction
            result = predict_anomaly(averages)
            def get_minor_anomaly_advice(user_input):
                sleep_duration, step_count, resting_heart_rate, stress_level, sleep_onset_time, hr_day_avg, hr_sleep_min = user_input
                issues = []
                if sleep_duration < 7 or sleep_duration > 9:
                    issues.append(("Sleep duration", "Aim for 7-9 hours. Try a regular bedtime and avoid screens before bed."))
                if step_count < 5000:
                    issues.append(("Step count", "Try to walk more—take stairs, short walks, or stretch breaks."))
                if resting_heart_rate < 60 or resting_heart_rate > 90:
                    issues.append(("Resting heart rate", "Practice relaxation and light exercise."))
                if stress_level >= 0.5:
                    issues.append(("Stress level", "Try meditation, deep breathing, or journaling."))
                if sleep_onset_time > 40:
                    issues.append(("Sleep onset time", "Avoid screens before bed and create a wind-down routine."))
                if hr_day_avg < 60 or hr_day_avg > 100:
                    issues.append(("Daytime average heart rate", "Do regular cardio and stay hydrated."))
                if hr_sleep_min < 40 or hr_sleep_min > 70:
                    issues.append(("Minimum sleep heart rate", "Practice relaxation and check your sleep environment."))
                return issues
            if result == "null":
                st.success("No anomaly detected.")
            elif result == "minor":
                issues = get_minor_anomaly_advice(averages)
                st.warning("Minor anomaly detected.")
                if issues:
                    st.markdown(
                        "<div style='background-color:#2d2d2d; border-radius:10px; padding:1em; margin-top:1em;'>"
                        "<span style='font-size:1.3em; color:#ffb347; font-weight:bold;'>Remedy</span><br><br>"
                        + "".join(
                            f"<div style='margin-bottom:0.7em;'><span style='color:#ffe5b4; font-size:1.1em; font-weight:bold;'>{factor}:</span> <span style='color:#fff;'>{remedy}</span></div>"
                            for factor, remedy in issues
                        )
                        + "</div>",
                        unsafe_allow_html=True
                    )
                else:
                    st.info("No specific factor identified. Try general wellness tips: regular sleep, exercise, and stress management.")
            else:
                st.error("Major anomaly detected! Please consult a doctor immediately.")
    except Exception as e:
        st.error(f"Error reading file: {e}")

# --- End CSV Upload Section ---

def get_minor_anomaly_advice(user_input):
    sleep_duration, step_count, resting_heart_rate, stress_level, sleep_onset_time, hr_day_avg, hr_sleep_min = user_input
    issues = []

    # Sleep Duration
    if sleep_duration < 6:
        issues.append(("Sleep duration", "You're severely sleep-deprived. Prioritize 7–9 hours. Seek help if persistent."))
    elif sleep_duration < 7:
        issues.append(("Sleep duration", "Try to increase sleep time to 7–9 hours with a fixed routine. Avoid caffeine late."))
    elif sleep_duration > 9:
        issues.append(("Sleep duration", "Oversleeping may signal fatigue or stress. Try regulating sleep-wake cycles."))

    # Step Count
    if step_count < 3000:
        issues.append(("Step count", "Extremely low activity. Try 10-min daily walks or active commuting."))
    elif step_count < 5000:
        issues.append(("Step count", "Try to reach 5k–8k steps daily through short breaks or light exercises."))
    elif step_count > 20000:
        issues.append(("Step count", "Excessive activity may indicate stress or overtraining. Ensure you're recovering well."))

    # Resting Heart Rate
    if resting_heart_rate < 50:
        issues.append(("Resting heart rate", "Unusually low RHR. May be fine for athletes; otherwise, consult a doctor."))
    elif resting_heart_rate > 90:
        issues.append(("Resting heart rate", "High RHR could mean stress, dehydration, or illness. Try relaxing and hydrating."))

    # Stress Level
    if stress_level >= 0.8:
        issues.append(("Stress level", "Critical stress levels detected. Seek support, therapy, or immediate mindfulness practices."))
    elif stress_level >= 0.5:
        issues.append(("Stress level", "High stress. Try breathing exercises, screen breaks, or physical activity."))

    # Sleep Onset Time
    if sleep_onset_time > 60:
        issues.append(("Sleep onset time", "You take too long to fall asleep. Avoid caffeine, screens, and heavy meals before bed."))
    elif sleep_onset_time < 5:
        issues.append(("Sleep onset time", "Falling asleep instantly may indicate sleep deprivation."))

    # Daytime HR
    if hr_day_avg < 55:
        issues.append(("Daytime average heart rate", "Very low. If you're not an athlete, consult a cardiologist."))
    elif hr_day_avg > 100:
        issues.append(("Daytime average heart rate", "High daytime HR. Try relaxation, hydration, and stress management."))

    # Min Sleep HR
    if hr_sleep_min < 40:
        issues.append(("Minimum sleep heart rate", "Unusually low during sleep. Could be normal or may need evaluation."))
    elif hr_sleep_min > 75:
        issues.append(("Minimum sleep heart rate", "Elevated during sleep. Avoid late meals, alcohol, and stress before bed."))

    # Triage
    if len(issues) >= 3:
        issues.append(("General Advice", "⚠️ Multiple anomalies detected. It's strongly recommended to consult a healthcare professional."))

    return issues


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
            if result == "null":
                st.success("No anomaly detected.")
            elif result == "minor":
                issues = get_minor_anomaly_advice(user_input)
                st.warning("Minor anomaly detected.")
                if issues:
                    st.markdown(
                        "<div style='background-color:#2d2d2d; border-radius:10px; padding:1em; margin-top:1em;'>"
                        "<span style='font-size:1.3em; color:#ffb347; font-weight:bold;'>Remedy</span><br><br>"
                        + "".join(
                            f"<div style='margin-bottom:0.7em;'><span style='color:#ffe5b4; font-size:1.1em; font-weight:bold;'>{factor}:</span> <span style='color:#fff;'>{remedy}</span></div>"
                            for factor, remedy in issues
                        )
                        + "</div>",
                        unsafe_allow_html=True
                    )
                else:
                    st.info("No specific factor identified. Try general wellness tips: regular sleep, exercise, and stress management.")
            else:
                st.error("Major anomaly detected! Please consult a doctor immediately.") 