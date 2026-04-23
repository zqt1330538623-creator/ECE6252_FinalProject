# ECE6252 Final Project — Gemma API Reproduction Package

This repository contains the **API-based reproduction package** for our ECE 4252/6252 FunML final project on **Foundation Model Risks & Governance**.

It focuses on two experiment tracks:

1. **Jailbreak robustness evaluation** using a hosted Gemma API model.
2. **Watermark experiment support notes** for the same prompt sets, with explicit documentation of what **can** and **cannot** be reproduced in API-only mode.

## What this repository is for

The original project compared release modes for foundation models and examined:

- refusal behavior on harmful and benign prompts,
- simple jailbreak robustness,
- usability vs. conservatism trade-offs,
- and the practical limits of watermark verification under different deployment settings.

This repository is the **Gemma API route** of that workflow.

## Repository structure

```text
.
├── common/
│   └── gemma_api.py                    # Shared hosted Gemma API wrapper
├── jailbreak_eval/
│   ├── data/
│   │   └── prompts_seed.jsonl          # Seed prompt set
│   ├── results/                        # Generated outputs, summaries, plots
│   └── scripts/
│       ├── prepare_prompts.py          # Builds evaluation prompt file
│       ├── run_gemma_api.py            # Calls hosted Gemma API on prompts
│       ├── analyze_results.py          # Computes ASR / over-refusal summary
│       └── plot_results.py             # Creates summary figure
├── watermark_eval/
│   ├── data/
│   │   ├── watermark_test_prompts.jsonl
│   │   ├── watermark_test_prompts_extended.jsonl
│   │   └── watermark_test_single.jsonl
│   ├── results/
│   └── scripts/
│       ├── run_gemma_api.py            # Plain API generation on watermark prompts
│       ├── run_watermark_suite.py      # Writes API-mode limitation note
│       ├── detect_watermark.py         # Explains why detection is unavailable here
│       └── plot_watermark_suite.py     # Placeholder plotting script if extended later
├── .env.example                        # Environment variable template
├── .gitignore
├── requirements.txt
├── pyproject.toml
├── run_jailbreak_pipeline.py           # Full jailbreak pipeline entrypoint
├── run_jailbreak_pipeline.ps1          # Windows PowerShell helper
├── run_watermark_plain_api.ps1         # Windows PowerShell helper
├── CITATION.cff
├── LICENSE
└── README.md
```

## Environment

- Python 3.10+
- A valid Gemini / Google GenAI API key
- Windows PowerShell or a standard terminal

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/zqt1330538623-creator/ECE6252_FinalProject.git
cd ECE6252_FinalProject
```

### 2. Create a virtual environment

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## API configuration

Copy `.env.example` to `.env` and fill in your key:

```env
GEMINI_API_KEY=your_api_key_here
GEMMA_MODEL=gemma-4-26b-a4b-it
GEMMA_THINKING_LEVEL=
```

`GEMMA_MODEL` can be changed if a different hosted Gemma model is available in your account.

## Quick start

### Smoke test

Run a short version first:

```bash
python run_jailbreak_pipeline.py --max-prompts 10
```

### Full jailbreak pipeline

```bash
python run_jailbreak_pipeline.py
```

This pipeline runs:

1. `jailbreak_eval/scripts/prepare_prompts.py`
2. `jailbreak_eval/scripts/run_gemma_api.py`
3. `jailbreak_eval/scripts/analyze_results.py`
4. `jailbreak_eval/scripts/plot_results.py`

### Windows helper

```powershell
.\run_jailbreak_pipeline.ps1
```

## Output files

After running the jailbreak pipeline, check:

- `jailbreak_eval/results/prompts.jsonl`
- `jailbreak_eval/results/raw_outputs.jsonl`
- `jailbreak_eval/results/summary.json`
- `jailbreak_eval/results/plots/summary.png`

## Watermark experiment notes

### What is supported in API mode

You can run plain hosted generations on the watermark prompt set:

```bash
python watermark_eval/scripts/run_gemma_api.py \
  --input watermark_eval/data/watermark_test_prompts.jsonl \
  --output watermark_eval/results/plain_api_outputs.jsonl
```

### What is **not** faithfully reproducible in API mode

The original local watermark experiment depended on:

- generation-time logits processing,
- custom green-list watermark injection,
- and token-ID access during detection.

The hosted API does **not** expose those internals, so this repository does **not** claim a full API-side reproduction of the original custom watermark pipeline.

To document that limitation, run:

```bash
python watermark_eval/scripts/run_watermark_suite.py
python watermark_eval/scripts/detect_watermark.py
```

Those scripts produce an explicit note explaining why the local watermark experiment cannot be reproduced exactly through hosted API access alone.

## Main scripts

### `run_jailbreak_pipeline.py`
Runs the full API evaluation pipeline end to end.

Useful options:

```bash
python run_jailbreak_pipeline.py --max-prompts 10
python run_jailbreak_pipeline.py --model gemma-4-26b-a4b-it
python run_jailbreak_pipeline.py --temperature 0.0 --max-output-tokens 256
```

### `jailbreak_eval/scripts/analyze_results.py`
Computes:

- misuse baseline ASR,
- misuse jailbreak ASR,
- benign over-refusal rate,
- error counts,
- category-level summary,
- and attack-level summary.

### `common/gemma_api.py`
Contains the shared API wrapper and generation helpers used by both evaluation tracks.

## Reproducing the reported workflow

The repository is organized so another student or TA can reproduce the API-side workflow by following these steps:

1. Clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies.
4. Add a valid API key in `.env`.
5. Run `python run_jailbreak_pipeline.py`.
6. Inspect JSONL outputs, summary statistics, and plots in `jailbreak_eval/results/`.
7. For the watermark branch, run the plain API prompt generation and keep the API limitation note as part of the documented result.

## Datasets / prompt files used in this repo

This repository includes the prompt files needed for the packaged workflow:

- `jailbreak_eval/data/prompts_seed.jsonl`
- `watermark_eval/data/watermark_test_prompts.jsonl`
- `watermark_eval/data/watermark_test_prompts_extended.jsonl`
- `watermark_eval/data/watermark_test_single.jsonl`

If you replace these prompt files, keep the same JSONL field structure expected by the scripts.

## Common issues

### `Missing GEMINI_API_KEY`
Copy `.env.example` to `.env` and make sure the key is present.

### API rate limit / temporary failures
The API wrapper includes simple retries. If needed, first run a smaller batch:

```bash
python run_jailbreak_pipeline.py --max-prompts 10
```

### Model name error
Check which model names are currently available to your account and update `GEMMA_MODEL` in `.env`.

## Notes for the course submission

This repository is intended to satisfy the code-repository part of the project submission by providing:

- setup instructions,
- dependency specification,
- experiment entrypoints,
- reproducible output locations,
- and explicit documentation of the API-only watermark limitation.

## Citation

If you reference this repository in a report, use the citation metadata in `CITATION.cff`.

## License

This repository currently includes an MIT license template for convenience. Replace it if your team wants a different license before publishing the repository more broadly.
