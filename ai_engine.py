import os
import json
from typing import Dict, Any

import requests
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from typing import Optional
try:
    from transformers import pipeline
except Exception:
    pipeline = None

# load .env from the project folder so `HF_API_TOKEN` (or OPENAI_API_KEY) is available
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=True)
try:
    import openai
except Exception:
    openai = None

try:
    from google import genai
except Exception:
    genai = None


# ai_engine.py
# Responsible for talking to the generative AI model. Prefer Hugging Face
# Inference API when `HF_API_TOKEN` is present; otherwise fall back to OpenAI.


def _init_openai():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY not set in environment")
    if openai is None:
        raise RuntimeError("openai package not installed")
    openai.api_key = api_key


def _init_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY not set in environment")
    if genai is None:
        raise RuntimeError("google-genai package not installed")

    return genai.Client(api_key=api_key)


def _query_hf(prompt: str, model: str, token: str, max_new_tokens: int = 200) -> str:
    client = InferenceClient(token=token)
    params = {"max_new_tokens": max_new_tokens, "temperature": 0.7}
    res = client.text_generation(model=model, inputs=prompt, parameters=params)

    # Normalize responses: client returns list of dicts or a dict with 'generated_text'
    if isinstance(res, list) and res and isinstance(res[0], dict) and "generated_text" in res[0]:
        return res[0]["generated_text"].strip()
    if isinstance(res, dict) and "generated_text" in res:
        return res["generated_text"].strip()

    # Fallback: stringify
    try:
        return json.dumps(res)
    except Exception:
        return str(res)


def _local_generate(prompt: str, model: str, max_new_tokens: int = 200) -> str:
    """Generate text locally with transformers pipeline (CPU)."""
    if pipeline is None:
        raise RuntimeError("transformers not installed for local generation")

    # Use text-generation pipeline; model may be a small model (gpt2/distilgpt2) or others
    gen = pipeline("text-generation", model=model, device=-1)
    out = gen(prompt, max_new_tokens=max_new_tokens, do_sample=False)
    if isinstance(out, list) and out and isinstance(out[0], dict) and "generated_text" in out[0]:
        return out[0]["generated_text"].strip()
    return str(out)


def generate_story(topic: str, max_tokens: int = 800) -> Dict[str, Any]:
    """
    Generate a structured story-style explanation for `topic`.

    Returns a dict with keys: `story`, `steps`, `summary`, `key_points`.
    Uses HF Inference API when `HF_API_TOKEN` is set; otherwise uses OpenAI.
    """
    if not topic or not topic.strip():
        raise ValueError("Topic must be a non-empty string")

    # Prompt asks the model to return JSON so downstream parsing is simple
    prompt = (
        "You are an expert teacher. Produce a JSON object with keys:"
        "\n- story: a story-style, technically accurate explanation of the topic in simple language for students"
        "\n- steps: a list of 6-12 step-by-step conceptual checkpoints or flow items"
        "\n- summary: a short summary (2-4 sentences)"
        "\n- key_points: a list of 5 highlighted takeaways"
        "\nMake the story engaging, keep language simple, and ensure technical accuracy."
        f"\nTopic: {topic}\nRespond ONLY with valid JSON."
    )

    # Prefer Gemini if token available
    gemini_key = os.getenv("GEMINI_API_KEY")
    gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    # Prefer Hugging Face if token available AND Gemini is not set
    hf_token = os.getenv("HF_API_TOKEN")
    hf_model = os.getenv("HF_MODEL", "gpt2")

    if gemini_key:
        try:
            client = _init_gemini()
            response = client.models.generate_content(
                model=gemini_model,
                contents=prompt
            )
            content = response.text.strip()
        except Exception as e:
            raise RuntimeError(f"Gemini generation failed: {e}")
    
   
    elif hf_token:
        # Try hosted HF first; if it fails, fall back to local transformers pipeline (if available)
        try:
            content = _query_hf(prompt=prompt, model=hf_model, token=hf_token, max_new_tokens=min(max_tokens, 1024))
        except Exception as e:
            # fall back to local model if transformers installed
            if pipeline is not None:
                try:
                    content = _local_generate(prompt, hf_model, max_new_tokens=min(max_tokens, 1024))
                except Exception as e2:
                    raise RuntimeError(f"HF generation failed: {e}; local fallback failed: {e2}")
            else:
                raise RuntimeError(f"HF generation failed: {e}")
    else:
        # Fallback to OpenAI
        _init_openai()
        try:
            resp = openai.ChatCompletion.create(
                model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                messages=[{"role": "system", "content": "You are a helpful assistant."},
                          {"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.7,
            )
            content = resp["choices"][0]["message"]["content"].strip()
        except Exception as e:
            raise RuntimeError(f"OpenAI generation failed: {e}")

    # Try to parse JSON. If model included backticks or markdown, try to strip them.
    try:
        parsed = json.loads(content)
    except Exception:
        start = content.find("{")
        end = content.rfind("}")
        if start != -1 and end != -1:
            try:
                parsed = json.loads(content[start : end + 1])
            except Exception:
                parsed = {"story": content, "steps": [], "summary": "", "key_points": []}
        else:
            parsed = {"story": content, "steps": [], "summary": "", "key_points": []}

    # Ensure keys exist
    for k in ["story", "steps", "summary", "key_points"]:
        if k not in parsed:
            parsed[k] = [] if k in ("steps", "key_points") else ""

    return parsed
