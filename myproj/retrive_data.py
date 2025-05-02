import paramiko
import os

# Raspberry Pi SSH credentials
pi_ip = "192.168.45.245"  # Replace with your Pi's IP address
pi_username = "gayathri"
pi_password = "gayathri"  # Replace with your actual password

# File paths
remote_path = "/home/gayathri/Desktop/rd/murmur_heart_disease.mp3"  # Path on Raspberry Pi
local_path = r"C:/Users/gayat/OneDrive/Documents/final_year1/myproj/received_audio/murmur_heart_disease.mp3"

# Create SSH client
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("Connecting to Raspberry Pi...")
    ssh.connect(pi_ip, username=pi_username, password=pi_password)

    # Open SFTP session and transfer file
    with ssh.open_sftp() as sftp:
        print(f"Downloading {remote_path} to {local_path}...")
        sftp.get(remote_path, local_path)
        print("Download complete!")

except Exception as e:
    print(f"Error: {e}")

finally:
    ssh.close()
