"""
detail_views.py
Detail View data preparation.
Per-song shape_similarity / contrast_ratio, trajectory data, and feature deviations.
"""

import numpy as np

ALIGNMENT_FEATURES = ['valence', 'energy', 'danceability', 'acousticness', 'liveness']


def _centered_cosine(v1, v2):
    c1 = v1 - v1.mean()
    c2 = v2 - v2.mean()
    n1, n2 = np.linalg.norm(c1), np.linalg.norm(c2)
    if n1 == 0 or n2 == 0:
        return 0.0
    return float(np.dot(c1, c2) / (n1 * n2))


def _contrast_ratio(v1, v2):
    s2 = np.std(v2, ddof=0)
    if s2 == 0:
        return 1.0
    return float(np.std(v1, ddof=0) / s2)


def prepare_detail_data(df, summary, song_stats_by_decade):
    audio_cols = [
        "valence", "energy", "danceability", "liveness",
        "acousticness", "instrumentalness", "speechiness"
    ]

    decade_averages = {}
    for decade in df["decade"].unique():
        dd = df[df["decade"] == decade]
        avg = {}
        for col in audio_cols:
            if col in dd.columns and dd[col].notna().any():
                avg[col] = float(dd[col].mean())
        if "loudness" in dd.columns and dd["loudness"].notna().any():
            avg["loudness_norm"] = max(0, min(1, (float(dd["loudness"].mean()) + 60) / 60))
        decade_averages[decade] = avg

    decade_vectors = {}
    for decade, avg in decade_averages.items():
        decade_vectors[decade] = np.array([avg.get(f, 0.0) for f in ALIGNMENT_FEATURES])

    overall_avg = {}
    for col in audio_cols:
        if col in df.columns and df[col].notna().any():
            overall_avg[col] = float(df[col].mean())

    artist_overall_averages = {}
    for artist in df["artist"].unique():
        ad = df[df["artist"] == artist]
        avg = {}
        for col in audio_cols:
            if col in ad.columns and ad[col].notna().any():
                avg[col] = float(ad[col].mean())
        if "loudness" in ad.columns and ad["loudness"].notna().any():
            avg["loudness_norm"] = max(0, min(1, (float(ad["loudness"].mean()) + 60) / 60))
        artist_overall_averages[artist] = avg

    metric_lookup = {}
    for _, row in summary.iterrows():
        key = f"{row['artist']}||{row['decade']}"
        s_s = row.get("shape_similarity")
        c_r = row.get("contrast_ratio")
        metric_lookup[key] = {
            "shape_similarity": float(s_s) if s_s == s_s else None,
            "contrast_ratio": float(c_r) if c_r == c_r else None,
        }

    artist_all_decades = {}
    for artist in df["artist"].unique():
        rows = summary[summary["artist"] == artist].sort_values("decade")
        decades_list = []
        for _, r in rows.iterrows():
            s_s = r.get("shape_similarity")
            c_r = r.get("contrast_ratio")
            f_s = r.get("final_score_decade")
            decades_list.append({
                "decade": str(r["decade"]),
                "shape_similarity": float(s_s) if s_s == s_s else None,
                "contrast_ratio": float(c_r) if c_r == c_r else None,
                "chart_score": float(f_s) if f_s == f_s else None,
                "appearances": int(r.get("appearance_count", 0)),
            })
        artist_all_decades[artist] = decades_list

    detail_data = {}

    for _, row in summary.iterrows():
        artist = row["artist"]
        decade = row["decade"]
        key = f"{artist}||{decade}"

        songs = song_stats_by_decade[
            (song_stats_by_decade["artist"] == artist) &
            (song_stats_by_decade["decade"] == decade)
        ].copy()
        songs = songs.sort_values("avg_rank").head(20)

        songs_data = df[(df["artist"] == artist) & (df["decade"] == decade)]
        song_features = {}
        song_shape_sims = {}
        song_contrast_ratios = {}

        decade_vec = decade_vectors.get(str(decade))

        for _, sr in songs.iterrows():
            song_name = sr["song"]
            song_df = songs_data[songs_data["song"] == song_name]
            if len(song_df) > 0:
                sa = {}
                for col in audio_cols:
                    if col in song_df.columns and song_df[col].notna().any():
                        sa[col] = float(song_df[col].mean())
                if "loudness" in song_df.columns and song_df["loudness"].notna().any():
                    sa["loudness_norm"] = max(0, min(1, (float(song_df["loudness"].mean()) + 60) / 60))
                song_features[song_name] = sa

                if decade_vec is not None:
                    s_vec = np.array([sa.get(f, 0.0) for f in ALIGNMENT_FEATURES])
                    song_shape_sims[song_name] = round(_centered_cosine(s_vec, decade_vec), 4)
                    song_contrast_ratios[song_name] = round(_contrast_ratio(s_vec, decade_vec), 4)

        decade_deviations = {}
        if decade in decade_averages:
            for col in audio_cols:
                if col in decade_averages[decade] and col in overall_avg:
                    decade_deviations[col] = decade_averages[decade][col] - overall_avg[col]

        artist_decade_audio = {}
        for col in ALIGNMENT_FEATURES:
            if col in songs_data.columns and songs_data[col].notna().any():
                artist_decade_audio[col] = float(songs_data[col].mean())

        artist_decade_deviations = {}
        da = decade_averages.get(decade, {})
        for col in ALIGNMENT_FEATURES:
            if col in artist_decade_audio and col in da:
                artist_decade_deviations[col] = artist_decade_audio[col] - da[col]

        metrics = metric_lookup.get(key, {})

        detail_data[key] = {
            "songs": songs[["song", "avg_rank", "peak_rank", "weeks", "song_score"]].to_dict("records"),
            "artist_audio": artist_overall_averages.get(artist, {}),
            "decade_audio": decade_averages.get(decade, {}),
            "decade_deviations": decade_deviations,
            "song_features": song_features,
            "song_shape_sims": song_shape_sims,
            "song_contrast_ratios": song_contrast_ratios,
            "total_songs": len(songs),
            "total_weeks": int(songs["weeks"].sum()),
            "shape_similarity": metrics.get("shape_similarity"),
            "contrast_ratio": metrics.get("contrast_ratio"),
            "artist_decade_audio": artist_decade_audio,
            "artist_decade_deviations": artist_decade_deviations,
            "artist_all_decades": artist_all_decades.get(artist, []),
        }

    return detail_data