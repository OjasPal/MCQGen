# 📝 MCQGen — AI-Powered MCQ Generator

MCQGen is a simple end-to-end GenAI project that takes a PDF or text file as input and automatically generates multiple-choice questions (MCQs) from its content using an LLM.

**Live App:**  [https://mcqgen-xaa35jepbrgpecswqhpqi5.streamlit.app/](https://mcqgen-xaa35jepbrgpecswqhpqi5.streamlit.app/)


## ✨ Features

- Upload a `.pdf` or `.txt` file as source material
- Choose the number of MCQs, subject, and complexity level
- Automatically generates MCQs with 4 options and the correct answer
- Displays results in a clean table, along with an AI-generated review of question quality
- Built entirely with open-source/free-tier tools — no paid APIs required

## 🛠️ Tech Stack

- **LangChain** (LCEL) — chaining prompts and LLM calls
- **Groq API** — fast LLM inference (using an open-source model served via Groq)
- **Streamlit** — web app interface and deployment
- **PyPDF2** — PDF text extraction
- **Python-dotenv** — environment variable management

## ⚙️ How It Works

1. User uploads a PDF/TXT file and specifies the number of questions, subject, and tone
2. The app extracts raw text from the uploaded file
3. A LangChain pipeline sends the text to an LLM (via Groq) with a structured prompt, asking it to generate MCQs in a fixed JSON format
4. A second chain step reviews the generated quiz for quality and complexity
5. The final quiz is parsed and displayed as a table, with the review shown alongside

## 🏗️ Architecture

```text
User Upload (PDF/TXT) ──► read_file() ──► Raw Text
                                              │
                                              ▼
              quiz_generation_prompt ──► LLM (Groq) ──► Raw JSON
                                              │
                                              ▼
                                      clean_json_output()
                                              │
                                              ▼
        quiz_evaluation_prompt ──► LLM (Groq) ──► Quiz Review
                                              │
                                              ▼
                get_table_data() ──► Streamlit UI (Table + Review)
```

## 📦 Installation (Run Locally)

```bash
# Clone the repository
git clone https://github.com/OjasPal/mcqgen.git
cd mcqgen

# Create and activate a virtual environment
conda create -n mcqgen python=3.12 -y
conda activate mcqgen

# Install dependencies
pip install -r dev-requirements.txt

# Add your Groq API key
# Create a .env file in the root directory with:
# GROQ_API_KEY=your_key_here

# Run the app
streamlit run StreamlitAPP.py
```

**Note:** `requirements.txt` is used for Streamlit Cloud deployment (excludes `-e .`, which Streamlit Cloud can't resolve). `dev-requirements.txt` includes `-e .` for local development, installing the project itself as an editable package.

## 🔑 Environment Variables

Create a `.env` file in the project root with:

GROQ_API_KEY=your_groq_api_key_here

Get a free API key at (https://console.groq.com).

## 📁 Project Structure

```text
mcqgen/
├── src/
│   └── mcqgenerator/
│       ├── MCQGenerator.py   # LangChain chain logic (quiz + review chains)
│       ├── utils.py          # File reading & response parsing
│       └── logger.py         # Logging configuration
├── StreamlitAPP.py           # Streamlit frontend
├── Response.json             # Expected MCQ JSON structure template
├── requirements.txt          # For Streamlit Cloud deployment
├── dev-requirements.txt      # For local development (includes -e .)
└── README.md
```


## 🎯 What I Learned

This project was my introduction to building real GenAI applications, including:
- Working with LangChain's LCEL (`RunnablePassthrough`, chained prompts)
- Prompt engineering for structured JSON output
- Handling and cleaning inconsistent LLM outputs (e.g., markdown-wrapped JSON)
- Deploying a Python app to Streamlit Community Cloud
- Managing secrets safely with `.env` and `.gitignore`

## 🔮 Future Improvements

- Support for larger documents using text chunking
- Difficulty-based question filtering
- Export quiz results as PDF/CSV

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---
Built by [Ojas Pal](https://github.com/OjasPal) as part of my AI/GenAI learning journey.
