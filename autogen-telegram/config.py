"""
Configuration for AutoGen Telegram Bot
Edit these values or set environment variables before running.
"""
import os

# ── Telegram ──
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8597970888:AAFXZBHYHdrCloAto-PCkiiNMSiZvDT5lNM")
ALLOWED_USERS = [int(x) for x in os.getenv("ALLOWED_USERS", "1176968735").split(",") if x.strip()]

# ── LLM configs for AutoGen ──
# Gamene API (Claude, GPT, Gemini)
GAMENE_API_KEY = os.getenv("GAMENE_API_KEY", "sk-ed70bc16720b4b689bf69f81e3d221f5")
GAMENE_BASE_URL = os.getenv("GAMENE_BASE_URL", "https://api.gamene.online/v1")

# DeepSeek API
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://dep.apphay.io.vn/v1")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "none")

# ── Model assignments per agent role ──
MANAGER_MODEL = os.getenv("MANAGER_MODEL", "claude-sonnet-4-6")
CODER_MODEL = os.getenv("CODER_MODEL", "claude-opus-4-6")
RESEARCHER_MODEL = os.getenv("RESEARCHER_MODEL", "gpt-4o-mini")
WRITER_MODEL = os.getenv("WRITER_MODEL", "deepseek-chat")

def get_llm_config(model: str) -> dict:
    """Return AutoGen llm_config for a given model name."""
    if "deepseek" in model:
        return {
            "config_list": [{
                "model": model,
                "api_key": DEEPSEEK_API_KEY,
                "base_url": DEEPSEEK_BASE_URL,
            }],
            "temperature": 0.7,
            "timeout": 300,
        }
    else:
        return {
            "config_list": [{
                "model": model,
                "api_key": GAMENE_API_KEY,
                "base_url": GAMENE_BASE_URL,
            }],
            "temperature": 0.7,
            "timeout": 300,
        }
