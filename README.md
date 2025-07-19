# Mental Health Anomaly Detector

A modern, user-friendly web app to detect mental health anomalies using wearable sensor data. Built for individuals and health/fitness companies to assess well-being and get actionable, personalized advice.

---

## 🚀 Features
- **Manual Data Entry:** Enter your weekly average health metrics (sleep, steps, heart rate, etc.)
- **Batch CSV Upload:** Upload a CSV file with daily data for automated analysis
- **Three-Level Anomaly Detection:** Results categorized as `No Anomaly`, `Minor Anomaly`, or `Major Anomaly`
- **Personalized Remedies:** For minor anomalies, get specific home remedies and solutions for each contributing factor
- **Modern UI:** Dark mode, orange theme, and clear, actionable feedback
- **(Optional) AI-Powered Q&A:** Ask health-related questions and get AI-generated advice (Llama/OpenAI integration)
- **(Optional) User Authentication:** Add login/registration for secure access

---

## 🛠️ Tech Stack

**Frontend:**
- Streamlit (UI, forms, file upload, results display)
- Custom CSS/HTML (dark mode, orange theme)
- Pandas (CSV reading/averaging in app)

**Backend/Model:**
- Python
- NumPy
- Pandas
- scikit-learn (for training/encoding)
- Custom neural network (NumPy-based)
- Pickle (model weights persistence)

**Data Handling:**
- CSV file upload (batch analysis)
- Manual data entry (weekly averages)

**DevOps/Deployment:**
- Git, GitHub (version control, code hosting)
- Streamlit Cloud (deployment)

**(Optional/Planned):**
- Llama/OpenAI API (personalized advice)
- streamlit-authenticator (user login/registration)

---

## 📦 Setup & Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/prakharDvedi/SupraThon.git
   cd SupraThon/Mental_health_ML-main
   ```
2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
3. **(Optional) Add your model weights:**
   - Place `model_weights.pkl` in the same directory as `app.py` and `model.py`.
   - (Do not upload large files to GitHub; use local or cloud storage.)
4. **Run the app locally:**
   ```sh
   streamlit run app.py
   ```

---

## 📝 Usage

- **Manual Entry:**
  1. Click "Start Assessment"
  2. Enter your weekly average values for each metric
  3. Submit to get your result and remedies

- **Batch CSV Upload:**
  1. Prepare a CSV file with columns:
     ```
     sleep_duration,step_count,resting_heart_rate,stress_level,sleep_onset_time,HR_day_avg,HR_sleep_min
     ```
  2. Each row = one day of data
  3. Upload the file in the app
  4. See the calculated averages, verdict, and remedies

- **(Optional) Ask a Question:**
  - Enter a health-related question and get an AI-powered answer (if enabled)

---

## 🤝 Contributing

1. Fork the repo and create your branch
2. Make your changes and commit
3. Push to your fork and submit a pull request
4. For major changes, open an issue first to discuss

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgements
- Built with Streamlit, NumPy, Pandas, and scikit-learn
- Inspired by the need for accessible, actionable mental health analytics
