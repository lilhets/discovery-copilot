"""Checks on step outputs: JSON schema first, then what the schema can't express (ADR 0001)."""
import json
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

SCHEMAS_DIR = Path(__file__).resolve().parents[1] / "schemas"


def _registry():
    registry = Registry()
    for path in SCHEMAS_DIR.glob("*.schema.json"):
        schema = json.loads(path.read_text())
        registry = registry.with_resource(schema["$id"], Resource.from_contents(schema))
    return registry


def validate_requirements(data, transcript):
    """Return a list of problems. Empty list means the output is usable."""
    schema = json.loads((SCHEMAS_DIR / "requirements.schema.json").read_text())
    validator = Draft202012Validator(schema, registry=_registry())
    errors = [f"{'/'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in validator.iter_errors(data)]
    if errors:
        return errors

    ids = [r["id"] for r in data["requirements"]]
    duplicates = sorted({i for i in ids if ids.count(i) > 1})
    if duplicates:
        errors.append(f"duplicate ids: {', '.join(duplicates)}")
    for r in data["requirements"]:
        if r["evidence_quote"] not in transcript:
            errors.append(f"{r['id']}: evidence_quote not found verbatim in transcript")
    return errors
