"""
encoder.py — FFmpeg x264 encoding wrapper
Supports preset/CRF tuning with encoding FPS measurement.
"""

import subprocess
import time
import re
import cv2


def get_total_frames(input_file: str) -> int:
    """Return total frame count of a video using OpenCV."""
    cap = cv2.VideoCapture(input_file)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    return total


def encode_video(
    input_file: str,
    output_file: str,
    preset: str = "fast",
    crf: int = 23,
) -> dict:
    """
    Encode a video with libx264.

    Parameters
    ----------
    input_file : str   Path to source video
    output_file : str  Path for encoded output
    preset : str       x264 preset (ultrafast / fast / medium / slow)
    crf : int          Constant Rate Factor — lower = better quality (18–35)

    Returns
    -------
    dict with keys:
        encoding_time (float) — wall-clock seconds
        encoding_fps  (float) — frames encoded per second
        total_frames  (int)   — total frame count
        preset        (str)
        crf           (int)
    """
    total_frames = get_total_frames(input_file)

    command = [
        "ffmpeg",
        "-y",
        "-i", input_file,
        "-c:v", "libx264",
        "-preset", preset,
        "-crf", str(crf),
        "-movflags", "+faststart",   # web-optimised: moov atom at front
        output_file,
    ]

    start = time.time()
    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    encoding_time = time.time() - start

    encoding_fps = total_frames / encoding_time if encoding_time > 0 else 0.0

    return {
        "encoding_time": round(encoding_time, 3),
        "encoding_fps":  round(encoding_fps, 2),
        "total_frames":  total_frames,
        "preset":        preset,
        "crf":           crf,
    }
