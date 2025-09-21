import os
import pytest
from src.services.rct.ner_service import run_ner_on_document, classify_category

# Create a temporary sample text file for testing
@pytest.fixture
def sample_text_file(tmp_path):
    file_path = tmp_path / "sample_doc.txt"
    content = (
        """1.
        This document, together with the document Basel III: International framework for
        liquidity risk measurement, standards and monitoring, presents the Basel Committee’s1
        reforms to strengthen global capital and liquidity rules with the goal of promoting a more
        resilient banking sector.The objective of the reforms is to improve the banking sector’s ability
        to absorb shocks arising from financial and economic stress, whatever the source, thus
        reducing the risk of spillover from the financial sector to the real economy.This document
        sets out the rules text and timelines to implement the Basel III framework.
        2.
        The Committee’s comprehensive reform package addresses the lessons of the
        financial crisis.Through its reform package, the Committee also aims to improve risk
        management and governance as well as strengthen banks’ transparency and disclosures.2
        Moreover, the reform package includes the Committee’s efforts to strengthen the resolution
        of systemically significant cross-border banks.3
        3.
        A strong and resilient banking system is the foundation for sustainable economic
        growth, as banks are at the centre of the credit intermediation process between savers and
        investors.Moreover, banks provide critical services to consumers, small and medium-sized
        enterprises, large corporate firms and governments who rely on them to conduct their daily
        business, both at a domestic and international level.
        4.
        One of the main reasons the economic and financial crisis, which began in 2007,
        became so severe was that the banking sectors of many countries had built up excessive on-
        and off-balance sheet leverage.This was accompanied by a gradual erosion of the level and
        quality of the capital base.At the same time, many banks were holding insufficient liquidity
        buffers.The banking system therefore was not able to absorb the resulting systemic trading
        and credit losses nor could it cope with the reintermediation of large off-balance sheet
        exposures that had built up in the shadow banking system.The crisis was further amplified
        by a procyclical deleveraging process and by the interconnectedness of systemic institutions
        through an array of complex transactions.During the most severe episode of the crisis, the
        market lost confidence in the solvency and liquidity of many banking institutions.The
        weaknesses in the banking sector were rapidly transmitted to the rest of the financial system
        and the real economy, resulting in a massive contraction of liquidity and credit availability.
        Ultimately the public sector had to step in with unprecedented injections of liquidity, capital
        support and guarantees, exposing taxpayers to large losses."""
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
    print(results)
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
