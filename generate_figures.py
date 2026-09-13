#!/usr/bin/env python3
"""Generate the figures used in the replication presentation.

All plots are generated locally from the CSV experiment outputs included in
this repository; no external plotting service or copied plot is required.
"""

from pathlib import Path

import csv

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parent
FIGURES = ROOT / "figures"


def load_csv(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def plot_replication_results():
    data = load_csv(ROOT / "replication_results.csv")
    names = [row["Dataset"] for row in data]
    paper = [int(row["Paper output bytes"]) for row in data]
    ours = [int(row["Our output bytes"]) for row in data]

    x = np.arange(len(names))
    width = 0.36

    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.bar(x - width / 2, paper, width, label="Paper")
    ax.bar(x + width / 2, ours, width, label="Our implementation")
    ax.set_ylabel("Encoded size (bytes)")
    ax.set_title("Replication of reported output sizes")
    ax.set_xticks(x, names)
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIGURES / "replication_output_sizes.png", dpi=200)
    plt.close(fig)


def plot_sensitivity_analysis():
    data = load_csv(ROOT / "sensitivity_analysis.csv")
    p = [float(row["Dominant-symbol probability"]) for row in data]
    entropy = [float(row["Entropy H(X) bits/symbol"]) for row in data]
    arithmetic = [float(row["Adaptive arithmetic bits/symbol"]) for row in data]
    huffman = [float(row["Binary Huffman bits/symbol"]) for row in data]

    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.plot(p, entropy, marker="o", label="Theoretical entropy H(X)")
    ax.plot(p, arithmetic, marker="o", label="Adaptive arithmetic coding")
    ax.plot(p, huffman, marker="o", label="Binary Huffman reference")
    ax.set_xlabel("Dominant-symbol probability")
    ax.set_ylabel("Bits per symbol")
    ax.set_title("Compression versus source skew")
    ax.legend()
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIGURES / "sensitivity_analysis.png", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    FIGURES.mkdir(exist_ok=True)
    plot_replication_results()
    plot_sensitivity_analysis()
    print(f"Figures written to: {FIGURES}")
