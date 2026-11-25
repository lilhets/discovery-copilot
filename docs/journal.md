# Journal

One line per work session: date, what was done, next step, blockers.

- 2026-10-22: AWS account set up (IAM Identity Center, CLI SSO profile, Budgets alarm at 10 USD/month). Repo structure created. Next: unblock Bedrock quota and make a first model call.
- 2026-11-24: Got step 1 running locally against Bedrock (Nova Lite, eu-west-3). First runs failed: the model wrapped its JSON in a code fence, then rewrote some quotes (capital letters, stitched sentences, one quote taken from the presales side). Added fence handling, made the quote check ignore case and edge punctuation, and wrote prompt v2 with stricter quote rules. v2 run on Ludora is valid. Next: score it.
- 2026-11-25: First scored run, v2 on Ludora: recall 0.67, precision 1.0, 2230/833 tokens, 4.8 s. Nothing invented, but it misses 4 requirements (image volume, personal data, Stripe, managed services). My guess is the "background facts" rule in the prompt makes it drop facts about the existing setup and the team. Next: prompt v3 on that rule only, then score all 4 scenarios, not just Ludora.
