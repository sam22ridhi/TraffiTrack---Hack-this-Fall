import streamlit as st
import os
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO
import mlflow
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from textblob import TextBlob
from geopy.geocoders import Nominatim
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000"))
mlflow.set_experiment("TraffiTrack Drug Monitoring")

st.set_page_config(page_title="🚦 TraffiTrack Pro", page_icon="🚦", layout="wide")

USER_ROLES = {
    "Admin": ["Home", "Dashboard", "Chat", "Analysis", "Settings"],
    "Analyst": ["Home", "Dashboard", "Chat", "Analysis"],
    "Guest": ["Home", "Dashboard", "Chat"]
}
st.sidebar.title("🔑 User Role")
role = st.sidebar.radio("Select your role", list(USER_ROLES.keys()))
menu_options = USER_ROLES[role]

if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'analysis_data' not in st.session_state:
    st.session_state.analysis_data = {}

def analyze_sentiment(input_text):
    blob = TextBlob(input_text)
    sentiment = blob.sentiment.polarity
    return "Positive" if sentiment > 0 else "Negative" if sentiment < 0 else "Neutral"

def get_location(city_name):
    geolocator = Nominatim(user_agent="TraffiTrackPro")
    location = geolocator.geocode(city_name)
    if location:
        return location.latitude, location.longitude
    else:
        return None, None

def detect_drugs(input_text):
    drug_keywords = ["MDMA", "LSD", "Mephedrone", "Cocaine", "Heroin"]
    detected_words = [word for word in drug_keywords if word.lower() in input_text.lower()]
    sentiment = analyze_sentiment(input_text)
    return detected_words, sentiment

def display_dashboard():
    st.title("📊 Real-Time Dashboard")
    if st.session_state.analysis_data:
        df = pd.DataFrame(st.session_state.analysis_data)
        st.write("### Insights into Drug-Related Messages")
        
        # Filter data by drug type and sentiment
        drug_filter = st.selectbox("Filter by Drug Type", ["All"] + list(set(df['Detected Drugs'].sum())))
        sentiment_filter = st.selectbox("Filter by Sentiment", ["All", "Positive", "Neutral", "Negative"])
        
        if drug_filter != "All":
            df = df[df['Detected Drugs'].apply(lambda x: drug_filter in x)]
        if sentiment_filter != "All":
            df = df[df['Sentiment'] == sentiment_filter]
        
        # Display bar chart
        fig = px.bar(df, x="User", y="Detected Messages", color="Sentiment", title="Drug Detection Insights by Sentiment")
        st.plotly_chart(fig)
        
        # Geolocation map with clusters
        st.write("### Geolocation of Messages")
        map_data = pd.DataFrame([get_location(city) for city in df['Location']], columns=["lat", "lon"])
        map_data.dropna(inplace=True)
        st.map(map_data)
        
        # Weekly trend analysis
        df['Date'] = pd.to_datetime(df['Timestamp']).dt.date
        weekly_trend = df.groupby('Date').size().reset_index(name='Counts')
        trend_fig = px.line(weekly_trend, x='Date', y='Counts', title='Weekly Trend of Detected Messages')
        st.plotly_chart(trend_fig)
    else:
        st.warning("No data available for the dashboard.")

def send_report():
    if st.button("Send Weekly Report"):
        report_data = json.dumps(st.session_state.analysis_data, indent=2)
        email = os.getenv("ADMIN_EMAIL")
        smtp_server = os.getenv("SMTP_SERVER")
        smtp_port = os.getenv("SMTP_PORT")
        smtp_user = os.getenv("SMTP_USER")
        smtp_password = os.getenv("SMTP_PASSWORD")

        if email and smtp_server and smtp_port and smtp_user and smtp_password:
            try:
                msg = MIMEMultipart()
                msg["From"] = smtp_user
                msg["To"] = email
                msg["Subject"] = "Weekly TraffiTrack Pro Report"
                msg.attach(MIMEText(report_data, "plain"))

                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.sendmail(smtp_user, email, msg.as_string())
                server.quit()

                st.success("Weekly report sent successfully!")
            except Exception as e:
                st.error(f"Failed to send report: {e}")
        else:
            st.error("SMTP settings are not configured properly.")

def display_home():
    st.title("🚦 Welcome to TraffiTrack Pro")
    st.markdown("This app uses AI to monitor drug-related activities and detect trends.")

def display_chat():
    st.title("💬 AI-Powered Chat")
    input_text = st.text_input("Enter your message:")
    if st.button("Analyze"):
        detected_drugs, sentiment = detect_drugs(input_text)
        if detected_drugs:
            st.success(f"Detected Drugs: {', '.join(detected_drugs)} | Sentiment: {sentiment}")
        else:
            st.info("No drugs detected.")
        st.session_state.messages.append({"input": input_text, "output": detected_drugs, "sentiment": sentiment})

def display_analysis():
    st.title("📋 Comprehensive Analysis")
    if st.session_state.messages:
        log_df = pd.DataFrame(st.session_state.messages)
        st.dataframe(log_df)
        st.download_button("Download Log", json.dumps(st.session_state.messages), file_name="message_log.json")

def display_settings():
    st.title("⚙️ System Settings")
    send_report()  # Option to trigger report manually

if 'Home' in menu_options and role == 'Admin':
    display_home()
elif 'Dashboard' in menu_options:
    display_dashboard()
elif 'Chat' in menu_options:
    display_chat()
elif 'Analysis' in menu_options:
    display_analysis()
elif 'Settings' in menu_options and role == 'Admin':
    display_settings()
