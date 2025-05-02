import os
import subprocess
import librosa
import numpy as np
from scipy.spatial.distance import euclidean
from pydub import AudioSegment

# Convert input audio to WAV
def convert_to_wav(input_path):
    # Define output folder
    output_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
    os.makedirs(output_folder, exist_ok=True)

    output_path = os.path.join(output_folder, "output.wav")  # Default output .wav file path

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

    print(f"Converted {input_path} to WAV: {output_path}")
    return output_path

# Function to extract MFCC from an audio file
def extract_mfcc(file_path):
    y, sr = librosa.load(file_path, sr=16000)
    y = librosa.util.fix_length(y, size=16000*5)  # Fix the length to a specific size (5 seconds)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    mfcc_mean = np.mean(mfcc.T, axis=0)
    return mfcc_mean

# Function to compare received audio with database
def compare_to_database(received_file, database_dir, threshold=50):
    input_mfcc = extract_mfcc(received_file)

    min_distance = float("inf")
    matched_file = None

    for filename in os.listdir(database_dir):
        db_path = os.path.join(database_dir, filename)
        
        # Convert MP3 files in the database to WAV before processing
        if filename.endswith(".mp3"):
            db_path = convert_to_wav(db_path)

        if db_path.endswith(".wav"):
            db_mfcc = extract_mfcc(db_path)
            dist = euclidean(input_mfcc, db_mfcc)

            if dist < min_distance:
                min_distance = dist
                matched_file = filename

    if min_distance < threshold:
        disease = matched_file.replace(".wav", "").replace(".mp3", "")
        print(f"🎯 Disease detected: {disease} (distance: {min_distance:.2f})")
    else:
        print(f"⚠️ No match found. Closest distance: {min_distance:.2f}")

# Main function to run the comparison
def main():
    received_audio = r"C:/Users/gayat/OneDrive/Documents/final_year1/myproj/received_audio/output.mp3"
    database_folder = r"C:/Users/gayat/OneDrive/Documents/final_year1/myproj/media/audio"
    
    # Convert the received audio (if it's not already in WAV format)
    received_audio_wav = convert_to_wav(received_audio)
    
    # Run the comparison against the database
    compare_to_database(received_audio_wav, database_folder)

# Execute the program
if __name__ == "__main__":
    main()
