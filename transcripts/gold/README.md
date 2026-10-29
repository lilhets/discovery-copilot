# Gold files

Expected answers for each scenario: requirements, key missing information and planted issues.

One JSON file per scenario, same name as the transcript:

- `requirements`: expected step 1 output. Must validate against `schemas/requirements.schema.json`. When scoring, match by content, not by ID number.
- `missing_info`: information the transcript leaves out on purpose. Step 2 should ask about each item. `blocking` marks the ones the design can't move forward without.
- `should_not_extract`: things mentioned in the call that are not requirements (out of scope, future ideas). Extracting them counts against precision.

Every `evidence_quote` is copied verbatim from the transcript.
