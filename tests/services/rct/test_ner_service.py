import os
import pytest
from src.services.rct.ner_service import run_ner_on_document, classify_category

# Create a temporary sample text file for testing
@pytest.fixture
def sample_text_file(tmp_path):
    file_path = tmp_path / "sample_doc.txt"
    content = (
        "Banks must maintain a minimum CET1 ratio of 4.5%.\n"
        "The leverage ratio shall not fall below 3%.\n"
        "Liquidity Coverage Ratio (LCR) should be at least 100%.\n"
        "Board members are required to oversee compliance.\n"
        "This is a general sentence with no obligation."
    )
    file_path.write_text(content, encoding="utf-8")
    return str(file_path)


def test_classify_category_capital():
    text = "Banks must maintain a minimum CET1 ratio of 4.5%."
    category = classify_category(text)
    assert category == "capital"


def test_classify_category_liquidity():
    text = "Liquidity Coverage Ratio (LCR) should be at least 100%."
    category = classify_category(text)
    assert category == "liquidity"


def test_run_ner_on_document_extraction(sample_text_file):
    results = run_ner_on_document(sample_text_file)

    # Ensure requirements were extracted
    assert len(results) >= 3

    # Check structure of first requirement
    first_req = results[0]
    assert "section_ref" in first_req
    assert "text" in first_req
    assert "category" in first_req
    assert "priority" in first_req
    assert "numbers" in first_req

    # Ensure the first requirement is tagged as capital
    assert results[0]["category"] == "capital"

    # Ensure a liquidity requirement exists
    liquidity_reqs = [r for r in results if r["category"] == "liquidity"]
    assert len(liquidity_reqs) > 0


def test_priorities_assigned(sample_text_file):
    results = run_ner_on_document(sample_text_file)
    priorities = {r["priority"] for r in results}

    # Must have at least high and medium priorities
    assert "high" in priorities
    assert "medium" in priorities
