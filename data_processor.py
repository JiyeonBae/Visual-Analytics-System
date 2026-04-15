"""
data_processor.py
Data loading, preprocessing, and metric computation.
Metrics: Centered Cosine Similarity (Shape) & Contrast Ratio (σ_artist / σ_era)
"""

import pandas as pd
import numpy as np

AUDIO_FEATURES = ['valence', 'energy', 'danceability', 'acousticness', 'liveness']


def _centered_cosine(v1, v2):
    """Centered cosine similarity (= Pearson correlation between feature vectors)."""
    c1 = v1 - v1.mean()
    c2 = v2 - v2.mean()
    n1, n2 = np.linalg.norm(c1), np.linalg.norm(c2)
    if n1 == 0 or n2 == 0:
        return 0.0
    return float(np.dot(c1, c2) / (n1 * n2))


def _contrast_ratio(v1, v2):
    """σ(artist) / σ(era): how spiky vs flat the artist profile is relative to era."""
    s2 = np.std(v2, ddof=0)
    if s2 == 0:
        return 1.0
    return float(np.std(v1, ddof=0) / s2)


def _compute_metrics(df, summary):
    """Compute shape_similarity + contrast_ratio per artist×decade."""
    decade_avgs = df.groupby('decade')[AUDIO_FEATURES].mean()
    artist_decade_avgs = (
        df.groupby(['decade', 'artist'])[AUDIO_FEATURES].mean().reset_index()
    )

    rows = []
    for _, row in artist_decade_avgs.iterrows():
        decade = row['decade']
        if decade not in decade_avgs.index:
            continue
        a_vec = row[AUDIO_FEATURES].values.astype(float)
        e_vec = decade_avgs.loc[decade][AUDIO_FEATURES].values.astype(float)
        rows.append({
            'decade': decade,
            'artist': row['artist'],
            'shape_similarity': round(_centered_cosine(a_vec, e_vec), 4),
            'contrast_ratio': round(_contrast_ratio(a_vec, e_vec), 4),
        })

    metrics_df = pd.DataFrame(rows)
    summary = summary.merge(metrics_df, on=['decade', 'artist'], how='left')
    return summary


def load_and_process_data(csv_path):
    df = pd.read_csv(csv_path)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    if "artist" not in df.columns:
        for cand in ["billboard_artist", "artists", "artist_name"]:
            if cand in df.columns:
                df["artist"] = df[cand]; break

    if "song" not in df.columns:
        for cand in ["name", "title", "track", "song_name"]:
            if cand in df.columns:
                df["song"] = df[cand]; break

    if "rank" not in df.columns:
        for cand in ["position", "chart_rank"]:
            if cand in df.columns:
                df["rank"] = df[cand]; break

    required_audio_cols = ['valence', 'energy', 'danceability', 'liveness', 'acousticness']
    initial_count = len(df)
    df = df.dropna(subset=required_audio_cols)
    removed_count = initial_count - len(df)
    if removed_count > 0:
        print(f"   Audio feature filtering: {initial_count:,} -> {len(df):,} ({len(df)/initial_count*100:.1f}%)")

    def extract_year(row):
        if "year" in row and pd.notnull(row["year"]):
            try: return int(row["year"])
            except: pass
        if "date" in row and pd.notnull(row["date"]):
            try: return pd.to_datetime(row["date"]).year
            except: pass
        return None

    df["year_"] = df.apply(extract_year, axis=1)
    df = df[pd.notnull(df["year_"])].copy()

    df["decade"] = df["year_"].apply(lambda y: f"{(int(y)//10)*10}s" if y else None)
    valid_decades = [f"{d}s" for d in range(1960, 2020, 10)]
    df["decade"] = df["decade"].astype(str).str.strip()
    df = df[df["decade"].isin(valid_decades)]
    df = df.dropna(subset=["artist", "song", "rank"]).copy()

    # ── Statistics ──
    song_rank_by_decade = (
        df.groupby(["decade", "artist", "song"], as_index=False)
        .agg(mean_rank=("rank", "mean"), weekly_appearances=("rank", "count"))
    )
    tmp = song_rank_by_decade.copy()
    tmp["w"] = tmp["weekly_appearances"].astype(float)
    tmp["wr"] = tmp["mean_rank"] * tmp["w"]

    rank_color = (
        tmp.groupby(["decade", "artist"], as_index=False)
        .agg(total_appearances=("weekly_appearances", "sum"),
             wr_sum=("wr", "sum"), w_sum=("w", "sum"))
    )
    rank_color["avg_rank_weighted"] = rank_color["wr_sum"] / rank_color["w_sum"]

    distinct_songs = (
        df.groupby(["decade", "artist"], as_index=False)["song"]
        .nunique().rename(columns={"song": "distinct_song_count"})
    )
    appearance_count = (
        df.groupby(["decade", "artist"], as_index=False)
        .agg(appearance_count=("rank", "count"))
    )

    summary = pd.merge(rank_color, distinct_songs, on=["decade", "artist"], how="inner")
    summary = pd.merge(summary, appearance_count, on=["decade", "artist"], how="inner")

    song_stats_by_decade = (
        df.groupby(["decade", "artist", "song"], as_index=False)
        .agg(avg_rank=("rank", "mean"), peak_rank=("rank", "min"), weeks=("rank", "count"))
    )
    song_stats_by_decade = song_stats_by_decade[song_stats_by_decade["avg_rank"] > 0].copy()
    song_stats_by_decade["song_score"] = song_stats_by_decade["weeks"] / song_stats_by_decade["avg_rank"]

    artist_decade_comp = (
        song_stats_by_decade.groupby(["decade", "artist"], as_index=False)
        .agg(total_songs=("song", "nunique"), weighted_rank_sum=("song_score", "sum"))
    )
    artist_decade_comp["final_score_decade"] = (
        artist_decade_comp["weighted_rank_sum"] * artist_decade_comp["total_songs"]
    )
    summary = summary.merge(
        artist_decade_comp[["decade", "artist", "final_score_decade"]],
        on=["decade", "artist"], how="left"
    )

    # ── Shape Similarity & Contrast Ratio ──
    summary = _compute_metrics(df, summary)
    print(f"   Shape Similarity: min={summary['shape_similarity'].min():.4f} max={summary['shape_similarity'].max():.4f}")
    print(f"   Contrast Ratio:   min={summary['contrast_ratio'].min():.4f} max={summary['contrast_ratio'].max():.4f}")

    # ── Y-axis ordering ──
    song_stats_all = (
        df.groupby(["artist", "song"], as_index=False)
        .agg(avg_rank=("rank", "mean"), weeks=("rank", "count"))
    )
    song_stats_all = song_stats_all[song_stats_all["avg_rank"] > 0].copy()
    song_stats_all["song_score"] = song_stats_all["weeks"] / song_stats_all["avg_rank"]

    artist_scores_all = (
        song_stats_all.groupby("artist", as_index=False)
        .agg(total_songs=("song", "nunique"), weighted_rank_sum=("song_score", "sum"))
    )
    artist_scores_all["final_score"] = (
        artist_scores_all["weighted_rank_sum"] * np.log1p(artist_scores_all["total_songs"])
    )

    viz_artists = summary["artist"].astype(str).unique().tolist()
    artist_scores_all = artist_scores_all[artist_scores_all["artist"].isin(viz_artists)].copy()
    artists_order = artist_scores_all.sort_values("final_score", ascending=False)["artist"].tolist()

    artist_rank_dict = {a: r + 1 for r, a in enumerate(artists_order)}
    summary["overall_rank"] = summary["artist"].map(artist_rank_dict)
    summary["artist_display"] = summary.apply(
        lambda row: f"#{int(row['overall_rank'])} {row['artist']}", axis=1
    )

    summary["decade"] = pd.Categorical(summary["decade"], categories=valid_decades, ordered=True)
    artists_display_order = [f"#{r+1} {a}" for r, a in enumerate(artists_order)]
    summary["artist_display"] = pd.Categorical(
        summary["artist_display"], categories=artists_display_order, ordered=True
    )

    return df, summary, song_stats_by_decade, artists_order, valid_decades