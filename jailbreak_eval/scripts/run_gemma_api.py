import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from common.gemma_api import (  # noqa: E402
    DEFAULT_MODEL,
    build_client,
    build_generation_config,
    generate_text,
)

PROJECT_DIR = ROOT / 'jailbreak_eval'
DEFAULT_INPUT = PROJECT_DIR / 'results' / 'prompts.jsonl'
DEFAULT_OUTPUT = PROJECT_DIR / 'results' / 'raw_outputs.jsonl'


def parse_args():
    parser = argparse.ArgumentParser(description='Run jailbreak prompts against the hosted Gemma API.')
    parser.add_argument('--input', type=Path, default=DEFAULT_INPUT)
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument('--model', default=DEFAULT_MODEL)
    parser.add_argument('--max-prompts', type=int, default=None)
    parser.add_argument('--max-output-tokens', type=int, default=256)
    parser.add_argument('--temperature', type=float, default=0.0)
    parser.add_argument('--top-p', type=float, default=None)
    parser.add_argument('--top-k', type=int, default=None)
    parser.add_argument('--thinking-level', default=None)
    parser.add_argument('--seed', type=int, default=1234)
    return parser.parse_args()


def main():
    args = parse_args()
    if not args.input.exists():
        raise FileNotFoundError(
            f'Input file not found: {args.input}. Run prepare_prompts.py first.'
        )

    client = build_client()
    config = build_generation_config(
        max_output_tokens=args.max_output_tokens,
        temperature=args.temperature,
        top_p=args.top_p,
        top_k=args.top_k,
        thinking_level=args.thinking_level,
        seed=args.seed,
    )

    rows = []
    with args.input.open('r', encoding='utf-8') as fin:
        for i, line in enumerate(fin, start=1):
            if args.max_prompts is not None and len(rows) >= args.max_prompts:
                break
            item = json.loads(line)
            result = generate_text(
                client,
                model=args.model,
                prompt=item['prompt'],
                config=config,
            )
            item['response'] = result['response_text']
            item['error'] = result['raw_error']
            item['finish_reason'] = result['finish_reason']
            item['usage_metadata'] = result['usage']
            item['runtime'] = {
                'backend': 'gemini_api',
                'model': args.model,
                'temperature': args.temperature,
                'top_p': args.top_p,
                'top_k': args.top_k,
                'max_output_tokens': args.max_output_tokens,
                'thinking_level': args.thinking_level,
                'seed': args.seed,
            }
            rows.append(item)
            if i % 10 == 0:
                print(f'Processed {i} prompts')

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('w', encoding='utf-8') as fout:
        for row in rows:
            fout.write(json.dumps(row, ensure_ascii=False) + '\n')

    print(f'Saved {len(rows)} rows to {args.output}')


if __name__ == '__main__':
    main()
