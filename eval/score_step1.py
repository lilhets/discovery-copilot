"""Score a step 1 run against its gold file: requirement recall and precision.

Matching is by content, not by ID number (ADR 0001), and it is checked by hand:

1. python eval/score_step1.py eval/runs/<run>.json
   First call: writes eval/matches/<run>.json with a suggested match for each predicted
   requirement (gold ID, or null when nothing in the gold fits). Review and fix it by hand.
2. python eval/score_step1.py eval/runs/<run>.json
   Once the matches file exists: computes the metrics from it.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def words(text):
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def similarity(a, b):
    wa = words(a["statement"] + " " + a["evidence_quote"])
    wb = words(b["statement"] + " " + b["evidence_quote"])
    return len(wa & wb) / len(wa | wb) if wa | wb else 0.0


def suggest(predicted, gold):
    matches = {}
    for p in predicted:
        best = max(gold, key=lambda g: similarity(p, g), default=None)
        score = similarity(p, best) if best else 0.0
        matches[p["id"]] = {
            "gold_id": best["id"] if best and score >= 0.2 else None,
            "similarity": round(score, 2),
            "predicted": p["statement"],
            "gold": best["statement"] if best else None,
        }
    return matches


def score(matches, gold):
    gold_ids = [g["id"] for g in gold]
    found = set()
    true_positives = 0
    for m in matches.values():
        if m["gold_id"] in gold_ids and m["gold_id"] not in found:
            found.add(m["gold_id"])
            true_positives += 1
    n_pred = len(matches)
    return {
        "gold": len(gold_ids),
        "predicted": n_pred,
        "true_positives": true_positives,
        "recall": round(len(found) / len(gold_ids), 2) if gold_ids else None,
        "precision": round(true_positives / n_pred, 2) if n_pred else None,
        "missed": [i for i in gold_ids if i not in found],
        "unmatched_predictions": [pid for pid, m in matches.items() if m["gold_id"] not in gold_ids],
    }


def main(run_path):
    run = json.loads(run_path.read_text())
    if not run["valid"]:
        sys.exit(f"Run is not valid, nothing to score: {run['errors']}")
    scenario = Path(run["transcript"]).stem
    gold = json.loads((ROOT / "transcripts" / "gold" / f"{scenario}.json").read_text())["requirements"]
    predicted = run["output"]["requirements"]

    matches_path = ROOT / "eval" / "matches" / run_path.name
    if not matches_path.exists():
        matches_path.parent.mkdir(exist_ok=True)
        matches_path.write_text(json.dumps(suggest(predicted, gold), indent=2, ensure_ascii=False) + "\n")
        print(f"Suggested matches written to {matches_path.relative_to(ROOT)}. Review them, then run again.")
        return

    result = score(json.loads(matches_path.read_text()), gold)
    result["usage"] = run["usage"]
    result["latency_s"] = run["latency_s"]
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main(Path(sys.argv[1]))
