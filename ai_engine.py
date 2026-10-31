import os
import re
import json
from pathlib import Path
from typing import Dict, Any, List

import requests
from dotenv import load_dotenv

try:
    from huggingface_hub import InferenceClient
except ImportError:
    InferenceClient = None
try:
    from google import genai
except ImportError:
    genai = None
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env", override=True)

# Words that are never allowed in a topic or in the AI's answer.
BLOCKED = [
    "sex", "porn", "nude", "naked", "xxx", "erotic", "nsfw", "fetish",
    "rape", "incest", "hentai", "onlyfans", "gore", "suicide method",
]

SAFE_FALLBACK = {
    "title": "Try another topic",
    "icon": "📚",
    "story": "This topic can't be used here. Please enter a school subject such as Photosynthesis, Cricket, Music or the Water Cycle.",
    "steps": [],
    "step_icons": [],
    "summary": "",
    "key_points": [],
}


def _is_unsafe(text: str) -> bool:
    t = text.lower()
    return any(re.search(r"\b" + re.escape(w), t) for w in BLOCKED)


def _clean(text: str) -> str:
    """Remove bullets, numbers and 'Step 1:' labels from the start of a line."""
    t = str(text).strip()
    t = re.sub(r"^\s*(?:[-•*]+|\d+[.)])\s*", "", t)
    t = re.sub(r"^\s*step\s*\d+\s*[:.\-]\s*", "", t, flags=re.IGNORECASE)
    return t.strip()


def _prompt(topic: str) -> str:
    return f"""You are an expert teacher for students aged 10 to 16.
Keep everything educational, child-safe and age-appropriate.
If the topic is adult, sexual, violent, hateful or unsafe, reply with exactly: {{"error": "unsafe"}}

Write accurate study notes about the topic below.
Return ONLY valid JSON, no extra text, no markdown fences:
{{
  "title": "short title",
  "icon": "ONE emoji that represents the topic",
  "story": "clear explanation in simple English, 5 to 7 sentences, with real facts",
  "steps": [{{"emoji": "one emoji", "text": "one complete sentence that teaches one fact or idea"}}],
  "summary": "2 to 3 sentence recap",
  "key_points": ["5 short factual statements a student should remember for an exam"]
}}

Rules:
- Every fact must be correct. Do not guess.
- Each step must be a full sentence that teaches something real. A step must NOT be a heading or a title.
- Steps must follow a logical order, from the basic idea to the details. Use 6 to 8 steps.
- Key points must be facts or definitions. They must NOT be learning goals such as "Understand..." or "Describe...".
- Do not put numbers, "Step 1:" or bullet symbols in steps or key points.
- No filler such as "scientists are still learning".
- Do not repeat the same fact in different places.

Topic: {topic}
"""


def _ollama(prompt, max_tokens):
    r = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": "llama3.2",
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
        },
        timeout=180,
    )
    r.raise_for_status()
    return r.json()["message"]["content"].strip()


def _gemini(prompt, max_tokens):
    if genai is None:
        raise RuntimeError("google-genai is not installed")
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    resp = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-3.8-flash"),
        contents=prompt,
    )
    return resp.text.strip()


def _openai(prompt, max_tokens):
    if OpenAI is None:
        raise RuntimeError("openai is not installed")
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    resp = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=[
            {"role": "system", "content": "You are a safe, accurate teacher for school students."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=max_tokens,
        temperature=0.4,
    )
    return resp.choices[0].message.content.strip()


def _hf(prompt, max_tokens):
    if InferenceClient is None:
        raise RuntimeError("huggingface_hub is not installed")
    client = InferenceClient(token=os.getenv("HF_API_TOKEN"))
    resp = client.chat_completion(
        model=os.getenv("HF_MODEL", "HuggingFaceH4/zephyr-7b-beta"),
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=0.4,
    )
    return resp.choices[0].message.content.strip()


def _parse(content: str) -> Dict[str, Any]:
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        s = content.find("{")
        e = content.rfind("}")
        if s != -1 and e != -1:
            try:
                return json.loads(content[s:e + 1])
            except json.JSONDecodeError:
                pass
    return {}


def generate_story(topic: str, max_tokens: int = 1200) -> Dict[str, Any]:
    topic = (topic or "").strip()
    if not topic:
        raise ValueError("Please enter a topic.")
    if len(topic) > 80 or _is_unsafe(topic):
        return dict(SAFE_FALLBACK)

    prompt = _prompt(topic)

    # Providers in order. Each runs only if the earlier ones gave nothing.
    providers = []
    if os.getenv("GEMINI_API_KEY"):
        providers.append(_gemini)
    if os.getenv("OPENAI_API_KEY"):
        providers.append(_openai)
    if os.getenv("HF_API_TOKEN"):
        providers.append(_hf)
    providers.append(_ollama)  # local only; fails quietly on a server

    print("[ai] providers to try:", [p.__name__ for p in providers])

    data = {}
    errors = []
    for fn in providers:
        try:
            data = _parse(fn(prompt, max_tokens))
            if data:
                print("[ai] used:", fn.__name__)
                break
            errors.append(f"{fn.__name__}: reply was not valid JSON")
            print("[ai]", fn.__name__, "gave no valid JSON")
        except Exception as e:
            errors.append(f"{fn.__name__}: {e}")
            print("[ai]", fn.__name__, "FAILED:", e)

    if not data:
        print("AI ERRORS:", errors)
        out = dict(SAFE_FALLBACK)
        out["title"] = topic
        out["story"] = (
            "The AI service is not available right now. Details: "
            + ("; ".join(errors)[:400] if errors else "no provider is set up")
        )
        return out

    if data.get("error") == "unsafe":
        return dict(SAFE_FALLBACK)

    # Normalise the answer into the format the app expects.
    steps: List[str] = []
    icons: List[str] = []
    for s in data.get("steps", []):
        if isinstance(s, dict):
            text = _clean(s.get("text", ""))
            emoji = str(s.get("emoji", "🔹")).strip()[:4] or "🔹"
        else:
            text = _clean(s)
            emoji = "🔹"
        if text:
            steps.append(text)
            icons.append(emoji)

    result = {
        "title": str(data.get("title") or topic),
        "icon": str(data.get("icon") or "📚")[:4],
        "story": str(data.get("story", "")),
        "steps": steps,
        "step_icons": icons,
        "summary": str(data.get("summary", "")),
        "key_points": [_clean(k) for k in data.get("key_points", []) if _clean(k)],
    }

    # Final check: if the AI's answer contains a blocked word, do not show it.
    if _is_unsafe(json.dumps(result)):
        return dict(SAFE_FALLBACK)

    return result