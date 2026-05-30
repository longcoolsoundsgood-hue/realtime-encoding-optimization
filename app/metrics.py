"""
metrics.py — Video quality and compression metrics
Provides: file size, compression ratio, bitrate, PSNR, SSIM, encoding FPS.
"""

import os
import subprocess
import re
import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim_func


# ── File size ─────────────────────────────────────────────────────────────────

def get_file_size_mb(path: str) -> float:
    """Return file size in megabytes."""
    return os.path.getsize(path) / (1024 * 1024)


def compression_ratio(original: str, compressed: str) -> float:
    """Return original_size / compressed_size."""
    return get_file_size_mb(original) / get_file_size_mb(compressed)


# ── Bitrate ───────────────────────────────────────────────────────────────────

def get_bitrate(video_path: str) -> float:
    """Return video bitrate in kbps via ffprobe."""
    command = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "format=bit_rate",
        "-of", "default=noprint_wrappers=1:nokey=1",
        video_path,
    ]
    result = subprocess.run(command, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True)
    try:
        return int(result.stdout.strip()) / 1000
    except ValueError:
        return 0.0


# ── PSNR ──────────────────────────────────────────────────────────────────────

def calculate_psnr(original: str, compressed: str) -> float | None:
    """
    Compute average PSNR (dB) between two videos using FFmpeg's psnr filter.
    Returns None if calculation fails.
    """
    command = [
        "ffmpeg",
        "-i", original,
        "-i", compressed,
        "-lavfi", "psnr",
        "-f", "null", "-",
    ]
    result = subprocess.run(command, stderr=subprocess.PIPE,
                            stdout=subprocess.PIPE, text=True)
    match = re.search(r"average:(\d+\.?\d*)", result.stderr)
    if match:
        return float(match.group(1))
    return None


# ── SSIM ──────────────────────────────────────────────────────────────────────

def calculate_ssim(original: str, compressed: str, max_frames: int = 30) -> float | None:
    """
    Compute average SSIM by sampling up to `max_frames` evenly spaced frames.
    Returns a value in [0, 1]; closer to 1 = higher structural similarity.
    """
    cap_o = cv2.VideoCapture(original)
    cap_c = cv2.VideoCapture(compressed)

    total = int(cap_o.get(cv2.CAP_PROP_FRAME_COUNT))
    if total == 0:
        cap_o.release(); cap_c.release()
        return None

    step = max(1, total // max_frames)
    scores = []

    for idx in range(0, total, step):
        cap_o.set(cv2.CAP_PROP_POS_FRAMES, idx)
        cap_c.set(cv2.CAP_PROP_POS_FRAMES, idx)

        ret_o, frame_o = cap_o.read()
        ret_c, frame_c = cap_c.read()

        if not ret_o or not ret_c:
            break

        # Resize compressed to match original if dimensions differ
        if frame_o.shape != frame_c.shape:
            frame_c = cv2.resize(frame_c, (frame_o.shape[1], frame_o.shape[0]))

        gray_o = cv2.cvtColor(frame_o, cv2.COLOR_BGR2GRAY)
        gray_c = cv2.cvtColor(frame_c, cv2.COLOR_BGR2GRAY)

        score, _ = ssim_func(gray_o, gray_c, full=True)
        scores.append(score)

    cap_o.release()
    cap_c.release()

    return round(float(np.mean(scores)), 4) if scores else None


# ── Video info ────────────────────────────────────────────────────────────────

def get_video_info(video_path: str) -> dict:
    """Return resolution, FPS, duration, and frame count of a video."""
    cap = cv2.VideoCapture(video_path)
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps    = cap.get(cv2.CAP_PROP_FPS)
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()

    duration = frames / fps if fps > 0 else 0

    return {
        "width":    width,
        "height":   height,
        "fps":      round(fps, 2),
        "frames":   frames,
        "duration": round(duration, 2),
    }


# ── Full metrics bundle ───────────────────────────────────────────────────────

def compute_all_metrics(original: str, compressed: str) -> dict:
    """
    Compute all quality and compression metrics in one call.

    Returns
    -------
    dict with keys:
        original_size_mb, compressed_size_mb,
        compression_ratio, bitrate_kbps,
        psnr, ssim,
        original_info, compressed_info
    """
    orig_mb = get_file_size_mb(original)
    comp_mb = get_file_size_mb(compressed)

    return {
        "original_size_mb":   round(orig_mb, 3),
        "compressed_size_mb": round(comp_mb, 3),
        "compression_ratio":  round(orig_mb / comp_mb, 2) if comp_mb else 0,
        "bitrate_kbps":       round(get_bitrate(compressed), 2),
        "psnr":               calculate_psnr(original, compressed),
        "ssim":               calculate_ssim(original, compressed),
        "original_info":      get_video_info(original),
        "compressed_info":    get_video_info(compressed),
    }
