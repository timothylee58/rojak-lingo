import subprocess

import modal

BASE_MODEL = "meta-llama/Llama-3.1-8B-Instruct"
ADAPTER_NAME = "rojak-v1"
ADAPTER_PATH = f"/out/{ADAPTER_NAME}/adapter"
PORT = 8000

app = modal.App("rojak-serve")
image = modal.Image.debian_slim(python_version="3.12").pip_install("vllm", "huggingface_hub")
volume = modal.Volume.from_name("rojak-out", create_if_missing=True)
# Weights are cached on a volume so a cold start does not re-download the base model.
hf_cache = modal.Volume.from_name("rojak-hf-cache", create_if_missing=True)


@app.function(
    image=image,
    gpu="H100",
    volumes={"/out": volume, "/root/.cache/huggingface": hf_cache},
    secrets=[modal.Secret.from_name("rojak-secrets")],
    # Scale to zero between eval runs so idle time does not burn credits.
    scaledown_window=300,
    timeout=60 * 60,
)
@modal.concurrent(max_inputs=32)
@modal.web_server(port=PORT, startup_timeout=15 * 60)
def serve() -> None:
    import os

    # One server hosts both models: requests with model=BASE_MODEL hit the base weights and
    # model=ADAPTER_NAME applies the LoRA, so the eval compares them on identical hardware.
    cmd = [
        "vllm", "serve", BASE_MODEL,
        "--host", "0.0.0.0",
        "--port", str(PORT),
        "--enable-lora",
        "--lora-modules", f"{ADAPTER_NAME}={ADAPTER_PATH}",
        "--max-lora-rank", "16",
        "--max-model-len", "2048",
        "--api-key", os.environ["MODAL_ENDPOINT_KEY"],
    ]
    subprocess.Popen(cmd)
