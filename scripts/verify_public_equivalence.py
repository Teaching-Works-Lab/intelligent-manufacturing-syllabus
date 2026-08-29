"""Block every private/public program difference outside the anonymization allowlist."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ALLOWLIST = (
    re.compile(r"^/program/(institution|college|title)$"),
    re.compile(r"^/source/(canonical_relative_path|original_filename|sha256)$"),
    re.compile(r"^/relations/\d+/provenance/source_file_hash$"),
)


def _escape(token: Any) -> str:
    return str(token).replace("~", "~0").replace("/", "~1")


def _differences(left: Any, right: Any, path: str = "") -> list[str]:
    if type(left) is not type(right):
        return [path or "/"]
    if isinstance(left, dict):
        paths = []
        for key in sorted(set(left) | set(right)):
            child = f"{path}/{_escape(key)}"
            if key not in left or key not in right:
                paths.append(child)
            else:
                paths.extend(_differences(left[key], right[key], child))
        return paths
    if isinstance(left, list):
        paths = []
        for index in range(max(len(left), len(right))):
            child = f"{path}/{index}"
            if index >= len(left) or index >= len(right):
                paths.append(child)
            else:
                paths.extend(_differences(left[index], right[index], child))
        return paths
    return [] if left == right else [path or "/"]


def _allowed(path: str) -> bool:
    return any(pattern.fullmatch(path) for pattern in ALLOWLIST)


def compare_programs(private: dict, public: dict) -> dict[str, list[str]]:
    differences = sorted(_differences(private, public))
    approved = [path for path in differences if _allowed(path)]
    unapproved = [path for path in differences if not _allowed(path)]
    return {
        "approved_differences": approved,
        "unapproved_differences": unapproved,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("private", type=Path)
    parser.add_argument("public", type=Path)
    args = parser.parse_args()
    private = json.loads(args.private.read_text(encoding="utf-8-sig"))
    public = json.loads(args.public.read_text(encoding="utf-8-sig"))
    result = compare_programs(private, public)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result["unapproved_differences"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
