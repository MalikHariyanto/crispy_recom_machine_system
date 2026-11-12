"""Descriptive charts and partition summaries for Colab; no model fitting here."""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

COLORS = ["#167C66", "#8DB488", "#E3BA6A", "#5C8DAD", "#BC7C6B", "#9F90B3", "#7D9B89", "#B1AB80"]


def _save(fig, directory, name):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    fig.savefig(directory / name, dpi=160, bbox_inches="tight", facecolor="white")


def plot_dataset_overview(reviews, output_dir):
    """Rating/length use review rows; destination pies count each ID only once."""
    catalog = reviews.drop_duplicates("id_destinasi")
    ratings = pd.to_numeric(reviews["rating"], errors="coerce")
    rating_counts = ratings.value_counts().reindex(range(1, 6), fill_value=0).sort_index()
    weather_reviews = reviews.rekomendasi_cuaca.value_counts().sort_index()
    weather_destinations = catalog.rekomendasi_cuaca.value_counts().sort_index()
    types = catalog.wisata.value_counts()
    lengths = reviews.teks_model.fillna("").str.split().str.len()
    fig, axes = plt.subplots(2, 2, figsize=(14, 10), layout="constrained")
    ax = axes[0, 0]
    bars = ax.bar(rating_counts.index, rating_counts.values, color=COLORS[0], width=.65)
    ax.bar_label(bars, padding=3)
    ax.set(title="Distribusi rating ulasan", xlabel="Rating (bintang)", ylabel="Jumlah ulasan", xticks=range(1, 6))
    ax.set_ylim(0, max(rating_counts.max() * 1.18, 1))
    ax = axes[0, 1]
    bars = ax.bar(weather_reviews.index, weather_reviews.values, color=COLORS[:len(weather_reviews)])
    ax.bar_label(bars, padding=3)
    ax.set(title="Distribusi label cuaca pada ulasan", ylabel="Jumlah ulasan")
    ax.set_ylim(0, max(weather_reviews.max() * 1.18, 1))
    axes[1, 0].pie(weather_destinations.values, labels=weather_destinations.index,
                   autopct="%1.1f%%", startangle=90, colors=COLORS, pctdistance=.78,
                   wedgeprops={"width": .45, "edgecolor": "white"})
    axes[1, 0].set_title(f"Proporsi label cuaca · {len(catalog)} destinasi")
    wedges, _, _ = axes[1, 1].pie(types.values, autopct="%1.1f%%", startangle=90,
                                 colors=COLORS, pctdistance=.78, wedgeprops={"edgecolor": "white"})
    axes[1, 1].legend(wedges, [f"{label} ({count})" for label, count in types.items()],
                         loc="center left", bbox_to_anchor=(1, .5), frameon=False)
    axes[1, 1].set_title("Proporsi jenis wisata · per destinasi")
    fig.suptitle("Eksplorasi dataset wisata Madura", fontsize=18, fontweight="bold")
    _save(fig, output_dir, "eda_rating_cuaca_jenis.png")
    histogram, ax = plt.subplots(figsize=(10, 4), layout="constrained")
    ax.hist(lengths, bins="auto", color=COLORS[0], edgecolor="white")
    ax.set(title="Histogram panjang teks ulasan", xlabel="Jumlah kata setelah preprocessing", ylabel="Jumlah ulasan")
    _save(histogram, output_dir, "histogram_panjang_ulasan.png")
    tables = {
        "rating": rating_counts.rename_axis("rating").reset_index(name="ulasan"),
        "cuaca_ulasan": weather_reviews.rename_axis("cuaca").reset_index(name="ulasan"),
        "cuaca_destinasi": weather_destinations.rename_axis("cuaca").reset_index(name="destinasi"),
        "jenis_destinasi": types.rename_axis("jenis_wisata").reset_index(name="destinasi"),
    }
    for name, table in tables.items():
        count_column = table.columns[-1]
        table["persentase"] = table[count_column] / table[count_column].sum() * 100
        table.to_csv(Path(output_dir) / f"eda_{name}.csv", index=False)
    tables["rating_tidak_valid"] = int((~ratings.isin(range(1, 6))).sum())
    return (fig, histogram), tables


def partition_summary(split):
    rows = []
    for name, frame in (("Train", split.train), ("Validation", split.validation), ("Test", split.test)):
        rows.append({"partisi": name, "ulasan": len(frame), "destinasi": frame.id_destinasi.nunique()})
    table = pd.DataFrame(rows).set_index("partisi")
    for unit in ("ulasan", "destinasi"):
        table[f"persen_{unit}"] = table[unit] / table[unit].sum() * 100
    return table


def plot_partition_overview(split, output_dir):
    """Show realized proportions after cleaning/group split, not nominal ratios."""
    table = partition_summary(split)
    fig, axes = plt.subplots(2, 2, figsize=(13, 9), layout="constrained")
    for column, unit in enumerate(("ulasan", "destinasi")):
        values = table[unit]
        ax = axes[0, column]
        bars = ax.bar(table.index, values, color=COLORS[:3])
        ax.bar_label(bars, labels=[f"{n:,}\n({pct:.1f}%)" for n, pct in zip(values, table[f"persen_{unit}"])], padding=3)
        ax.set(title=f"Pembagian {unit}", ylabel=f"Jumlah {unit}")
        ax.set_ylim(0, max(values.max() * 1.25, 1))
        axes[1, column].pie(values, labels=table.index, autopct="%1.1f%%", colors=COLORS[:3],
                           startangle=90, wedgeprops={"width": .5, "edgecolor": "white"})
        axes[1, column].set_title(f"Proporsi aktual {unit}")
    fig.suptitle("Pembagian train / validation / test", fontsize=17, fontweight="bold")
    _save(fig, output_dir, "pembagian_data.png")
    table.to_csv(Path(output_dir) / "ringkasan_pembagian_data.csv")
    return fig, table
