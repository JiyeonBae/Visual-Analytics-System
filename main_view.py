"""
main_view.py
Main scatter plot chart (artist × decade × performance).
Dark theme to match the overall visualization.
"""

import plotly.express as px
import numpy as np


def create_main_chart(summary, valid_decades, artists_display_order):
    cmin = float(np.nanmin(summary["final_score_decade"]))
    cmax = float(np.nanmax(summary["final_score_decade"]))

    fig = px.scatter(
        summary,
        x="decade",
        y="artist_display",
        size="appearance_count",
        color="final_score_decade",
        color_continuous_scale="SunsetDark",
        opacity=1.0,
        range_color=[cmin, cmax],
        size_max=45,
        custom_data=["artist", "decade"],
        hover_data={
            "artist_display": False,
            "decade": True,
            "overall_rank": True,
            "final_score_decade": False,
            "avg_rank_weighted": ":.2f",
            "distinct_song_count": True,
            "appearance_count": True,
            "total_appearances": False,
        },
        title=(
            "How Did Top Artists' Success and Styles Change Across Six Decades (1960s\u20132010s)?"
            "<br><sup>Bubble Size = Total Weeks on Chart | "
            "Color Intensity = Performance Score</sup>"
        ),
    )

    for artist_display, g in summary.groupby("artist_display", observed=True):
        g = g.sort_values("decade")
        fig.add_scatter(
            x=g["decade"],
            y=g["artist_display"],
            mode="lines",
            line=dict(color="rgba(150,150,150,0.35)", width=2),
            showlegend=False,
            hoverinfo="skip",
        )

    lines = [tr for tr in fig.data if getattr(tr, "mode", "") == "lines"]
    markers = [tr for tr in fig.data if "marker" in getattr(tr, "mode", "markers")]
    fig.data = tuple(lines + markers)

    fig.update_layout(
        xaxis=dict(
            title="Decade (1960s\u20132010s)",
            categoryorder="array",
            categoryarray=valid_decades,
            gridcolor="rgba(0,0,0,0.07)",
        ),
        yaxis=dict(
            title="Artist (Ranked by Overall Score)",
            categoryorder="array",
            categoryarray=artists_display_order,
            autorange="reversed",
            gridcolor="rgba(0,0,0,0.07)",
        ),
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.8)",
        font=dict(family="DM Sans, sans-serif", color="#555"),
        coloraxis_colorbar=dict(
            title="Decade Score<br>(weeks/rank x songs)", thickness=25
        ),
    )
    return fig