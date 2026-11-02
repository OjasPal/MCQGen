import os
import json
import PyPDF2
import traceback

def read_file(file):
    if file.name.endswith(".pdf"):
        try:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted
            return text
        except Exception as e:
            raise Exception(f"error reading the PDF file: {e}")

    elif file.name.endswith(".txt"):
        return file.read().decode("utf-8")

    else:
        raise Exception(
            "unsupported file format only pdf and text file suppoted"
        )

import html

def parse_quiz_items(quiz_input):
    try:
        if isinstance(quiz_input, dict):
            quiz_dict = quiz_input
        else:
            quiz_dict = json.loads(quiz_input)

        items = []
        for key, value in quiz_dict.items():
            mcq = value.get("mcq", "")
            raw_opts = value.get("options", {})
            options = [(opt_key, opt_val) for opt_key, opt_val in raw_opts.items()]
            correct = value.get("correct", "")
            items.append({"question": mcq, "options": options, "correct": correct})
        return items
    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__)
        return []

def render_mcqs_html(quiz_items, show_answers=False):
    cards = []
    for idx, item in enumerate(quiz_items, start=1):
        q_text = html.escape(str(item.get("question", "")))
        correct_val = html.escape(str(item.get("correct", "")))
        options_html = []
        for opt_key, opt_text in item.get("options", []):
            escaped_key = html.escape(str(opt_key).upper())
            escaped_val = html.escape(str(opt_text))
            options_html.append(
                f'<div class="mcq-option"><span class="mcq-opt-key">{escaped_key}</span> <span class="mcq-opt-val">{escaped_val}</span></div>'
            )
        opts_str = "\n".join(options_html)
        answer_badge = f'<div class="mcq-correct-badge">✓ Correct Answer: {correct_val}</div>' if show_answers else ""
        cards.append(f'''<div class="mcq-card">
            <div class="mcq-header">
                <div class="mcq-title-row">
                    <span class="mcq-qnum">Q{idx}</span>
                    <span class="mcq-qtext">{q_text}</span>
                </div>
                {answer_badge}
            </div>
            <div class="mcq-options-grid">{opts_str}</div>
        </div>''')
    return "\n".join(cards)

def get_table_data(quiz_str):
    try:
        # convert the quiz from a str to dict
        quiz_dict = json.loads(quiz_str)
        quiz_table_data = []

        # iterate over the quiz dictionary and extract the required information
        for key, value in quiz_dict.items():
            mcq = value["mcq"]
            options = " || ".join(
                [
                    f"{option}-> {option_value}" for option, option_value in value["options"].items()
                ]
            )

            correct = value["correct"]
            quiz_table_data.append({"MCQ": mcq, "Choices": options, "Correct": correct})

        return quiz_table_data

    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__)
        return False
