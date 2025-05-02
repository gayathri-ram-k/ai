from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import os
import librosa
import numpy as np
from datasketch import MinHash, MinHashLSH
from .models import DiseaseDetection


import subprocess, os

def user_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            print(f"User {username} logged in successfully!")
            return redirect('home')  # Redirect directly to diagnosis after login
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')
    return render(request, 'login.html')

def user_signup(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists.")
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password1)
                user.save()
                messages.success(request, "Account created successfully! Please login.")
                return redirect('login')
        else:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')

    return render(request, 'signup.html')



def extract_features(audio_path, n_mfcc=13, bins=64):
    y, sr = librosa.load(audio_path, sr=16000)
    y = librosa.util.fix_length(y, size=16000 * 5)  # Pad/trim to 5s
    y = y / np.max(np.abs(y))  # Normalize

    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
    delta = librosa.feature.delta(mfcc)
    delta2 = librosa.feature.delta(mfcc, order=2)
    
    combined = np.vstack((mfcc, delta, delta2))
    mean_features = np.mean(combined.T, axis=0)

    # Quantize values into bins (turn floats into integers)
    quantized = np.digitize(mean_features, np.linspace(np.min(mean_features), np.max(mean_features), bins))

    mh = MinHash(num_perm=128)
    for val in quantized:
        mh.update(str(val).encode('utf-8'))

    return mh


def build_lsh_index(threshold=0.6):
    """Create an LSH index for the database."""
    lsh = MinHashLSH(threshold=0.5, num_perm=128)

    # Fetch audio files from the database (DiseaseDetection model)
    for disease in DiseaseDetection.objects.all():
        file_path = disease.audio.path  # Get the file path of the audio in the database
        mh = extract_features(file_path)
        lsh.insert(str(disease.id), mh)  # Insert disease ID (key) and MinHash (value)

    return lsh

def query_received_audio(received_folder, lsh):
    """Check received files against the LSH index."""
    results = {}
    for file in os.listdir(received_folder):
        if file.endswith(('.wav', '.mp3', '.ogg', '.flac')):
            file_path = os.path.join(received_folder, file)
            mh = extract_features(file_path)
            matches = lsh.query(mh)  # Returns list of matching disease IDs
            results[file] = matches
    return results

def home(request):
    received_folder = "C:/Users/gayat/Desktop/pi_audio"
 # folder containing received audio

    # Step 1: Preprocess database into LSH index
    lsh = build_lsh_index(threshold=0.6)

    # Step 2: Query the received audio files
    similarity_results = query_received_audio(received_folder, lsh)

    # Step 3: Initialize diagnosis list
    diagnosis = []

    # Step 4: For each received file, check if there's a match in the database
    for received_file, matches in similarity_results.items():
        if matches:
            match_id = matches[0] # Query the database to get disease name and remarks using the matched IDs
            # for match_id in matches:
            try:
                    disease = DiseaseDetection.objects.get(id=match_id)
                    diagnosis.append({
                        'file': received_file,
                        'disease_name': disease.disease_name,
                        'remarks': disease.remarks
                    })
            except DiseaseDetection.DoesNotExist:
                    diagnosis.append({
                        'file': received_file,
                        'disease_name': 'No match',
                        'remarks': 'No remarks available'
                    })
        else:
            diagnosis.append({
                'file': received_file,
                'disease_name': 'normal',
                'remarks': 'normal patient'

            })
        print(diagnosis)
            
    # Render results in a template
    return render(request, 'diagnosis.html', {'diagnosis': diagnosis})


def run_diagnosis(request):
    print("=== Starting Diagnosis ===")

    simulate_pi = False  # Set to True to skip SSH and simulate Pi recording

    if not simulate_pi:
        # 1. Trigger Raspberry Pi to record and send file
        pi_ip = "192.168.72.245"  # Replace with actual IP
        pi_user = "gayathri"
        remote_script = "/home/gayathri/Desktop/record_audio.py"

        try:
            print(f"Connecting to Raspberry Pi at {pi_ip}...")
            subprocess.run(
                ["ssh", f"{pi_user}@{pi_ip}", f"python3 {remote_script}"],
                check=True
            )
            print("✅ Recording and transfer complete.")
        except subprocess.CalledProcessError as e:
            print("❌ Remote recording failed:", e)
            return render(request, 'diagnosis.html', {
                'diagnosis': [],
                'error': 'Recording failed! Please check Raspberry Pi connection.'
            })
    else:
        print("🧪 Simulating Raspberry Pi recording step...")

    # 2. Run comparison logic
    print("🔍 Running audio similarity check...")
    return home(request)  # Your diagnosis logic is in the home() view



def user_logout(request):
    logout(request)
    return redirect('login')

