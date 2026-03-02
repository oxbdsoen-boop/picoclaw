"""
OpenAI-Compatible Adapter for dep.apphay.io.vn DeepSeek API
────────────────────────────────────────────────────────────
Chuyển đổi OpenAI format → DeepSeek custom API format
Để PicoClaw có thể dùng được API dep.apphay.io.vn

Endpoint gốc: POST dep.apphay.io.vn/chat {"message":"...", "model":"..."}
Adapter:       POST localhost:9090/v1/chat/completions (OpenAI format)
"""

import json
import time
import logging
import os

import requests
from flask import Flask, request, jsonify

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("deepseek-adapter")

app = Flask(__name__)

DEEPSEEK_BASE = os.getenv("DEEPSEEK_BASE_URL", "https://dep.apphay.io.vn")
TIMEOUT = int(os.getenv("DEEPSEEK_TIMEOUT", "120"))

# Model name mapping: OpenAI-style → dep.apphay.io.vn model names
MODEL_MAP = {
    # Direct mappings
    "deepseek-v3": "DeepSeek-V3",
    "deepseek-v3-0324": "DeepSeek-V3-0324",
    "deepseek-v3.1": "DeepSeek-V3.1",
    "deepseek-v3.2": "DeepSeek-V3.2",
    "deepseek-r1": "DeepSeek-R1",
    "deepseek-r1-0528": "DeepSeek-R1-0528",
    "deepseek-r1-distill": "DeepSeek-R1-Distill",
    "deepseek-coder": "DeepSeek-Coder",
    "deepseek-coder-v2": "DeepSeek-Coder-V2",
    "deepseek-coder-6.7b-base": "DeepSeek-Coder-6.7B-base",
    "deepseek-coder-6.7b-instruct": "DeepSeek-Coder-6.7B-instruct",
    "deepseek-vl": "DeepSeek-VL",
    "deepseek-prover-v2": "DeepSeek-Prover-V2",
    "deepseek-v2": "DeepSeek-V2",
    "deepseek-v2.5": "DeepSeek-V2.5",
    "deepseek-chat": "DeepSeek-V3",  # alias
}


def resolve_model(model_name: str) -> str:
    """Resolve model name to dep.apphay.io.vn format."""
    if not model_name:
        return "DeepSeek-V3"
    # Strip provider prefix (openai/, deepseek/)
    clean = model_name.split("/")[-1].lower().strip()
    return MODEL_MAP.get(clean, model_name)


def extract_message(messages: list) -> str:
    """Extract the user's message from OpenAI messages array."""
    # Get the last user message
    for msg in reversed(messages):
        if msg.get("role") == "user":
            content = msg.get("content", "")
            if isinstance(content, list):
                # Handle multimodal content
                parts = []
                for part in content:
                    if isinstance(part, dict) and part.get("type") == "text":
                        parts.append(part["text"])
                    elif isinstance(part, str):
                        parts.append(part)
                return " ".join(parts)
            return str(content)
    # Fallback: concatenate all messages
    parts = []
    for msg in messages:
        role = msg.get("role", "")
        content = msg.get("content", "")
        if content and role != "system":
            parts.append(f"{content}")
    return "\n".join(parts) if parts else ""


@app.route("/v1/chat/completions", methods=["POST"])
def chat_completions():
    """OpenAI-compatible chat completions endpoint."""
    data = request.get_json(force=True)

    model_raw = data.get("model", "DeepSeek-V3")
    model = resolve_model(model_raw)
    messages = data.get("messages", [])
    message_text = extract_message(messages)

    if not message_text:
        return jsonify({"error": {"message": "No message content", "type": "invalid_request_error"}}), 400

    log.info(f"Request: model={model}, message={message_text[:80]}...")

    # Call dep.apphay.io.vn/chat
    try:
        resp = requests.post(
            f"{DEEPSEEK_BASE}/chat",
            json={"message": message_text, "model": model},
            timeout=TIMEOUT,
        )
        resp_data = resp.json()
    except requests.Timeout:
        return jsonify({"error": {"message": "DeepSeek API timeout", "type": "server_error"}}), 504
    except Exception as e:
        log.error(f"DeepSeek API error: {e}")
        return jsonify({"error": {"message": str(e), "type": "server_error"}}), 502

    if not resp_data.get("success"):
        err_msg = resp_data.get("error", "Unknown error")
        return jsonify({"error": {"message": err_msg, "type": "api_error"}}), 500

    # Convert to OpenAI format
    content = resp_data.get("response", "")
    completion_id = f"chatcmpl-deepseek-{int(time.time())}"

    openai_response = {
        "id": completion_id,
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": content,
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": len(message_text.split()),
            "completion_tokens": len(content.split()),
            "total_tokens": len(message_text.split()) + len(content.split()),
        },
    }

    log.info(f"Response: model={model}, length={len(content)}")
    return jsonify(openai_response)


@app.route("/v1/models", methods=["GET"])
def list_models():
    """OpenAI-compatible models list."""
    models = []
    for key in MODEL_MAP:
        models.append({
            "id": key,
            "object": "model",
            "created": int(time.time()),
            "owned_by": "deepseek",
        })
    return jsonify({"object": "list", "data": models})


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"})


if __name__ == "__main__":
    port = int(os.getenv("ADAPTER_PORT", "9090"))
    log.info(f"Starting OpenAI adapter on port {port}")
    log.info(f"Proxying to: {DEEPSEEK_BASE}")
    app.run(host="0.0.0.0", port=port)
