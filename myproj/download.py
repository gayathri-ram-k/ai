import os
import requests

# URL of the file to download
url = "http://localhost:8000/recorded/test.wav"

# Directory where the audio file will be saved
output_dir = "received_audio"
os.makedirs(output_dir, exist_ok=True)  # Create the directory if it doesn't exist

# Full path to save the downloaded file
filename = os.path.join(output_dir, "test.wav")

try:
    response = requests.get(url, stream=True)
    response.raise_for_status()  # Raise an error on bad status

    # Save the file
    with open(filename, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                file.write(chunk)

    print(f"File downloaded successfully: {filename}")

except requests.exceptions.RequestException as e:
    print(f"Error downloading file: {e}")
