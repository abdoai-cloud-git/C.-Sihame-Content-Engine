import streamlit as st
import json
import random
import google.generativeai as genai

# Page config
st.set_page_config(page_title="Coach Siham AI Writer", page_icon="✨", layout="centered")

# Load compiled corpus dataset
@st.cache_data
def load_corpus():
    try:
        with open("corpus.json", 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

corpus = load_corpus()

# UI Layout
st.title("✨ Coach Siham AI Writer")
st.markdown("Generates Telegram posts mimicking Coach Siham's calming, spiritual, and reflective tone.")

with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("Google Gemini API Key", type="password")
    st.markdown("[Get an API key here](https://aistudio.google.com/app/apikey)")
    
    if api_key:
        genai.configure(api_key=api_key)
        
    st.markdown("---")
    res = len(corpus) if corpus else 0
    st.write(f"This AI writer uses a clean dataset of **{res}** past Telegram posts to capture the exact tone and style of Coach Siham via dynamic few-shot prompting.")

st.subheader("What would you like to write about today?")
topic = st.text_area("Enter a theme, topic, or specific idea:", placeholder="e.g. Dealing with anxiety, reflection on Al-Wadud, inner child healing, calming the nervous system...")

if st.button("Generate Post ✍️"):
    if not api_key:
        st.error("Please enter your Google Gemini API key in the sidebar.")
    elif not topic:
        st.warning("Please enter a topic to write about.")
    elif not corpus:
        st.error("Corpus data not found. Please ensure corpus.json exists in the same directory.")
    else:
        with st.spinner("Channeling Coach Siham's energy... ✨"):
            try:
                # Select random posts as stylistic examples for the AI to mimic
                examples = random.sample(corpus, min(3, len(corpus)))
                examples_text = "\n\n---\n\n".join([ex["text"] for ex in examples])
                
                # Constructing the System Prompt
                system_prompt = f"""You are an expert AI ghostwriter for Coach Siham, a spiritual and psychological well-being coach. 
Your goal is to write a Telegram post about the given topic in her EXACT tone, style, and vocabulary.

### COACH SIHAM's Persona & Tone:
- **Tone:** Calming, soothing, reflective, profoundly empathetic, and deeply spiritual.
- **Topics:** Nervous system regulation (الجهاز العصبي), trauma healing, inner peace (الطمأنينة), inner child (نسخ متألمة), and Islamic spiritual psychology (Names of Allah, Quranic reflections).
- **Style:** She uses very short paragraphs (1-2 sentences), abundant line breaks, and simple but poetic Arabic (MSA mixed with light, soft phrasing).
- **Formatting:** Use emojis elegantly but sparingly (✨, ☘️, 💚, 🤍, 🌿). Often ends with her signature `#سهام_عثامنية`.
- **Message:** Always shifts the focus from "hustle and pressure" to "stillness, acceptance, and internal peace."
- **Context:** Her programs (like "اربعينية الازدهار") are free community commitments where participants remind each other of calmness and read designated Quranic verses; they are not paid services.

### Stylistic Examples from her past posts (Mimic their structure and tone perfectly):
{examples_text}

### INSTRUCTIONS:
Write a new Telegram post for Coach Siham about the following topic. Match her paragraph spacing, sentence length, and vocabulary perfectly. DO NOT write an introduction or conclusion to your response, just output the post itself.

TOPIC: {topic}
"""
                
                # Generate content
                model = genai.GenerativeModel('gemini-1.5-pro-latest')
                response = model.generate_content(system_prompt)
                
                st.success("Post Generated Successfully!")
                
                st.markdown("### Generated Post:")
                # Use a text area for easy copying
                st.text_area("Result", value=response.text, height=400, label_visibility="collapsed")
                
                # Option to download the post as a file
                st.download_button(
                    label="Download Post 📥",
                    data=response.text,
                    file_name="coach_siham_post.txt",
                    mime="text/plain"
                )
                
            except Exception as e:
                st.error(f"Error generating post: {str(e)}")
