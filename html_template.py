"""
html_template.py
HTML template with JavaScript for the interactive visualization.

Visual Design:
  View 1 — Main Bubble Chart (artist × decade × performance)
  View 2 — Quadrant Trajectory Map (THE novel contribution)
           X = Shape Similarity, Y = Contrast Ratio
           Lines show decade-to-decade movement per artist
           Background quadrant shading with semantic labels
  View 3 — Dual Metric Trajectories (temporal line charts)
  View 4 — Detail Panel (on-click: metric badges, deviation bars, radar)

Metric Design (Cronbach & Gleser 1953; Breese et al. 1998):
  Axis 1: Profile Shape Similarity (Centered Cosine ≡ Pearson r)
  Axis 2: Profile Contrast Ratio (σ_artist / σ_era)
  Empirically orthogonal (Pearson r ≈ 0.00, p > 0.05).
"""


def generate_html(plotly_chart_html, detail_data_json, trajectory_json):
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Artist–Era Profile Analysis | Billboard Hot 100 (1960–2019)</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,500;0,9..40,700;1,9..40,400&family=JetBrains+Mono:wght@400;600&display=swap');

        :root {{
            --bg: #f8f9fa;
            --surface: #ffffff;
            --surface2: #f1f3f5;
            --border: #dee2e6;
            --text: #333333;
            --text2: #868e96;
            --accent: #667eea;
            --green: #059669;
            --purple: #7c3aed;
            --red: #ef553b;
            --amber: #d97706;
            --q-ac: rgba(5, 150, 105, 0.06);
            --q-sc: rgba(29, 78, 216, 0.06);
            --q-pm: rgba(185, 28, 28, 0.06);
            --q-mm: rgba(161, 98, 7, 0.06);
        }}

        * {{ margin:0; padding:0; box-sizing:border-box; }}
        body {{
            font-family: 'DM Sans', sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.5;
        }}

        .main-container {{ max-width: 1600px; margin: 0 auto; padding: 24px; }}

        /* ── Section Cards ── */
        .card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
        }}
        .card-header {{
            font-size: 15px;
            font-weight: 700;
            color: var(--text);
            margin-bottom: 6px;
            letter-spacing: -0.02em;
        }}
        .card-sub {{
            font-size: 12px;
            color: var(--text2);
            margin-bottom: 18px;
            font-family: 'JetBrains Mono', monospace;
        }}

        /* ── Main Chart ── */
        #mainChart {{
            width: 100% !important;
            min-height: 75vh !important;
        }}
        #mainChart .js-plotly-plot {{ width: 100% !important; min-height: 75vh !important; }}

        /* ── Overview Grid ── */
        .overview-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }}
        .overview-grid .card.full {{ grid-column: 1 / -1; }}

        #quadrantChart {{ width: 100%; height: 520px; }}

        /* ── Quadrant Legend ── */
        .quadrant-legend {{
            display: flex;
            justify-content: center;
            gap: 16px;
            margin-top: 10px;
            flex-wrap: wrap;
        }}
        .q-item {{
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 12px;
            padding: 6px 10px;
            border-radius: 8px;
            border: 1px solid var(--border);
            white-space: nowrap;
        }}
        .q-label {{ font-weight: 600; }}
        .q-desc {{ color: var(--text2); font-size: 11px; }}

        /* ── Stat Validation Badge ── */
        .stat-badge {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            padding: 4px 10px;
            border-radius: 6px;
            background: var(--surface2);
            border: 1px solid var(--border);
            color: var(--text2);
            margin-right: 8px;
        }}
        .stat-badge .dot {{ width:6px; height:6px; border-radius:50%; background: var(--green); }}

        /* ── Prompt Banner ── */
        .prompt-banner {{
            text-align: center;
            color: var(--text2);
            padding: 12px;
            font-size: 13px;
            border: 1px dashed var(--border);
            border-radius: 8px;
            margin-bottom: 20px;
        }}

        /* ── Detail Grid ── */
        .detail-container {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }}
        .detail-box {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 24px;
        }}
        .detail-header {{
            font-size: 15px;
            font-weight: 700;
            color: var(--text);
            margin-bottom: 16px;
            padding-left: 12px;
            border-left: 3px solid var(--accent);
        }}
        .info-box {{
            background: var(--surface2);
            border: 1px solid var(--border);
            padding: 14px;
            border-radius: 8px;
            margin-bottom: 16px;
        }}
        .info-box p {{ margin: 6px 0; font-size: 13px; color: var(--text2); }}
        .info-box strong {{ color: var(--accent); }}

        /* ── Metric Badge ── */
        .metric-badge-row {{ display: flex; gap: 10px; margin-bottom: 14px; }}
        .metric-card {{
            flex: 1;
            padding: 14px;
            border-radius: 8px;
            border: 1px solid var(--border);
            text-align: center;
        }}
        .metric-card.shape {{ border-color: var(--green); background: rgba(52,211,153,0.06); }}
        .metric-card.contrast {{ border-color: var(--purple); background: rgba(167,139,250,0.06); }}
        .metric-card .metric-label {{
            font-size: 10px; font-weight: 600; text-transform: uppercase;
            letter-spacing: 0.8px; margin-bottom: 4px;
        }}
        .metric-card.shape .metric-label {{ color: var(--green); }}
        .metric-card.contrast .metric-label {{ color: var(--purple); }}
        .metric-card .metric-value {{
            font-size: 24px; font-weight: 700; line-height: 1.1;
            font-family: 'JetBrains Mono', monospace;
        }}
        .metric-card.shape .metric-value {{ color: var(--green); }}
        .metric-card.contrast .metric-value {{ color: var(--purple); }}
        .metric-card .metric-desc {{ font-size: 10px; color: var(--text2); margin-top: 3px; }}

        .quadrant-tag {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 16px;
            font-size: 11px;
            font-weight: 600;
            margin-bottom: 12px;
            letter-spacing: 0.3px;
        }}
        .quadrant-tag.amplified-conformist {{ background: #ecfdf5; color: #047857; border: 1px solid #a7f3d0; }}
        .quadrant-tag.smoothed-conformist {{ background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; }}
        .quadrant-tag.polarized-maverick {{ background: #fef2f2; color: #b91c1c; border: 1px solid #fecaca; }}
        .quadrant-tag.muted-maverick {{ background: #fefce8; color: #a16207; border: 1px solid #fde68a; }}

        /* ── Artist-Era Block (unified container) ── */
        .artist-era-block {{
            background: var(--surface);
            border: 1.5px solid var(--border);
            padding: 16px;
            border-radius: 10px;
            margin-bottom: 14px;
        }}

        /* ── Artist-Era Deviation ── */
        .artist-era-signature {{
            padding: 0;
            margin-bottom: 0;
        }}
        .artist-era-title {{
            font-weight: 600; font-size: 13px;
            margin-bottom: 10px; color: var(--text);
        }}

        /* ── Diverging Bars ── */
        .bar-chart-container {{ display:flex; flex-direction:column; gap:8px; }}
        .bar-row {{ display:flex; align-items:center; gap:8px; }}
        .bar-label {{ width:110px; font-size:11px; font-weight:600; text-align:right; color:var(--text2); }}
        .bar-track {{
            flex:1; height:20px; background:var(--surface2);
            border-radius:4px; position:relative; overflow:visible;
        }}
        .bar-fill {{
            position:absolute; height:100%; transition:width 0.3s ease; border-radius:4px;
        }}
        .bar-fill.negative {{ right:50%; background: #60a5fa; }}
        .bar-fill.positive {{ left:50%; background: var(--red); }}
        .bar-center-line {{
            position:absolute; left:50%; top:-2px; bottom:-2px;
            width:1px; background:var(--text2); z-index:2; opacity:0.4;
        }}
        .bar-value {{
            width:46px; font-size:11px; font-weight:700; text-align:center;
            font-family:'JetBrains Mono', monospace;
        }}
        .bar-value.negative {{ color:#60a5fa; }}
        .bar-value.positive {{ color:var(--red); }}

        /* ── Song Signature ── */
        .song-signature {{
            background: var(--surface);
            border: 1px solid rgba(248,113,113,0.3);
            padding: 14px;
            border-radius: 8px;
            margin-bottom: 14px;
        }}
        .song-signature-title {{
            font-weight:600; font-size:13px; margin-bottom:10px; color:var(--red);
        }}
        .song-metric-badge {{
            display:inline-block; font-size:10px; font-weight:600;
            padding:2px 7px; border-radius:8px; margin-left:5px;
            font-family:'JetBrains Mono', monospace;
        }}

        /* ── Table ── */
        table {{ width:100%; border-collapse:collapse; font-size:12px; }}
        th {{
            background: var(--surface2);
            color: #5368E8;
            padding: 10px 8px;
            text-align: left;
            font-weight: 600;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            position: sticky; top: 0;
        }}
        td {{ padding:9px 8px; border-bottom:1px solid var(--border); color:var(--text); }}
        tr {{ cursor:pointer; transition:background 0.15s; }}
        tr:hover {{ background: var(--surface2); }}
        tr.selected {{ background: rgba(108,138,255,0.1) !important; border-left:3px solid var(--accent); }}
        .table-container {{
            max-height: 460px; overflow-y: auto;
            border: 1px solid var(--border); border-radius: 8px;
        }}

        .initial-message {{
            grid-column: 1 / -1;
            text-align: center;
            color: var(--text2);
            padding: 50px 20px;
            font-size: 15px;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
        }}

        #eraRadarChart, #songRadarChart {{ min-height: 380px; }}
        .song-signature #songRadarChart {{
            margin-top: 12px; padding-top: 12px;
            border-top: 1px solid rgba(248,113,113,0.15);
        }}

        @media (max-width: 1200px) {{
            .detail-container {{ grid-template-columns: 1fr; }}
            .overview-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="main-container">

        <!-- ═══ V1: Main Bubble Chart ═══ -->
        <div class="card">
            {plotly_chart_html}
        </div>

        <!-- ═══ V2: Quadrant Trajectory (Novel Contribution) ═══ -->
        <div class="card full">
            <div class="card-header">Artist–Era Quadrant Trajectory Map</div>
            <div class="card-sub">
                X = Shape Similarity (centered cosine) &nbsp;|&nbsp;
                Y = Contrast Ratio (&sigma;_artist / &sigma;_era) &nbsp;|&nbsp;
                Lines = decade-to-decade movement
                &nbsp;&nbsp;
                <span class="stat-badge"><span class="dot"></span> Axes verified orthogonal (Pearson r &asymp; 0.00, p &gt; 0.05)</span>
            </div>
            <div id="quadrantChart"></div>
            <div class="quadrant-legend">
                <div class="q-item" style="background:#ecfdf5; border-color:#a7f3d0;">
                    <span class="q-label" style="color:#047857;">Amplified Conformist</span><span class="q-desc">&nbsp;Same pattern, more extreme peaks</span>
                </div>
                <div class="q-item" style="background:#eff6ff; border-color:#bfdbfe;">
                    <span class="q-label" style="color:#1d4ed8;">Smoothed Conformist</span><span class="q-desc">&nbsp;Same pattern, more uniform</span>
                </div>
                <div class="q-item" style="background:#fef2f2; border-color:#fecaca;">
                    <span class="q-label" style="color:#b91c1c;">Polarized Maverick</span><span class="q-desc">&nbsp;Different pattern, extreme peaks</span>
                </div>
                <div class="q-item" style="background:#fefce8; border-color:#fde68a;">
                    <span class="q-label" style="color:#a16207;">Muted Maverick</span><span class="q-desc">&nbsp;Different pattern, flat profile</span>
                </div>
            </div>
        </div>

        <!-- ═══ Detail Prompt ═══ -->
        <div class="prompt-banner" id="permanentMessage">
            Click any bubble in the main chart to explore detailed song information and audio features
        </div>

        <!-- ═══ V4: Detail Panel ═══ -->
        <div class="detail-container">
            <div class="detail-box" id="detailSection" style="display:none;">
                <div class="detail-header">Song Performance Metrics</div>
                <div id="infoBox" class="info-box"></div>
                <div class="table-container"><div id="songTable"></div></div>
            </div>
            <div class="detail-box" id="audioSection" style="display:none;">
                <div class="detail-header" id="audioHeader">Audio Features Profile</div>
                <div class="artist-era-block" id="artistEraBlock">
                    <div id="metricBadge"></div>
                    <div id="artistEraContainer"></div>
                    <div id="radarContainer"><div id="eraRadarChart"></div></div>
                </div>
                <div id="songSignatureContainer"></div>
            </div>
            <div class="initial-message" id="initialMessage">
                Click any bubble to see details here
            </div>
        </div>
    </div>

    <script>
        // ══════════════════════════════════════════════
        // DATA EMBED
        // ══════════════════════════════════════════════
        const detailData = {detail_data_json};
        const trajectoryData = {trajectory_json};

        let chartInitialized = false;
        let currentArtist = '';
        let currentDecade = '';
        let currentData = null;

        // ══════════════════════════════════════════════
        // QUADRANT THRESHOLDS (median-based)
        // ══════════════════════════════════════════════
        const allShapeSims = [];
        const allContrastRatios = [];
        Object.values(detailData).forEach(function(d) {{
            if (d.shape_similarity != null) allShapeSims.push(d.shape_similarity);
            if (d.contrast_ratio != null) allContrastRatios.push(d.contrast_ratio);
        }});
        allShapeSims.sort(function(a,b){{ return a-b; }});
        allContrastRatios.sort(function(a,b){{ return a-b; }});
        const medianShapeSim = allShapeSims.length > 0 ? allShapeSims[Math.floor(allShapeSims.length/2)] : 0.97;
        const medianContrast = 1.0;  // Theoretical boundary: σ_artist/σ_era = 1.0

        function getQuadrant(shapeSim, contrastRatio) {{
            const highShape = shapeSim >= medianShapeSim;
            const highContrast = contrastRatio >= medianContrast;
            if (highShape && highContrast) return {{ label:'Amplified Conformist', css:'amplified-conformist', icon:'' }};
            if (highShape && !highContrast) return {{ label:'Smoothed Conformist', css:'smoothed-conformist', icon:'' }};
            if (!highShape && highContrast) return {{ label:'Polarized Maverick', css:'polarized-maverick', icon:'' }};
            return {{ label:'Muted Maverick', css:'muted-maverick', icon:'' }};
        }}

        // ══════════════════════════════════════════════
        // COLORS & CONSTANTS
        // ══════════════════════════════════════════════
        const COLORS = [
            '#e6194b','#3cb44b','#4363d8','#f58231','#911eb4',
            '#42d4f4','#f032e6','#6B8E23','#A0522D','#469990'
        ];
        const ARTIST_COLORS = {{}};
        Object.keys(trajectoryData).forEach(function(artist, idx) {{
            ARTIST_COLORS[artist] = COLORS[idx % COLORS.length];
        }});
        const DECADE_ORDER = ['1960s','1970s','1980s','1990s','2000s','2010s'];
        const DECADE_SYMBOLS = {{ '1960s':'circle','1970s':'square','1980s':'diamond',
                                  '1990s':'cross','2000s':'star','2010s':'hexagram' }};

        // Light plotly template
        const LIGHT_LAYOUT = {{
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(255,255,255,0.8)',
            font: {{ family: 'DM Sans', color: '#555', size: 11 }},
            xaxis: {{ gridcolor: 'rgba(0,0,0,0.07)', zerolinecolor: 'rgba(0,0,0,0.12)' }},
            yaxis: {{ gridcolor: 'rgba(0,0,0,0.07)', zerolinecolor: 'rgba(0,0,0,0.12)' }}
        }};

        // ══════════════════════════════════════════════
        // RESIZE HANDLER
        // ══════════════════════════════════════════════
        function resizeMainChart() {{
            if (!chartInitialized) return;
            const el = document.getElementById('mainChart');
            if (el && el.data) Plotly.Plots.resize(el);
        }}

        window.addEventListener('load', function() {{
            setTimeout(function() {{ chartInitialized = true; }}, 500);
            renderQuadrantChart();
        }});

        let resizeTimeout;
        window.addEventListener('resize', function() {{
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(function() {{
                resizeMainChart();
                ['quadrantChart',
                 'eraRadarChart','songRadarChart'].forEach(function(id) {{
                    const el = document.getElementById(id);
                    if (el && el.data) Plotly.Plots.resize(id);
                }});
            }}, 250);
        }});

        // ══════════════════════════════════════════════
        // V2: QUADRANT TRAJECTORY MAP (Novel Contribution)
        // ══════════════════════════════════════════════
        function renderQuadrantChart() {{
            const artists = Object.keys(trajectoryData);
            const traces = [];

            // Compute global bounds
            let xMin=1, xMax=-1, yMin=Infinity, yMax=0;
            artists.forEach(function(a) {{
                trajectoryData[a].forEach(function(p) {{
                    if (p.shape_similarity < xMin) xMin = p.shape_similarity;
                    if (p.shape_similarity > xMax) xMax = p.shape_similarity;
                    if (p.contrast_ratio < yMin) yMin = p.contrast_ratio;
                    if (p.contrast_ratio > yMax) yMax = p.contrast_ratio;
                }});
            }});
            const xPad = (xMax - xMin) * 0.08;
            const yPad = (yMax - yMin) * 0.08;

            // Quadrant background shapes
            const shapes = [
                // Amplified Conformist (top-right)
                {{ type:'rect', x0:medianShapeSim, x1:xMax+xPad, y0:medianContrast, y1:yMax+yPad,
                   fillcolor:'rgba(236,253,245,0.5)', line:{{ width:0 }}, layer:'below' }},
                // Smoothed Conformist (bottom-right)
                {{ type:'rect', x0:medianShapeSim, x1:xMax+xPad, y0:yMin-yPad, y1:medianContrast,
                   fillcolor:'rgba(239,246,255,0.5)', line:{{ width:0 }}, layer:'below' }},
                // Polarized Maverick (top-left)
                {{ type:'rect', x0:xMin-xPad, x1:medianShapeSim, y0:medianContrast, y1:yMax+yPad,
                   fillcolor:'rgba(254,242,242,0.5)', line:{{ width:0 }}, layer:'below' }},
                // Muted Maverick (bottom-left)
                {{ type:'rect', x0:xMin-xPad, x1:medianShapeSim, y0:yMin-yPad, y1:medianContrast,
                   fillcolor:'rgba(254,252,232,0.5)', line:{{ width:0 }}, layer:'below' }},
                // Median lines
                {{ type:'line', x0:medianShapeSim, x1:medianShapeSim, y0:yMin-yPad, y1:yMax+yPad,
                   line:{{ color:'rgba(0,0,0,0.15)', width:1, dash:'dot' }}, layer:'below' }},
                {{ type:'line', x0:xMin-xPad, x1:xMax+xPad, y0:medianContrast, y1:medianContrast,
                   line:{{ color:'rgba(0,0,0,0.15)', width:1, dash:'dot' }}, layer:'below' }},
            ];

            // Quadrant labels as annotations
            const annotations = [
                {{ x:xMax+xPad*0.5, y:yMax+yPad*0.3, text:'Amplified<br>Conformist',
                   showarrow:false, font:{{ size:10, color:'#047857' }}, xanchor:'right', yanchor:'top' }},
                {{ x:xMax+xPad*0.5, y:yMin-yPad*0.3, text:'Smoothed<br>Conformist',
                   showarrow:false, font:{{ size:10, color:'#1d4ed8' }}, xanchor:'right', yanchor:'bottom' }},
                {{ x:xMin-xPad*0.5, y:yMax+yPad*0.3, text:'Polarized<br>Maverick',
                   showarrow:false, font:{{ size:10, color:'#b91c1c' }}, xanchor:'left', yanchor:'top' }},
                {{ x:xMin-xPad*0.5, y:yMin-yPad*0.3, text:'Muted<br>Maverick',
                   showarrow:false, font:{{ size:10, color:'#a16207' }}, xanchor:'left', yanchor:'bottom' }},
            ];


            artists.forEach(function(artist, idx) {{
                const d = trajectoryData[artist];
                if (d.length === 0) return;
                const color = COLORS[idx % COLORS.length];

                traces.push({{
                    x: d.map(function(p){{ return p.shape_similarity; }}),
                    y: d.map(function(p){{ return p.contrast_ratio; }}),
                    mode: 'lines+markers+text',
                    name: artist,
                    line: {{ color: color, width: 2, shape: 'spline' }},
                    opacity: 0.8,
                    marker: {{
                        size: 6,
                        color: color,
                        symbol: 'circle',
                        line: {{ color: 'rgba(255,255,255,0.8)', width: 1 }}
                    }},
                    text: d.map(function(p){{ return p.decade.replace('s',''); }}),
                    textposition: 'top center',
                    textfont: {{ size: 9, color: color, family: 'JetBrains Mono' }},
                    hovertemplate: '<b>' + artist + '</b><br>%{{text}}s<br>Shape: %{{x:.4f}}<br>Contrast: %{{y:.4f}}<extra></extra>'
                }});
            }});

            Plotly.newPlot('quadrantChart', traces, {{
                ...LIGHT_LAYOUT,
                xaxis: {{
                    ...LIGHT_LAYOUT.xaxis,
                    title: {{ text: 'Shape Similarity (Centered Cosine)', font: {{ size: 12 }} }},
                    range: [xMin - xPad, xMax + xPad],
                    tickformat: '.2f'
                }},
                yaxis: {{
                    ...LIGHT_LAYOUT.yaxis,
                    title: {{ text: 'Contrast Ratio (\\u03c3_artist / \\u03c3_era)', font: {{ size: 12 }} }},
                    range: [yMin - yPad, yMax + yPad],
                    tickformat: '.2f'
                }},
                shapes: shapes,
                annotations: [...annotations],
                legend: {{
                    orientation: 'h', yanchor: 'top', y: -0.12,
                    xanchor: 'center', x: 0.5,
                    font: {{ size: 10, color: '#9498ab' }}
                }},
                margin: {{ l: 65, r: 30, t: 20, b: 80 }},
                height: 520
            }}, {{ responsive: true }});
        }}

        // ══════════════════════════════════════════════
        // ══════════════════════════════════════════════
        // METRIC BADGE (Detail Panel)
        // ══════════════════════════════════════════════
        function generateMetricBadge(data) {{
            if (data.shape_similarity == null) return '';
            const shapeSim = data.shape_similarity;
            const contrastRatio = data.contrast_ratio;
            const quadrant = getQuadrant(shapeSim, contrastRatio);

            let contrastDesc = 'Same spread as era';
            if (contrastRatio > 1.1) contrastDesc = 'Spikier profile than era';
            else if (contrastRatio < 0.9) contrastDesc = 'Flatter profile than era';

            return `
                <div class="quadrant-tag ${{quadrant.css}}">
                    ${{quadrant.label}}
                </div>
                <div class="metric-badge-row">
                    <div class="metric-card shape">
                        <div class="metric-label">Shape Similarity</div>
                        <div class="metric-value">${{shapeSim.toFixed(4)}}</div>
                        <div class="metric-desc">Pattern correspondence with era</div>
                    </div>
                    <div class="metric-card contrast">
                        <div class="metric-label">Contrast Ratio</div>
                        <div class="metric-value">${{contrastRatio.toFixed(4)}}</div>
                        <div class="metric-desc">${{contrastDesc}}</div>
                    </div>
                </div>
            `;
        }}

        // ══════════════════════════════════════════════
        // ARTIST–ERA DEVIATION
        // ══════════════════════════════════════════════
        function generateArtistEraDeviation(artist, decade, data) {{
            const devs = data.artist_decade_deviations;
            if (!devs) return '';

            const featureNames = {{
                'valence': 'Valence',
                'energy': 'Energy',
                'danceability': 'Danceability',
                'acousticness': 'Acousticness',
                'liveness': 'Liveness'
            }};

            const items = Object.entries(devs)
                .filter(function(e) {{ return featureNames[e[0]]; }})
                .map(function(e) {{ return {{ feature:e[0], value:e[1], abs:Math.abs(e[1]) }}; }})
                .sort(function(a,b) {{ return b.abs - a.abs; }});

            if (items.length === 0) return '';

            let html = `
                <div class="artist-era-signature">
                    <div class="artist-era-title">${{artist}} vs Era Average (${{decade}})</div>
                    <div class="bar-chart-container">
            `;

            items.forEach(function(item) {{
                const percent = (item.value * 100).toFixed(0);
                const absPercent = Math.abs(item.value * 100);
                const width = Math.min((absPercent / 60) * 50, 50);
                const cssClass = item.value > 0 ? 'positive' : 'negative';
                const sign = item.value > 0 ? '+' : '';
                html += `
                    <div class="bar-row">
                        <div class="bar-label">${{featureNames[item.feature]}}</div>
                        <div class="bar-track">
                            <div class="bar-center-line"></div>
                            <div class="bar-fill ${{cssClass}}" style="width:${{width}}%;"></div>
                        </div>
                        <div class="bar-value ${{cssClass}}">${{sign}}${{percent}}%</div>
                    </div>
                `;
            }});

            html += '</div></div>';
            return html;
        }}

        // ══════════════════════════════════════════════
        // SONG SIGNATURE
        // ══════════════════════════════════════════════
        function generateSongSignature(songName, songFeatures, data) {{
            if (!songFeatures || !data.decade_audio) return '';

            const featureNames = {{
                'valence': 'Valence',
                'energy': 'Energy',
                'danceability': 'Danceability',
                'liveness': 'Liveness',
                'acousticness': 'Acousticness'
            }};

            const deviations = [];
            Object.keys(featureNames).forEach(function(key) {{
                if (songFeatures[key] !== undefined && data.decade_audio[key] !== undefined) {{
                    const dev = songFeatures[key] - data.decade_audio[key];
                    if (Math.abs(dev) >= 0.05) {{
                        deviations.push({{ feature:key, value:dev, abs:Math.abs(dev) }});
                    }}
                }}
            }});

            const songShape = data.song_shape_sims ? data.song_shape_sims[songName] : null;
            const songContrast = data.song_contrast_ratios ? data.song_contrast_ratios[songName] : null;
            let badges = '';
            if (songShape != null) {{
                badges += ' <span class="song-metric-badge" style="color:#047857;background:#ecfdf5;border:1px solid #a7f3d0;">Shape ' + songShape.toFixed(4) + '</span>';
            }}
            if (songContrast != null) {{
                badges += ' <span class="song-metric-badge" style="color:#6d28d9;background:#f5f3ff;border:1px solid #c4b5fd;">Contrast ' + songContrast.toFixed(2) + '</span>';
            }}

            deviations.sort(function(a,b){{ return b.abs - a.abs; }});

            let html = `
                <div class="song-signature">
                    <div class="song-signature-title">${{songName}} <span style="font-size:11px;font-weight:400;color:var(--text2);">— Deviations from ${{currentDecade}} Era Average</span> ${{badges}}</div>
            `;

            if (deviations.length > 0) {{
                html += '<div class="bar-chart-container">';
                deviations.forEach(function(item) {{
                    const percent = (item.value * 100).toFixed(0);
                    const absPercent = Math.abs(item.value * 100);
                    const width = Math.min((absPercent / 100) * 50, 50);
                    const cssClass = item.value > 0 ? 'positive' : 'negative';
                    const sign = item.value > 0 ? '+' : '';
                    html += `
                        <div class="bar-row">
                            <div class="bar-label">${{featureNames[item.feature]}}</div>
                            <div class="bar-track">
                                <div class="bar-center-line"></div>
                                <div class="bar-fill ${{cssClass}}" style="width:${{width}}%;"></div>
                            </div>
                            <div class="bar-value ${{cssClass}}">${{sign}}${{percent}}%</div>
                        </div>
                    `;
                }});
                html += '</div>';
            }} else {{
                html += '<div style="color:var(--text2);font-size:12px;text-align:center;padding:8px;">All features within +/-5% of era average</div>';
            }}

            html += '<div id="songRadarChart"></div></div>';
            return html;
        }}

        // ══════════════════════════════════════════════
        // CLICK HANDLER
        // ══════════════════════════════════════════════
        document.getElementById('mainChart').on('plotly_click', function(data) {{
            const point = data.points[0];
            if (!point.customdata) return;
            const artist = point.customdata[0];
            const decade = point.customdata[1];
            const key = artist + '||' + decade;
            if (!detailData[key]) return;
            updateDetailViews(artist, decade, detailData[key]);
        }});

        // ══════════════════════════════════════════════
        // DETAIL VIEW UPDATE
        // ══════════════════════════════════════════════
        function updateDetailViews(artist, decade, data) {{
            currentArtist = artist;
            currentDecade = decade;
            currentData = data;

            document.getElementById('initialMessage').style.display = 'none';
            document.getElementById('detailSection').style.display = 'block';
            document.getElementById('audioSection').style.display = 'block';

            document.getElementById('infoBox').innerHTML = `
                <p><strong>Artist:</strong> ${{artist}}</p>
                <p><strong>Decade:</strong> ${{decade}}</p>
                <p><strong>Total Songs:</strong> ${{data.total_songs}}</p>
                <p><strong>Total Weeks on Chart:</strong> ${{data.total_weeks}}</p>
            `;

            let tableHTML = `<table><thead><tr>
                <th>Song</th>
                <th style="text-align:center;">Avg Rank</th>
                <th style="text-align:center;">Peak</th>
                <th style="text-align:center;">Weeks</th>
            </tr></thead><tbody>`;

            data.songs.forEach(function(song, idx) {{
                const rowBg = idx % 2 === 0 ? '' : 'background-color:#f8f9fa;';
                const esc = song.song.replace(/'/g, "\\\\'").replace(/"/g, '&quot;');
                const peakColor = Math.round(song.peak_rank) === 1 ? 'var(--red)' : 'var(--text)';
                tableHTML += `
                    <tr style="${{rowBg}}" data-song-name="${{song.song}}" onclick="selectSong('${{esc}}')">
                        <td><strong>${{song.song}}</strong></td>
                        <td style="text-align:center;">${{song.avg_rank.toFixed(2)}}</td>
                        <td style="text-align:center;"><strong style="color:${{peakColor}}">${{Math.round(song.peak_rank)}}</strong></td>
                        <td style="text-align:center;">${{song.weeks}}</td>
                    </tr>
                `;
            }});
            tableHTML += '</tbody></table>';
            document.getElementById('songTable').innerHTML = tableHTML;

            document.getElementById('metricBadge').innerHTML = generateMetricBadge(data);
            document.getElementById('artistEraContainer').innerHTML = generateArtistEraDeviation(artist, decade, data);

            // Apply artist color to block, header, and title
            const artistColor = ARTIST_COLORS[artist] || 'var(--accent)';
            document.getElementById('artistEraBlock').style.borderColor = artistColor + '80';
            document.getElementById('audioHeader').style.borderLeftColor = artistColor;
            const eraTitle = document.querySelector('.artist-era-title');
            if (eraTitle) eraTitle.style.color = artistColor;
            document.getElementById('radarContainer').innerHTML = '<div id="eraRadarChart"></div>';
            document.getElementById('songSignatureContainer').innerHTML = '';
            updateRadarChart(null);

            document.getElementById('detailSection').scrollIntoView({{ behavior:'smooth', block:'nearest' }});
        }}

        // ══════════════════════════════════════════════
        // SONG SELECTION
        // ══════════════════════════════════════════════
        function selectSong(songName) {{
            const rows = document.querySelectorAll('#songTable tr[data-song-name]');
            rows.forEach(function(row) {{
                row.classList.toggle('selected', row.getAttribute('data-song-name') === songName);
            }});
            const songFeatures = currentData.song_features[songName];
            if (songFeatures) {{
                document.getElementById('radarContainer').innerHTML = '';
                document.getElementById('songSignatureContainer').innerHTML = generateSongSignature(songName, songFeatures, currentData);
                updateRadarChart(songName);
            }} else {{
                document.getElementById('songSignatureContainer').innerHTML = '';
                document.getElementById('radarContainer').innerHTML = '<div id="eraRadarChart"></div>';
                updateRadarChart(null);
            }}
        }}

        // ══════════════════════════════════════════════
        // RADAR CHART
        // ══════════════════════════════════════════════
        function updateRadarChart(selectedSong) {{
            const data = currentData;
            const artist = currentArtist;
            const decade = currentDecade;
            const targetId = selectedSong ? 'songRadarChart' : 'eraRadarChart';

            const featureLabels = {{
                'valence': 'Valence', 'energy': 'Energy',
                'danceability': 'Danceability', 'liveness': 'Liveness',
                'acousticness': 'Acousticness'
            }};

            const features=[], decadeValues=[], artistValues=[], songValues=[];
            const featureKeys = Object.keys(featureLabels);
            featureKeys.forEach(function(key) {{
                if (data.decade_audio && data.decade_audio[key] !== undefined) {{
                    features.push(featureLabels[key]);
                    decadeValues.push(data.decade_audio[key] || 0);
                    const aVal = (data.artist_decade_audio && data.artist_decade_audio[key] !== undefined)
                        ? data.artist_decade_audio[key]
                        : (data.artist_audio && data.artist_audio[key] !== undefined ? data.artist_audio[key] : 0);
                    artistValues.push(aVal);
                    if (selectedSong && data.song_features && data.song_features[selectedSong] && data.song_features[selectedSong][key] !== undefined) {{
                        songValues.push(data.song_features[selectedSong][key]);
                    }} else if (selectedSong) {{
                        songValues.push(0);
                    }}
                }}
            }});

            if (features.length === 0) {{
                document.getElementById(targetId).innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:380px;color:var(--text2);">No audio feature data</div>';
                return;
            }}

            features.push(features[0]);
            decadeValues.push(decadeValues[0]);
            artistValues.push(artistValues[0]);
            if (selectedSong && songValues.length > 0) songValues.push(songValues[0]);

            const radarData = [
                {{
                    type:'scatterpolar', r:decadeValues, theta:features,
                    fill:'toself', fillcolor:'rgba(102,126,234,0.12)',
                    line:{{ color:'rgba(102,126,234,0.7)', width:1.5, dash:'dot' }},
                    marker:{{ size:5, color:'rgba(102,126,234,0.8)' }},
                    name: decade + ' Average',
                    hovertemplate: '<b>%{{theta}}</b><br>' + decade + ' Avg: %{{r:.3f}}<extra></extra>'
                }},
                {{
                    type:'scatterpolar', r:artistValues, theta:features,
                    fill:'none',
                    line:{{ color:'#059669', width:2 }},
                    marker:{{ size:5, color:'#059669' }},
                    name: artist + ' (' + decade + ')',
                    hovertemplate: '<b>%{{theta}}</b><br>Artist: %{{r:.3f}}<extra></extra>'
                }}
            ];

            if (selectedSong && songValues.length > 0) {{
                radarData.push({{
                    type:'scatterpolar', r:songValues, theta:features,
                    fill:'none',
                    line:{{ color:'#ef553b', width:2 }},
                    marker:{{ size:5, color:'#ef553b' }},
                    name: selectedSong,
                    hovertemplate: '<b>%{{theta}}</b><br>' + selectedSong + ': %{{r:.3f}}<extra></extra>'
                }});
            }}

            Plotly.newPlot(targetId, radarData, {{
                polar: {{
                    radialaxis: {{
                        visible:true, range:[0,1],
                        showticklabels:true,
                        tickfont:{{ size:10, color:'#888' }},
                        gridcolor:'rgba(0,0,0,0.08)'
                    }},
                    angularaxis: {{
                        tickfont:{{ size:11, color:'#555' }},
                        linecolor:'rgba(0,0,0,0.1)'
                    }},
                    bgcolor:'rgba(0,0,0,0)'
                }},
                showlegend:true,
                legend: {{
                    orientation:'h', yanchor:'bottom', y:-0.25,
                    xanchor:'center', x:0.5,
                    font:{{ size:10, color:'#888' }}
                }},
                margin:{{ l:55, r:55, t:30, b:70 }},
                paper_bgcolor:'rgba(0,0,0,0)',
                plot_bgcolor:'rgba(0,0,0,0)'
            }}, {{ responsive:true }});
        }}
    </script>
</body>
</html>
"""
    return html