from __future__ import annotations

import copy
import json

import pytest

from verify_public_equivalence import compare_programs


def private_fixture() -> dict:
    return {
        "program": {
            "title": "Named School Intelligent Manufacturing",
            "institution": "Named School",
            "college": "Named College",
            "major": "智能制造工程",
            "major_code": "080213T",
        },
        "courses": [{"id": "C-1", "credits": 2, "offering_unit": "机械学院"}],
        "relations": [
            {
                "source": "C-1",
                "target": "1.1",
                "type": "course_supports_indicator",
                "provenance": {"source_file_hash": "private-hash", "source_symbol": "●", "review_decision_id": "R-1"},
            }
        ],
        "source": {"canonical_relative_path": "private/source.pdf", "sha256": "private-hash"},
    }


def public_fixture() -> dict:
    value = private_fixture()
    value["program"].update(
        title="示例高校智能制造工程本科专业人才培养方案（2025版）",
        institution="示例高校",
        college="示例工学院",
    )
    value["source"].update(canonical_relative_path="private-source/智能制造工程-2025.pdf", sha256="0" * 64)
    value["relations"][0]["provenance"]["source_file_hash"] = "0" * 64
    return value


def test_compare_masks_only_the_anonymization_allowlist():
    result = compare_programs(private_fixture(), public_fixture())
    assert result["unapproved_differences"] == []
    assert set(result["approved_differences"]) == {
        "/program/title",
        "/program/institution",
        "/program/college",
        "/source/canonical_relative_path",
        "/source/sha256",
        "/relations/0/provenance/source_file_hash",
    }


def test_compare_blocks_course_or_relationship_changes():
    altered = public_fixture()
    altered["courses"][0]["credits"] = 3
    altered["relations"][0]["provenance"]["source_symbol"] = "○"
    result = compare_programs(private_fixture(), altered)
    assert result["unapproved_differences"] == [
        "/courses/0/credits",
        "/relations/0/provenance/source_symbol",
    ]
