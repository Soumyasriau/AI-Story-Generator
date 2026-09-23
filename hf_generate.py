import os
import sys
import argparse
from huggingface_hub import InferenceClient


def query_hf(token: str, model: str, prompt: str, max_new_tokens: int = 200):
    client = InferenceClient(token=token)
    params = {"max_new_tokens": max_new_tokens, "temperature": 0.7}
    # Different versions of huggingface_hub expose slightly different method signatures.
    # Try several call forms and return the first successful result.
    last_err = None
    for call in (
        lambda: client.text_generation(model=model, inputs=prompt, parameters=params),
        lambda: client.text_generation(model=model, prompt=prompt, parameters=params),
        lambda: client.text_generation(model=model, data=prompt),
        lambda: getattr(client, "generate", lambda **kw: (_ for _ in ()).throw(AttributeError("no generate")))(model=model, inputs=prompt, parameters=params),
        lambda: getattr(client, "predict", lambda **kw: (_ for _ in ()).throw(AttributeError("no predict")))(model=model, inputs=prompt),
    ):
        try:
            return call()
        except Exception as e:
            last_err = e
            continue
    # If none worked, raise the last error for debugging
    raise RuntimeError(f"HF client invocation failed: {last_err}")


def main():
    p = argparse.ArgumentParser(description="Call Hugging Face Inference API to generate text")
    p.add_argument("--token", help="Hugging Face API token (or use HF_API_TOKEN env var)")
    p.add_argument("--model", default=os.getenv("HF_MODEL", "gpt2"), help="Model repo id (default: gpt2)")
    p.add_argument("--prompt", required=True, help="Prompt text to send to the model")
    p.add_argument("--max-tokens", type=int, default=200, help="Max new tokens to generate")
    args = p.parse_args()

    token = args.token or os.getenv("HF_API_TOKEN")
    if not token:
        print("Error: No HF API token provided. Set HF_API_TOKEN or pass --token.")
        sys.exit(2)

    try:
        out = query_hf(token=token, model=args.model, prompt=args.prompt, max_new_tokens=args.max_tokens)
    except Exception as e:
        print(f"Generation failed: {e}")
        sys.exit(1)

    # InferenceClient.text_generation returns a list of dicts with 'generated_text'
    if isinstance(out, list) and out and isinstance(out[0], dict) and "generated_text" in out[0]:
        print(out[0]["generated_text"].strip())
    elif isinstance(out, dict) and "generated_text" in out:
        print(out["generated_text"].strip())
    else:
        print(out)


if __name__ == "__main__":
    main()
