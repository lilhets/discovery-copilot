# Journal

One line per work session: date, what was done, next step, blockers.

- 2026-10-22: AWS account set up (IAM Identity Center, CLI SSO profile, Budgets alarm at 10 USD/month). Repo structure created. Next: unblock Bedrock quota and make a first model call.

## 2026-11-08: Bedrock unblocked

**Problem:** since Oct 17, every Bedrock call failed. First a ThrottlingException on the very first request (Nova Lite access granted, but all applied quotas were 0 while the AWS defaults were non-zero). Then, once the quotas were restored, an
AccessDeniedException saying the account was "currently being verified".

**What I did:**
- Checked Service Quotas in us-east-1 and eu-west-3, confirmed applied = 0 vs default > 0
- Opened a support case asking for the default values (not an increase). Got a refusal first ("not enough usage"), but the quotas ended up being restored anyway
- Found the real blocker with a CloudShell test: account verification stuck for weeks
- Replied in the same case, AWS removed the restriction on Nov 7

**Decision:** eu-west-3 (Paris) with the EU cross-region inference profile `eu.amazon.nova-lite-v1:0`. Paris has no on-demand quota for Nova Lite, only CRIS, and the EU profile keeps inference inside the EU.

**Lesson:** a ThrottlingException on a new account isn't always a usage problem. Check applied vs default quotas first, then account status.

First model call validated, let's start!
