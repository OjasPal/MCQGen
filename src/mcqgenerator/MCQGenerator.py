import os
import json
import streamlit as st
import pandas as pd
import traceback
from dotenv import load_dotenv, find_dotenv
from src.mcqgenerator.utils import read_file, get_table_data
from src.mcqgenerator.logger import logging

#Importing necessary packages from langchain
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.callbacks import UsageMetadataCallbackHandler
from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables import RunnableLambda

load_dotenv()

KEY=os.getenv("GROQ_API_KEY") or st.secrets["GROQ_API_KEY"]

llm = ChatGroq(groq_api_key=KEY, model_name="openai/gpt-oss-20b", temperature=0.7)

import re
def clean_json_output(text: str) -> str:
    text = re.sub(r"^```(?:json)?\s*", "", text.strip())
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


TEMPLATE="""
Text:{text}
You are an expert MCQ maker. Given the above text, it is your job to \
create a quiz of {number} multiple choice questions for {subject} students in {tone} tone.
Make sure the questions are not repeated and check all the questions to be conforming the text as well.
Make sure to format your response like RESPONSE_JSON below and use it as a guide. \
Ensure to make {number} MCQs
### RESPONSE_JSON
{response_json}

"""

quiz_generation_prompt = PromptTemplate(
    input_variables=["text", "number", "subject", "tone", "response_json"],
    template=TEMPLATE
)

quiz_chain = quiz_generation_prompt | llm | StrOutputParser() |  RunnableLambda(clean_json_output)

TEMPLATE2="""
You are an expert english grammarian and writer. Given a Multiple Choice Quiz for {subject} students.\
You need to evaluate the complexity of the question and give a complete analysis of the quiz. Only use at max 50 words for complexity
if the quiz is not at per with the cognitive and analytical abilities of the students,\
update the quiz questions which needs to be changed and change the tone such that it perfectly fits the student abilities
Quiz_MCQs:
{quiz}

Check from an expert English Writer of the above quiz:
"""

quiz_evaluation_prompt = PromptTemplate(
    input_variables=["subject", "quiz"],
    template=TEMPLATE2
)

review_chain = quiz_evaluation_prompt | llm | StrOutputParser()

generate_evaluate_chain = (
    RunnablePassthrough.assign(quiz=quiz_chain)
    | RunnablePassthrough.assign(review=review_chain)
)