from unittest.mock import MagicMock
import sys
import pytest
from streamlit.testing.v1 import AppTest


def test_updated_quiz_section_removed_from_ui(monkeypatch):
    sample_quiz = [
        {
            "question": "What is AI?",
            "options": [("a", "Option 1"), ("b", "Option 2"), ("c", "Option 3"), ("d", "Option 4")],
            "correct": "a"
        }
    ]
    sample_report_with_updated_quiz = (
        "## Evaluation report\n\n"
        "**Report formatting regression sample**\n\n"
        "- First finding\n"
        "- Second finding\n\n"
        "A readable assessment paragraph.\n\n"
        "### Updated Quiz:\n"
        "{\"1\": {\"mcq\": \"New question\", \"options\": {\"a\": \"1\", \"b\": \"2\"}, \"correct\": \"a\"}}"
    )

    mock_mcq_module = MagicMock()
    mock_chain = MagicMock()
    mock_mcq_module.generate_evaluate_chain = mock_chain
    monkeypatch.setitem(sys.modules, "src.mcqgenerator.MCQGenerator", mock_mcq_module)

    app = AppTest.from_file("StreamlitAPP.py")
    app.session_state["quiz_items"] = sample_quiz
    app.session_state["quiz_review"] = sample_report_with_updated_quiz
    app.run()

    assert not app.exception
    assert mock_chain.invoke.call_count == 0

    rendered_text = " ".join([m.value for m in app.markdown])
    assert "Updated Quiz" not in rendered_text
    assert "Report formatting regression sample" in rendered_text

    chk = app.checkbox(key="show_answers_toggle")
    assert chk.value is False
    chk.check().run()

    assert not app.exception
    assert mock_chain.invoke.call_count == 0
    rendered_text_after = " ".join([m.value for m in app.markdown])
    assert "Updated Quiz" not in rendered_text_after
