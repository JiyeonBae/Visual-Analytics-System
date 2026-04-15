# Hot 100 Interactive Visualization

## Environment Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

#### Using Virtual Environment (Recommended)

**macOS/Linux:**
```bash
cd vis/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Windows:**
```bash
cd vis/
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Quick Install (Alternative)
```bash
pip install pandas numpy plotly
```

## Running the Visualization

### Step 1: Generate the HTML file
```bash
python main.py
```

This will create `interactive_hot100.html` in the current directory.

### Step 2: Open the visualization
```bash
# macOS
open interactive_hot100.html

# Linux
xdg-open interactive_hot100.html

# Windows
start interactive_hot100.html
```

Or simply double-click the `interactive_hot100.html` file.

## File Structure
```
vis/
├── main.py                  # Main execution script
├── data_processor.py        # Data loading and preprocessing
├── detail_views.py          # Detail view data preparation
├── main_view.py             # Main chart generation
├── html_template.py         # HTML template generation
├── hot100_top10_1960_2019_enriched.csv  # Dataset
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Expected Output
- `interactive_hot100.html`: Standalone interactive visualization

## Features
- **Main Chart**: Interactive scatter plot showing artist performance across decades
- **Detail Views**: Click any bubble to see:
  - Song performance metrics table
  - Era signature (decade's musical characteristics)
  - Song signature (individual song's audio features)
  - Radar charts comparing artist, era, and song profiles

## System Requirements
- Works on macOS, Linux, and Windows
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection required only for Plotly CDN

## Troubleshooting

### If you get import errors:
```bash
pip install --upgrade pandas numpy plotly
```

### If the HTML file doesn't open:
- Manually open it with your web browser
- Right-click → Open with → Chrome/Firefox/Safari

## Notes
- The generated HTML file is completely standalone
- No Python needed to view the visualization after generation
- All interactivity works offline (except Plotly CDN loading)