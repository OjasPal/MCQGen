import ast
import html
import json
import pytest


def load_function_from_file(file_path, func_name):
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()
    tree = ast.parse(source, filename=file_path)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            code = compile(ast.Module(body=[node], type_ignores=[]), file_path, "exec")
            env = {"json": json, "html": html}
            exec(code, env)
            return env[func_name]
    raise NameError(f"Function {func_name} not found in {file_path}")


def test_parse_quiz_items_structure():
    parse_quiz_items = load_function_from_file("src/mcqgenerator/utils.py", "parse_quiz_items")
    raw_json = json.dumps({
        "1": {
            "mcq": "What is the output of 2 + 2?",
            "options": {"a": "3", "b": "4", "c": "5", "d": "6"},
            "correct": "b"
        },
        "2": {
            "mcq": "Which keyword is used for functions in Python?",
            "options": {"a": "func", "b": "def", "c": "function", "d": "define"},
            "correct": "b"
        }
    })
    parsed = parse_quiz_items(raw_json)
    assert len(parsed) == 2
    assert parsed[0]["question"] == "What is the output of 2 + 2?"
    assert parsed[0]["correct"] == "b"
    assert len(parsed[0]["options"]) == 4
    assert parsed[0]["options"][1] == ("b", "4")


def test_render_mcqs_html_escaped_and_answer_toggle():
    render_mcqs_html = load_function_from_file("src/mcqgenerator/utils.py", "render_mcqs_html")
    items = [
        {
            "question": "Is <script>alert('xss')</script> dangerous?",
            "options": [("a", "<b>Yes</b>"), ("b", "No"), ("c", "Maybe"), ("d", "None")],
            "correct": "a"
        }
    ]
    html_hidden = render_mcqs_html(items, show_answers=False)
    assert html.escape("Is <script>alert('xss')</script> dangerous?") in html_hidden
    assert "<script>" not in html_hidden
    assert html.escape("<b>Yes</b>") in html_hidden
    assert "Correct Answer:" not in html_hidden

    html_shown = render_mcqs_html(items, show_answers=True)
    assert "Correct Answer:" in html_shown
    assert "A" in html_shown or "a" in html_shown


def test_streamlit_session_state_preservation():
    with open("StreamlitAPP.py", "r", encoding="utf-8") as f:
        content = f.read()
    assert "st.session_state" in content
    assert "show_answers" in content
    assert ".stApp" in content
