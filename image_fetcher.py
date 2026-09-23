import os
import shutil
import time
from pathlib import Path
from typing import List

from bing_image_downloader import downloader

# image_fetcher.py
# Downloads educational images using bing-image-downloader and returns file paths.


def download_images(topic: str, limit: int = 4, output_dir: str = None) -> List[str]:
    """
    Download up to `limit` images related to topic using smart queries.
    Returns list of file paths.
    """
    if not topic or not topic.strip():
        raise ValueError("Topic must be provided for image search")

    if output_dir is None:
        output_dir = os.path.join(os.getcwd(), "storylearn_ai", "assets", "images")

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    queries = [
        f"{topic} diagram",
        f"{topic} explained illustration",
        f"{topic} infographic",
        f"{topic} concept art",
    ]

    collected = []

    for q in queries:
        if len(collected) >= limit:
            break
        # bing-image-downloader will create a folder under output_dir with the query name
        safe_q = q.replace(" ", "_")[:80]
        try:
            # download remaining images for this query
            remaining = limit - len(collected)
            downloader.download(q, limit=remaining, output_dir=output_dir, adult_filter_off=True, force_replace=False, timeout=60, verbose=False)

            # downloaded files live in output_dir/<query>/
            folder = Path(output_dir) / safe_q
            if not folder.exists():
                # sometimes the library sanitizes differently; attempt to locate by partial name
                for child in Path(output_dir).iterdir():
                    if child.is_dir() and child.name.lower().startswith(safe_q.split("_")[0].lower()):
                        folder = child
                        break

            if folder.exists():
                for f in folder.iterdir():
                    if f.is_file() and f.suffix.lower() in (".jpg", ".jpeg", ".png"):
                        collected.append(str(f))
                        if len(collected) >= limit:
                            break

            # be nice to the network
            time.sleep(1)

        except Exception:
            # keep going if a query fails
            continue

    # If downloads are nested (some versions create dataset/<query>), flatten and return first `limit`
    return collected[:limit]
