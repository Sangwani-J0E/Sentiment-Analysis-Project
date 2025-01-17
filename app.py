import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
from PIL import Image
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from textblob import TextBlob
import nltk

# Download NLTK data
nltk.download('omw-1.4')
nltk.download('stopwords')
nltk.download('wordnet')

# Set up page configuration
im = Image.open("twe.png")
st.set_page_config(
    page_title="Tweet Sentiment Analysis",
    page_icon=im,
    layout="wide",
)

# Initialize session state for recent searches
if "recent_searches" not in st.session_state:
    st.session_state.recent_searches = []

# Header section
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2rem;
        font-weight: bold;
        color: #4CAF50;
        text-align: center;
        padding: 10px 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #333;
        text-align: center;
    }
    .sentiment-label {
        font-size: 1.5rem;
        font-weight: bold;
        margin-top: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main-header">📊 Tweet Sentiment Analysis App</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Analyze tweet sentiments and visualize the results</div>', unsafe_allow_html=True)

# Sidebar for input
st.sidebar.header("Input Parameters")
tweet = st.sidebar.text_input("Enter a Tweet or Phrase", placeholder="Type something...")
lang = st.sidebar.selectbox('Select Language:', ('en', 'es', 'it', 'fr', 'ar'))
limit = st.sidebar.number_input("Number of Tweets to Analyze", min_value=1, max_value=1000, value=100)
start_date = st.sidebar.date_input("Start Date")
end_date = st.sidebar.date_input("End Date")
analyze_button = st.sidebar.button("Analyze")
recent_searches_button = st.sidebar.button("View Recent Searches")

# Function to determine sentiment label and color
def get_sentiment_label(polarity):
    if polarity > 0:
        return "Positive 😊", "green"
    elif polarity < 0:
        return "Negative 😢", "red"
    else:
        return "Neutral 😐", "yellow"

# Function to analyze sentiments
def analyze_sentiment(input_text):
    if not input_text:
        st.warning("Please enter text for analysis.")
        return

    # Preprocessing
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))
    words = input_text.split()
    cleaned_text = " ".join(
        [lemmatizer.lemmatize(word) for word in words if word.lower() not in stop_words]
    )

    # Sentiment analysis
    blob = TextBlob(cleaned_text)
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity

    # Get sentiment label and color
    sentiment_label, sentiment_color = get_sentiment_label(polarity)

    # Store results in session state
    st.session_state.recent_searches.append(
        {"Tweet": input_text, "Polarity": polarity, "Subjectivity": subjectivity, "Sentiment": sentiment_label}
    )

    # Results section
    st.markdown("### Sentiment Analysis Results")
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Polarity", value=f"{polarity:.2f}", delta=None, delta_color="off")
    with col2:
        st.metric(label="Subjectivity", value=f"{subjectivity:.2f}", delta=None, delta_color="off")

    # Display sentiment label
    st.markdown(
        f'<div class="sentiment-label" style="color: {sentiment_color};">{sentiment_label}</div>',
        unsafe_allow_html=True,
    )

    # Visualize sentiment polarity
    st.markdown("### Polarity Distribution")
    df = pd.DataFrame({"Metric": ["Polarity", "Subjectivity"], "Value": [polarity, subjectivity]})
    fig = px.bar(df, x="Metric", y="Value", color="Metric", text="Value", height=400)
    st.plotly_chart(fig, use_container_width=True)

    # Display processed text
    st.markdown("### Processed Input Text")
    st.code(cleaned_text, language="text")


# Analyze the input if the button is clicked
if analyze_button:
    analyze_sentiment(tweet)

# Display recent searches if the button is clicked
if recent_searches_button:
    st.markdown("## Recent Searches")
    if st.session_state.recent_searches:
        df_recent = pd.DataFrame(st.session_state.recent_searches)
        st.dataframe(df_recent)
        st.download_button(
            label="Download Recent Searches",
            data=df_recent.to_csv(index=False),
            file_name="recent_searches.csv",
            mime="text/csv",
        )
    else:
        st.info("No recent searches available. Start analyzing some tweets!")
