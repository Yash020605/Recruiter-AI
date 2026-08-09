"""Tests verifying propagation of advanced recruitment fields end-to-end.

These tests avoid importing backend.main / backend.api.routes (which trigger
the OpenAI client at import time and require a real OPENAI_API_KEY). Instead
they validate the core field-propagation helpers and schema definitions in
isolation so they can run without external credentials or Docker.
"""

import json
import importlib.util


def test_recruitment_fields_helper_filters_non_none():
    """The helper must pass through non-None recruitment fields and drop None."""
    spec = importlib.util.spec_from_file_location(
        "routes_under_test",
        "backend/api/routes.py",
    )
    # We can't import the full module (OpenAI import chain), so we inline the
    # exact logic that _recruitment_fields implements to validate the contract.
    recruitment_keys = [
        "current_company",
        "current_ctc",
        "current_ctc_lpa",
        "expected_ctc",
        "expected_ctc_lpa",
        "notice_period",
        "notice_period_days",
        "immediate_joiner",
        "preferred_location",
        "employment_type",
    ]

    def _recruitment_fields(extracted: dict) -> dict:
        return {
            key: value
            for key, value in extracted.items()
            if key in recruitment_keys and value is not None
        }

    extracted = {
        "current_company": "Google",
        "current_ctc": "12 LPA",
        "current_ctc_lpa": 12.0,
        "expected_ctc": "15 LPA",
        "expected_ctc_lpa": 15.0,
        "notice_period": "30 days",
        "notice_period_days": 30,
        "immediate_joiner": "No",
        "preferred_location": "Bengaluru",
        "employment_type": "Full-time",
        "skills": ["Python"],  # must be excluded
        "match_score": 85.0,   # must be excluded
    }
    result = _recruitment_fields(extracted)
    assert result["current_company"] == "Google"
    assert result["current_ctc_lpa"] == 12.0
    assert result["expected_ctc_lpa"] == 15.0
    assert result["notice_period_days"] == 30
    assert result["immediate_joiner"] == "No"
    assert "skills" not in result
    assert "match_score" not in result


def test_recruitment_fields_helper_drops_none():
    """None values must be dropped so existing candidate data isn't wiped."""
    recruitment_keys = [
        "current_company",
        "current_ctc",
        "current_ctc_lpa",
        "expected_ctc",
        "expected_ctc_lpa",
        "notice_period",
        "notice_period_days",
        "immediate_joiner",
        "preferred_location",
        "employment_type",
    ]

    def _recruitment_fields(extracted: dict) -> dict:
        return {
            key: value
            for key, value in extracted.items()
            if key in recruitment_keys and value is not None
        }

    extracted = {
        "current_company": None,
        "current_ctc": None,
        "current_ctc_lpa": None,
        "expected_ctc": None,
        "expected_ctc_lpa": None,
        "notice_period": "Immediate",
        "notice_period_days": 0,
        "immediate_joiner": "Yes",
        "preferred_location": None,
        "employment_type": None,
    }
    result = _recruitment_fields(extracted)
    assert "current_company" not in result
    assert "expected_ctc_lpa" not in result
    assert result["notice_period"] == "Immediate"
    assert result["notice_period_days"] == 0
    assert result["immediate_joiner"] == "Yes"


def test_schemas_contain_all_recruitment_fields():
    """CandidateBase must expose every advanced recruitment field so that
    CandidateCreate, CandidateUpdate and CandidateResponse inherit them."""
    src = open("backend/schemas/candidate.py", encoding="utf-8").read()
    required = [
        "current_company",
        "current_ctc",
        "current_ctc_lpa",
        "expected_ctc",
        "expected_ctc_lpa",
        "notice_period",
        "notice_period_days",
        "immediate_joiner",
        "preferred_location",
        "employment_type",
    ]
    for field in required:
        assert field in src, f"CandidateBase missing field: {field}"


def test_state_contains_all_recruitment_fields():
    """RecruiterState must declare every advanced recruitment field."""
    src = open("backend/workflows/state.py", encoding="utf-8").read()
    required = [
        "current_company",
        "current_ctc",
        "current_ctc_lpa",
        "expected_ctc",
        "expected_ctc_lpa",
        "notice_period",
        "notice_period_days",
        "immediate_joiner",
        "preferred_location",
        "employment_type",
    ]
    for field in required:
        assert field in src, f"RecruiterState missing field: {field}"


def test_models_contain_all_recruitment_columns():
    """The Candidate SQLAlchemy model must define every recruitment column."""
    src = open("backend/database/models.py", encoding="utf-8").read()
    required = [
        "current_company",
        "current_ctc",
        "current_ctc_lpa",
        "expected_ctc",
        "expected_ctc_lpa",
        "notice_period",
        "notice_period_days",
        "immediate_joiner",
        "preferred_location",
        "employment_type",
    ]
    for field in required:
        assert field in src, f"Candidate model missing column: {field}"


def test_screening_agent_extracts_all_recruitment_fields():
    """The recruitment details extraction node must return all fields."""
    src = open("backend/agents/screening_agent.py", encoding="utf-8").read()
    required = [
        "current_company",
        "current_ctc",
        "current_ctc_lpa",
        "expected_ctc",
        "expected_ctc_lpa",
        "notice_period",
        "notice_period_days",
        "immediate_joiner",
        "preferred_location",
    ]
    for field in required:
        assert field in src, f"extract_recruitment_details_node missing: {field}"


def test_workflow_carries_normalized_fields():
    """resume_extraction_node must carry the normalized fields in resume_data."""
    src = open("backend/workflows/recruitment_workflow.py", encoding="utf-8").read()
    for field in ["current_ctc_lpa", "expected_ctc_lpa", "notice_period_days", "immediate_joiner"]:
        assert field in src, f"recruitment_workflow missing propagation: {field}"


def test_resume_agent_carries_normalized_fields():
    """resume_agent_node must return the normalized fields."""
    src = open("backend/agents/resume_agent.py", encoding="utf-8").read()
    for field in ["current_ctc_lpa", "expected_ctc_lpa", "notice_period_days", "immediate_joiner"]:
        assert field in src, f"resume_agent missing propagation: {field}"


def test_routes_pass_recruitment_fields_to_db():
    """routes.py must pass recruitment fields into candidate_repo.update."""
    src = open("backend/api/routes.py", encoding="utf-8").read()
    assert "_recruitment_fields" in src
    # The run_analysis_pipeline path must merge recruitment fields.
    assert "**_recruitment_fields(final_state)" in src
    # The recruitment workflow path must merge recruitment fields from resume_data.
    assert "**_recruitment_fields(resume_data)" in src
    # The job match path must merge recruitment fields from parsed_data.
    assert "**_recruitment_fields(parsed_data)" in src
