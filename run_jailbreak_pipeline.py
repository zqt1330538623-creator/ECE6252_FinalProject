import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(cmd):
    print('\n>>>', ' '.join(str(x) for x in cmd))
    subprocess.run(cmd, check=True, cwd=ROOT)


def main():
    parser = argparse.ArgumentParser(description='Run the full Gemma API jailbreak pipeline.')
    parser.add_argument('--model', default=None)
    parser.add_argument('--max-prompts', type=int, default=None)
    parser.add_argument('--max-output-tokens', type=int, default=256)
    parser.add_argument('--temperature', type=float, default=0.0)
    parser.add_argument('--top-p', type=float, default=None)
    parser.add_argument('--top-k', type=int, default=None)
    parser.add_argument('--thinking-level', default=None)
    parser.add_argument('--seed', type=int, default=1234)
    args = parser.parse_args()

    run([sys.executable, 'jailbreak_eval/scripts/prepare_prompts.py'])

    api_cmd = [
        sys.executable,
        'jailbreak_eval/scripts/run_gemma_api.py',
        '--max-output-tokens', str(args.max_output_tokens),
        '--temperature', str(args.temperature),
        '--seed', str(args.seed),
    ]
    if args.model:
        api_cmd += ['--model', args.model]
    if args.max_prompts is not None:
        api_cmd += ['--max-prompts', str(args.max_prompts)]
    if args.top_p is not None:
        api_cmd += ['--top-p', str(args.top_p)]
    if args.top_k is not None:
        api_cmd += ['--top-k', str(args.top_k)]
    if args.thinking_level:
        api_cmd += ['--thinking-level', args.thinking_level]
    run(api_cmd)

    run([sys.executable, 'jailbreak_eval/scripts/analyze_results.py'])
    run([sys.executable, 'jailbreak_eval/scripts/plot_results.py'])

    print('\nDone. Check jailbreak_eval/results/.')


if __name__ == '__main__':
    main()
