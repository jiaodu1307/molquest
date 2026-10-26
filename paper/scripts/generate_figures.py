#!/usr/bin/env python3
"""Generate every data-driven figure used by the paper."""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path

os.environ.setdefault("SOURCE_DATE_EPOCH", "0")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from rdkit import Chem, DataStructs, RDLogger
from rdkit.Chem import rdFingerprintGenerator
from scipy.cluster.hierarchy import leaves_list, linkage
from scipy.spatial.distance import squareform

RDLogger.DisableLog("rdApp.*")

PAPER_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = PAPER_ROOT / "figures" / "generated"
PDF_METADATA = {"CreationDate": None, "ModDate": None}

plt.rcParams.update(
    {
        "font.size": 9,
        "axes.titlesize": 10,
        "axes.labelsize": 9,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "legend.fontsize": 8.5,
        "pdf.fonttype": 42,
    }
)


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def accuracy_values() -> tuple[list[str], np.ndarray, np.ndarray, np.ndarray]:
    models = json.loads((PAPER_ROOT / "config" / "models.json").read_text(encoding="utf-8"))
    results = load_csv(PAPER_ROOT / "data" / "derived" / "main_results.csv")
    by_key = {(row["model"], row["mode"]): row for row in results}
    values = []
    for model in models:
        agent = float(by_key[(model["id"], "agent")]["accuracy"])
        baseline = float(by_key[(model["id"], "baseline")]["accuracy"])
        values.append((model["name"], agent, baseline, agent - baseline))
    values.sort(key=lambda item: item[1], reverse=True)

    names = [item[0] for item in values]
    agent = np.array([item[1] for item in values])
    baseline = np.array([item[2] for item in values])
    deltas = np.array([item[3] for item in values])
    return names, agent, baseline, deltas


def style_horizontal_axis(axis: plt.Axes) -> None:
    axis.grid(axis="x", color="#D9DDE1", linewidth=0.6, alpha=0.8)
    axis.set_axisbelow(True)
    axis.spines[["top", "right", "left"]].set_visible(False)
    axis.tick_params(axis="both", labelsize=8.5)
    axis.tick_params(axis="y", length=0)


def plot_accuracy_delta() -> None:
    names, _, _, deltas = accuracy_values()
    gain_color = "#009E73"
    loss_color = "#D55E00"

    ordered = sorted(zip(names, deltas), key=lambda item: item[1], reverse=True)
    ordered_names = [item[0] for item in ordered]
    ordered_values = np.array([item[1] for item in ordered])
    colors = [gain_color if value >= 0 else loss_color for value in ordered_values]
    y = np.arange(len(ordered))

    fig, axis = plt.subplots(figsize=(7.0, 5.0))
    axis.barh(y, ordered_values, height=0.58, color=colors, edgecolor="none", zorder=2)
    axis.set_yticks(y, labels=ordered_names)
    axis.invert_yaxis()
    axis.set_xlim(-12.5, 12.5)
    axis.set_xticks([-10, -5, 0, 5, 10])
    axis.axvline(0, color="#3A3A3A", linewidth=1.0, zorder=3)
    axis.set_xlabel("Agent − Baseline (percentage points)", labelpad=7)

    for row, value in zip(y, ordered_values):
        offset = 0.28 if value >= 0 else -0.28
        axis.text(
            value + offset,
            row,
            f"{value:+.2f}",
            va="center",
            ha="left" if value >= 0 else "right",
            fontsize=8,
            color="#222222",
        )

    axis.text(0.74, 1.015, "Improved under Agent", transform=axis.transAxes,
              ha="center", va="bottom", fontsize=8.5, color=gain_color, fontweight="semibold")
    axis.text(0.26, 1.015, "Reduced under Agent", transform=axis.transAxes,
              ha="center", va="bottom", fontsize=8.5, color=loss_color, fontweight="semibold")
    style_horizontal_axis(axis)
    fig.subplots_adjust(left=0.27, right=0.97, top=0.88, bottom=0.13)
    fig.savefig(OUTPUT / "accuracy_delta.pdf", bbox_inches="tight", metadata=PDF_METADATA)
    plt.close(fig)


def molecular_similarity() -> tuple[np.ndarray, np.ndarray]:
    molecules = json.loads((PAPER_ROOT / "data" / "snapshots" / "molecules_530.json").read_text(encoding="utf-8"))
    generator = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
    fingerprints = []
    for row in molecules:
        mol = Chem.MolFromSmiles(row["smiles"])
        if mol is None:
            raise RuntimeError(f"Invalid benchmark SMILES for UUID {row['uuid']}")
        fingerprints.append(generator.GetFingerprint(mol))
    n = len(fingerprints)
    similarity = np.eye(n, dtype=float)
    for index, fingerprint in enumerate(fingerprints):
        if index:
            sims = DataStructs.BulkTanimotoSimilarity(fingerprint, fingerprints[:index])
            similarity[index, :index] = sims
            similarity[:index, index] = sims
    return similarity, np.array([row["uuid"] for row in molecules])


def plot_chemical_space() -> None:
    from sklearn.manifold import TSNE

    similarity, _ = molecular_similarity()
    distance = 1.0 - similarity
    np.fill_diagonal(distance, 0.0)

    embedding = TSNE(
        n_components=3,
        metric="precomputed",
        init="random",
        perplexity=30,
        learning_rate="auto",
        random_state=42,
    ).fit_transform(distance)
    fig = plt.figure(figsize=(6.4, 5.2))
    ax = fig.add_subplot(111, projection="3d")
    ax.scatter(embedding[:, 0], embedding[:, 1], embedding[:, 2], s=8, alpha=0.7, color="#f28e2b")
    ax.set_xlabel("Dim. 1")
    ax.set_ylabel("Dim. 2")
    ax.set_zlabel("")
    ax.set_title("Chemical-space embedding", fontweight="semibold", pad=8)
    fig.subplots_adjust(left=0.02, right=0.88, bottom=0.04, top=0.92)
    fig.text(0.92, 0.53, "Dim. 3", rotation=90, ha="center", va="center")
    fig.savefig(OUTPUT / "chemical_space_tsne.pdf", bbox_inches="tight", metadata=PDF_METADATA)
    plt.close(fig)

    pairwise = similarity[np.triu_indices_from(similarity, k=1)]
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    ax.hist(pairwise, bins=np.linspace(0, 1, 41), color="#76b7b2", edgecolor="#235b63")
    mean_similarity = float(pairwise.mean())
    ax.axvline(mean_similarity, color="#D55E00", linestyle="--", linewidth=1.2,
               label=f"Mean: {mean_similarity:.3f}")
    ax.set_xlabel("Pairwise Tanimoto similarity")
    ax.set_ylabel("Pair count")
    ax.set_title("Pairwise structural similarity", fontweight="semibold", pad=8)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(OUTPUT / "pairwise_similarity.pdf", bbox_inches="tight", metadata=PDF_METADATA)
    plt.close(fig)

    condensed = squareform(distance, checks=False)
    order = leaves_list(linkage(condensed, method="average"))
    ordered = similarity[np.ix_(order, order)]
    fig, ax = plt.subplots(figsize=(6.2, 5.4))
    image = ax.imshow(ordered, vmin=0, vmax=1, cmap="viridis", interpolation="nearest", rasterized=True)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("Clustered similarity matrix", fontweight="semibold", pad=8)
    colorbar = fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    colorbar.set_label("Tanimoto similarity")
    fig.tight_layout()
    fig.savefig(OUTPUT / "similarity_matrix.pdf", bbox_inches="tight", metadata=PDF_METADATA)
    plt.close(fig)


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    plot_accuracy_delta()
    plot_chemical_space()
    print(f"Generated four figures under {OUTPUT.relative_to(PAPER_ROOT)}")


if __name__ == "__main__":
    main()
