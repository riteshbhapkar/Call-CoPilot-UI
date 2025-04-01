# # 

# import queue
# import sys
# import time
# import threading
# import sounddevice as sd
# import numpy as np
# from google.cloud import speech
# from datetime import datetime
# import os

# # Set the Google Cloud credentials environment variable (adjust path as needed)
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/apple/Downloads/dark-pipe-455309-q0-db032846253e.json"

# # ==== Configuration ====
# SAMPLE_RATE = 16000        # in Hz
# BLOCKSIZE = 2048           # frames per chunk
# CHANNELS_PER_DEVICE = 1    # capture mono from each device

# # Queues to hold audio blocks from each device.
# mic_q = queue.Queue()
# bh_q = queue.Queue()

# def mic_callback(indata, frames, time_info, status):
#     """Callback for microphone stream (Agent)."""
#     if status:
#         print("Mic status:", status, file=sys.stderr)
#     mic_q.put(indata.copy())

# def bh_callback(indata, frames, time_info, status):
#     """Callback for BlackHole stream (Customer)."""
#     if status:
#         print("BlackHole status:", status, file=sys.stderr)
#     bh_q.put(indata.copy())

# def get_stereo_block():
#     """
#     Retrieve one block from each queue and combine them into a stereo block.
#     Returns a numpy array of shape (n_frames, 2) with int16 data.
#     Also prints RMS values for debugging.
#     """
#     mic_block = mic_q.get()    # shape (frames, 1)
#     bh_block = bh_q.get()      # shape (frames, 1)
#     n_frames = min(mic_block.shape[0], bh_block.shape[0])
#     mic_block = mic_block[:n_frames, 0]
#     bh_block = bh_block[:n_frames, 0]
#     # Calculate RMS levels for debugging:
#     rms_mic = np.sqrt(np.mean(mic_block.astype(np.float32)**2))
#     rms_bh = np.sqrt(np.mean(bh_block.astype(np.float32)**2))
#     print(f"DEBUG: Mic RMS: {rms_mic:.4f}, BlackHole RMS: {rms_bh:.4f}")
#     stereo_block = np.column_stack((mic_block, bh_block))
#     return stereo_block

# def audio_generator():
#     """Generator that yields interleaved stereo audio (2 channels) as bytes."""
#     while True:
#         stereo_block = get_stereo_block()  # shape (n_frames, 2)
#         yield stereo_block.astype(np.int16).tobytes()

# def listen_print_loop(responses):
#     """
#     Processes streaming responses from Google Cloud Speech-to-Text.
#     Expects separate recognition per channel.
#     Prints separate transcripts for each channel:
#       Channel 0 -> Agent
#       Channel 1 -> Customer
#     """
#     for response in responses:
#         if not response.results:
#             continue
#         result = response.results[0]
#         if not result.alternatives:
#             continue

#         # If separate recognition is enabled, the API returns a "channels" field.
#         if hasattr(result, "channels") and result.channels:
#             for ch_index, channel_result in enumerate(result.channels):
#                 label = "Agent" if ch_index == 0 else "Customer"
#                 transcript = (channel_result.alternatives[0].transcript 
#                               if channel_result.alternatives else "")
#                 print(f"\n[{datetime.now().strftime('%H:%M:%S')}] {label} Transcript:")
#                 print(transcript)
#             print("-" * 50)
#         else:
#             transcript = result.alternatives[0].transcript
#             print(f"[{datetime.now().strftime('%H:%M:%S')}] {transcript}")
#         sys.stdout.flush()

# def main():
#     # List available audio devices.
#     devices = sd.query_devices()
#     print("\n=== Available Audio Devices ===")
#     for i, device in enumerate(devices):
#         print(f"[{i}] {device['name']} (inputs: {device['max_input_channels']})")
#     print("===============================\n")
    
#     mic_index = int(input("Enter device index for your microphone (Agent): "))
#     bh_index = int(input("Enter device index for your BlackHole device (Customer): "))
    
#     # Open separate input streams for the mic and BlackHole.
#     mic_stream = sd.InputStream(device=mic_index, samplerate=SAMPLE_RATE,
#                                 blocksize=BLOCKSIZE, channels=CHANNELS_PER_DEVICE,
#                                 dtype='int16', callback=mic_callback)
#     bh_stream = sd.InputStream(device=bh_index, samplerate=SAMPLE_RATE,
#                                blocksize=BLOCKSIZE, channels=CHANNELS_PER_DEVICE,
#                                dtype='int16', callback=bh_callback)
    
#     mic_stream.start()
#     bh_stream.start()
#     print("Both audio streams started. Ensure that your system audio (YouTube) is routed to BlackHole.")
    
#     # Set up Google Cloud Speech-to-Text with separate recognition per channel.
#     client = speech.SpeechClient()
    
#     config = speech.RecognitionConfig(
#         encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
#         sample_rate_hertz=SAMPLE_RATE,
#         language_code="en-IN",  # For Hinglish; alternatively try "hi-IN" for predominantly Hindi.
#         audio_channel_count=2,  # Two channels: mic and BlackHole.
#         enable_automatic_punctuation=True,
#         enable_separate_recognition_per_channel=True  # Force independent recognition per channel.
#     )
    
#     streaming_config = speech.StreamingRecognitionConfig(
#         config=config,
#         interim_results=True,
#     )
    
#     print("Connecting to Google Cloud Speech-to-Text...")
#     requests = (speech.StreamingRecognizeRequest(audio_content=content)
#                 for content in audio_generator())
    
#     responses = client.streaming_recognize(config=streaming_config, requests=requests)
#     try:
#         listen_print_loop(responses)
#     except KeyboardInterrupt:
#         print("\nTranscription stopped by user.")
#     finally:
#         mic_stream.stop()
#         bh_stream.stop()

# if __name__ == "__main__":
#     main()

import queue
import sys
import time
import threading
import sounddevice as sd
import numpy as np
from google.cloud import speech
from datetime import datetime
import os

# Set the Google Cloud credentials environment variable (adjust path as needed)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/apple/Downloads/dark-pipe-455309-q0-db032846253e.json"

# ==== Configuration ====
SAMPLE_RATE = 16000        # in Hz
BLOCKSIZE = 2048           # frames per chunk
CHANNELS = 1               # mono audio for each stream

# Queues for separate audio blocks from each device.
agent_q = queue.Queue()
customer_q = queue.Queue()

def agent_callback(indata, frames, time_info, status):
    """Callback for the microphone stream (Agent)."""
    if status:
        print("Agent mic status:", status, file=sys.stderr)
    agent_q.put(indata.copy())

def customer_callback(indata, frames, time_info, status):
    """Callback for the BlackHole stream (Customer)."""
    if status:
        print("Customer BlackHole status:", status, file=sys.stderr)
    customer_q.put(indata.copy())

def agent_audio_generator():
    """Generator that yields audio chunks from the agent (mic) as bytes."""
    while True:
        block = agent_q.get()  # shape (frames, 1)
        yield block.astype(np.int16).tobytes()

def customer_audio_generator():
    """Generator that yields audio chunks from the customer (BlackHole) as bytes."""
    while True:
        block = customer_q.get()  # shape (frames, 1)
        yield block.astype(np.int16).tobytes()

def listen_print_loop(label, responses):
    """
    Processes streaming responses from Google Cloud Speech-to-Text.
    Simply prints out the transcript for this session with the given label.
    """
    for response in responses:
        if not response.results:
            continue
        result = response.results[0]
        if not result.alternatives:
            continue
        transcript = result.alternatives[0].transcript
        
        # Only print if there's actual content
        if transcript.strip():
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] {label} Transcript Update:")
            print(transcript)
            print("-" * 50)
            sys.stdout.flush()

def stream_recognition(label, audio_gen):
    """
    Streams audio from a given generator to Google Cloud Speech-to-Text.
    Each session is independent. The 'label' parameter is used to tag the output.
    """
    client = speech.SpeechClient()
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=SAMPLE_RATE,
        language_code="hi-IN",  # Default to English
        alternative_language_codes=["en-US"],  # Support Hindi as alternative for Hinglish
        enable_automatic_punctuation=True,
        model="latest_long"  # Use latest model optimized for longer audio
    )
    streaming_config = speech.StreamingRecognitionConfig(
        config=config,
        interim_results=True,
    )
    
    try:
        requests = (speech.StreamingRecognizeRequest(audio_content=content) 
                    for content in audio_gen)
        responses = client.streaming_recognize(config=streaming_config, requests=requests)
        listen_print_loop(label, responses)
    except Exception as e:
        print(f"Error in {label} recognition stream: {e}")

def find_default_devices(devices):
    """Find reasonable default devices based on their names."""
    default_mic = None
    default_blackhole = None
    
    for i, device in enumerate(devices):
        name = device['name'].lower()
        inputs = device['max_input_channels']
        
        # Skip devices with no input channels
        if inputs <= 0:
            continue
            
        # Check for typical microphone names
        if "microphone" in name or "mic" in name:
            default_mic = i
            
        # Check for BlackHole or other virtual audio devices
        if "blackhole" in name or "loopback" in name:
            default_blackhole = i
    
    # If we couldn't find specific devices, use the first available input devices
    if default_mic is None:
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                default_mic = i
                break
                
    if default_blackhole is None and default_mic is not None:
        # Use the next available input device after the mic
        for i, device in enumerate(devices):
            if i != default_mic and device['max_input_channels'] > 0:
                default_blackhole = i
                break
    
    return default_mic, default_blackhole

def main():
    # List available audio devices.
    devices = sd.query_devices()
    print("\n=== Available Audio Devices ===")
    for i, device in enumerate(devices):
        print(f"[{i}] {device['name']} (inputs: {device['max_input_channels']})")
    print("===============================\n")
    
    # Find reasonable defaults
    default_mic, default_bh = find_default_devices(devices)
    
    # Handle input for agent mic
    try:
        mic_input = input(f"Enter device index for your microphone (Agent){' [default: ' + str(default_mic) + ']' if default_mic is not None else ''}: ")
        agent_index = int(mic_input) if mic_input.strip() else default_mic
        if agent_index is None:
            raise ValueError("No suitable microphone device found")
    except ValueError as e:
        if "No suitable" in str(e):
            print(f"Error: {e}")
            return
        print(f"Invalid input. Using default microphone at index {default_mic}.")
        agent_index = default_mic
    
    # Handle input for customer audio
    try:
        bh_input = input(f"Enter device index for your BlackHole device (Customer){' [default: ' + str(default_bh) + ']' if default_bh is not None else ''}: ")
        customer_index = int(bh_input) if bh_input.strip() else default_bh
        if customer_index is None:
            raise ValueError("No suitable BlackHole/secondary device found")
    except ValueError as e:
        if "No suitable" in str(e):
            print(f"Error: {e}")
            return
        print(f"Invalid input. Using default BlackHole at index {default_bh}.")
        customer_index = default_bh
    
    # Open separate input streams.
    agent_stream = None
    customer_stream = None
    
    try:
        # Open separate input streams.
        agent_stream = sd.InputStream(device=agent_index, samplerate=SAMPLE_RATE,
                                    blocksize=BLOCKSIZE, channels=CHANNELS,
                                    dtype='int16', callback=agent_callback)
        customer_stream = sd.InputStream(device=customer_index, samplerate=SAMPLE_RATE,
                                        blocksize=BLOCKSIZE, channels=CHANNELS,
                                        dtype='int16', callback=customer_callback)
        
        agent_stream.start()
        customer_stream.start()
        print("Both audio streams started successfully!")
        print("Speak on the mic (Agent) and play your YouTube video (Customer).")
        
        # Start two threads for independent streaming recognition.
        agent_thread = threading.Thread(target=stream_recognition, 
                                        args=("Agent", agent_audio_generator()), 
                                        daemon=True)
        customer_thread = threading.Thread(target=stream_recognition, 
                                           args=("Customer", customer_audio_generator()), 
                                           daemon=True)
        
        agent_thread.start()
        customer_thread.start()
        
        print("\nTranscription started. Press Ctrl+C to stop.")
        
        # Keep the main thread running
        while True:
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nTranscription stopped by user.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up resources
        if agent_stream is not None and agent_stream.active:
            agent_stream.stop()
            agent_stream.close()
        if customer_stream is not None and customer_stream.active:
            customer_stream.stop()
            customer_stream.close()
        print("Audio streams closed.")

if __name__ == "__main__":
    main()
