"""Bedrock model calls (Converse API), with token and latency logging."""
import os
import json
import time
from dataclasses import dataclass

import boto3
from botocore.config import Config

DEFAULT_MODEL = "eu.amazon.nova-lite-v1:0"
DEFAULT_REGION = "eu-west-3"

_RETRY_CONFIG = Config(retries={"max_attempts": 5, "mode": "adaptive"})


@dataclass
class LLMResult:
    text: str
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    latency_s: float
    stop_reason: str


def _client():
    region = os.environ.get("AWS_REGION", DEFAULT_REGION)
    return boto3.client("bedrock-runtime", region_name=region, config=_RETRY_CONFIG)


def call_llm(system, user, max_tokens=4096):
    model = os.environ.get("LLM_MODEL", DEFAULT_MODEL)
    client = _client()

    start = time.perf_counter()
    response = client.converse(
        modelId=model,
        system=[{"text": system}],
        messages=[{"role": "user", "content": [{"text": user}]}],
        inferenceConfig={"maxTokens": max_tokens, "temperature": 0},
    )
    latency = time.perf_counter() - start

    stop_reason = response["stopReason"]
    if stop_reason in ("guardrail_intervened", "content_filtered"):
        raise RuntimeError(f"Model output blocked: {stop_reason}")
    if stop_reason == "max_tokens":
        raise RuntimeError("Output truncated: max_tokens reached")

    content = response["output"]["message"]["content"]
    text = "".join(block["text"] for block in content if "text" in block)
    usage = response["usage"]
    return LLMResult(
        text=text,
        provider="bedrock",
        model=model,
        input_tokens=usage["inputTokens"],
        output_tokens=usage["outputTokens"],
        latency_s=round(latency, 2),
        stop_reason=stop_reason,
    )

def extract_json(text):
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        text = text.rsplit("```", 1)[0]
    return json.loads(text)