import os
import subprocess

input_path = "song.mp4"
output_folder = os.path.join(os.path.dirname(os.path.abspath(_file_)), 'output')
os.makedirs(output_folder, exist_ok=True)

output_path = os.path.join(output_folder, "output.wav")  # Changed to .wav

try:
    # Try automatic detection (works for common formats)
    subprocess.run([
        "ffmpeg", "-y", "-i", input_path, output_path
    ], check=True)
except subprocess.CalledProcessError:
    # Fallback for raw PCM: 16-bit signed little-endian, mono, 44100 Hz
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "s16le",            # sample format
        "-ar", "44100",           # sample rate
        "-ac", "1",               # mono
        "-i", input_path,
        output_path
    ], check=True)

print("Converted to WAV:", output_path)