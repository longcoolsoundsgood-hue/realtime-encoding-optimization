"""
main.py — Real-Time Encoding Optimization
Streamlit app: encode videos, visualise quality/speed trade-offs.
"""

import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

from app.encoder import encode_video
from app.metrics import compute_all_metrics, get_video_info
from app.benchmark import run_benchmark

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Real-Time Encoding Optimizer",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Sora:wght@300;400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Sora', sans-serif;
}

/* Dark header banner */
.main-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 60%, #0f3460 100%);
    border-radius: 14px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    border: 1px solid #1e40af33;
}
.main-header h1 {
    color: #e2e8f0;
    font-size: 2rem;
    font-weight: 700;
    margin: 0 0 0.3rem 0;
    letter-spacing: -0.5px;
}
.main-header p {
    color: #94a3b8;
    font-size: 0.95rem;
    margin: 0;
}

/* Metric cards */
.metric-card {
    background: #0f172a;
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 1.1rem 1.3rem;
    text-align: center;
    margin: 4px;
}
.metric-card .label {
    color: #64748b;
    font-size: 0.75rem;
    font-family: 'JetBrains Mono', monospace;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.4rem;
}
.metric-card .value {
    color: #38bdf8;
    font-size: 1.6rem;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
    line-height: 1;
}
.metric-card .unit {
    color: #475569;
    font-size: 0.8rem;
    margin-top: 0.2rem;
}

/* Quality badge */
.quality-badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
}
.q-excellent { background: #052e16; color: #4ade80; border: 1px solid #166534; }
.q-good      { background: #072a1d; color: #34d399; border: 1px solid #065f46; }
.q-fair      { background: #2d1b05; color: #fb923c; border: 1px solid #7c2d12; }
.q-poor      { background: #2d0505; color: #f87171; border: 1px solid #7f1d1d; }

/* Section headers */
.section-title {
    color: #e2e8f0;
    font-size: 1.05rem;
    font-weight: 600;
    margin: 1rem 0 0.5rem 0;
    padding-bottom: 0.3rem;
    border-bottom: 1px solid #1e3a5f;
}

/* Info box */
.info-box {
    background: #0f2744;
    border-left: 3px solid #3b82f6;
    border-radius: 0 8px 8px 0;
    padding: 0.7rem 1rem;
    font-size: 0.85rem;
    color: #93c5fd;
    margin: 0.5rem 0;
}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
  <h1>🎬 Real-Time Encoding Optimizer</h1>
  <p>Tune x264 encoder parameters · Measure FPS, PSNR, SSIM, bitrate · Compare presets</p>
</div>
""", unsafe_allow_html=True)

# ── Directories ───────────────────────────────────────────────────────────────
os.makedirs("datasets", exist_ok=True)
os.makedirs("outputs",  exist_ok=True)

INPUT_PATH  = "datasets/input.mp4"
OUTPUT_PATH = "outputs/output.mp4"

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Encoder Settings")

    preset = st.selectbox(
        "Preset",
        ["ultrafast", "fast", "medium", "slow"],
        index=1,
        help="ultrafast = highest FPS, lowest quality. slow = lowest FPS, best quality."
    )

    crf = st.slider(
        "CRF (Constant Rate Factor)",
        min_value=18, max_value=35, value=23,
        help="18 = near-lossless (large file). 35 = high compression (small file)."
    )

    st.markdown("""
    <div class="info-box">
    <b>CRF Guide</b><br>
    18–22 → Near-lossless<br>
    23–27 → Good quality ✓<br>
    28–32 → Acceptable<br>
    33–35 → High compression
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📘 About")
    st.caption(
        "Encodes with **libx264** via FFmpeg. "
        "Metrics: PSNR, SSIM, bitrate, compression ratio, encoding FPS."
    )

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["🎯  Single Encode", "📊  Preset Benchmark"])


# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — Single Encode
# ════════════════════════════════════════════════════════════════════════════
with tab1:

    uploaded = st.file_uploader(
        "Upload a video file",
        type=["mp4", "mov", "avi"],
        label_visibility="collapsed"
    )

    if uploaded:
        with open(INPUT_PATH, "wb") as f:
            f.write(uploaded.read())

        info = get_video_info(INPUT_PATH)
        size_mb = os.path.getsize(INPUT_PATH) / 1e6

        # Original video + info
        col_vid, col_info = st.columns([3, 2])
        with col_vid:
            st.markdown('<div class="section-title">Original Video</div>', unsafe_allow_html=True)
            st.video(INPUT_PATH)
        with col_info:
            st.markdown('<div class="section-title">Source Info</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="metric-card"><div class="label">Resolution</div>
            <div class="value" style="font-size:1.1rem">{info['width']}×{info['height']}</div></div>
            <div class="metric-card"><div class="label">Source FPS</div>
            <div class="value">{info['fps']}</div></div>
            <div class="metric-card"><div class="label">Duration</div>
            <div class="value">{info['duration']}</div><div class="unit">seconds</div></div>
            <div class="metric-card"><div class="label">File Size</div>
            <div class="value">{size_mb:.1f}</div><div class="unit">MB</div></div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        if st.button("▶ Start Encoding", type="primary", use_container_width=True):
            with st.spinner(f"Encoding with preset=**{preset}**, CRF=**{crf}**…"):
                enc  = encode_video(INPUT_PATH, OUTPUT_PATH, preset=preset, crf=crf)
                mtr  = compute_all_metrics(INPUT_PATH, OUTPUT_PATH)

            # ── Metric cards ────────────────────────────────────────────────
            st.markdown('<div class="section-title">📈 Encoding Results</div>', unsafe_allow_html=True)

            c1, c2, c3, c4, c5, c6 = st.columns(6)
            cards = [
                (c1, "Encoding Time", f"{enc['encoding_time']:.2f}", "sec"),
                (c2, "Encoding FPS",  f"{enc['encoding_fps']:.1f}",  "fps"),
                (c3, "Compression",   f"{mtr['compression_ratio']:.1f}", "×"),
                (c4, "Bitrate",       f"{mtr['bitrate_kbps']:.0f}", "kbps"),
                (c5, "PSNR",          f"{mtr['psnr']:.2f}" if mtr['psnr'] else "N/A", "dB"),
                (c6, "SSIM",          f"{mtr['ssim']:.4f}" if mtr['ssim'] else "N/A", ""),
            ]
            for col, label, value, unit in cards:
                with col:
                    st.markdown(f"""
                    <div class="metric-card">
                      <div class="label">{label}</div>
                      <div class="value">{value}</div>
                      <div class="unit">{unit}</div>
                    </div>""", unsafe_allow_html=True)

            # ── Quality badge ────────────────────────────────────────────────
            psnr_val = mtr['psnr']
            if psnr_val:
                if psnr_val >= 40:
                    badge = '<span class="quality-badge q-excellent">● Excellent Quality (≥40 dB)</span>'
                elif psnr_val >= 35:
                    badge = '<span class="quality-badge q-good">● Good Quality (35–40 dB)</span>'
                elif psnr_val >= 30:
                    badge = '<span class="quality-badge q-fair">● Fair Quality (30–35 dB)</span>'
                else:
                    badge = '<span class="quality-badge q-poor">● Poor Quality (<30 dB)</span>'
                st.markdown(badge, unsafe_allow_html=True)

            # ── Compressed video ─────────────────────────────────────────────
            st.markdown('<div class="section-title">Compressed Output</div>', unsafe_allow_html=True)
            col_out, col_compare = st.columns(2)
            with col_out:
                st.video(OUTPUT_PATH)
                out_mb = mtr['compressed_size_mb']
                st.caption(f"Output: {out_mb:.2f} MB  |  {mtr['compressed_info']['fps']} FPS  |  Preset: {preset}  |  CRF: {crf}")

            with col_compare:
                # Bar chart: original vs compressed size
                fig, ax = plt.subplots(figsize=(4, 3))
                fig.patch.set_facecolor("#0f172a")
                ax.set_facecolor("#0f172a")
                labels = ["Original", "Compressed"]
                sizes  = [mtr["original_size_mb"], mtr["compressed_size_mb"]]
                colors = ["#3b82f6", "#38bdf8"]
                bars = ax.bar(labels, sizes, color=colors, width=0.4, edgecolor="none", zorder=3)
                ax.set_ylabel("Size (MB)", color="#94a3b8", fontsize=9)
                ax.set_title("File Size Comparison", color="#e2e8f0", fontsize=10, pad=10)
                ax.tick_params(colors="#94a3b8", labelsize=8)
                for spine in ax.spines.values():
                    spine.set_color("#1e3a5f")
                ax.yaxis.grid(True, color="#1e3a5f", linewidth=0.5, zorder=0)
                for bar, val in zip(bars, sizes):
                    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                            f"{val:.1f} MB", ha="center", va="bottom",
                            color="#e2e8f0", fontsize=8, fontweight="bold")
                plt.tight_layout()
                st.pyplot(fig)
                plt.close()

    else:
        st.markdown("""
        <div style="text-align:center; padding:3rem; color:#475569; border:2px dashed #1e3a5f; border-radius:12px;">
            <div style="font-size:3rem">📁</div>
            <div style="font-size:1.1rem; margin-top:0.5rem">Upload a video to get started</div>
            <div style="font-size:0.85rem; margin-top:0.3rem">Supports .mp4 · .mov · .avi</div>
        </div>
        """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — Preset Benchmark
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("""
    <div class="info-box">
    Encodes the uploaded video with <b>all 4 presets</b> at the selected CRF, then plots
    FPS vs Quality trade-offs side by side.
    </div>
    """, unsafe_allow_html=True)

    bench_crf = st.slider("CRF for benchmark", 18, 35, 23, key="bench_crf")

    can_benchmark = os.path.exists(INPUT_PATH)
    if not can_benchmark:
        st.warning("Upload a video in the **Single Encode** tab first.")

    if can_benchmark and st.button("🚀 Run Full Benchmark (all presets)", type="primary", use_container_width=True):
        progress_bar = st.progress(0, text="Starting benchmark…")
        status_text  = st.empty()

        def on_progress(i, total, preset_name):
            pct = int((i / total) * 100)
            progress_bar.progress(pct, text=f"Encoding preset: **{preset_name}** ({i+1}/{total})")
            status_text.caption(f"Running {preset_name}…")

        with st.spinner("Benchmarking all presets…"):
            df = run_benchmark(INPUT_PATH, "outputs/benchmark",
                               crf=bench_crf, progress_callback=on_progress)

        progress_bar.progress(100, text="✅ Benchmark complete!")
        status_text.empty()

        st.session_state["bench_df"] = df

    # ── Show results if available ────────────────────────────────────────────
    if "bench_df" in st.session_state:
        df = st.session_state["bench_df"]

        st.markdown('<div class="section-title">📊 Results Table</div>', unsafe_allow_html=True)
        display_cols = ["Preset", "Encoding Time (s)", "Encoding FPS",
                        "Compression Ratio", "Bitrate (kbps)", "PSNR (dB)", "SSIM", "Output Size (MB)"]
        st.dataframe(
            df[display_cols].style.format({
                "Encoding Time (s)": "{:.2f}",
                "Encoding FPS":      "{:.1f}",
                "Compression Ratio": "{:.2f}",
                "Bitrate (kbps)":    "{:.1f}",
                "PSNR (dB)":         "{:.2f}",
                "SSIM":              "{:.4f}",
                "Output Size (MB)":  "{:.2f}",
            }).background_gradient(subset=["Encoding FPS"], cmap="Blues")
             .background_gradient(subset=["PSNR (dB)"], cmap="Greens"),
            use_container_width=True
        )

        # ── Charts ───────────────────────────────────────────────────────────
        st.markdown('<div class="section-title">📈 FPS vs Quality Trade-off Charts</div>', unsafe_allow_html=True)

        DARK_BG   = "#0f172a"
        GRID_COL  = "#1e3a5f"
        TEXT_COL  = "#94a3b8"
        TITLE_COL = "#e2e8f0"
        PALETTE   = ["#38bdf8", "#34d399", "#fb923c", "#f472b6"]

        def style_ax(ax, title, xlabel, ylabel):
            ax.set_facecolor(DARK_BG)
            ax.set_title(title, color=TITLE_COL, fontsize=10, pad=8)
            ax.set_xlabel(xlabel, color=TEXT_COL, fontsize=8)
            ax.set_ylabel(ylabel, color=TEXT_COL, fontsize=8)
            ax.tick_params(colors=TEXT_COL, labelsize=7)
            for spine in ax.spines.values():
                spine.set_color(GRID_COL)
            ax.yaxis.grid(True, color=GRID_COL, linewidth=0.5, zorder=0)
            ax.xaxis.grid(True, color=GRID_COL, linewidth=0.5, zorder=0)

        fig, axes = plt.subplots(1, 3, figsize=(13, 4))
        fig.patch.set_facecolor(DARK_BG)
        presets_list = df["Preset"].tolist()

        # Chart 1: Encoding FPS by preset
        ax = axes[0]
        bars = ax.bar(presets_list, df["Encoding FPS"], color=PALETTE, edgecolor="none", zorder=3)
        style_ax(ax, "Encoding FPS by Preset", "Preset", "FPS (frames/sec)")
        for bar, val in zip(bars, df["Encoding FPS"]):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    f"{val:.0f}", ha="center", va="bottom", color=TITLE_COL, fontsize=7.5, fontweight="bold")
        ax.axhline(y=30, color="#f59e0b", linestyle="--", linewidth=1, label="Real-time threshold (30 FPS)", zorder=4)
        ax.legend(fontsize=7, facecolor=DARK_BG, labelcolor=TEXT_COL, edgecolor=GRID_COL)

        # Chart 2: PSNR by preset
        ax = axes[1]
        psnr_vals = df["PSNR (dB)"].fillna(0).tolist()
        bars = ax.bar(presets_list, psnr_vals, color=PALETTE, edgecolor="none", zorder=3)
        style_ax(ax, "PSNR (dB) by Preset", "Preset", "PSNR (dB)")
        ax.axhline(y=35, color="#4ade80", linestyle="--", linewidth=1, label="Good quality (35 dB)", zorder=4)
        ax.legend(fontsize=7, facecolor=DARK_BG, labelcolor=TEXT_COL, edgecolor=GRID_COL)
        for bar, val in zip(bars, psnr_vals):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                    f"{val:.1f}", ha="center", va="bottom", color=TITLE_COL, fontsize=7.5, fontweight="bold")

        # Chart 3: FPS vs PSNR scatter (trade-off curve)
        ax = axes[2]
        fps_vals  = df["Encoding FPS"].tolist()
        for i, (x, y, label, c) in enumerate(zip(fps_vals, psnr_vals, presets_list, PALETTE)):
            ax.scatter(x, y, color=c, s=100, zorder=5, edgecolors="white", linewidths=0.5)
            ax.annotate(label, (x, y), textcoords="offset points", xytext=(6, 4),
                        fontsize=7.5, color=c)
        if len(fps_vals) > 1:
            ax.plot(fps_vals, psnr_vals, color="#475569", linestyle="--", linewidth=1, zorder=3)
        style_ax(ax, "FPS vs PSNR Trade-off", "Encoding FPS", "PSNR (dB)")

        plt.tight_layout(pad=2)
        st.pyplot(fig)
        plt.close()

        # Compression ratio chart
        fig2, ax2 = plt.subplots(figsize=(7, 3))
        fig2.patch.set_facecolor(DARK_BG)
        bars2 = ax2.barh(presets_list, df["Compression Ratio"], color=PALETTE, edgecolor="none", zorder=3)
        style_ax(ax2, "Compression Ratio by Preset (higher = smaller file)", "Compression Ratio (×)", "Preset")
        for bar, val in zip(bars2, df["Compression Ratio"]):
            ax2.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height()/2,
                     f"{val:.2f}×", va="center", color=TITLE_COL, fontsize=8, fontweight="bold")
        plt.tight_layout()
        st.pyplot(fig2)
        plt.close()

        # ── Key insights ─────────────────────────────────────────────────────
        st.markdown('<div class="section-title">💡 Key Insights</div>', unsafe_allow_html=True)

        fastest = df.loc[df["Encoding FPS"].idxmax(), "Preset"]
        best_q  = df.loc[df["PSNR (dB)"].idxmax(), "Preset"] if df["PSNR (dB)"].notna().any() else "N/A"
        best_r  = df.loc[df["Compression Ratio"].idxmax(), "Preset"]
        fps_range = df["Encoding FPS"].max() / df["Encoding FPS"].min()
        psnr_range = df["PSNR (dB)"].max() - df["PSNR (dB)"].min() if df["PSNR (dB)"].notna().all() else 0

        ic1, ic2, ic3 = st.columns(3)
        with ic1:
            st.info(f"⚡ **Fastest preset:** `{fastest}`\n\nBest for real-time pipelines requiring high throughput.")
        with ic2:
            st.success(f"🏆 **Best quality:** `{best_q}`\n\nHighest PSNR — use for archival or offline encoding.")
        with ic3:
            st.warning(f"📦 **Best compression:** `{best_r}`\n\nSmallest output file for a given CRF.")

        st.markdown(f"""
        <div class="info-box">
        Across all presets at CRF {bench_crf}: encoding FPS varies by
        <b>{fps_range:.1f}×</b>, while PSNR varies by only <b>{psnr_range:.1f} dB</b>.
        This confirms that preset selection has a much larger impact on speed than on quality.
        </div>
        """, unsafe_allow_html=True)
