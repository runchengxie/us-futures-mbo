from __future__ import annotations

import argparse
from pathlib import Path

import databento as db
import matplotlib.pyplot as plt


ACTION_LABELS = {
    "A": "Add",
    "C": "Cancel",
    "M": "Modify",
    "F": "Fill",
    "T": "Trade",
    "R": "Clear",
    "N": "None",
}
COLORS = {
    "Add": "#245b8f",
    "Cancel": "#d9773f",
    "Modify": "#6d8f3d",
    "Fill": "#9b6bb3",
    "Trade": "#c49a3a",
    "Clear": "#6b7280",
    "None": "#cbd5e1",
}


def profile_files(paths: list[Path], sample_count: int = 100_000) -> list[dict]:
    unique: dict[tuple, tuple[Path, db.DBNStore]] = {}
    for path in paths:
        store = db.DBNStore.from_file(path)
        identity = (str(store.schema), tuple(store.symbols), str(store.start), str(store.end))
        if identity not in unique or path.stat().st_size > unique[identity][0].stat().st_size:
            unique[identity] = (path, store)

    rows = []
    for path, store in sorted(unique.values(), key=lambda item: item[1].start):
        frame = next(store.to_df(count=sample_count))
        counts = frame["action"].value_counts(normalize=True)
        rows.append(
            {
                "label": store.start.strftime("%Y-%m-%d"),
                "path": str(path),
                "size_gb": path.stat().st_size / 1024**3,
                "actions": {ACTION_LABELS.get(str(k), str(k)): float(v) for k, v in counts.items()},
                "sample_rows": len(frame),
                "schema": str(store.schema),
                "symbols": ", ".join(store.symbols),
            }
        )
    return rows


def make_chart(rows: list[dict], output: Path) -> None:
    labels = [row["label"] for row in rows]
    fig, (ax_mix, ax_size) = plt.subplots(1, 2, figsize=(13, 6), gridspec_kw={"width_ratios": [1.8, 1]})
    fig.patch.set_facecolor("#f8fafc")
    for ax in (ax_mix, ax_size):
        ax.set_facecolor("#f8fafc")
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", color="#e2e8f0", linewidth=0.8)
        ax.set_axisbelow(True)

    bottom = [0.0] * len(rows)
    order = ["Add", "Cancel", "Modify", "Fill", "Trade", "Clear", "None"]
    for action in order:
        values = [row["actions"].get(action, 0.0) * 100 for row in rows]
        ax_mix.bar(labels, values, bottom=bottom, label=action, color=COLORS[action], width=0.68)
        bottom = [a + b for a, b in zip(bottom, values)]
    ax_mix.set_title("MBO action composition", loc="left", color="#0f172a", weight="bold")
    ax_mix.set_ylabel("Share of first 100,000 records (%)")
    ax_mix.set_ylim(0, 100)
    ax_mix.tick_params(axis="x", rotation=25)
    ax_mix.legend(frameon=False, ncol=2, loc="upper left", bbox_to_anchor=(0, -0.18))

    sizes = [row["size_gb"] for row in rows]
    ax_size.bar(labels, sizes, color="#245b8f", width=0.58)
    ax_size.set_title("On-disk file size", loc="left", color="#0f172a", weight="bold")
    ax_size.set_ylabel("GB, compressed DBN/Zstandard")
    ax_size.tick_params(axis="x", rotation=25)
    for index, value in enumerate(sizes):
        ax_size.text(index, value, f"{value:.2f}", ha="center", va="bottom", fontsize=9)

    fig.suptitle("NQ + MNQ MBO sample profile", x=0.06, ha="left", fontsize=17, weight="bold", color="#0f172a")
    fig.text(0.06, 0.91, "GLBX.MDP3 · mbo · continuous symbols · first 100,000 records per file", color="#475569")
    fig.text(0.06, 0.02, "Source: local Databento DBN files. Action mix is a structural sample, not a full-session estimate.", color="#64748b", fontsize=9)
    fig.tight_layout(rect=(0, 0.07, 1, 0.88))
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=160, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path, default=Path("data"))
    parser.add_argument("--output", type=Path, default=Path("reports/mbo_sample_profile.png"))
    args = parser.parse_args()
    paths = list(args.data_root.glob("nq_mnq_*.dbn.zst"))
    paths += list((args.data_root / "raw").rglob("*.dbn.zst")) if (args.data_root / "raw").exists() else []
    if not paths:
        raise SystemExit("no DBN files found")
    make_chart(profile_files(paths), args.output)
    print(args.output)


if __name__ == "__main__":
    main()
