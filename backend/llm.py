"""Single entry point for model calls, so every step logs tokens and latency the same way.

Provider is picked with LLM_PROVIDER:
- "bedrock" (default): Claude on Amazon Bedrock, AWS credentials from the usual chain (AWS_PROFILE, SSO...).
- "anthropic": plan B, the Claude API directly (ANTHROPIC_API_KEY).
"""
import os
import time
from dataclasses import dataclass

from anthropic import Anthropic, AnthropicBedrockMantle

DEFAULT_MODEL = "claude-opus-5-5"


@dataclass
class LLMResult:
    text: str
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    latency_s: float
    stop_reason: str


def _client(provider):
    if provider == "bedrock":
        return AnthropicBedrockMantle(aws_region=os.environ.get("AWS_REGION", "us-east-1"))
    if provider == "anthropic":
        return Anthropic()
    raise ValueError(f"Unknown LLM_PROVIDER: {provider}")


def call_llm(system, user, max_tokens=16000):
    provider = os.environ.get("LLM_PROVIDER", "bedrock")
    model = os.environ.get("LLM_MODEL", DEFAULT_MODEL)
    effort = os.environ.get("LLM_EFFORT", "medium")
    client = _client(provider)

    request = dict(
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
        output_config={"effort": effort},
    )
    start = time.perf_counter()
    if provider == "bedrock":
        response = client.messages.create(model=f"anthropic.{model}", **request)
    else:
        # Server-side fallback: if the model declines, the API retries on a fallback model.
        response = client.beta.messages.create(
            model=model,
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            **request,
        )
    latency = time.perf_counter() - start

    if response.stop_reason == "refusal":
        raise RuntimeError(f"Model declined the request: {response.stop_details}")
    if response.stop_reason == "max_tokens":
        raise RuntimeError("Output truncated: max_tokens reached")

    text = "".join(b.text for b in response.content if b.type == "text")
    return LLMResult(
        text=text,
        provider=provider,
        model=response.model,
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
        latency_s=round(latency, 2),
        stop_reason=response.stop_reason,
    )
