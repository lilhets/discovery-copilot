# ADR 0001: Stable IDs and run_state versioning

Date: 2026-10-29
Status: accepted

## Context

The roadmap includes multi-meeting updates: each new transcript updates `run_state` and moves the architecture from v0 to v1 with a changelog. To write that changelog, the copilot has to refer to individual items across meetings ("Q3 was answered in meeting 2", "R5 was contradicted"). Adding this after steps 1 and 2 ship would mean changing their schemas, prompts and gold answers.

## Options

1. Add IDs and versioning only when multi-meeting support is built.
2. Add them now, in the step 1 and step 2 schemas.

## Decision

Option 2. From the first version of the schemas:

- Requirements have stable IDs `R1`, `R2`, ... and questions `Q1`, `Q2`, ... An ID is never renumbered or reused, even when an item is dropped in a later meeting.
- Questions have a `status` (`open` / `answered`). An answered question also has `answered_in`, the version of the meeting that answered it.
- `run_state` has a `version`: `v0` after the first meeting, then `v1`, `v2`, ...

## Consequences

- Components (`requirement_ids[]`) and questions (`requirement_ids[]`) can point to requirements by ID from the start.
- JSON Schema can't check that IDs are unique or stable across versions. The pipeline code and the eval harness must check that.
- Gold answers in `transcripts/gold/` use the same IDs. When scoring, match requirements by content, not by ID number, because the model may number them differently from the gold file.
- Later, multi-meeting support will probably need a status on requirements as well (for example `active` / `contradicted`). That will be a follow-up ADR.
