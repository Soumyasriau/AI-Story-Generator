import os
import re
import tempfile
from pathlib import Path
from typing import List

import requests
from dotenv import load_dotenv

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None

from ai_engine import _is_unsafe

load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env", override=True)

HEADERS = {"User-Agent": "StoryLearnAI/1.0 (student study app)"}
API = "https://commons.wikimedia.org/w/api.php"
OK_TYPES = {"image/jpeg", "image/png"}


def _matches(topic: str, title: str) -> bool:
    """Keep a picture only if its title contains a word from the topic."""
    words = [w for w in re.findall(r"[a-z0-9]+", topic.lower()) if len(w) > 2]
    t = title.lower()
    return bool(words) and any(w in t for w in words)


def _search(topic: str, want: int = 12):
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrnamespace": 6,
        "gsrsearch": f"{topic} filetype:bitmap",
        "gsrlimit": want,
        "prop": "imageinfo",
        "iiprop": "url|mime",
        "iiurlwidth": 640,
    }
    r = requests.get(API, params=params, headers=HEADERS, timeout=15)
    r.raise_for_status()
    pages = r.json().get("query", {}).get("pages", {})
    print(f"[images] Wikimedia returned {len(pages)} results for '{topic}'")
    results = []
    for p in pages.values():
        info = (p.get("imageinfo") or [{}])[0]
        if info.get("mime") not in OK_TYPES:
            continue
        title = p.get("title", "")
        if _is_unsafe(title) or not _matches(topic, title):
            continue
        url = info.get("thumburl") or info.get("url")
        if url:
            results.append((title, url, info["mime"]))
    print(f"[images] {len(results)} matched the topic by title")
    return results


def _is_safe_image(data: bytes, mime: str) -> bool:
    """Ask Gemini. Anything other than a clear SAFE is rejected."""
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        print("[images] IMAGE CHECK ERROR: GEMINI_API_KEY is missing")
        return False
    if genai is None:
        print("[images] IMAGE CHECK ERROR: google-genai is not installed")
        return False
    try:
        client = genai.Client(api_key=key)
        resp = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-3.8-flash"),
            contents=[
                types.Part.from_bytes(data=data, mime_type=mime),
                "Is this image safe and suitable for a school study app for students "
                "aged 10 to 16? Reply UNSAFE if it contains nudity, sexual content, "
                "violence, gore, weapons, drugs, alcohol, hate symbols, frightening "
                "content, or a photo of a private person. Otherwise reply SAFE. "
                "Answer with one word only: SAFE or UNSAFE.",
            ],
        )
        answer = resp.text.strip().upper()
        print(f"[images] Gemini said: {answer}")
        return answer == "SAFE"
    except Exception as e:
        print("[images] IMAGE CHECK ERROR:", e)
        return False


def download_images(topic: str, limit: int = 4, output_dir: str = None) -> List[str]:
    topic = (topic or "").strip()
    if not topic or _is_unsafe(topic):
        return []

    out = Path(output_dir or tempfile.mkdtemp(prefix="storylearn_"))
    out.mkdir(parents=True, exist_ok=True)

    try:
        candidates = _search(topic)
    except Exception as e:
        print("[images] SEARCH ERROR:", e)
        return []

    saved: List[str] = []
    for title, url, mime in candidates:
        if len(saved) >= limit:
            break
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            r.raise_for_status()
            if len(r.content) > 3_000_000:
                continue
            if not _is_safe_image(r.content, mime):
                continue
            ext = ".png" if mime == "image/png" else ".jpg"
            path = out / f"img_{len(saved) + 1}{ext}"
            path.write_bytes(r.content)
            saved.append(str(path))
        except Exception as e:
            print("[images] DOWNLOAD ERROR:", e)
            continue
    print(f"[images] {len(saved)} safe pictures saved")
    return saved