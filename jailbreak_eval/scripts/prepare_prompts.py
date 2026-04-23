import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from common.gemma_api import load_jsonl, write_jsonl  # noqa: E402

PROJECT_DIR = ROOT / 'jailbreak_eval'
DEFAULT_SEED = PROJECT_DIR / 'data' / 'prompts_seed.jsonl'
DEFAULT_OUTPUT = PROJECT_DIR / 'results' / 'prompts.jsonl'


def parse_args():
    parser = argparse.ArgumentParser(
        description='Prepare JailbreakBench-style prompts for the Gemma API evaluation.'
    )
    parser.add_argument('--seed', type=Path, default=DEFAULT_SEED)
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only validate the input prompt file and print a short summary.',
    )
    return parser.parse_args()


def main():
    args = parse_args()
    if not args.seed.exists():
        raise FileNotFoundError(
            f'Cannot find seed prompt file: {args.seed}. '
            'This API package ships with a cached prompt set, so the file should exist.'
        )

    rows = load_jsonl(args.seed)
    misuse = sum(1 for row in rows if row.get('split') == 'misuse')
    benign = sum(1 for row in rows if row.get('split') == 'benign')
    attacks = sorted({row.get('attack_name', 'unknown') for row in rows})

    print(f'Seed file: {args.seed}')
    print(f'Rows: {len(rows)} | misuse={misuse} | benign={benign}')
    print(f'Attack names: {", ".join(attacks)}')

    if args.validate_only:
        return

    args.output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(args.seed, args.output)
    print(f'Wrote prompts to {args.output}')


if __name__ == '__main__':
    main()
