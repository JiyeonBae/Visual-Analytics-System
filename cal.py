"""
html_template.py
HTML 템플릿과 JavaScript 코드를 생성하는 모듈 (반응형)

Layout:
  Hero:    Quadrant Trajectory Map (Shape Sim × Contrast Ratio + temporal arrows)
  Nav:     Bubble Chart (artist×decade navigator)
  Detail:  Badge(Quadrant + Dual Metric) + Artist–Era Deviation + Radar/Song Signature

Metric Design:
  Axis 1: Profile Shape Similarity (Centered Cosine, LOO) — r ≈ 0.00 with Axis 2
  Axis 2: Profile Contrast Ratio (σ_artist / σ_era, LOO)
  → Mathematically independent; all 4 quadrants populated.
"""


def generate_html(plotly_chart_html, detail_data_json, trajectory_json):
    """
    완전한 HTML 문서 생성

    Args:
        plotly_chart_html: Plotly가 생성한 차트 HTML
        detail_data_json: Detail View 데이터의 JSON
        trajectory_json: 아티스트별 shape_similarity/contrast_ratio trajectory JSON

    Returns:
        html_string: 완성된 HTML 문자열
    """
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Hot 100 Interactive Visualization</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f8f9fa;
        }}
        .main-container {{
            width: 100%;
            min-height: 100vh;
            padding: 20px;
        }}
        .chart-container {{
            width: 100%;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 20px;
            margin-bottom: 15px;
            overflow: hidden;
        }}
        #mainChart {{
            width: 100% !important;
            min-height: 45vh !important;
            height: auto !important;
        }}
        #mainChart .js-plotly-plot {{
            width: 100% !important;
            min-height: 45vh !important;
            height: auto !important;
        }}

        /* ── Hero: Quadrant Trajectory Map ── */
        .hero-box {{
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 20px;
            margin-bottom: 15px;
        }}
        #quadrantTrajectoryMap {{
            width: 100%;
            height: 600px;
        }}

        /* ── Secondary: Bubble Navigation ── */
        .nav-chart-container {{
            width: 100%;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 15px;
            margin-bottom: 15px;
            overflow: hidden;
        }}
        .nav-chart-label {{
            font-size: 12px;
            color: #888;
            text-align: center;
            margin-bottom: 5px;
            font-weight: 500;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }}

        /* ── Detail Grid ── */
        .detail-container {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            width: 100%;
        }}
        .detail-box {{
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 25px;
        }}
        .detail-header {{
            font-size: 18px;
            font-weight: bold;
            color: #333;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
        }}
        .detail-header::before {{
            content: '';
            display: inline-block;
            width: 4px;
            height: 20px;
            background-color: #40e0d0;
            margin-right: 10px;
            border-radius: 2px;
        }}
        .info-box {{
            background: white;
            border: 2px solid #667eea;
            color: #333;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.08);
        }}
        .info-box p {{
            margin: 8px 0;
            font-size: 14px;
        }}
        .info-box strong {{
            font-weight: 600;
            color: #667eea;
        }}

        /* ── Metric Badge ── */
        .metric-badge-row {{
            display: flex;
            gap: 12px;
            margin-bottom: 15px;
        }}
        .metric-card {{
            flex: 1;
            padding: 14px 16px;
            border-radius: 8px;
            border: 2px solid;
            text-align: center;
            box-shadow: 0 2px 6px rgba(0,0,0,0.06);
        }}
        .metric-card.shape {{
            border-color: #10b981;
            background: linear-gradient(135deg, #ecfdf5 0%, #f0fdf4 100%);
        }}
        .metric-card.contrast {{
            border-color: #8b5cf6;
            background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);
        }}
        .metric-card .metric-label {{
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
        }}
        .metric-card.shape .metric-label {{
            color: #059669;
        }}
        .metric-card.contrast .metric-label {{
            color: #7c3aed;
        }}
        .metric-card .metric-value {{
            font-size: 26px;
            font-weight: 700;
            line-height: 1.1;
        }}
        .metric-card.shape .metric-value {{
            color: #047857;
        }}
        .metric-card.contrast .metric-value {{
            color: #6d28d9;
        }}
        .metric-card .metric-desc {{
            font-size: 10px;
            color: #888;
            margin-top: 3px;
        }}
        .quadrant-tag {{
            display: inline-block;
            padding: 5px 14px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 15px;
            letter-spacing: 0.3px;
        }}
        .quadrant-tag.amplified-conformist {{
            background: #ecfdf5;
            color: #047857;
            border: 1px solid #a7f3d0;
        }}
        .quadrant-tag.smoothed-conformist {{
            background: #eff6ff;
            color: #1d4ed8;
            border: 1px solid #bfdbfe;
        }}
        .quadrant-tag.polarized-maverick {{
            background: #fef2f2;
            color: #b91c1c;
            border: 1px solid #fecaca;
        }}
        .quadrant-tag.muted-maverick {{
            background: #fefce8;
            color: #a16207;
            border: 1px solid #fde68a;
        }}

        /* ── Artist–Era Deviation ── */
        .artist-era-signature {{
            background: white;
            border: 2px solid #8b5cf6;
            color: #333;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            box-shadow: 0 2px 6px rgba(139, 92, 246, 0.12);
        }}
        .artist-era-title {{
            font-weight: 600;
            font-size: 14px;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            color: #8b5cf6;
        }}
        .artist-era-title::before {{
            content: '🔍';
            margin-right: 6px;
            font-size: 16px;
        }}
        .artist-era-subtitle {{
            font-weight: 400;
            color: #999;
            margin-left: 8px;
        }}

        /* ── Diverging Bar (shared) ── */
        .bar-chart-container {{
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}
        .bar-row {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .bar-label {{
            width: 120px;
            font-size: 12px;
            font-weight: 600;
            text-align: right;
            color: #333;
        }}
        .bar-track {{
            flex: 1;
            height: 24px;
            background: #f0f0f0;
            border-radius: 4px;
            position: relative;
            overflow: visible;
        }}
        .bar-fill {{
            position: absolute;
            height: 100%;
            transition: width 0.3s ease;
            border-radius: 4px;
        }}
        .bar-fill.neg-purple {{
            right: 50%;
            background: #8b5cf6;
        }}
        .bar-fill.pos-purple {{
            left: 50%;
            background: #f59e0b;
        }}
        .bar-fill.negative {{
            right: 50%;
            background: #3b82f6;
        }}
        .bar-fill.positive {{
            left: 50%;
            background: #ef553b;
        }}
        .bar-value {{
            width: 50px;
            font-size: 12px;
            font-weight: 700;
            text-align: center;
        }}
        .bar-value.neg-purple {{
            color: #8b5cf6;
        }}
        .bar-value.pos-purple {{
            color: #f59e0b;
        }}
        .bar-value.negative {{
            color: #3b82f6;
        }}
        .bar-value.positive {{
            color: #ef553b;
        }}
        .bar-center-line {{
            position: absolute;
            left: 50%;
            top: -2px;
            bottom: -2px;
            width: 2px;
            background: #333;
            z-index: 2;
            transform: translateX(-50%);
        }}

        /* ── Song Signature ── */
        .song-signature {{
            background: white;
            border: 2px solid #ef553b;
            color: #333;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            box-shadow: 0 2px 6px rgba(239, 85, 59, 0.15);
        }}
        .song-signature-title {{
            font-weight: 600;
            font-size: 14px;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            color: #ef553b;
        }}
        .song-signature-title::before {{
            content: '🎵';
            margin-right: 6px;
            font-size: 16px;
        }}
        .song-signature-subtitle {{
            font-weight: 400;
            color: #999;
            margin-left: 8px;
        }}
        .song-signature-artist {{
            font-weight: 700;
        }}
        .song-metric-badge {{
            display: inline-block;
            font-size: 10px;
            font-weight: 600;
            padding: 2px 8px;
            border-radius: 10px;
            margin-left: 6px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            font-weight: normal;
        }}
        th {{
            background: linear-gradient(135deg, #40e0d0 0%, #48d1cc 100%);
            color: white;
            padding: 12px 10px;
            text-align: left;
            font-weight: 600;
            position: sticky;
            top: 0;
        }}
        td {{
            padding: 10px;
            border-bottom: 1px solid #e9ecef;
        }}
        tr {{
            cursor: pointer;
            transition: background-color 0.2s;
        }}
        tr:hover {{
            background-color: #f8f9fa;
        }}
        tr.selected {{
            background-color: #fff3cd !important;
            border-left: 3px solid #ef553b;
        }}
        .table-container {{
            max-height: 500px;
            overflow-y: auto;
            border: 1px solid #dee2e6;
            border-radius: 8px;
        }}
        .initial-message {{
            grid-column: 1 / -1;
            text-align: center;
            color: #999;
            padding: 60px 20px;
            font-size: 18px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .initial-message::before {{
            content: '👇';
            display: block;
            font-size: 36px;
            margin-bottom: 10px;
        }}
        .initial-message-permanent {{
            width: 100%;
            color: white;
            padding: 15px 20px;
            font-size: 16px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            margin-bottom: 20px;
            font-weight: 500;
            letter-spacing: 0.5px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }}
        .initial-message-permanent::before {{
            content: '☝️';
            font-size: 24px;
            animation: bounce 2s infinite;
        }}
        @keyframes bounce {{
            0%, 20%, 50%, 80%, 100% {{
                transform: translateY(0);
            }}
            40% {{
                transform: translateY(-10px);
            }}
            60% {{
                transform: translateY(-5px);
            }}
        }}
        #eraRadarChart, #songRadarChart {{
            min-height: 400px;
        }}
        .song-signature #songRadarChart {{
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid rgba(239, 85, 59, 0.2);
        }}
        @media (max-width: 1200px) {{
            .detail-container {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="main-container">
        <!-- Hero: Quadrant Trajectory Map -->
        <div class="hero-box">
            <div id="quadrantTrajectoryMap"></div>
        </div>

        <!-- 안내 메시지 -->
        <div class="initial-message-permanent" id="permanentMessage">
            Click any point above to explore that artist×decade — or use the navigation chart below
        </div>

        <!-- Secondary: Bubble Navigation Chart -->
        <div class="nav-chart-container">
            <div class="nav-chart-label">📊 Artist × Decade Navigator — click a bubble to select</div>
            {plotly_chart_html}
        </div>

        <div class="detail-container">
            <!-- Left Panel: Song Performance -->
            <div class="detail-box" id="detailSection" style="display:none;">
                <div class="detail-header">📊 Song Performance Metrics</div>
                <div id="infoBox" class="info-box"></div>
                <div class="table-container">
                    <div id="songTable"></div>
                </div>
            </div>

            <!-- Right Panel: Audio Features -->
            <div class="detail-box" id="audioSection" style="display:none;">
                <div class="detail-header">🎵 Audio Features Profile</div>
                <div id="metricBadge"></div>
                <div id="artistEraContainer"></div>
                <div id="radarContainer"><div id="eraRadarChart"></div></div>
                <div id="songSignatureContainer"></div>
            </div>

            <div class="initial-message" id="initialMessage">
                Click any point on the trajectory map or any bubble in the navigator to see details here
            </div>
        </div>
    </div>

    <script>
        // ══════════════════════════════════════════════
        // 데이터 임베드
        // ══════════════════════════════════════════════
        const detailData = {detail_data_json};
        const trajectoryData = {trajectory_json};

        // 전역 변수
        let chartInitialized = false;
        let currentArtist = '';
        let currentDecade = '';
        let currentData = null;

        // ══════════════════════════════════════════════
        // Shape Similarity & Contrast Ratio 임계값 (median 기반 quadrant)
        // ══════════════════════════════════════════════
        const allShapeSims = [];
        const allContrastRatios = [];
        Object.values(detailData).forEach(function(d) {{
            if (d.shape_similarity !== null && d.shape_similarity !== undefined) allShapeSims.push(d.shape_similarity);
            if (d.contrast_ratio !== null && d.contrast_ratio !== undefined) allContrastRatios.push(d.contrast_ratio);
        }});
        allShapeSims.sort(function(a, b) {{ return a - b; }});
        allContrastRatios.sort(function(a, b) {{ return a - b; }});
        const medianShapeSim = allShapeSims.length > 0 ? allShapeSims[Math.floor(allShapeSims.length / 2)] : 0.97;
        const medianContrast = allContrastRatios.length > 0 ? allContrastRatios[Math.floor(allContrastRatios.length / 2)] : 1.0;

        function getQuadrant(shapeSim, contrastRatio) {{
            const highShape = shapeSim >= medianShapeSim;
            const highContrast = contrastRatio >= medianContrast;
            if (highShape && highContrast) return {{ label: 'Amplified Conformist', css: 'amplified-conformist', icon: '🔊' }};
            if (highShape && !highContrast) return {{ label: 'Smoothed Conformist', css: 'smoothed-conformist', icon: '🎹' }};
            if (!highShape && highContrast) return {{ label: 'Polarized Maverick', css: 'polarized-maverick', icon: '🎸' }};
            return {{ label: 'Muted Maverick', css: 'muted-maverick', icon: '🌊' }};
        }}

        // ══════════════════════════════════════════════
        // 차트 크기 조정
        // ══════════════════════════════════════════════
        function resizeMainChart() {{
            if (!chartInitialized) return;
            const mainChart = document.getElementById('mainChart');
            if (mainChart && mainChart.data) {{
                Plotly.Plots.resize(mainChart);
            }}
        }}

        window.addEventListener('load', function() {{
            setTimeout(function() {{
                chartInitialized = true;
            }}, 500);
            renderQuadrantTrajectory();
        }});

        let resizeTimeout;
        window.addEventListener('resize', function() {{
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(function() {{
                resizeMainChart();

                ['quadrantTrajectoryMap', 'mainChart', 'eraRadarChart', 'songRadarChart'].forEach(function(id) {{
                    const el = document.getElementById(id);
                    if (el && el.data) {{
                        Plotly.Plots.resize(id);
                    }}
                }});
            }}, 250);
        }});

        // ══════════════════════════════════════════════
        // SHARED: colors & artist list
        // ══════════════════════════════════════════════
        const COLORS = [
            '#e6194b', '#3cb44b', '#4363d8', '#f58231', '#911eb4',
            '#42d4f4', '#f032e6', '#bfef45', '#fabed4', '#469990'
        ];
        const DECADE_ORDER = ['1960s', '1970s', '1980s', '1990s', '2000s', '2010s'];

        // ══════════════════════════════════════════════
        // QUADRANT TRAJECTORY MAP (novel encoding)
        // X: Shape Similarity, Y: Contrast Ratio
        // Arrows: decade-to-decade temporal trajectory
        // ══════════════════════════════════════════════
        function renderQuadrantTrajectory() {{
            const artists = Object.keys(trajectoryData);
            const traces = [];
            const annotations = [];

            // ── 1. Compute axis ranges ──
            let xMin = 1, xMax = 0, yMin = Infinity, yMax = 0;
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
            const xLo = xMin - xPad, xHi = xMax + xPad;
            const yLo = yMin - yPad, yHi = yMax + yPad;

            // ── 2. Quadrant background shapes ──
            const quadShapes = [
                // Amplified Conformist (top-right)
                {{ type: 'rect', xref: 'x', yref: 'y', x0: medianShapeSim, x1: xHi + 0.1, y0: medianContrast, y1: yHi + 0.5,
                   fillcolor: 'rgba(16,185,129,0.07)', line: {{ width: 0 }}, layer: 'below' }},
                // Smoothed Conformist (bottom-right)
                {{ type: 'rect', xref: 'x', yref: 'y', x0: medianShapeSim, x1: xHi + 0.1, y0: yLo - 0.5, y1: medianContrast,
                   fillcolor: 'rgba(59,130,246,0.07)', line: {{ width: 0 }}, layer: 'below' }},
                // Polarized Maverick (top-left)
                {{ type: 'rect', xref: 'x', yref: 'y', x0: xLo - 0.1, x1: medianShapeSim, y0: medianContrast, y1: yHi + 0.5,
                   fillcolor: 'rgba(239,68,68,0.07)', line: {{ width: 0 }}, layer: 'below' }},
                // Muted Maverick (bottom-left)
                {{ type: 'rect', xref: 'x', yref: 'y', x0: xLo - 0.1, x1: medianShapeSim, y0: yLo - 0.5, y1: medianContrast,
                   fillcolor: 'rgba(245,158,11,0.07)', line: {{ width: 0 }}, layer: 'below' }},
                // Median vertical line
                {{ type: 'line', xref: 'x', yref: 'y', x0: medianShapeSim, x1: medianShapeSim, y0: yLo - 0.5, y1: yHi + 0.5,
                   line: {{ color: 'rgba(120,120,120,0.4)', width: 1.5, dash: 'dot' }}, layer: 'below' }},
                // Median horizontal line
                {{ type: 'line', xref: 'x', yref: 'y', x0: xLo - 0.1, x1: xHi + 0.1, y0: medianContrast, y1: medianContrast,
                   line: {{ color: 'rgba(120,120,120,0.4)', width: 1.5, dash: 'dot' }}, layer: 'below' }},
            ];

            // ── 3. Quadrant labels ──
            const qLabelStyle = {{ font: {{ size: 11, color: 'rgba(100,100,100,0.6)' }}, showarrow: false, xref: 'x', yref: 'y' }};
            const qLabels = [
                Object.assign({{ x: (medianShapeSim + xHi) / 2, y: yHi - yPad * 0.3, text: '🔊 Amplified Conformist' }}, qLabelStyle),
                Object.assign({{ x: (medianShapeSim + xHi) / 2, y: yLo + yPad * 0.3, text: '🎹 Smoothed Conformist' }}, qLabelStyle),
                Object.assign({{ x: (xLo + medianShapeSim) / 2, y: yHi - yPad * 0.3, text: '🎸 Polarized Maverick' }}, qLabelStyle),
                Object.assign({{ x: (xLo + medianShapeSim) / 2, y: yLo + yPad * 0.3, text: '🌊 Muted Maverick' }}, qLabelStyle),
            ];

            // ── 4. Data points + trajectory arrows ──
            artists.forEach(function(artist, idx) {{
                const d = trajectoryData[artist];
                if (d.length === 0) return;
                const color = COLORS[idx % COLORS.length];

                // Scatter points
                traces.push({{
                    x: d.map(function(p) {{ return p.shape_similarity; }}),
                    y: d.map(function(p) {{ return p.contrast_ratio; }}),
                    mode: 'markers',
                    name: artist,
                    marker: {{
                        size: 12,
                        color: color,
                        opacity: 0.9,
                        line: {{ width: 2, color: 'white' }}
                    }},
                    text: d.map(function(p) {{ return p.decade; }}),
                    hovertemplate: '<b>' + artist + '</b><br>%{{text}}<br>Shape Sim: %{{x:.4f}}<br>Contrast: %{{y:.4f}}<extra></extra>'
                }});

                // Decade labels (text trace for clean rendering)
                traces.push({{
                    x: d.map(function(p) {{ return p.shape_similarity; }}),
                    y: d.map(function(p) {{ return p.contrast_ratio; }}),
                    mode: 'text',
                    text: d.map(function(p) {{ return p.decade.replace('s',''); }}),
                    textposition: 'top center',
                    textfont: {{ size: 9, color: color, family: 'monospace' }},
                    showlegend: false,
                    hoverinfo: 'skip'
                }});

                // Trajectory arrows between consecutive decades
                for (let i = 0; i < d.length - 1; i++) {{
                    const x0 = d[i].shape_similarity;
                    const y0 = d[i].contrast_ratio;
                    const x1 = d[i + 1].shape_similarity;
                    const y1 = d[i + 1].contrast_ratio;

                    // Shorten arrow: start 20% in, end 80% in (avoid overlapping markers)
                    const dx = x1 - x0, dy = y1 - y0;
                    const sx = x0 + dx * 0.22, sy = y0 + dy * 0.22;
                    const ex = x0 + dx * 0.78, ey = y0 + dy * 0.78;

                    annotations.push({{
                        x: ex, y: ey,
                        ax: sx, ay: sy,
                        xref: 'x', yref: 'y',
                        axref: 'x', ayref: 'y',
                        showarrow: true,
                        arrowhead: 3,
                        arrowsize: 1.3,
                        arrowwidth: 2.2,
                        arrowcolor: color,
                        opacity: 0.6
                    }});
                }}
            }});

            // ── 5. Plot ──
            Plotly.newPlot('quadrantTrajectoryMap', traces, {{
                title: {{
                    text: 'Artist Profile Trajectory Map<br><sup>How each artist\'s sonic profile shifted across decades — arrows show temporal direction</sup>',
                    font: {{ size: 14 }}
                }},
                xaxis: {{
                    title: 'Profile Shape Similarity (Centered Cosine)',
                    range: [xLo, xHi],
                    tickformat: '.2f',
                    gridcolor: 'rgba(220,220,220,0.4)',
                    zeroline: false
                }},
                yaxis: {{
                    title: 'Profile Contrast Ratio (σ_artist / σ_era)',
                    range: [yLo, yHi],
                    tickformat: '.2f',
                    gridcolor: 'rgba(220,220,220,0.4)',
                    zeroline: false
                }},
                shapes: quadShapes,
                annotations: qLabels.concat(annotations),
                template: 'plotly_white',
                height: 520,
                margin: {{ l: 65, r: 30, t: 60, b: 55 }},
                legend: {{
                    orientation: 'h',
                    yanchor: 'top',
                    y: -0.12,
                    xanchor: 'center',
                    x: 0.5,
                    font: {{ size: 10 }}
                }},
                plot_bgcolor: 'rgba(252,252,252,1)'
            }}, {{ responsive: true }});
        }}

        // ══════════════════════════════════════════════
        // METRIC BADGE 생성 (Quadrant + Dual Metrics)
        // ══════════════════════════════════════════════
        function generateMetricBadge(data) {{
            if (data.shape_similarity === null || data.shape_similarity === undefined) {{
                return '';
            }}

            const shapeSim = data.shape_similarity;
            const contrastRatio = data.contrast_ratio;
            const quadrant = getQuadrant(shapeSim, contrastRatio);

            // Contrast interpretation
            let contrastDesc = 'Same spread as era';
            if (contrastRatio > 1.1) contrastDesc = 'Spikier profile than era';
            else if (contrastRatio < 0.9) contrastDesc = 'Flatter profile than era';

            return `
                <div class="quadrant-tag ${{quadrant.css}}">
                    ${{quadrant.icon}} ${{quadrant.label}}
                </div>
                <div class="metric-badge-row">
                    <div class="metric-card shape">
                        <div class="metric-label">Shape Similarity</div>
                        <div class="metric-value">${{shapeSim.toFixed(4)}}</div>
                        <div class="metric-desc">Pattern correspondence ↔ Radar overlap</div>
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
        // ARTIST–ERA DEVIATION BAR CHART
        // ══════════════════════════════════════════════
        function generateArtistEraDeviation(artist, decade, data) {{
            const devs = data.artist_decade_deviations;
            if (!devs) return '';

            const featureNames = {{
                'valence': '😊 Valence',
                'energy': '⚡ Energy',
                'danceability': '💃 Danceability',
                'acousticness': '🎸 Acousticness',
                'liveness': '🎤 Liveness'
            }};

            const items = Object.entries(devs)
                .filter(function(entry) {{ return featureNames[entry[0]]; }})
                .map(function(entry) {{ return {{ feature: entry[0], value: entry[1], abs: Math.abs(entry[1]) }}; }})
                .sort(function(a, b) {{ return b.abs - a.abs; }});

            if (items.length === 0) return '';

            let html = `
                <div class="artist-era-signature">
                    <div class="artist-era-title">${{artist}} vs ${{decade}} Average
                        <span class="artist-era-subtitle">— Per-feature deviations</span>
                    </div>
                    <div class="bar-chart-container">
            `;

            items.forEach(function(item) {{
                const percent = (item.value * 100).toFixed(0);
                const absPercent = Math.abs(item.value * 100);
                const width = Math.min((absPercent / 60) * 50, 50);
                const cssClass = item.value > 0 ? 'pos-purple' : 'neg-purple';
                const sign = item.value > 0 ? '+' : '';

                html += `
                    <div class="bar-row">
                        <div class="bar-label">${{featureNames[item.feature]}}</div>
                        <div class="bar-track">
                            <div class="bar-center-line"></div>
                            <div class="bar-fill ${{cssClass}}" style="width: ${{width}}%;"></div>
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
            if (!songFeatures || !data.decade_audio) {{
                return '';
            }}

            const featureNames = {{
                'valence': '😊 Valence',
                'energy': '⚡ Energy',
                'danceability': '💃 Danceability',
                'liveness': '🎤 Liveness',
                'acousticness': '🎸 Acousticness'
            }};

            const deviations = [];
            Object.keys(featureNames).forEach(function(key) {{
                if (songFeatures[key] !== undefined && data.decade_audio[key] !== undefined) {{
                    const deviation = songFeatures[key] - data.decade_audio[key];
                    if (Math.abs(deviation) >= 0.05) {{
                        deviations.push({{ feature: key, value: deviation, abs: Math.abs(deviation) }});
                    }}
                }}
            }});

            // Song-level metric badges
            const songShape = data.song_shape_sims ? data.song_shape_sims[songName] : null;
            const songContrast = data.song_contrast_ratios ? data.song_contrast_ratios[songName] : null;
            let badges = '';
            if (songShape !== null && songShape !== undefined) {{
                badges += ' <span class="song-metric-badge" style="color:#047857;background:#ecfdf5;border:1px solid #a7f3d0;">Shape: ' + songShape.toFixed(4) + '</span>';
            }}
            if (songContrast !== null && songContrast !== undefined) {{
                badges += ' <span class="song-metric-badge" style="color:#6d28d9;background:#f5f3ff;border:1px solid #c4b5fd;">Contrast: ' + songContrast.toFixed(2) + '</span>';
            }}

            let noDevMessage = '';
            if (deviations.length === 0) {{
                noDevMessage = '<div style="color:#999; font-size:13px; text-align:center; padding:10px;">All features within ±5% of era average</div>';
            }}

            deviations.sort(function(a, b) {{ return b.abs - a.abs; }});

            let html = `
                <div class="song-signature">
                    <div class="song-signature-title">${{songName}}${{badges}}
                        <span class="song-signature-subtitle">by <span class="song-signature-artist">${{currentArtist}}</span> — Deviations from ${{currentDecade}} Average</span>
                    </div>
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
                                <div class="bar-fill ${{cssClass}}" style="width: ${{width}}%;"></div>
                            </div>
                            <div class="bar-value ${{cssClass}}">${{sign}}${{percent}}%</div>
                        </div>
                    `;
                }});
                html += '</div>';
            }} else {{
                html += noDevMessage;
            }}

            html += `
                    <div id="songRadarChart"></div>
                </div>
            `;
            return html;
        }}

        // ══════════════════════════════════════════════
        // QUADRANT MAP: Highlight selected point
        // ══════════════════════════════════════════════
        let highlightTraceIdx = -1;

        function highlightQuadrantPoint(artist, decade) {{
            const d = trajectoryData[artist];
            if (!d) return;
            const pt = d.find(function(p) {{ return p.decade === decade; }});
            if (!pt) return;

            const highlightTrace = {{
                x: [pt.shape_similarity],
                y: [pt.contrast_ratio],
                mode: 'markers',
                marker: {{
                    size: 22,
                    color: 'rgba(0,0,0,0)',
                    line: {{ width: 3, color: '#ef553b' }}
                }},
                showlegend: false,
                hoverinfo: 'skip'
            }};

            const mapDiv = document.getElementById('quadrantTrajectoryMap');
            if (highlightTraceIdx >= 0 && mapDiv.data && highlightTraceIdx < mapDiv.data.length) {{
                Plotly.deleteTraces('quadrantTrajectoryMap', highlightTraceIdx);
            }}
            Plotly.addTraces('quadrantTrajectoryMap', highlightTrace);
            highlightTraceIdx = mapDiv.data.length - 1;
        }}

        // ══════════════════════════════════════════════
        // 클릭 이벤트: Quadrant Trajectory Map (primary)
        // ══════════════════════════════════════════════
        document.getElementById('quadrantTrajectoryMap').on('plotly_click', function(data) {{
            const point = data.points[0];
            // Only respond to marker traces (every other trace is text labels)
            if (!point || point.curveNumber % 2 !== 0) return;

            const artistIdx = Math.floor(point.curveNumber / 2);
            const artists = Object.keys(trajectoryData);
            if (artistIdx >= artists.length) return;

            const artist = artists[artistIdx];
            const ptIdx = point.pointIndex;
            const decade = trajectoryData[artist][ptIdx].decade;
            const key = artist + '||' + decade;

            if (!detailData[key]) return;

            // Highlight selected point on quadrant map
            highlightQuadrantPoint(artist, decade);
            updateDetailViews(artist, decade, detailData[key]);
        }});

        // ══════════════════════════════════════════════
        // 클릭 이벤트: Bubble Navigator (secondary)
        // ══════════════════════════════════════════════
        document.getElementById('mainChart').on('plotly_click', function(data) {{
            const point = data.points[0];
            if (!point.customdata) return;

            const artist = point.customdata[0];
            const decade = point.customdata[1];
            const key = artist + '||' + decade;

            if (!detailData[key]) {{
                alert('No detail data available for this selection');
                return;
            }}

            highlightQuadrantPoint(artist, decade);
            updateDetailViews(artist, decade, detailData[key]);
        }});

        // ══════════════════════════════════════════════
        // DETAIL VIEW 업데이트
        // ══════════════════════════════════════════════
        function updateDetailViews(artist, decade, data) {{
            currentArtist = artist;
            currentDecade = decade;
            currentData = data;

            document.getElementById('initialMessage').style.display = 'none';
            document.getElementById('detailSection').style.display = 'block';
            document.getElementById('audioSection').style.display = 'block';

            // Info Box
            document.getElementById('infoBox').innerHTML = `
                <p><strong>🎤 Artist:</strong> ${{artist}}</p>
                <p><strong>📅 Decade:</strong> ${{decade}}</p>
                <p><strong>🎵 Total Songs:</strong> ${{data.total_songs}}</p>
                <p><strong>📊 Total Weeks on Chart:</strong> ${{data.total_weeks}}</p>
            `;

            // Song Table
            let tableHTML = `
                <table>
                    <thead>
                        <tr>
                            <th>Song</th>
                            <th style="text-align:center;">Average Rank</th>
                            <th style="text-align:center;">Peak Rank</th>
                            <th style="text-align:center;">Weeks on Chart</th>
                        </tr>
                    </thead>
                    <tbody>
            `;

            data.songs.forEach(function(song, idx) {{
                const rowBg = idx % 2 === 0 ? '' : 'background-color: #f8f9fa;';
                const escapedSongName = song.song.replace(/'/g, "\\\\'").replace(/"/g, '&quot;');
                const peakRank = Math.round(song.peak_rank);
                const peakColor = peakRank === 1 ? '#ef553b' : '#333';

                tableHTML += `
                    <tr style="${{rowBg}}" data-song-name="${{song.song}}" onclick="selectSong('${{escapedSongName}}')">
                        <td><strong>${{song.song}}</strong></td>
                        <td style="text-align:center;">${{song.avg_rank.toFixed(2)}}</td>
                        <td style="text-align:center;"><strong style="color:${{peakColor}}">${{peakRank}}</strong></td>
                        <td style="text-align:center;">${{song.weeks}}</td>
                    </tr>
                `;
            }});

            tableHTML += '</tbody></table>';
            document.getElementById('songTable').innerHTML = tableHTML;

            // ── Right Panel ──
            // 1) Metric Badge (Quadrant + Shape Sim + Contrast Ratio)
            document.getElementById('metricBadge').innerHTML = generateMetricBadge(data);

            // 2) Artist–Era Deviation
            document.getElementById('artistEraContainer').innerHTML = generateArtistEraDeviation(artist, decade, data);

            // 3) Radar Chart (기본 상태)
            document.getElementById('radarContainer').innerHTML = '<div id="eraRadarChart"></div>';
            document.getElementById('songSignatureContainer').innerHTML = '';
            updateRadarChart(null);

            // 부드러운 스크롤
            document.getElementById('detailSection').scrollIntoView({{
                behavior: 'smooth',
                block: 'nearest'
            }});
        }}

        // ══════════════════════════════════════════════
        // SONG SELECTION
        // ══════════════════════════════════════════════
        function selectSong(songName) {{
            // 테이블 행 선택 표시
            const rows = document.querySelectorAll('#songTable tr[data-song-name]');
            rows.forEach(function(row) {{
                if (row.getAttribute('data-song-name') === songName) {{
                    row.classList.add('selected');
                }} else {{
                    row.classList.remove('selected');
                }}
            }});

            const songFeatures = currentData.song_features[songName];
            if (songFeatures) {{
                // Radar를 Song Signature 안으로 이동
                document.getElementById('radarContainer').innerHTML = '';
                document.getElementById('songSignatureContainer').innerHTML = generateSongSignature(songName, songFeatures, currentData);
                updateRadarChart(songName);
            }} else {{
                // 곡 선택 해제 시 Radar 원위치
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
                'valence': 'Valence<br>(Positivity)',
                'energy': 'Energy',
                'danceability': 'Danceability',
                'liveness': 'Liveness',
                'acousticness': 'Acousticness'
            }};

            const features = [];
            const decadeValues = [];
            const artistValues = [];
            const songValues = [];

            const featureKeys = Object.keys(featureLabels);
            featureKeys.forEach(function(key) {{
                if (data.decade_audio && data.decade_audio[key] !== undefined) {{
                    features.push(featureLabels[key]);
                    decadeValues.push(data.decade_audio[key] || 0);

                    // 해당 decade 내 아티스트 평균
                    const artistVal = (data.artist_decade_audio && data.artist_decade_audio[key] !== undefined)
                        ? data.artist_decade_audio[key]
                        : (data.artist_audio && data.artist_audio[key] !== undefined ? data.artist_audio[key] : 0);
                    artistValues.push(artistVal);

                    if (selectedSong && data.song_features && data.song_features[selectedSong] && data.song_features[selectedSong][key] !== undefined) {{
                        songValues.push(data.song_features[selectedSong][key]);
                    }} else if (selectedSong) {{
                        songValues.push(0);
                    }}
                }}
            }});

            if (features.length === 0) {{
                document.getElementById(targetId).innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:400px;color:#999;">No audio feature data available</div>';
                return;
            }}

            // 순환선
            features.push(features[0]);
            decadeValues.push(decadeValues[0]);
            artistValues.push(artistValues[0]);
            if (selectedSong && songValues.length > 0) {{
                songValues.push(songValues[0]);
            }}

            const radarData = [
                {{
                    type: 'scatterpolar',
                    r: decadeValues,
                    theta: features,
                    fill: 'toself',
                    fillcolor: 'rgba(102, 126, 234, 0.15)',
                    line: {{ color: 'rgb(102, 126, 234)', width: 2, dash: 'dot' }},
                    marker: {{ size: 6, color: 'rgb(102, 126, 234)' }},
                    name: decade + ' Average',
                    hovertemplate: '<b>%{{theta}}</b><br>' + decade + ' Avg: %{{r:.3f}}<extra></extra>'
                }},
                {{
                    type: 'scatterpolar',
                    r: artistValues,
                    theta: features,
                    fill: 'none',
                    line: {{ color: 'rgb(46, 204, 113)', width: 2 }},
                    marker: {{ size: 6, color: 'rgb(46, 204, 113)' }},
                    name: artist + ' (' + decade + ')',
                    hovertemplate: '<b>%{{theta}}</b><br>Artist: %{{r:.3f}}<extra></extra>'
                }}
            ];

            if (selectedSong && songValues.length > 0) {{
                radarData.push({{
                    type: 'scatterpolar',
                    r: songValues,
                    theta: features,
                    fill: 'none',
                    line: {{ color: 'rgb(239, 85, 59)', width: 2 }},
                    marker: {{ size: 6, color: 'rgb(239, 85, 59)' }},
                    name: selectedSong,
                    hovertemplate: '<b>%{{theta}}</b><br>' + selectedSong + ': %{{r:.3f}}<extra></extra>'
                }});
            }}

            const radarLayout = {{
                polar: {{
                    radialaxis: {{
                        visible: true,
                        range: [0, 1],
                        showticklabels: true,
                        tickfont: {{ size: 11 }},
                        gridcolor: 'rgba(200, 200, 200, 0.3)'
                    }},
                    angularaxis: {{
                        tickfont: {{ size: 12, color: '#333' }},
                        linecolor: 'rgba(200, 200, 200, 0.5)'
                    }},
                    bgcolor: 'rgba(250, 250, 250, 0.5)'
                }},
                showlegend: true,
                legend: {{
                    orientation: 'h',
                    yanchor: 'bottom',
                    y: -0.25,
                    xanchor: 'center',
                    x: 0.5,
                    font: {{ size: 10 }}
                }},
                margin: {{ l: 60, r: 60, t: 40, b: 80 }},
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)'
            }};

            Plotly.newPlot(targetId, radarData, radarLayout, {{ responsive: true }});
        }}
    </script>
</body>
</html>
"""
    return html