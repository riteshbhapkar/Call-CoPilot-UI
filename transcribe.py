import sounddevice as sd
import numpy as np
# import whisper  # Comment out or remove this line
import queue
import threading
import time
import sys
import os

# Add this import check and correction
try:
    import whisper
    # Verify it's the right whisper package
    whisper.load_model
except (ImportError, AttributeError):
    print("Detecting incorrect whisper package. Installing the correct OpenAI whisper package...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-y", "whisper"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openai-whisper"])
    print("OpenAI Whisper installed. Importing the correct package...")
    import whisper

# ------------------------------
# Configuration & Global Variables
# ------------------------------

# Sampling rate for both streams
SAMPLERATE = 16000  
# Duration of each audio chunk (in seconds) - increased for better context
CHUNK_DURATION = 2.0  
# Number of channels (mono for transcription)
CHANNELS = 1  
# Lower silence threshold to capture more audio
SILENCE_THRESHOLD = 0.005

# ------------------------------
# Helper Functions
# ------------------------------
def list_audio_devices():
    """List all available audio devices to help with device selection."""
    print("\n=== Available Audio Devices ===")
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        print(f"[{i}] {device['name']} (inputs: {device['max_input_channels']}, outputs: {device['max_output_channels']})")
    print("===============================\n")
    return devices

# ------------------------------
# Device Selection
# ------------------------------
def select_devices():
    """Help the user select the correct audio devices for agent and customer."""
    devices = list_audio_devices()
    
    print("For the agent microphone, select the device with input channels (like your built-in mic).")
    agent_idx = input("Enter agent microphone device number (or press Enter for default): ")
    
    print("\nFor the customer audio, select the virtual audio device capturing system audio (like BlackHole).")
    print("If you haven't set up a virtual audio device, see the setup instructions in the README.")
    customer_idx = input("Enter customer audio device number (or press Enter for default): ")
    
    return (int(agent_idx) if agent_idx.strip() else None, 
            int(customer_idx) if customer_idx.strip() else None)

# ------------------------------
# Load the Whisper Model
# ------------------------------
def load_whisper_model(model_name="medium"):
    """Load the Whisper model with error handling."""
    print(f"Loading Whisper model: {model_name}...")
    try:
        model = whisper.load_model(model_name)
        print("Model loaded successfully!")
        return model
    except Exception as e:
        print(f"Error loading Whisper model: {e}")
        print("Make sure you have installed OpenAI Whisper correctly.")
        sys.exit(1)

# ------------------------------
# Audio Queues for Streaming
# ------------------------------
agent_audio_queue = queue.Queue()
customer_audio_queue = queue.Queue()

# ------------------------------
# Audio Callback Function
# ------------------------------
def audio_callback(indata, frames, time_info, status, q):
    """
    This callback receives a chunk of audio data from the stream and places a copy into the provided queue.
    """
    if status:
        print(f"Audio stream status: {status}")
    q.put(indata.copy())

# ------------------------------
# Audio Recording Thread Function
# ------------------------------
def record_audio(device_index, audio_q, source_name):
    """
    Opens an input stream for the given device and continuously records audio in chunks.
    """
    try:
        with sd.InputStream(device=device_index,
                            channels=CHANNELS,
                            samplerate=SAMPLERATE,
                            blocksize=int(SAMPLERATE * CHUNK_DURATION),
                            callback=lambda indata, frames, time_info, status: audio_callback(indata, frames, time_info, status, audio_q)):
            print(f"Successfully started recording from {source_name} (device {device_index})")
            while True:
                time.sleep(CHUNK_DURATION)  # Keep the thread alive; audio is processed via the callback
    except Exception as e:
        print(f"Error recording from {source_name} (device {device_index}): {e}")
        print("Check if the device exists and has input channels.")
        sys.exit(1)

# ------------------------------
# Transcription Worker Function
# ------------------------------
def transcribe_worker(audio_q, speaker_label, model):
    """
    Continuously takes audio chunks from the queue, processes them through Whisper,
    and prints the transcribed text along with the speaker label.
    """
    print(f"Starting transcription for {speaker_label}...")
    
    while True:
        try:
            # Retrieve an audio chunk from the queue
            audio_chunk = audio_q.get(timeout=CHUNK_DURATION * 2)
        except queue.Empty:
            continue
        
        # Ensure audio is in the right shape: flatten to mono if needed
        if audio_chunk.ndim > 1:
            audio_chunk = np.mean(audio_chunk, axis=1)
        
        # Normalize and ensure correct dtype (float32)
        audio_chunk = np.array(audio_chunk, dtype=np.float32)

        # Lower threshold for silence detection
        if np.abs(audio_chunk).mean() < SILENCE_THRESHOLD:
            continue

        # Whisper expects audio as a 1D numpy array at the expected sample rate.
        try:
            # Let Whisper auto-detect language instead of forcing Hindi
            result = model.transcribe(audio_chunk)  # Removed language="hi"
            text = result.get("text", "").strip()
            if text:  # Only print if there's actual transcribed text
                timestamp = time.strftime("%H:%M:%S")
                print(f"[{timestamp}] {speaker_label}: {text}")
        except Exception as e:
            print(f"[Error during {speaker_label} transcription: {e}]")

# ------------------------------
# Main Function to Launch Threads
# ------------------------------
def main():
    print("=" * 50)
    print("Real-time Call Transcription with Speaker Diarization")
    print("=" * 50)
    print("\nThis script will transcribe both agent (microphone) and customer (speaker) audio.")
    print("For Mac users: To capture system audio, you need a virtual audio device like BlackHole.")
    print("Setup instructions: https://github.com/ExistentialAudio/BlackHole\n")
    
    # Allow the user to select devices or use defaults
    agent_device_index, customer_device_index = select_devices()
    
    # Load the Whisper model
    model = load_whisper_model("medium")
    
    # Start audio recording threads
    agent_thread = threading.Thread(target=record_audio, 
                                   args=(agent_device_index, agent_audio_queue, "Agent Microphone"), 
                                   daemon=True)
    customer_thread = threading.Thread(target=record_audio, 
                                      args=(customer_device_index, customer_audio_queue, "Customer Audio"), 
                                      daemon=True)
    
    # Start transcription threads for each audio stream
    agent_transcription_thread = threading.Thread(target=transcribe_worker, 
                                                args=(agent_audio_queue, "Agent", model), 
                                                daemon=True)
    customer_transcription_thread = threading.Thread(target=transcribe_worker, 
                                                   args=(customer_audio_queue, "Customer", model), 
                                                   daemon=True)
    
    # Start all threads
    agent_thread.start()
    # customer_thread.start()
    # customer_transcription_thread.start()
    agent_transcription_thread.start()
    # customer_transcription_thread.start()
    
    print("\nStreaming transcription started. Press Ctrl+C to stop.")
    
    try:
        # Keep the main thread alive while daemon threads run in the background.
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopping transcription...")

if __name__ == "__main__":
    main()
