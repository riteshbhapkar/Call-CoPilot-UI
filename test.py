# import os
# import json
# import threading
# import time
# import numpy as np
# import sounddevice as sd
# import websocket
# from datetime import datetime

# # ==== Configuration ====
# # Using your actual API key
# DEEPGRAM_API_KEY = "86e4253557d5243bde10eb96462b7ad4a41138d3"

# # Alternative simple configuration
# DEEPGRAM_WS_URL = "wss://api.deepgram.com/v1/listen?encoding=linear16&sample_rate=16000"

# # Audio settings
# SAMPLE_RATE = 16000
# CHANNELS = 1
# BLOCKSIZE = 2048
# DEBUG = True

# # Global variables
# ws = None
# last_audio_sent = 0
# is_receiving_data = False
# selected_device = None  # Store the selected device

# def on_message(ws, message):
#     """Process incoming messages from Deepgram"""
#     global is_receiving_data
#     is_receiving_data = True
    
#     try:
#         if DEBUG:
#             print(f"Received from Deepgram: {message[:100]}...")
            
#         data = json.loads(message)
        
#         # Check for transcript data
#         if "type" in data:
#             if data["type"] == "Results":
#                 # Extract transcript from response
#                 transcript = None
                
#                 # Try the standard path
#                 if "channel" in data and "alternatives" in data["channel"]:
#                     alternatives = data["channel"]["alternatives"]
#                     if alternatives and len(alternatives) > 0:
#                         transcript = alternatives[0].get("transcript", "").strip()
                
#                 # If standard path failed, try alternatives
#                 if not transcript:
#                     # Try different paths
#                     if "transcript" in data:
#                         transcript = data["transcript"]
                
#                 # Print the transcript if found
#                 if transcript:
#                     timestamp = datetime.now().strftime("%H:%M:%S")
#                     print(f"\n[{timestamp}] Transcript: {transcript}")
#                     print("-" * 50)
#             else:
#                 # Non-transcript message (like UtteranceEnd)
#                 if DEBUG:
#                     print(f"Message type: {data['type']}")
#     except Exception as e:
#         print(f"Error processing message: {e}")

# def on_error(ws, error):
#     """Handle WebSocket errors"""
#     print(f"WebSocket error: {error}")
#     if "401" in str(error):
#         print("\n⚠️ AUTHENTICATION ERROR: Your API key is invalid or expired.")
#         print("Get a new key at: https://console.deepgram.com")
#     elif "400" in str(error):
#         print("\n⚠️ BAD REQUEST: There's an issue with the URL parameters.")
#         print("Valid parameters are: encoding, sample_rate, model, language, tier, version")
#         print(f"Current URL: {DEEPGRAM_WS_URL}")
#     elif "404" in str(error):
#         print("\n⚠️ NOT FOUND: The API endpoint couldn't be found.")
#         print("Check if the base URL is correct: wss://api.deepgram.com/v1/listen")

# def on_close(ws, close_status_code, close_msg):
#     print(f"WebSocket closed: {close_status_code} - {close_msg}")

# def on_open(ws):
#     print("✅ Connected to Deepgram!")
#     print("Ready to transcribe. Please speak...")
    
#     # Updated configuration for Hindi/Hinglish based on latest docs
#     config = {
#         "interim_results": True,
#         "model": "general",  # Use 'general' instead of 'nova-2' for better Hindi support
#         "language": "",    # Standard code for Hindi
#         "smart_format": True,
#         "punctuate": True,
#         "encoding": "linear16",
#         "sample_rate": 16000
#     }
#     ws.send(json.dumps(config))

# def audio_callback(indata, frames, time_info, status):
#     """Send audio data to Deepgram"""
#     global last_audio_sent
    
#     if status:
#         print(f"Audio status: {status}")
    
#     try:
#         # Calculate audio level
#         audio_rms = np.sqrt(np.mean(indata**2))
        
#         # Convert to int16
#         audio_data = (indata * 32767).astype(np.int16).tobytes()
        
#         # Send to Deepgram if connected
#         if ws and ws.sock and ws.sock.connected:
#             ws.send(audio_data, opcode=websocket.ABNF.OPCODE_BINARY)
#             last_audio_sent = time.time()
            
#             # Occasionally show audio levels
#             if time.time() % 3 < 0.1:
#                 print(f"Audio level: {audio_rms:.6f}")
#     except Exception as e:
#         print(f"Error sending audio: {e}")

# def select_audio_device():
#     """Let the user choose an audio input device"""
#     print("\n=== Available Audio Devices ===")
#     devices = sd.query_devices()
#     for i, device in enumerate(devices):
#         print(f"[{i}] {device['name']} (inputs: {device['max_input_channels']}, outputs: {device['max_output_channels']})")
#     print("===============================\n")
    
#     print("Select an audio input device to use for transcription.")
#     device_idx = input("Enter device number (or press Enter for default): ").strip()
    
#     # Wait for user input before proceeding
#     if device_idx:
#         try:
#             idx = int(device_idx)
#             if 0 <= idx < len(devices):
#                 if devices[idx]['max_input_channels'] > 0:
#                     return idx
#                 else:
#                     print("Selected device has no input channels. Using default.")
#                     return None
#             else:
#                 print("Invalid device number. Using default.")
#                 return None
#         except ValueError:
#             print("Invalid input. Using default.")
#             return None
#     return None

# def start_audio_stream():
#     """Start capturing audio after device selection"""
#     # Get user input for device selection
#     global selected_device
#     selected_device = select_audio_device()
    
#     print("\nStarting audio stream...")
    
#     try:
#         with sd.InputStream(device=selected_device,
#                             samplerate=SAMPLE_RATE, 
#                             blocksize=BLOCKSIZE,
#                             channels=CHANNELS, 
#                             dtype='float32', 
#                             callback=audio_callback):
#             print(f"Audio stream started with device {selected_device}.")
#             print("Please speak into your microphone...")
#             print("Press Ctrl+C to stop.")
            
#             # Keep checking for data
#             while True:
#                 time.sleep(0.1)
#     except Exception as e:
#         print(f"Audio stream error: {e}")

# def start_deepgram_ws():
#     """Connect to Deepgram WebSocket API"""
#     global ws
#     headers = {"Authorization": f"Token {DEEPGRAM_API_KEY}"}
    
#     print(f"Connecting to Deepgram with URL: {DEEPGRAM_WS_URL}")
    
#     ws = websocket.WebSocketApp(DEEPGRAM_WS_URL,
#                               header=headers,
#                               on_message=on_message,
#                               on_error=on_error,
#                               on_close=on_close,
#                               on_open=on_open)
#     ws.run_forever()

# if __name__ == "__main__":
#     print("=" * 60)
#     print("Real-time Speech Transcription using Deepgram")
#     print("=" * 60)
    
#     # First, start Deepgram connection
#     ws_thread = threading.Thread(target=start_deepgram_ws, daemon=True)
#     ws_thread.start()
    
#     # Wait for connection to establish
#     time.sleep(2)
    
#     # Now start the audio stream (which will wait for device selection)
#     try:
#         start_audio_stream()
#     except KeyboardInterrupt:
#         print("\nStopping transcription...")
#         if ws:
#             ws.close()

import os
import json
import threading
import time
import numpy as np
import sounddevice as sd
import websocket
from datetime import datetime

# ==== Configuration ====
# Using your provided AssemblyAI API key:
ASSEMBLYAI_API_KEY = "e65938ce3a84406290f3afa4e8070180"

# AssemblyAI realtime WebSocket endpoint (sample_rate parameter required)
ASSEMBLYAI_WS_URL = "wss://api.assemblyai.com/v2/realtime/ws?sample_rate=16000"

# Audio settings: (for this example, we capture mono audio)
SAMPLE_RATE = 16000   # in Hz
CHANNELS = 1          # mono audio (adjust if your Aggregate Device outputs multichannel)
BLOCKSIZE = 2048      # number of frames per chunk
DEBUG = True

# Global variables
ws = None
last_audio_sent = 0
is_receiving_data = False
selected_device = None  # To store the selected audio input device

# Dictionary for mapping speaker labels to names.
# For a simple heuristic, the first speaker encountered will be "Agent" and the second "Customer".
speaker_mapping = {}

def on_message(ws, message):
    """
    Process incoming messages from AssemblyAI.
    AssemblyAI returns JSON messages that include a "text" field (the transcript)
    and optionally a "words" array with word-level details including speaker labels.
    """
    global is_receiving_data, speaker_mapping
    is_receiving_data = True
    try:
        if DEBUG:
            print(f"Received message (first 100 chars): {message[:100]}...")
        data = json.loads(message)
        
        if "text" in data:
            transcript_text = data["text"].strip()
            words = data.get("words", [])
            speaker_transcripts = {}
            for word in words:
                spk = word.get("speaker")
                if spk is not None:
                    # Map numeric speaker label to role using our heuristic.
                    if spk not in speaker_mapping:
                        if len(speaker_mapping) == 0:
                            speaker_mapping[spk] = "Agent"
                        elif len(speaker_mapping) == 1:
                            speaker_mapping[spk] = "Customer"
                        else:
                            speaker_mapping[spk] = f"Speaker {spk}"
                    speaker_name = speaker_mapping[spk]
                    word_text = word.get("punctuated_word", word.get("word", ""))
                    if speaker_name not in speaker_transcripts:
                        speaker_transcripts[speaker_name] = word_text
                    else:
                        speaker_transcripts[speaker_name] += " " + word_text
            # Print the transcript with timestamp and speaker labels.
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"\n[{timestamp}] Transcription Update:")
            if speaker_transcripts:
                for speaker, t in speaker_transcripts.items():
                    print(f"{speaker}: {t}")
            else:
                print(f"Transcript: {transcript_text}")
            print("-" * 50)
        else:
            if DEBUG:
                print(f"Non-transcription message received: {data}")
    except Exception as e:
        print(f"Error processing message: {e}")

def on_error(ws, error):
    """Handle WebSocket errors."""
    print(f"WebSocket error: {error}")

def on_close(ws, close_status_code, close_msg):
    """Handle WebSocket closure."""
    print(f"WebSocket closed: {close_status_code} - {close_msg}")

def on_open(ws):
    """Send configuration message to AssemblyAI when WebSocket is open."""
    print("✅ Connected to AssemblyAI!")
    # Send configuration message with speaker_labels enabled.
    config = {
        "config": {
            "audio_encoding": "linear16",
            "sample_rate": SAMPLE_RATE,
            "speaker_labels": True,
            "format_text": True,
            "language": "en-US"  # Change if needed (AssemblyAI supports many languages)
        }
    }
    ws.send(json.dumps(config))
    print("Configuration sent to AssemblyAI.")

def audio_callback(indata, frames, time_info, status):
    """Send captured audio data to AssemblyAI over the WebSocket."""
    global last_audio_sent
    if status:
        print(f"Audio status: {status}")
    try:
        # Convert the float32 audio data (range [-1,1]) to int16 PCM bytes.
        audio_data = (indata * 32767).astype(np.int16).tobytes()
        if ws and ws.sock and ws.sock.connected:
            ws.send(audio_data, opcode=websocket.ABNF.OPCODE_BINARY)
            last_audio_sent = time.time()
            # Optionally, print audio level every few seconds.
            if time.time() % 3 < 0.1:
                rms = np.sqrt(np.mean(indata**2))
                print(f"Audio level: {rms:.6f}")
    except Exception as e:
        print(f"Error sending audio: {e}")

def select_audio_device():
    """Prompt the user to select an audio input device."""
    print("\n=== Available Audio Devices ===")
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        print(f"[{i}] {device['name']} (inputs: {device['max_input_channels']}, outputs: {device['max_output_channels']})")
    print("===============================\n")
    
    device_idx = input("Enter device number (or press Enter for default): ").strip()
    if device_idx:
        try:
            idx = int(device_idx)
            if 0 <= idx < len(devices):
                if devices[idx]['max_input_channels'] > 0:
                    return idx
                else:
                    print("Selected device has no input channels. Using default.")
                    return None
            else:
                print("Invalid device number. Using default.")
                return None
        except ValueError:
            print("Invalid input. Using default.")
            return None
    return None

def start_audio_stream():
    """Start capturing audio from the selected input device."""
    global selected_device
    selected_device = select_audio_device()
    print("\nStarting audio stream...")
    try:
        with sd.InputStream(device=selected_device,
                            samplerate=SAMPLE_RATE, 
                            blocksize=BLOCKSIZE,
                            channels=CHANNELS, 
                            dtype='float32', 
                            callback=audio_callback):
            print(f"Audio stream started using device {selected_device}.")
            print("Speak now... Press Ctrl+C to stop.")
            while True:
                time.sleep(0.1)
    except Exception as e:
        print(f"Audio stream error: {e}")

def start_assemblyai_ws():
    """Connect to AssemblyAI's realtime WebSocket endpoint."""
    global ws
    headers = {"authorization": ASSEMBLYAI_API_KEY}
    print(f"Connecting to AssemblyAI at: {ASSEMBLYAI_WS_URL}")
    ws = websocket.WebSocketApp(ASSEMBLYAI_WS_URL,
                                header=headers,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close,
                                on_open=on_open)
    ws.run_forever()

if __name__ == "__main__":
    print("=" * 60)
    print("Real-time Speech Transcription using AssemblyAI")
    print("=" * 60)
    
    # Start the AssemblyAI WebSocket connection in a separate thread.
    ws_thread = threading.Thread(target=start_assemblyai_ws, daemon=True)
    ws_thread.start()
    
    # Give the connection a moment to establish.
    time.sleep(2)
    
    # Start capturing audio.
    try:
        start_audio_stream()
    except KeyboardInterrupt:
        print("\nStopping transcription...")
        if ws:
            ws.close()
