import json
from pathlib import Path

import modal

GPU = "H100"

app = modal.App("rojak-train")
# Pinned to the versions in uv.lock so the remote env matches the locally verified API.
# bitsandbytes has no macOS build, so it is intentionally absent from the lock.
image = modal.Image.debian_slim(python_version="3.12").pip_install(
    "torch==2.15.0",
    "transformers==5.22.1",
    "peft==0.21.2",
    "trl==1.17.1",
    "datasets==5.1.0",
    "bitsandbytes",
    "accelerate==1.15.0",
    "wandb==0.31.0",
)
volume = modal.Volume.from_name("rojak-out", create_if_missing=True)


@app.function(
    image=image,
    gpu=GPU,
    timeout=6 * 60 * 60,
    volumes={"/out": volume},
    secrets=[modal.Secret.from_name("rojak-secrets")],
)
def train(rows: list[dict], cfg: dict, run_name: str) -> str:
    import os

    import torch
    from datasets import Dataset
    from peft import LoraConfig
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    from trl import SFTConfig, SFTTrainer

    tokenizer = AutoTokenizer.from_pretrained(cfg["base_model"])
    model = AutoModelForCausalLM.from_pretrained(
        cfg["base_model"],
        quantization_config=BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
        ),
        device_map="auto",
    )
    peft_config = LoraConfig(
        r=cfg["lora"]["r"],
        lora_alpha=cfg["lora"]["alpha"],
        lora_dropout=cfg["lora"]["dropout"],
        target_modules="all-linear",
        task_type="CAUSAL_LM",
    )
    # transformers 5.x dropped warmup_ratio; warm up 3% of total optimizer steps instead.
    total_steps = max(
        1,
        len(rows)
        * cfg["train"]["epochs"]
        // (cfg["train"]["batch_size"] * cfg["train"]["grad_accum"]),
    )
    args = SFTConfig(
        output_dir=f"/out/{run_name}",
        num_train_epochs=cfg["train"]["epochs"],
        per_device_train_batch_size=cfg["train"]["batch_size"],
        gradient_accumulation_steps=cfg["train"]["grad_accum"],
        learning_rate=cfg["train"]["learning_rate"],
        lr_scheduler_type="cosine",
        warmup_steps=max(1, int(total_steps * 0.03)),
        logging_steps=10,
        save_strategy="epoch",
        bf16=True,
        max_length=cfg["max_seq_len"],
        seed=cfg["seed"],
        run_name=run_name,
        report_to="wandb" if os.environ.get("WANDB_API_KEY") else "none",
    )
    dataset = Dataset.from_list([{"messages": r["messages"]} for r in rows])
    trainer = SFTTrainer(
        model=model,
        args=args,
        train_dataset=dataset,
        processing_class=tokenizer,
        peft_config=peft_config,
    )
    trainer.train()
    trainer.save_model(f"/out/{run_name}/adapter")
    volume.commit()
    return f"/out/{run_name}/adapter"


@app.local_entrypoint()
def main(
    train_file: str = "data/synthetic/train.clean.jsonl",
    run_name: str = "rojak-v1",
    limit: int = 0,
) -> None:
    import yaml

    cfg = yaml.safe_load((Path(__file__).parent / "config.yaml").read_text())
    rows = [json.loads(line) for line in Path(train_file).read_text(encoding="utf-8").splitlines() if line]
    if limit:
        rows = rows[:limit]
    print(f"training {run_name} on {len(rows)} rows with {cfg['base_model']}")
    print("adapter saved to", train.remote(rows, cfg, run_name))
