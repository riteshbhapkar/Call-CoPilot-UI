# Real-time Dual-Channel Speech Transcription

This tool enables real-time transcription of two separate audio streams: your microphone (for your voice) and system audio (for the other person/audio source), with automatic speaker labeling.

## Overview

The `googletest.py` script uses Google Cloud Speech-to-Text API to provide:

- Separate real-time transcription of two audio streams
- Automatic speaker labeling ("Agent" for your mic, "Customer" for system audio)
- Support for Hindi/English/Hinglish transcription
- Auto-detection of available audio devices

Perfect for transcribing customer service calls, interviews, YouTube videos, or any scenario where you need to capture both your voice and another audio source.

## Requirements

- Python 3.6+
- Google Cloud account with Speech-to-Text API enabled
- Google Cloud credentials JSON file
- BlackHole 2ch (virtual audio device for macOS)
- Python libraries: `sounddevice`, `numpy`, `google-cloud-speech`

## Installation

### 1. Install Required Python Libraries

```bash
pip install sounddevice numpy google-cloud-speech
```

### 2. Install BlackHole 2ch Virtual Audio Device

BlackHole allows you to route system audio to our script for transcription.

#### Installation Options:

**Option A: Using Homebrew (Recommended)**
```bash
brew install blackhole-2ch
```

**Option B: Manual Installation**
1. Download from the [BlackHole GitHub repository](https://github.com/ExistentialAudio/BlackHole)
2. Follow the installation instructions in their README

### 3. Set Up Google Cloud Credentials

1. Create a project in Google Cloud Console
2. Enable the Speech-to-Text API
3. Create a service account and download the JSON credentials file
4. Update the path in the script:
   ```python
   os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/path/to/your/credentials.json"
   ```

## Configuring BlackHole

To route system audio to BlackHole for transcription:

### Method 1: Multi-Output Device (for hearing audio while transcribing)

1. Open "Audio MIDI Setup" (search in Spotlight)
2. Click the "+" button in the bottom left and select "Create Multi-Output Device"
3. Check both "BlackHole 2ch" and your speakers/headphones
4. In System Settings/Preferences → Sound → Output, select the "Multi-Output Device"

### Method 2: Direct Output (for transcription only)

1. In System Settings/Preferences → Sound → Output, select "BlackHole 2ch"
2. Any audio playing will be silently routed to the transcription tool

## Running the Script

1. Ensure BlackHole is configured as your audio output
2. Open a terminal and navigate to the script directory
3. Run the script:
   ```bash
   python googletest.py
   ```
4. When prompted, select your microphone and BlackHole as input devices
5. Start speaking and playing audio (YouTube video, recording, etc.)

## Understanding the Output

The script provides real-time transcriptions with speaker labels:

```
[12:34:56] Agent Transcript Update:
Hello, this is my voice from the microphone.
--------------------------------------------------

[12:35:01] Customer Transcript Update:
This is the voice from system audio or YouTube.
--------------------------------------------------
```

## Troubleshooting

### No Audio Detected from BlackHole
- Ensure BlackHole is selected as your output device
- Check that media is actually playing
- Try increasing the volume of the audio source

### Microphone Not Working
- Make sure your microphone is not muted
- Check permission settings for terminal/application
- Try selecting a different input device

### API Errors
- Verify your Google Cloud credentials file path is correct
- Ensure your Google Cloud project has the Speech-to-Text API enabled
- Check you have billing enabled on your Google Cloud account

## Advanced Configuration

You can modify these parameters in the script to customize behavior:

- `SAMPLE_RATE`: Audio sample rate (default: 16000 Hz)
- `language_code`: Primary language for transcription
- `alternative_language_codes`: Secondary language support
- `model`: Google Speech model to use
