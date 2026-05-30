# 🎬 Real-Time Encoding Optimization

> Tune x264 encoder parameters · Measure FPS, PSNR, SSIM, bitrate · Compare presets in real time

A Streamlit-based web application for optimizing H.264 video encoding using FFmpeg's libx264 encoder. Upload a video, select encoding parameters, and instantly visualize the quality–speed trade-off through interactive charts and side-by-side comparisons.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Usage Guide](#usage-guide)
- [Project Structure](#project-structure)
- [Metrics Explained](#metrics-explained)
- [Reproducing Benchmark Results](#reproducing-benchmark-results)
- [Dataset / Test Inputs](#dataset--test-inputs)
- [Dependencies](#dependencies)

---

## Overview

This project explores the relationship between x264 encoding **speed (FPS)** and **visual quality (PSNR/SSIM)** across different preset configurations. It provides a live interactive demo where users can:

- Encode a video with any preset + CRF combination
- View real-time encoding metrics
- Run a full benchmark across all 4 presets
- Visualize FPS vs Quality trade-offs with annotated charts

---

## Features

| Feature | Description |
|---|---|
| **Single Encode** | Upload → encode with chosen preset/CRF → view metrics instantly |
| **Preset Benchmark** | Auto-encode with ultrafast / fast / medium / slow at a fixed CRF |
| **FPS vs Quality Charts** | Bar charts + scatter trade-off plot |
| **PSNR & SSIM** | Full quality metrics computed per encode |
| **Compression Ratio** | Original vs compressed file size comparison |
| **Quality Badge** | Automatic classification (Excellent / Good / Fair / Poor) |
| **Interactive Sliders** | CRF control (18–35) and preset selector |

---

## System Requirements

- **Python** 3.9 – 3.12
- **FFmpeg** (must be installed separately — see below)
- **OS**: Linux, macOS, or Windows (WSL recommended for Windows)
- **RAM**: 4 GB minimum; 8 GB recommended for large videos

---

## Installation

### Step 1 — Install FFmpeg

**Ubuntu / Debian:**
```bash
sudo apt update && sudo apt install ffmpeg -y
```

**macOS (Homebrew):**
```bash
brew install ffmpeg
```

**Verify installation:**
```bash
ffmpeg -version
ffprobe -version
```

---

### Step 2 — Clone the Repository

```bash
git clone https://github.com/longcoolsoundsgood-hue/realtime-encoding-optimization.git
cd realtime-encoding-optimization
```

---

### Step 3 — Set Up Python Environment

**Create and activate a virtual environment (recommended):**

```bash
python3 -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
```

---

### Step 4 — Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

## Running the Application

```bash
streamlit run main.py
```

The app opens at **http://localhost:8501** in your browser.

---

## Usage Guide

### Tab 1 — Single Encode

1. Upload a `.mp4`, `.mov`, or `.avi` file using the file uploader
2. In the **sidebar**, select a **Preset** and adjust the **CRF** slider
3. Click **▶ Start Encoding**
4. View results: encoding time, FPS, compression ratio, bitrate, PSNR, SSIM
5. Compare original vs compressed video side by side

### Tab 2 — Preset Benchmark

1. Ensure a video is already uploaded (from Tab 1)
2. Set the **CRF for benchmark** slider
3. Click **🚀 Run Full Benchmark (all presets)**
4. View the results table and three trade-off charts:
   - Encoding FPS by Preset
   - PSNR (dB) by Preset
   - FPS vs PSNR Scatter Plot
   - Compression Ratio by Preset

---

## Project Structure

```
realtime-encoding-optimization/
│
├── app/
│   ├── __init__.py          # Package init
│   ├── encoder.py           # FFmpeg x264 encoding wrapper + FPS measurement
│   ├── metrics.py           # PSNR, SSIM, bitrate, compression ratio, video info
│   └── benchmark.py         # Multi-preset benchmark runner → DataFrame
│
├── datasets/                # Place input video files here (auto-created)
├── outputs/                 # Encoded output files saved here (auto-created)
│
├── main.py                  # Streamlit application entry point
├── requirements.txt         # Python dependencies
├── .gitignore
└── README.md
```

---

## Metrics Explained

| Metric | Description | Better |
|---|---|---|
| **Encoding FPS** | Frames encoded per second (wall-clock) | Higher |
| **Encoding Time (s)** | Total wall-clock seconds for encoding | Lower |
| **PSNR (dB)** | Peak Signal-to-Noise Ratio — pixel-level fidelity | Higher (≥35 dB = good) |
| **SSIM** | Structural Similarity Index — perceptual quality | Higher (closer to 1.0) |
| **Bitrate (kbps)** | Output video bitrate in kilobits per second | Depends on use case |
| **Compression Ratio** | Original size ÷ Compressed size | Higher = smaller file |

### Preset Summary

| Preset | Speed | Quality | Use Case |
|---|---|---|---|
| `ultrafast` | Highest FPS | Lowest PSNR | Live streaming, real-time pipelines |
| `fast` | High FPS | Good PSNR | Balanced production use |
| `medium` | Moderate | Better PSNR | Default recommendation |
| `slow` | Lowest FPS | Best PSNR | Archival, offline encoding |

### CRF Guide

| CRF Range | Quality Level |
|---|---|
| 18–22 | Near-lossless |
| 23–27 | Good quality (recommended) |
| 28–32 | Acceptable |
| 33–35 | High compression, lower quality |

---

## Reproducing Benchmark Results

To reproduce the benchmark results shown in the report:

```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Launch app
streamlit run main.py

# 3. In the browser:
#    - Tab 1: Upload your test video
#    - Tab 2: Set CRF = 23, click "Run Full Benchmark"
```

**Expected output files** (saved to `outputs/benchmark/`):
```
bench_ultrafast_crf23.mp4
bench_fast_crf23.mp4
bench_medium_crf23.mp4
bench_slow_crf23.mp4
```

**To run benchmark programmatically (without UI):**

```python
from app.benchmark import run_benchmark

df = run_benchmark(
    input_file="datasets/input.mp4",
    output_dir="outputs/benchmark",
    crf=23
)
print(df[["Preset", "Encoding FPS", "PSNR (dB)", "SSIM", "Compression Ratio"]])
```

---

## Dataset / Test Inputs

The application accepts any standard video file (`.mp4`, `.mov`, `.avi`).

**Recommended test sources:**

| Source | Description | URL |
|---|---|---|
| Big Buck Bunny | Open-source animation, various resolutions | https://peach.blender.org/download/ |
| Tears of Steel | Open-source live-action/VFX | https://mango.blender.org/download/ |
| Xiph.org Test Media | Standard video codec test sequences | https://media.xiph.org/video/derf/ |

**To use your own video:**
1. Place the file in the `datasets/` folder
2. Upload it via the Streamlit UI, or rename it to `datasets/input.mp4`

---

## Dependencies

### Python Packages (see `requirements.txt`)

| Package | Version | Purpose |
|---|---|---|
| `streamlit` | ≥1.30.0 | Web UI framework |
| `opencv-python` | ≥4.8.0 | Frame extraction, SSIM computation |
| `scikit-image` | ≥0.21.0 | SSIM metric (structural_similarity) |
| `numpy` | ≥1.24.0 | Numerical operations |
| `pandas` | ≥2.0.0 | Benchmark results as DataFrame |
| `matplotlib` | ≥3.7.0 | Chart rendering |
| `ffmpeg-python` | ≥0.2.0 | FFmpeg Python bindings |
| `Pillow` | ≥10.0.0 | Image utilities |

### System Dependencies

| Tool | Purpose |
|---|---|
| `ffmpeg` | Video encoding (libx264), PSNR computation via `psnr` filter |
| `ffprobe` | Bitrate extraction from encoded files |

---

## Troubleshooting

**`ffmpeg: command not found`**
→ Install FFmpeg via your package manager (see Installation Step 1)

**`ModuleNotFoundError`**
→ Ensure your virtual environment is activated and `pip install -r requirements.txt` was run

**PSNR shows `N/A`**
→ Usually occurs when video dimensions differ; the app handles this automatically with resize

**Slow benchmark on large videos**
→ Use a shorter clip (10–30 seconds) for quick benchmarking; `ultrafast` preset encodes fastest

---

## License

This project is developed for academic purposes as part of the Multimedia Data Compression and Coding course.
