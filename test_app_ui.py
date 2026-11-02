from unittest.mock import MagicMock
import sys
import pytest
from streamlit.testing.v1 import AppTest


def test_app_ui_rendering_and_checkbox_toggle(monkeypatch):
    sample_quiz = [
        {
            "question": "What is AI?",
            "options": [("a", "Option 1"), ("b", "Option 2"), ("c", "Option 3"), ("d", "Option 4")],
            "correct": "a"
        }
    ]
    sample_report = (
        "## Evaluation report\n\n"
        "**Report formatting regression sample**\n\n"
        "- First finding\n"
        "- Second finding\n\n"
        "A readable assessment paragraph."
    )

    # Mock the chain in sys.modules to avoid requiring external API credentials or langchain_groq
    mock_mcq_module = MagicMock()
    mock_chain = MagicMock()
    mock_mcq_module.generate_evaluate_chain = mock_chain
    monkeypatch.setitem(sys.modules, "src.mcqgenerator.MCQGenerator", mock_mcq_module)

    app = AppTest.from_file("StreamlitAPP.py")
    app.session_state["quiz_items"] = sample_quiz
    app.session_state["quiz_review"] = sample_report
    app.run()

    assert not app.exception
    assert mock_chain.invoke.call_count == 0
    assert len(app.checkbox) >= 1
    chk = app.checkbox(key="show_answers_toggle")
    assert chk.value is False

    # Toggle checkbox to True
    chk.check().run()

    assert not app.exception
    assert mock_chain.invoke.call_count == 0
    assert app.session_state["quiz_items"] == sample_quiz
    assert app.session_state["quiz_review"] == sample_report
    assert app.checkbox(key="show_answers_toggle").value is True
