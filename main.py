"""
main.py
Integrates all modules and generates the interactive HTML visualization.
"""

import json
import pandas as pd
from data_processor import load_and_process_data
from main_view import create_main_chart
from detail_views import prepare_detail_data
from html_template import generate_html

CSV_PATH = "hot100_top10_1960_2019_enriched.csv"
OUTPUT_FILE = "interactive_hot100.html"


def main():
    print("Hot 100 Interactive Visualization Generator")
    print("=" * 60)

    print("\nStep 1: Loading and processing data...")
    df, summary, song_stats_by_decade, artists_order, valid_decades = load_and_process_data(CSV_PATH)
    print(f"   {len(df)} records, {len(artists_order)} artists, {len(valid_decades)} decades")

    print("\nStep 2: Creating main chart...")
    artists_display_order = [f"#{r+1} {a}" for r, a in enumerate(artists_order)]
    fig = create_main_chart(summary, valid_decades, artists_display_order)

    print("\nStep 3: Preparing detail view data...")
    detail_data = prepare_detail_data(df, summary, song_stats_by_decade)
    print(f"   {len(detail_data)} artist x decade combinations")

    print("\nStep 3.5: Extracting trajectories...")
    trajectory = {}
    for artist in artists_order:
        rows = summary[summary['artist'] == artist].sort_values('decade')
        trajectory[artist] = [
            {
                "decade": str(r['decade']),
                "shape_similarity": float(r['shape_similarity']),
                "contrast_ratio": float(r['contrast_ratio']),
            }
            for _, r in rows.iterrows()
            if pd.notna(r.get('shape_similarity')) and pd.notna(r.get('contrast_ratio'))
        ]
    trajectory_json = json.dumps(trajectory)

    # Statistical validation
    from scipy.stats import pearsonr
    shape_vals = summary['shape_similarity'].dropna().values
    contrast_vals = summary['contrast_ratio'].dropna().values
    min_len = min(len(shape_vals), len(contrast_vals))
    if min_len > 2:
        r_val, p_val = pearsonr(shape_vals[:min_len], contrast_vals[:min_len])
        print(f"\n   Orthogonality check: Pearson r = {r_val:+.4f}, p = {p_val:.4f}")
        print(f"   {'PASS: Axes are independent' if p_val > 0.05 else 'WARN: Axes may be correlated'}")

    print("\nStep 4: Generating HTML...")
    fig.update_layout(autosize=True)
    temp_html = fig.to_html(
        include_plotlyjs='cdn',
        full_html=False,
        div_id='mainChart',
        config={'responsive': True}
    )
    detail_json = json.dumps(detail_data)

    html_content = generate_html(temp_html, detail_json, trajectory_json)

    print("\nStep 5: Saving...")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"\n{'='*60}")
    print(f"Done: {OUTPUT_FILE} ({len(html_content):,} bytes)")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()