import os
import subprocess
import re

def get_file_size(path):
    return os.path.getsize(path) / (1024 * 1024)

def compression_ratio(original, compressed):

    original_size = get_file_size(original)
    compressed_size = get_file_size(compressed)

    return original_size / compressed_size

def get_bitrate(video_path):

    command = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "format=bit_rate",
        "-of", "default=noprint_wrappers=1:nokey=1",
        video_path
    ]

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    bitrate = int(result.stdout.strip())

    return bitrate / 1000
def calculate_psnr(original, compressed):

    command = [
        "ffmpeg",
        "-i", original,
        "-i", compressed,
        "-lavfi", "psnr",
        "-f", "null",
        "-"
    ]

    result = subprocess.run(
        command,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True
    )

    output = result.stderr

    match = re.search(r'average:(\d+\.\d+)', output)

    if match:
        return float(match.group(1))

    return None
