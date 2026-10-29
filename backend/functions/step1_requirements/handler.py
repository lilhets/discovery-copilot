"""Step 1: extract requirements from a transcript.

Local run:
    python backend/functions/step1_requirements/handler.py transcripts/scenarios/01_ludora.txt
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "backend"))

from llm import call_llm  # noqa: E402
from validation import validate_requirements  # noqa: E402

PROMPT_VERSION = "step1_requirements.v1"


def run_step1(transcript):
    system = (ROOT / "prompts" / f"{PROMPT_VERSION}.md").read_text()
    user = f"<transcript>\n{transcript}\n</transcript>"
    result = call_llm(system, user)

    try:
        output = json.loads(result.text)
        errors = validate_requirements(output, transcript)
    except json.JSONDecodeError as e:
        output, errors = None, [f"invalid JSON: {e}"]

    return {
        "step": "step1_requirements",
        "prompt_version": PROMPT_VERSION,
        "provider": result.provider,
        "model": result.model,
        "usage": {"input_tokens": result.input_tokens, "output_tokens": result.output_tokens},
        "latency_s": result.latency_s,
        "valid": not errors,
        "errors": errors,
        "output": output,
        "raw_text": None if output else result.text,
    }


def lambda_handler(event, context):
    return run_step1(event["transcript"])


if __name__ == "__main__":
    transcript_path = Path(sys.argv[1])
    run = run_step1(transcript_path.read_text())
    run["transcript"] = str(transcript_path)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = ROOT / "eval" / "runs" / f"{stamp}_{transcript_path.stem}_step1.json"
    out.write_text(json.dumps(run, indent=2, ensure_ascii=False) + "\n")

    print(f"valid={run['valid']} tokens in/out={run['usage']['input_tokens']}/{run['usage']['output_tokens']} "
          f"latency={run['latency_s']}s -> {out.relative_to(ROOT)}")
    for e in run["errors"]:
        print("  -", e)
