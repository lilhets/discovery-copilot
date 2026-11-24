"""Step output checks: JSON schema, unique IDs, verbatim quotes."""
import json
import re
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

SCHEMAS_DIR = Path(__file__).resolve().parents[1] / "schemas"
_EDGE_CHARS = " .,;:!?\"'«»()[]-…"


def _registry():
    registry = Registry()
    for path in SCHEMAS_DIR.glob("*.schema.json"):
        schema = json.loads(path.read_text())
        registry = registry.with_resource(schema["$id"], Resource.from_contents(schema))
    return registry


def _normalize(text):
    text = text.replace("\u2019", "'").replace("\u2018", "'").replace("\u201c", '"').replace("\u201d", '"')
    return re.sub(r"\s+", " ", text).lower()


def quote_in_transcript(quote, transcript):
    """Verbatim match, ignoring case, whitespace and punctuation at the quote's edges."""
    q = _normalize(quote).strip(_EDGE_CHARS)
    return bool(q) and q in _normalize(transcript)


def validate_requirements(data, transcript):
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
        if not quote_in_transcript(r["evidence_quote"], transcript):
            errors.append(f"{r['id']}: evidence_quote not found verbatim in transcript")
    return errors
