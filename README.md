# Gemma API Reproduction Package

This package is a cleaned **Gemma API reproduction package** prepared from the uploaded project files.

## 1. Project purpose

This project is designed to run a **jailbreak / refusal evaluation** workflow. The main steps are:

- prepare evaluation prompts
- generate responses with the **Gemma API**
- collect evaluation results
- summarize the outputs with plots and metrics

The package has been organized into an **API-based reproduction workflow**, so you do not need to load local Hugging Face Gemma weights for the main pipeline.

---

## 2. What was changed

The original workflow was reorganized into a **Gemma API mode**. The main runnable files are:

- `jailbreak_eval/scripts/run_gemma_api.py`
- `run_jailbreak_pipeline.py`
- `run_jailbreak_pipeline.ps1`

You can now reproduce the main jailbreak evaluation through the API by providing a valid `GEMINI_API_KEY`.

---

## 3. Directory overview

- `common/gemma_api.py`: shared wrapper for Gemma API calls
- `jailbreak_eval/`: runnable jailbreak evaluation code
- `.env.example`: template for environment variables
- `requirements.txt`: Python dependencies

---

## 4. How to run in VS Code (Windows)

### Step 1: Open the project
Extract the zip file and open the **project root folder** in VS Code.

### Step 2: Create a virtual environment
Run the following commands in the VS Code terminal:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Step 3: Install dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Configure the API key
Copy `.env.example` to `.env`, then fill in your API key:

```env
GEMINI_API_KEY=your_key
GEMMA_MODEL=gemma-4-26b-a4b-it
```

### Step 5: Run the jailbreak pipeline
```powershell
python run_jailbreak_pipeline.py
```

Or run the PowerShell script:

```powershell
.\run_jailbreak_pipeline.ps1
```

After the run, check these output files:

- `jailbreak_eval/results/prompts.jsonl`
- `jailbreak_eval/results/raw_outputs.jsonl`
- `jailbreak_eval/results/summary.json`
- `jailbreak_eval/results/plots/summary.png`

---

## 5. Optional smoke test

To test the pipeline on a smaller subset first:

```powershell
python run_jailbreak_pipeline.py --max-prompts 10
```

---

## 6. Common issues

### `Missing GEMINI_API_KEY`
This usually means `.env` was not filled correctly, or the environment variable was not loaded in the terminal session.

### `429` / rate limit errors
The script includes basic retry handling. For a quick validation, start with `--max-prompts 10`.

### Why is the model name not the original local model?
This package was converted to an API-based workflow. Because of that, it uses an API-available model name instead of the original local-weight route.
