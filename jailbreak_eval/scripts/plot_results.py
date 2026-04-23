import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

DEFAULT_INPUT = Path('jailbreak_eval/results/summary.json')
DEFAULT_OUTPUT = Path('jailbreak_eval/results/plots/summary.png')


def parse_args():
    parser = argparse.ArgumentParser(description='Plot jailbreak summary statistics.')
    parser.add_argument('--input', type=Path, default=DEFAULT_INPUT)
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def load_summary(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def annotate_bars(ax, bars):
    for bar in bars:
        value = bar.get_height()
        ax.annotate(
            f'{value:.2f}',
            (bar.get_x() + bar.get_width() / 2, value),
            xytext=(0, 4),
            textcoords='offset points',
            ha='center',
            va='bottom',
            fontsize=9,
        )


def plot_overall(ax, summary):
    labels = ['Baseline ASR', 'Jailbreak ASR', 'Benign OR']
    values = [
        summary['overall']['misuse_baseline_asr'],
        summary['overall']['misuse_jailbreak_asr'],
        summary['overall']['benign_overrefusal_rate'],
    ]
    bars = ax.bar(labels, values)
    annotate_bars(ax, bars)
    ax.set_ylim(0, 1.0)
    ax.set_ylabel('Rate')
    ax.set_title('Overall Summary')
    ax.grid(axis='y', linestyle='--', alpha=0.35)


def plot_categories(ax, summary):
    categories = sorted(summary['by_category'])
    x = np.arange(len(categories))
    width = 0.25

    baseline = [summary['by_category'][cat]['baseline_asr'] for cat in categories]
    jailbreak = [summary['by_category'][cat]['jailbreak_asr'] for cat in categories]
    benign = [summary['by_category'][cat]['benign_overrefusal_rate'] for cat in categories]

    ax.bar(x - width, baseline, width=width, label='Baseline ASR')
    ax.bar(x, jailbreak, width=width, label='Jailbreak ASR')
    ax.bar(x + width, benign, width=width, label='Benign OR')
    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=20, ha='right')
    ax.set_ylim(0, 1.0)
    ax.set_ylabel('Rate')
    ax.set_title('Category-wise Rates')
    ax.legend(frameon=False)
    ax.grid(axis='y', linestyle='--', alpha=0.35)


def plot_attacks(ax, summary):
    attacks = sorted(summary['by_attack'])
    values = [summary['by_attack'][name]['jailbreak_asr'] for name in attacks]
    bars = ax.bar(attacks, values)
    annotate_bars(ax, bars)
    ax.set_ylim(0, 1.0)
    ax.set_ylabel('Rate')
    ax.set_title('Attack-wise Jailbreak ASR')
    ax.grid(axis='y', linestyle='--', alpha=0.35)


def main():
    args = parse_args()
    summary = load_summary(args.input)

    fig, axes = plt.subplots(3, 1, figsize=(11, 15), constrained_layout=True)
    plot_overall(axes[0], summary)
    plot_categories(axes[1], summary)
    plot_attacks(axes[2], summary)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=220, bbox_inches='tight')
    print(f'Saved plot to {args.output}')


if __name__ == '__main__':
    main()
