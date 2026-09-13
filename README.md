# Arithmetic Coding for Data Compression — Replication

Independent implementation and replication of the central experiments in:

> Ian H. Witten, Radford M. Neal, and John G. Cleary, **“Arithmetic Coding for Data Compression,”** *Communications of the ACM*, Vol. 30, No. 6, pp. 520–540, June 1987.

## 1. Purpose

This repository contains the implementation used for the information theory term-paper replication. The main objective is to independently reproduce the two artificial test-file results reported by Witten, Neal, and Cleary (1987), while also performing an additional source-skew sensitivity experiment.

The implementation uses the practical design described in the paper:

- 16-bit arithmetic coding range
- maximum cumulative frequency of 16,383
- adaptive model with initial frequency 1 for every symbol
- 256 byte symbols plus an explicit EOF symbol (257 symbols total)
- integer arithmetic
- interval renormalization, including the underflow/E3 case
- adaptive frequency updating and frequency halving when the model approaches the maximum frequency

## 2. Repository structure

```text
.
├── arithmetic_coding_replication.py   # Main implementation and experiments
├── generate_figures.py                # Generates all presentation plots
├── requirements.txt                   # Python dependency specification
├── replication_results.csv            # Replication measurements
├── sensitivity_analysis.csv           # Extension experiment measurements
├── figures/
│   └── sensitivity_analysis.png
├── tests/
│   └── test_arithmetic_coding.py      # Automated correctness/replication tests
├── README.md
└── .gitignore
```

## 3. Requirements

- Python 3.9 or newer
- NumPy (listed in `requirements.txt`)
- Matplotlib (used to generate the presentation figures)

The arithmetic coder itself uses Python's standard library; NumPy is used for the independent sensitivity experiment and Matplotlib is used by `generate_figures.py` to create the plots.

## 4. Setup

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 5. Run the replication

From the repository root:

```bash
python arithmetic_coding_replication.py
```

The program will:

1. Construct the paper's **Alphabet** test file (100,000 bytes).
2. Construct the paper's **Skew statistics** test file (100,000 bytes).
3. Encode each file using the adaptive arithmetic coder.
4. Decode each encoded stream and verify an exact round trip.
5. Report output size and bits per character.
6. Run the additional binary source-skew sensitivity experiment.

The expected central replication results are:

| Dataset | Input | Paper output | Our output | Bits/character | Round trip |
|---|---:|---:|---:|---:|---|
| Alphabet | 100,000 bytes | 59,292 bytes | 59,292 bytes | 4.74335 | Pass |
| Skew statistics | 100,000 bytes | 12,092 bytes | 12,092 bytes | 0.96736 | Pass |

The exact byte counts are the primary replication target.

## 6. Run automated tests

The repository includes tests so the implementation is not dependent on a notebook or manual inspection.

Run:

```bash
python -m unittest discover -s tests -v
```

The tests check:

- exact encode/decode round trips for several inputs;
- round trips for both paper test files; and
- the reported 59,292-byte and 12,092-byte output sizes.

## 7. Reproduce the figures/data

The CSV files contain the measurements used in the presentation:

- `replication_results.csv` — paper-versus-implementation output sizes and bits/character.
- `sensitivity_analysis.csv` — theoretical entropy, adaptive arithmetic-coding performance, and the illustrative binary Huffman baseline for different source-skew probabilities.

The PNG files in `figures/` are generated from the experiment data and are included as supporting artifacts for the presentation. To regenerate them from the CSV files, run:

```bash
python generate_figures.py
```

This makes the plot-generation process reproducible and keeps the figures under student-written code rather than relying on copied/generated external plots.

## 8. Additional sensitivity experiment

The paper replication uses its specified artificial files. As an extension beyond the paper, the implementation also generates binary IID sources with dominant-symbol probabilities:

```text
0.50, 0.60, 0.70, 0.80, 0.90, 0.95, 0.99
```

For each probability, the script compares:

- theoretical binary entropy `H(X)`;
- measured bits/symbol from the adaptive arithmetic coder; and
- a simple binary Huffman reference of 1 bit/symbol.

This experiment is explicitly an **extension**, not a reproduction of the paper's complete adaptive-Huffman benchmark.

## 9. Reproducibility notes

- The sensitivity experiment uses NumPy random seed `42`.
- The two replication datasets are deterministic and constructed directly in the script according to the paper's descriptions.
- No external dataset is required to run the central replication.
- The original paper's full English text benchmark file is not distributed with this repository; therefore, the repository does not claim to reproduce every row of the paper's performance tables.

## 10. Academic integrity / scope

This is an independent implementation for replication. The code was written to reproduce the algorithmic behavior and central artificial test results reported in the assigned paper. The paper remains the source for the original experimental claims; the measurements in this repository are independently generated by the submitted code.

## 11. Reference

Witten, I. H., Neal, R. M., & Cleary, J. G. (1987). Arithmetic coding for data compression. *Communications of the ACM, 30*(6), 520–540. https://doi.org/10.1145/214762.214771
