import os
import html
import json
import pandas as pd
import traceback
from dotenv import load_dotenv, find_dotenv
from src.mcqgenerator.utils import read_file, parse_quiz_items, render_mcqs_html
from src.mcqgenerator.logger import logging
from langchain_core.callbacks import UsageMetadataCallbackHandler
import streamlit as st

st.set_page_config(page_title="MCQGen — AI Quiz Maker", page_icon="⚡", layout="wide")

with open('Response.json', 'r') as file:
    RESPONSE_JSON = json.load(file)

# Black Glassmorphism theme styles
st.markdown("""
<style>
    .stApp, [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at 10% 20%, rgba(26, 26, 36, 1) 0%, rgba(10, 10, 14, 1) 90%);
        color: #f3f4f6;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    [data-testid="stHeader"] {
        background-color: rgba(10, 10, 14, 0.6);
        backdrop-filter: blur(10px);
    }
    .glass-card {
        background: rgba(22, 24, 33, 0.75);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.45);
    }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #ffffff 0%, #94a3b8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 8px;
    }
    .hero-sub {
        color: #94a3b8;
        font-size: 1rem;
        margin-bottom: 24px;
    }
    .mcq-card {
        background: rgba(26, 28, 38, 0.7);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 18px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
    }
    .mcq-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 12px;
        margin-bottom: 14px;
    }
    .mcq-title-row {
        display: flex;
        align-items: baseline;
        gap: 10px;
    }
    .mcq-qnum {
        background: rgba(99, 102, 241, 0.25);
        color: #818cf8;
        font-weight: 700;
        font-size: 0.85rem;
        padding: 4px 10px;
        border-radius: 8px;
        border: 1px solid rgba(99, 102, 241, 0.4);
    }
    .mcq-qtext {
        font-size: 1.05rem;
        font-weight: 600;
        color: #f1f5f9;
        line-height: 1.5;
    }
    .mcq-correct-badge {
        background: rgba(16, 185, 129, 0.18);
        color: #34d399;
        font-weight: 600;
        font-size: 0.85rem;
        padding: 4px 12px;
        border-radius: 8px;
        border: 1px solid rgba(16, 185, 129, 0.4);
        white-space: nowrap;
    }
    .mcq-options-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 10px;
        margin-top: 10px;
    }
    .mcq-option {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 10px;
        padding: 10px 14px;
        display: flex;
        align-items: center;
        gap: 10px;
        color: #cbd5e1;
        font-size: 0.95rem;
    }
    .mcq-opt-key {
        background: rgba(255, 255, 255, 0.08);
        color: #e2e8f0;
        font-weight: 600;
        font-size: 0.8rem;
        padding: 2px 7px;
        border-radius: 6px;
    }
    .report-card {
        background: rgba(20, 22, 32, 0.8);
        backdrop-filter: blur(14px);
        border: 1px solid rgba(99, 102, 241, 0.25);
        border-radius: 14px;
        padding: 20px;
        margin-top: 24px;
    }
    .report-heading {
        color: #a5b4fc;
        font-size: 1.25rem;
        font-weight: 700;
        margin-bottom: 10px;
    }
    .report-content {
        color: #cbd5e1;
        line-height: 1.6;
        font-size: 0.95rem;
        white-space: pre-wrap;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero-title">⚡ MCQGen — Intelligent Quiz Studio</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Generate neatly structured multiple-choice questions with AI-powered quality review.</div>', unsafe_allow_html=True)

if "quiz_items" not in st.session_state:
    st.session_state.quiz_items = []
if "quiz_review" not in st.session_state:
    st.session_state.quiz_review = ""

with st.form("user_inputs"):
    uploaded_file = st.file_uploader("Source Material (.pdf or .txt)", type=["pdf", "txt"])
    col1, col2, col3 = st.columns(3)
    with col1:
        mcq_count = st.number_input("Number of MCQs", min_value=3, max_value=50, value=5)
    with col2:
        subject = st.text_input("Subject / Domain", placeholder="e.g. Machine Learning", max_chars=30)
    with col3:
        tone = st.text_input("Complexity / Tone", placeholder="e.g. Intermediate", max_chars=30)

    submitted = st.form_submit_button("Generate MCQs")

if submitted:
    if not uploaded_file:
        st.warning("Please upload a PDF or TXT file to begin.")
    elif not subject or not tone:
        st.warning("Please provide both subject and complexity level.")
    else:
        with st.spinner("Generating MCQs and evaluating quiz..."):
            try:
                from src.mcqgenerator.MCQGenerator import generate_evaluate_chain
                text = read_file(uploaded_file)
                callback = UsageMetadataCallbackHandler()
                response = generate_evaluate_chain.invoke(
                    {
                        "text": text,
                        "number": mcq_count,
                        "subject": subject,
                        "tone": tone,
                        "response_json": json.dumps(RESPONSE_JSON)
                    },
                    config={"callbacks": [callback]}
                )
                if isinstance(response, dict):
                    quiz = response.get("quiz", "")
                    st.session_state.quiz_items = parse_quiz_items(quiz)
                    st.session_state.quiz_review = response.get("review", "")
                else:
                    st.error("Unexpected response format from model.")
            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)
                st.error("Error generating MCQs. Please verify API key and input content.")

if st.session_state.quiz_items:
    st.markdown("### 📋 Generated Questions")
    show_answers = st.checkbox("Show answers", value=False, key="show_answers_toggle")

    questions_html = render_mcqs_html(st.session_state.quiz_items, show_answers=show_answers)
    st.html(questions_html)

    if st.session_state.quiz_review:
        st.markdown("### 📊 Quiz Quality Evaluation Report")
        st.markdown(st.session_state.quiz_review)
