"""
benchmark.py — Multi-preset benchmark runner
Encodes the same input with all preset/CRF combinations and returns
a DataFrame of results for chart rendering.
"""

import os
import pandas as pd
from app.encoder import encode_video
from app.metrics import compute_all_metrics


PRESETS = ["ultrafast", "fast", "medium", "slow"]


def run_benchmark(
    input_file: str,
    output_dir: str,
    crf: int = 23,
    presets: list[str] = None,
    progress_callback=None,
) -> pd.DataFrame:
    """
    Encode `input_file` with each preset at fixed `crf`.
    Returns a DataFrame with one row per preset.

    Parameters
    ----------
    input_file        : path to source video
    output_dir        : directory for encoded outputs
    crf               : CRF value to use for all runs
    presets           : list of presets to test (default: all 4)
    progress_callback : optional callable(i, total, preset) for UI updates
    """
    if presets is None:
        presets = PRESETS

    os.makedirs(output_dir, exist_ok=True)
    rows = []

    for i, preset in enumerate(presets):
        if progress_callback:
            progress_callback(i, len(presets), preset)

        out_path = os.path.join(output_dir, f"bench_{preset}_crf{crf}.mp4")

        enc = encode_video(input_file, out_path, preset=preset, crf=crf)
        mtr = compute_all_metrics(input_file, out_path)

        rows.append({
            "Preset":           preset,
            "CRF":              crf,
            "Encoding Time (s)": enc["encoding_time"],
            "Encoding FPS":     enc["encoding_fps"],
            "Compression Ratio": mtr["compression_ratio"],
            "Bitrate (kbps)":   mtr["bitrate_kbps"],
            "PSNR (dB)":        mtr["psnr"],
            "SSIM":             mtr["ssim"],
            "Output Size (MB)": mtr["compressed_size_mb"],
            "Output Path":      out_path,
        })

    return pd.DataFrame(rows)
