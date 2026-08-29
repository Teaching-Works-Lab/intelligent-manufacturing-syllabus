from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

from curriculum_core.io import load_program
from curriculum_core.query import prepare_syllabus, trace_course
from curriculum_core.render import render_query


ROOT = Path(__file__).parents[1]
PROGRAM = ROOT / "data" / "program.json"


def test_python_syllabus_uses_only_official_or_pending_fields():
    program = load_program(PROGRAM)
    result = prepare_syllabus(program, "25JD21402")

    assert result["program_edition"] == "2025"
    assert result["official_course"]["title"] == "工程建模与科学计算可视化基础（Python）"
    assert result["official_course"]["credits"] == 2
    assert result["official_course"]["hours"]["total_hours"] == 32
    assert result["official_course"]["semester"] == 2
    assert result["official_course"]["assessment"] == "考查"
    assert result["official_course"]["offering_unit"] == "机械学院"
    assert set(result["pending_syllabus_fields"].values()) == {"待编制"}
    assert {
        "course_objectives",
        "teaching_content",
        "schedule",
        "textbooks",
        "assessment_details",
    } == set(result["pending_syllabus_fields"])


def test_robot_query_separates_official_indicators_from_derived_objective_paths():
    program = load_program(PROGRAM)
    result = trace_course(program, "机器人技术与应用（A）")

    assert result["program_edition"] == "2025"
    assert {item["target"] for item in result["official_indicator_relations"]} == {
        "1.2", "3.1", "3.2", "4.1", "4.2", "5.1", "5.2", "7.2", "10.1", "12.1", "12.2"
    }
    assert all(item["type"] == "course_supports_indicator" for item in result["official_indicator_relations"])
    assert all(item["provenance"]["source_kind"] == "official_direct" for item in result["official_indicator_relations"])
    assert {item["target"] for item in result["derived_objective_relations"]} == {"OBJ-1", "OBJ-2", "OBJ-3", "OBJ-4"}
    assert all(item["source_kind"] == "derived_transitive" for item in result["derived_objective_relations"])
    assert all(len(item["via"]) == 2 for item in result["derived_objective_relations"])
    markdown = render_query(result)
    assert "数据版本：2025" in markdown
    assert "## 官方指标点支撑" in markdown
    assert "## 派生培养目标路径" in markdown
    assert "- 25JD31403 -> OBJ-2（经由 1.2 -> GR-1）" in markdown
    assert "- 25JD31403 -> OBJ-2（经由 3.1 -> GR-3）" in markdown
    objective_two_paths = [item for item in result["derived_objective_relations"] if item["target"] == "OBJ-2"]
    rendered_objective_two_paths = [line for line in markdown.splitlines() if line.startswith("- 25JD31403 -> OBJ-2（经由 ")]
    assert len(rendered_objective_two_paths) == len(objective_two_paths)
    assert len(set(rendered_objective_two_paths)) == len(objective_two_paths)


def test_out_of_scope_course_is_declined_and_routed_to_factory():
    result = subprocess.run(
        [sys.executable, "scripts/curriculum.py", "query", "data/program.json", "--course", "临床医学导论"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 2
    assert result.stdout == ""
    assert "超出智能制造工程 2025 版数据集" in result.stderr
    assert "training-program-skill-factory" in result.stderr


def test_query_rendering_is_deterministic():
    command = [sys.executable, "scripts/curriculum.py", "query", "data/program.json", "--course", "25JD31403", "--format", "markdown"]
    first = subprocess.run(command, cwd=ROOT, check=True, capture_output=True).stdout
    second = subprocess.run(command, cwd=ROOT, check=True, capture_output=True).stdout
    assert first == second


def test_bundled_program_satisfies_bundled_json_schema():
    import jsonschema

    program = json.loads(PROGRAM.read_text(encoding="utf-8"))
    schema = json.loads((ROOT / "references" / "program.schema.json").read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(program)


def test_generation_metadata_discloses_factory_commit_and_template_digest():
    metadata = json.loads((ROOT / "generated-from.json").read_text(encoding="utf-8"))
    assert metadata["factory_commit"] == "af96d38ab1b8f1d63caf20646f2317c14879f744"
    assert metadata["template_digest"] == "sha256:0e1341f2228e4cfc8810df608edea9e0ae8e0f0a213c3770f69665a29aa1daea"
    assert re.fullmatch(r"sha256:[0-9a-f]{64}", metadata["template_digest"])
    assert metadata["template_digest_algorithm"].startswith("sha256(canonical JSON array")
    assert metadata["source_program"] == "data/program.json"
    assert metadata["source_schema_version"] == "1.0.0"
    assert metadata["template"] == "syllabus-skill"
    assert metadata["validator"] == "curriculum_core.validation.validate_program"


def test_public_manifest_matches_bundled_program_and_documents_exist():
    program = json.loads(PROGRAM.read_text(encoding="utf-8"))
    manifest = json.loads((ROOT / "data" / "manifest.public.json").read_text(encoding="utf-8"))

    assert manifest["program_sha256"] == hashlib.sha256(PROGRAM.read_bytes()).hexdigest()
    assert manifest["counts"] == {
        "training_objectives": len(program["training_objectives"]),
        "graduation_requirements": len(program["graduation_requirements"]),
        "indicators": len(program["indicators"]),
        "courses": len(program["courses"]),
        "course_groups": len(program["course_groups"]),
        "relations": len(program["relations"]),
    }
    assert (ROOT / "data" / "course-catalog.md").is_file()
    assert (ROOT / "data" / "validation-report.md").is_file()
    assert (ROOT / "ANONYMIZATION.md").is_file()
