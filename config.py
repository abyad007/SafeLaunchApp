# config.py
# ─────────────────────────────────────────────────────────────────────────────
# Central configuration for the Versigent Safe Launch Generator.
# IT / deployment team edits this file once during setup.
# Application code reads from here — no hardcoded URLs or settings elsewhere.
#
# LLM SETUP:
#   vLLM  (recommended for enterprise):
#     1. Install on your Linux server:
#        pip install vllm
#        python -m vllm.entrypoints.openai.api_server \
#               --model mistralai/Mistral-7B-Instruct-v0.3 \
#               --port 8000
#     2. Set LLM_ENDPOINT below to http://your-server:8000
#
#   Ollama (for individual laptop use):
#     1. Install from https://ollama.com
#     2. Run: ollama pull mistral
#     3. Set LLM_ENDPOINT below to http://localhost:11434
#     4. Set LLM_PROVIDER to "ollama"
#
#   Disabled (rule-based extraction only):
#     Set LLM_ENABLED = False
#     No GPU, no server needed — works everywhere
# ─────────────────────────────────────────────────────────────────────────────

# ── LLM Settings ─────────────────────────────────────────────────────────────

# Set to False to always use rule-based extraction (default, works without any server)
LLM_ENABLED: bool = True

# Provider: "vllm" or "ollama"
# Both use the same OpenAI-compatible API — the difference is the endpoint path.
# vllm  → POST /v1/chat/completions
# ollama → POST /api/chat  (also supports /v1/chat/completions in newer versions)
LLM_PROVIDER: str = "vllm"   # "vllm" | "ollama"

# Endpoint where the LLM server is running
# vLLM  default: http://localhost:8000
# Ollama default: http://localhost:11434
LLM_ENDPOINT: str = "http://localhost:8000"

# Model name to use for extraction
# vLLM:   must match the --model argument you started the server with
# Ollama: must match a model you've pulled (e.g. "mistral", "qwen2.5:7b")
LLM_MODEL: str = "mistralai/Mistral-7B-Instruct-v0.3"

# How long to wait for the LLM server to respond (seconds)
# Increase if your server is slow or the procedure file is large
LLM_TIMEOUT: int = 60

# Maximum tokens the LLM can return per extraction call
LLM_MAX_TOKENS: int = 2048

# Temperature — keep low for extraction (deterministic, not creative)
LLM_TEMPERATURE: float = 0.05

# ── Extraction Settings ───────────────────────────────────────────────────────

# Maximum characters of procedure text sent to the LLM per request
# Larger = more context = better results, but slower and uses more memory
# Mistral 7B / Qwen 7B context window: 32k tokens (~24k chars safe limit)
LLM_MAX_INPUT_CHARS: int = 12000

# If LLM returns fewer items than this threshold, fall back to rule-based
# (safety net in case the LLM response is garbled or empty)
LLM_MIN_ITEMS_THRESHOLD: int = 3

# ── App Settings ──────────────────────────────────────────────────────────────

APP_TITLE: str = "Versigent Safe Launch Generator"
APP_VERSION: str = "2.0"
