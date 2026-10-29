"""Recompute the complete confirmatory analysis without modifying recorded outputs."""

import hashlib
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.v2.analyze import analyze, write_outputs


def portable(value):
    if isinstance(value, dict):
        return {key: portable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [portable(item) for item in value]
    if isinstance(value, str):
        return value.removeprefix(str(ROOT) + "/")
    return value


def main():
    frozen = json.loads((ROOT / "preregistration/FROZEN.json").read_text())
    digest = hashlib.sha256((ROOT / "preregistration/preregistration.md").read_bytes()).hexdigest()
    if digest != frozen["prereg_sha256"]:
        raise SystemExit("FAIL: preregistration checksum mismatch")
    recorded = json.loads((ROOT / "data/v2/analysis/confirm/results.json").read_text())
    reproduced = analyze("confirm")
    # These fields describe execution provenance, not statistical output.
    provenance = ("executed_utc", "analysis_code_sha256", "code_revision")
    differences = {key: {"recorded": recorded["metadata"][key],
                         "reproduced": reproduced["metadata"][key]}
                   for key in provenance if recorded["metadata"][key] != reproduced["metadata"][key]}
    with tempfile.TemporaryDirectory(prefix=".reproduce-", dir=ROOT) as directory:
        write_outputs(reproduced, directory)
        expected, actual = portable(recorded), portable(reproduced)
        for key in provenance:
            expected["metadata"].pop(key)
            actual["metadata"].pop(key)
        if actual != expected:
            raise SystemExit("FAIL: scientific outputs or non-exempt metadata differ")
        print("PASS: all scientific outputs and non-exempt metadata match exactly")
        print("Normalized repository-root prefixes in paths; provenance differences:")
        print(json.dumps(differences, indent=2))
        print("Temporary results, report and figures removed after comparison.")


if __name__ == "__main__":
    main()
