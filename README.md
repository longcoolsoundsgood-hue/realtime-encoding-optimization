# 🎬 Real-Time Encoding Optimization

> Tune x264 encoder parameters · Measure FPS, PSNR, SSIM, bitrate · Compare presets side-by-side

A web-based interactive tool for real-time video encoding optimization. Upload a video, adjust encoding parameters, and instantly visualize the **speed vs. quality trade-off** with detailed metrics and charts.

---

## 📌 Table of Contents

- [What This Project Does](#what-this-project-does)
- [How the Program Works](#how-the-program-works)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Running the App](#running-the-app)
- [Usage Guide](#usage-guide)
- [Project Structure](#project-structure)
- [Metrics Explained](#metrics-explained)
- [Reproducing Results](#reproducing-results)
- [Troubleshooting](#troubleshooting)

---

## 🎯 What This Project Does

Video encoding always involves a fundamental trade-off: **the faster you encode, the lower the quality**. This project makes that trade-off visible and measurable.

Using the **H.264/x264 encoder** via FFmpeg, the app lets you:

- Upload any video and encode it with different settings
- Control **encoding preset** (speed) and **CRF** (quality)
- Measure exactly how fast the encoder runs (**Encoding FPS**)
- Measure output quality (**PSNR** and **SSIM**)
- Compare all 4 presets automatically with the **Benchmark** feature

---

## ⚙️ How the Program Works

The app has **2 main features** accessible via tabs:

### Tab 1 — Single Encode

```
User uploads video
       ↓
Choose preset (ultrafast / fast / medium / slow) + CRF (18–35)  ← Sidebar
       ↓
Click "Start Encoding"
       ↓
encoder.py  →  calls FFmpeg subprocess with libx264
       ↓
metrics.py  →  calculates PSNR, SSIM, bitrate, compression ratio
       ↓
Display: compressed video + 6 metric cards + file size chart
```

**What you see after encoding:**
| Metric | Description |
|--------|-------------|
| Encoding Time | How many seconds the encode took |
| Encoding FPS | Frames encoded per second (key speed metric) |
| Compression Ratio | How many times smaller the output is |
| Bitrate | Data rate of the compressed video (kbps) |
| PSNR | Pixel-level quality score (dB) — higher = better |
| SSIM | Structural similarity score (0–1) — closer to 1 = better |

A **quality badge** automatically labels the result (Excellent / Good / Fair / Poor) based on PSNR value.

---

### Tab 2 — Preset Benchmark

```
Uses the same uploaded video
       ↓
Encodes 4 times: ultrafast → fast → medium → slow  (same CRF)
       ↓
benchmark.py  →  collects all metrics into a DataFrame
       ↓
Display:
  - Results table (all metrics, color-coded)
  - Chart 1: Encoding FPS by preset (bar)
  - Chart 2: PSNR by preset (bar)
  - Chart 3: FPS vs PSNR scatter (trade-off curve)
  - Chart 4: Compression ratio by preset (horizontal bar)
  - Key insights: fastest / best quality / best compression
```

---

## 🖥️ System Requirements

| Component | Requirement | Notes |
|-----------|-------------|-------|
| OS | Ubuntu 20.04+ / Debian / macOS | Windows not tested |
| Python | **3.9 – 3.12** | 3.8 and below not supported |
| FFmpeg | 4.0 or higher | **Must be installed separately — not via pip** |
| RAM | 4 GB minimum | 8 GB recommended for HD video |
| Storage | 1 GB free space | |

> ⚠️ **FFmpeg is a system-level tool.** It cannot be installed via `pip`. You must install it manually before running the app.

---

## 🛠️ Installation

### Step 1 — Install FFmpeg

**Ubuntu / Debian:**
```bash
sudo apt update && sudo apt install ffmpeg -y
ffmpeg -version   # must show version 4.x or higher
```

**macOS:**
```bash
brew install ffmpeg
ffmpeg -version
```

> If `ffmpeg -version` fails → stop here and fix FFmpeg before continuing.

---

### Step 2 — Clone the Repository

```bash
git clone https://github.com/longcoolsoundsgood-hue/realtime-encoding-optimization.git
cd realtime-encoding-optimization
```

---

### Step 3 — Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

---

### Step 4 — Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

### Step 5 — Create Required Directories

```bash
mkdir -p datasets outputs
```

---

## ▶️ Running the App

```bash
source venv/bin/activate
streamlit run main.py
```

Open browser: **http://localhost:8501**

---

## 📖 Usage Guide

### Single Encode
1. Upload a `.mp4`, `.mov`, or `.avi` file
2. In the **sidebar**, select a preset and CRF value
3. Click **▶ Start Encoding**
4. View the compressed video, 6 metric cards, and file size chart

### Preset Benchmark
1. Make sure a video is uploaded in the Single Encode tab first
2. Switch to the **📊 Preset Benchmark** tab
3. Set the CRF value for the benchmark
4. Click **🚀 Run Full Benchmark (all presets)**
5. View the results table, 4 charts, and key insights

---

## 📁 Project Structure

```
realtime-encoding-optimization/
├── app/
│   ├── __init__.py       # Makes app/ a Python package
│   ├── encoder.py        # FFmpeg encoding wrapper + FPS measurement
│   ├── metrics.py        # PSNR, SSIM, bitrate, compression ratio
│   └── benchmark.py      # Multi-preset benchmark runner
├── datasets/             # Input video files (git-ignored)
├── outputs/              # Encoded outputs + benchmark results (git-ignored)
├── main.py               # Streamlit app: UI, tabs, charts
├── requirements.txt      # Python dependencies
└── README.md
```

---

## 📊 Metrics Explained

| Metric | Formula / Method | Interpretation |
|--------|-----------------|----------------|
| **Encoding FPS** | total_frames / encoding_time | > 30 = real-time capable |
| **Compression Ratio** | original_size / compressed_size | Higher = smaller file |
| **Bitrate (kbps)** | ffprobe format=bit_rate | Lower = smaller file |
| **PSNR (dB)** | FFmpeg `psnr` lavfi filter | > 35 dB = good quality |
| **SSIM** | scikit-image, sampled 30 frames | > 0.95 = excellent |

**PSNR Reference:**
- ≥ 40 dB → Excellent
- 35–40 dB → Good ✓
- 30–35 dB → Fair
- < 30 dB → Poor

---

## 🔬 Reproducing Results

### Get a test video
```bash
# Big Buck Bunny 720p — standard benchmark video
wget -O datasets/input.mp4 \
  "https://sample-videos.com/video321/mp4/720/big_buck_bunny_720p_1mb.mp4"
```

### Expected results (CRF=23, 720p, ~30s clip)

| Preset | Encoding FPS | PSNR (dB) | Compression Ratio | Output Size |
|--------|-------------|-----------|-------------------|-------------|
| ultrafast | 300–450 | 32–34 | 8–10× | smaller |
| fast | 150–225 | 34–36 | 9–11× | ↓ |
| medium | 72–120 | 35–38 | 10–13× | ↓ |
| slow | 30–51 | 36–39 | 11–15× | smallest |

> Results vary by CPU. Run the Benchmark tab to get exact numbers on your machine.

---

## 🔧 Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `ffmpeg: command not found` | FFmpeg not installed | `sudo apt install ffmpeg -y` |
| `No matching distribution found` | Old pinned requirements | Use updated `requirements.txt` with `>=` |
| `ModuleNotFoundError: cv2` | opencv not installed | `pip install opencv-python` |
| `FileNotFoundError: datasets/input.mp4` | Folder missing | `mkdir -p datasets outputs` |
| `streamlit: command not found` | venv not active | `source venv/bin/activate` |
| Benchmark tab: "Upload a video first" | No input file | Go to Single Encode tab and upload first |

---

## 📦 Key Dependencies

| Library | Purpose |
|---------|---------|
| streamlit ≥ 1.30 | Web UI |
| ffmpeg-python ≥ 0.2 | FFmpeg Python bindings |
| opencv-python ≥ 4.8 | Frame reading, video info |
| scikit-image ≥ 0.21 | SSIM calculation |
| matplotlib ≥ 3.7 | Charts and plots |
| pandas ≥ 2.0 | Benchmark results table |

---

*For educational use — Multimedia Data Compression and Coding course project.*# Real-Time Encoding Optimization
 
A web-based tool for real-time video encoding optimization using FFmpeg and Streamlit. Upload a video, tune encoder parameters, and instantly see quality/speed trade-offs with detailed metrics.
 
---
 
## Table of Contents
 
- [Overview](#overview)
- [Features](#features)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Running the App](#running-the-app)
- [Usage Guide](#usage-guide)
- [Project Structure](#project-structure)
- [Metrics Explained](#metrics-explained)
- [Reproducing Results](#reproducing-results)
- [Troubleshooting](#troubleshooting)
---
 
## Overview
 
This project addresses the fundamental trade-off in video encoding: **speed vs. quality**. By exposing FFmpeg's x264 encoder parameters through an interactive UI, users can empirically observe how encoding preset and CRF value affect:
 
- Output file size and compression ratio
- Visual quality (PSNR)
- Encoding throughput (FPS)
- Bitrate
---
 
## Features
 
- **Video Upload**: Supports `.mp4`, `.mov`, `.avi` formats
- **Preset Selection**: `ultrafast`, `fast`, `medium`, `slow`
- **CRF Slider**: Range 18–35 (18 = near-lossless, 35 = high compression)
- **Live Metrics**: Encoding time, compression ratio, bitrate, PSNR
- **Side-by-side Playback**: Compare original vs. compressed video
---
 
## System Requirements
 
| Component | Requirement | Notes |
|-----------|-------------|-------|
| OS | Ubuntu 20.04+ / Debian / macOS | Windows not tested |
| Python | **3.9 – 3.12** | ⚠️ 3.8 and below not supported |
| FFmpeg | 4.0 or higher | **Must be installed separately — see Step 1** |
| RAM | 4 GB minimum | 8 GB recommended for large videos |
| Storage | 1 GB free space | |
 
> **Important:** FFmpeg is a system-level dependency and **cannot** be installed via `pip`.  
> You must install it manually before running the app (see Step 1 below).
 
---
 
## Installation
 
### Step 1 — Install FFmpeg (required)
 
**Ubuntu / Debian:**
```bash
sudo apt update
sudo apt install ffmpeg -y
ffmpeg -version   # should print version 4.x or higher
```
 
**macOS (Homebrew):**
```bash
brew install ffmpeg
ffmpeg -version
```
 
> If `ffmpeg -version` fails, stop here and fix FFmpeg before continuing.
 
---
 
### Step 2 — Clone the Repository
 
```bash
git clone https://github.com/longcoolsoundsgood-hue/realtime-encoding-optimization.git
cd realtime-encoding-optimization
```
 
---
 
### Step 3 — Create a Virtual Environment
 
```bash
python3 -m venv venv
source venv/bin/activate      # Linux / macOS
# venv\Scripts\activate       # Windows (if applicable)
```
 
You should see `(venv)` appear at the start of your terminal prompt.
 
---
 
### Step 4 — Install Python Dependencies
 
```bash
pip install -r requirements.txt
```
 
This installs all required Python packages. pip will automatically select versions compatible with your Python version (3.9–3.12).
 
---
 
### Step 5 — Create Required Directories
 
```bash
mkdir -p datasets outputs
```
 
---
 
## Running the App
 
```bash
# Make sure virtual environment is active
source venv/bin/activate
 
# Launch the Streamlit app
streamlit run main.py
```
 
Open your browser and navigate to: **http://localhost:8501**
 
---
 
## Usage Guide
 
1. **Upload a Video** — Click "Browse files" and select a `.mp4`, `.mov`, or `.avi` file.
2. **Choose a Preset** — Select encoding speed preset from the dropdown:
   - `ultrafast`: Fastest encoding, largest file, lowest quality
   - `fast`: Good balance for real-time use
   - `medium`: Default FFmpeg setting
   - `slow`: Better compression, slower speed
3. **Set CRF Value** — Use the slider (18–35):
   - Lower value = higher quality, larger file
   - Higher value = lower quality, smaller file
4. **Start Encoding** — Click the **Start Encoding** button.
5. **View Results** — See the compressed video and all metrics below.
---
 
## Project Structure
 
```
realtime-encoding-optimization/
├── app/
│   ├── encoder.py          # FFmpeg encoding wrapper
│   └── metrics.py          # Metrics calculation (PSNR, bitrate, ratio)
├── datasets/               # Input video files (not tracked by git)
├── outputs/                # Encoded output files (not tracked by git)
├── main.py                 # Streamlit application entry point
├── requirements.txt        # Python dependencies (version-flexible)
└── README.md               # This file
```
 
---
 
## Metrics Explained
 
| Metric | Description | Good Value |
|--------|-------------|------------|
| **Encoding Time (s)** | Wall-clock time for encoding | Lower = faster |
| **Encoding FPS** | Frames encoded per second | > 30 for real-time |
| **Compression Ratio** | Original size / Compressed size | Higher = smaller file |
| **Bitrate (kbps)** | Data rate of encoded video | Depends on content |
| **PSNR (dB)** | Peak Signal-to-Noise Ratio — quality measure | > 35 dB = good quality |
 
**PSNR Reference:**
- > 40 dB — Excellent (near-lossless)
- 35–40 dB — Good (visually acceptable)
- 30–35 dB — Fair (visible artifacts)
- < 30 dB — Poor
---
 
## Reproducing Results
 
### Recommended Test Video
 
```bash
# Download a standard benchmark video (Big Buck Bunny 720p)
wget -O datasets/input.mp4 \
  "https://sample-videos.com/video321/mp4/720/big_buck_bunny_720p_1mb.mp4"
 
# Or use any local video file
cp /path/to/your/video.mp4 datasets/input.mp4
```
 
### Expected Results by Preset (CRF=23, 720p input)
 
| Preset | Encoding Time | Est. FPS | Compression Ratio | PSNR |
|--------|--------------|----------|-------------------|------|
| ultrafast | ~4–6s | ~300–450 | ~8–10× | ~32–34 dB |
| fast | ~8–12s | ~150–225 | ~9–11× | ~34–36 dB |
| medium | ~15–25s | ~72–120 | ~10–13× | ~35–38 dB |
| slow | ~35–60s | ~30–51 | ~11–15× | ~36–39 dB |
 
> Results vary by CPU, video content complexity, and resolution.
 
### Configuration Used for Benchmarks
 
```
Input:    720p H.264 MP4, ~30 FPS, 60 seconds
Encoder:  libx264
CRF:      18, 23, 28, 35
Presets:  ultrafast, fast, medium, slow
Platform: Ubuntu 22.04, Python 3.10
```
 
---
 
## Troubleshooting
 
| Error | Cause | Fix |
|-------|-------|-----|
| `ffmpeg: command not found` | FFmpeg not installed | Run `sudo apt install ffmpeg -y` |
| `No matching distribution found for contourpy==x.x.x` | Old pinned requirements | Use the updated `requirements.txt` with `>=` versions |
| `ModuleNotFoundError: No module named 'cv2'` | opencv not installed | Run `pip install opencv-python` |
| `FileNotFoundError: datasets/input.mp4` | datasets folder missing | Run `mkdir -p datasets outputs` |
| `streamlit: command not found` | venv not active | Run `source venv/bin/activate` first |
| App opens but encoding hangs | FFmpeg version too old | Run `ffmpeg -version` — must be 4.0+ |
 
---
 
## Dependencies
 
All Python dependencies are in `requirements.txt` with flexible version ranges (`>=`) to ensure compatibility across Python 3.9–3.12:
 
| Library | Min Version | Purpose |
|---------|------------|---------|
| streamlit | 1.30.0 | Web UI framework |
| ffmpeg-python | 0.2.0 | FFmpeg Python bindings |
| opencv-python | 4.8.0 | Video frame analysis |
| numpy | 1.24.0 | Numerical operations |
| scikit-image | 0.21.0 | Image quality metrics |
| matplotlib | 3.7.0 | Charts and visualization |
| pandas | 2.0.0 | Data handling |
 
