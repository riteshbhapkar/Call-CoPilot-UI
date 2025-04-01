# # # # # 
# # # # import assemblyai as aai
# # # # from assemblyai import TranscriptionConfig
# # # # from datetime import datetime

# # # # # ==== Configuration ====
# # # # aai.settings.api_key = "e65938ce3a84406290f3afa4e8070180"

# # # # # Path to your audio file (ensure the file exists)
# # # # AUDIO_FILE_PATH = "./Testaudio.m4a"

# # # # # Transcription options now passed through a TranscriptionConfig object.
# # # # transcription_options = {
# # # #     "speaker_labels": True,    # Enable speaker diarization
# # # #     "language": "hi",          # Hindi language code
# # # #     "punctuate": True,         # Enable punctuation
# # # #     "format_text": True        # Enable smart formatting
# # # # }

# # # # def main():
# # # #     print(f"{datetime.now().strftime('%H:%M:%S')} - Starting transcription for {AUDIO_FILE_PATH}")
# # # #     transcriber = aai.Transcriber()
    
# # # #     # Create a configuration object using TranscriptionConfig.
# # # #     config = TranscriptionConfig(**transcription_options)
    
# # # #     # Transcribe the file using the configuration object.
# # # #     transcript = transcriber.transcribe(AUDIO_FILE_PATH, config=config)
    
# # # #     # Print the full transcript text.
# # # #     print("\n--- Full Transcript Text ---")
# # # #     print(transcript.text)
# # # #     print("----------------------------\n")
    
# # # #     # Check if word-level data (with speaker labels) is available.
# # # #     if not hasattr(transcript, "words") or not transcript.words:
# # # #         print("No word-level data available. Speaker diarization may not be enabled in this result.")
# # # #         return

# # # #     # Map speakers: first encountered speaker becomes "Agent", second "Customer".
# # # #     speaker_mapping = {}
# # # #     for word in transcript.words:
# # # #         spk = word.get("speaker")
# # # #         if spk is None:
# # # #             continue
# # # #         if spk not in speaker_mapping:
# # # #             if len(speaker_mapping) == 0:
# # # #                 speaker_mapping[spk] = "Agent"
# # # #             elif len(speaker_mapping) == 1:
# # # #                 speaker_mapping[spk] = "Customer"
# # # #             else:
# # # #                 speaker_mapping[spk] = f"Speaker {spk}"
    
# # # #     # Group words into segments when speaker changes.
# # # #     segments = []
# # # #     current_speaker = None
# # # #     current_segment = []
    
# # # #     for word in transcript.words:
# # # #         spk = word.get("speaker")
# # # #         if spk is None:
# # # #             continue
# # # #         speaker_label = speaker_mapping.get(spk, f"Speaker {spk}")
# # # #         if speaker_label != current_speaker:
# # # #             if current_segment:
# # # #                 segments.append((current_speaker, " ".join(current_segment)))
# # # #             current_speaker = speaker_label
# # # #             current_segment = [word.get("punctuated_word", word.get("word", ""))]
# # # #         else:
# # # #             current_segment.append(word.get("punctuated_word", word.get("word", "")))
    
# # # #     if current_segment:
# # # #         segments.append((current_speaker, " ".join(current_segment)))
    
# # # #     # Print the speaker-labeled transcript.
# # # #     print("\n--- Speaker-Labeled Transcript ---")
# # # #     for speaker, text in segments:
# # # #         print(f"{speaker}: {text}")
# # # #     print("------------------------------------\n")

# # # # if __name__ == "__main__":
# # # #     main()

# # # import assemblyai as aai
# # # from assemblyai import TranscriptionConfig
# # # from datetime import datetime

# # # # ==== Configuration ====
# # # aai.settings.api_key = "e65938ce3a84406290f3afa4e8070180"

# # # # Path to your audio file (ensure the file exists)
# # # AUDIO_FILE_PATH = "/Users/apple/Desktop/Testaudio.m4a"


# # # # Transcription options using the correct parameter name for language
# # # transcription_options = {
# # #     "speaker_labels": True,    # Enable speaker diarization
# # #     "language_code": "hi",       # Use 'hi' for Hindi
# # #     "punctuate": True,         # Enable punctuation
# # #     "format_text": True        # Enable smart formatting
# # # }

# # # def main():
# # #     print(f"{datetime.now().strftime('%H:%M:%S')} - Starting transcription for {AUDIO_FILE_PATH}")
# # #     transcriber = aai.Transcriber()
    
# # #     # Create a configuration object with our updated parameters.
# # #     config = TranscriptionConfig(**transcription_options)
    
# # #     # Transcribe the file using the configuration object.
# # #     transcript = transcriber.transcribe(AUDIO_FILE_PATH, config=config)
    
# # #     # Print the full transcript text.
# # #     print("\n--- Full Transcript Text ---")
# # #     print(transcript.text)
# # #     print("----------------------------\n")
    
# # #     # Check if word-level data (with speaker labels) is available.
# # #     if not hasattr(transcript, "words") or not transcript.words:
# # #         print("No word-level data available. Speaker diarization may not be enabled in this result.")
# # #         return

# # #     # Map speakers: first encountered speaker becomes "Agent", second "Customer".
# # #     speaker_mapping = {}
# # #     for word in transcript.words:
# # #         spk = word.get("speaker")
# # #         if spk is None:
# # #             continue
# # #         if spk not in speaker_mapping:
# # #             if len(speaker_mapping) == 0:
# # #                 speaker_mapping[spk] = "Agent"
# # #             elif len(speaker_mapping) == 1:
# # #                 speaker_mapping[spk] = "Customer"
# # #             else:
# # #                 speaker_mapping[spk] = f"Speaker {spk}"
    
# # #     # Group words into segments by speaker change.
# # #     segments = []
# # #     current_speaker = None
# # #     current_segment = []
    
# # #     for word in transcript.words:
# # #         spk = word.get("speaker")
# # #         if spk is None:
# # #             continue
# # #         speaker_label = speaker_mapping.get(spk, f"Speaker {spk}")
# # #         if speaker_label != current_speaker:
# # #             if current_segment:
# # #                 segments.append((current_speaker, " ".join(current_segment)))
# # #             current_speaker = speaker_label
# # #             current_segment = [word.get("punctuated_word", word.get("word", ""))]
# # #         else:
# # #             current_segment.append(word.get("punctuated_word", word.get("word", "")))
    
# # #     if current_segment:
# # #         segments.append((current_speaker, " ".join(current_segment)))
    
# # #     # Print the speaker-labeled transcript.
# # #     print("\n--- Speaker-Labeled Transcript ---")
# # #     for speaker, text in segments:
# # #         print(f"{speaker}: {text}")
# # #     print("------------------------------------\n")

# # # if __name__ == "__main__":
# # #     main()

# # import assemblyai as aai
# # from assemblyai import TranscriptionConfig
# # from datetime import datetime

# # # ==== Configuration ====
# # aai.settings.api_key = "e65938ce3a84406290f3afa4e8070180"

# # # Path to your audio file (ensure this file exists)
# # AUDIO_FILE_PATH = "/Users/apple/Desktop/Testaudio.m4a"

# # # Updated transcription options using correct parameter names
# # transcription_options = {
# #     "speaker_labels": True,   # Enable speaker diarization
# #     "language_code": "hi",      # Use 'hi' for Hindi
# #     "punctuate": True,          # Enable punctuation
# #     "format_text": True         # Enable smart formatting
# # }

# # def main():
# #     print(f"{datetime.now().strftime('%H:%M:%S')} - Starting transcription for {AUDIO_FILE_PATH}")
# #     transcriber = aai.Transcriber()
    
# #     # Create a configuration object using TranscriptionConfig
# #     config = TranscriptionConfig(**transcription_options)
    
# #     # Transcribe the file using the configuration object
# #     transcript = transcriber.transcribe(AUDIO_FILE_PATH, config=config)
    
# #     # Print the full transcript text
# #     print("\n--- Full Transcript Text ---")
# #     print(transcript.text)
# #     print("----------------------------\n")
    
# #     # Check if word-level data (with speaker labels) is available.
# #     if not hasattr(transcript, "words") or not transcript.words:
# #         print("No word-level data available. Speaker diarization may not be enabled in this result.")
# #         return

# #     # Map speakers: first encountered speaker becomes "Agent", second "Customer"
# #     speaker_mapping = {}
# #     for word in transcript.words:
# #         spk = word.speaker  # Access the attribute directly
# #         if spk is None:
# #             continue
# #         if spk not in speaker_mapping:
# #             if len(speaker_mapping) == 0:
# #                 speaker_mapping[spk] = "Agent"
# #             elif len(speaker_mapping) == 1:
# #                 speaker_mapping[spk] = "Customer"
# #             else:
# #                 speaker_mapping[spk] = f"Speaker {spk}"
    
# #     # Group words into segments when speaker changes
# #     segments = []
# #     current_speaker = None
# #     current_segment = []
    
# #     for word in transcript.words:
# #         spk = word.speaker
# #         if spk is None:
# #             continue
# #         speaker_label = speaker_mapping.get(spk, f"Speaker {spk}")
# #         # Use punctuated_word if available; otherwise fallback to word
# #         word_text = word.punctuated_word if hasattr(word, "punctuated_word") and word.punctuated_word else word.word
# #         if speaker_label != current_speaker:
# #             if current_segment:
# #                 segments.append((current_speaker, " ".join(current_segment)))
# #             current_speaker = speaker_label
# #             current_segment = [word_text]
# #         else:
# #             current_segment.append(word_text)
    
# #     if current_segment:
# #         segments.append((current_speaker, " ".join(current_segment)))
    
# #     # Print the speaker-labeled transcript
# #     print("\n--- Speaker-Labeled Transcript ---")
# #     for speaker, text in segments:
# #         print(f"{speaker}: {text}")
# #     print("------------------------------------\n")

# # if __name__ == "__main__":
# #     main()
# import assemblyai as aai
# from assemblyai import TranscriptionConfig
# from datetime import datetime

# # ==== Configuration ====
# aai.settings.api_key = "e65938ce3a84406290f3afa4e8070180"

# # Path to your audio file (ensure this file exists)
# AUDIO_FILE_PATH = "/Users/apple/Desktop/test2.m4a"

# # Transcription options using the updated parameter names.
# transcription_options = {
#     "speaker_labels": True,    # Enable speaker diarization
#     "language_code": "hi",       # Use 'hi' for Hindi
#     "punctuate": True,         # Enable punctuation
#     "format_text": True        # Enable smart formatting
# }

# def main():
#     print(f"{datetime.now().strftime('%H:%M:%S')} - Starting transcription for {AUDIO_FILE_PATH}")
#     transcriber = aai.Transcriber()
    
#     # Create a configuration object using TranscriptionConfig
#     config = TranscriptionConfig(**transcription_options)
    
#     # Transcribe the file using the configuration object.
#     transcript = transcriber.transcribe(AUDIO_FILE_PATH, config=config)
    
#     # Print the full transcript text.
#     print("\n--- Full Transcript Text ---")
#     print(transcript.text)
#     print("----------------------------\n")
    
#     # Check if word-level data (with speaker labels) is available.
#     if not hasattr(transcript, "words") or not transcript.words:
#         print("No word-level data available. Speaker diarization may not be enabled in this result.")
#         return

#     # Map speakers: first encountered speaker becomes "Agent", second "Customer"
#     speaker_mapping = {}
#     for word in transcript.words:
#         spk = word.speaker  # Access the speaker attribute
#         if spk is None:
#             continue
#         if spk not in speaker_mapping:
#             if len(speaker_mapping) == 0:
#                 speaker_mapping[spk] = "Agent"
#             elif len(speaker_mapping) == 1:
#                 speaker_mapping[spk] = "Customer"
#             else:
#                 speaker_mapping[spk] = f"Speaker {spk}"
    
#     # Group words into segments when the speaker changes.
#     segments = []
#     current_speaker = None
#     current_segment = []
    
#     for word in transcript.words:
#         spk = word.speaker
#         if spk is None:
#             continue
#         speaker_label = speaker_mapping.get(spk, f"Speaker {spk}")
#         # Use punctuated_word if available; if not, fallback to converting the word object to string.
#         word_text = getattr(word, "punctuated_word", None)
#         if not word_text:
#             word_text = str(word)
#         if speaker_label != current_speaker:
#             if current_segment:
#                 segments.append((current_speaker, " ".join(current_segment)))
#             current_speaker = speaker_label
#             current_segment = [word_text]
#         else:
#             current_segment.append(word_text)
    
#     if current_segment:
#         segments.append((current_speaker, " ".join(current_segment)))
    
#     # Print the speaker-labeled transcript.
#     print("\n--- Speaker-Labeled Transcript ---")
#     for speaker, text in segments:
#         print(f"{speaker}: {text}")
#     print("------------------------------------\n")

# if __name__ == "__main__":
#     main()
import assemblyai as aai
from assemblyai import TranscriptionConfig
from datetime import datetime

# ==== Configuration ====
aai.settings.api_key = "e65938ce3a84406290f3afa4e8070180"

# Path to your 2-channel audio file (Testaudio.m4a) 
AUDIO_FILE_PATH = "/Users/apple/Desktop/test2.m4a"

# Transcription options – enable speaker diarization.
# (Note: For multichannel diarization, recording a true stereo file is essential.)
transcription_options = {
    "speaker_labels": True,
    "language_code": "hi",       # 'hi' for Hindi
    "punctuate": True,
    "format_text": True
}

def main():
    print(f"{datetime.now().strftime('%H:%M:%S')} - Starting transcription for {AUDIO_FILE_PATH}")
    transcriber = aai.Transcriber()
    
    # Create a configuration object using the current options.
    config = TranscriptionConfig(**transcription_options)
    
    # Transcribe the file using AssemblyAI's file transcription endpoint.
    transcript = transcriber.transcribe(AUDIO_FILE_PATH, config=config)
    
    # Print the full transcript text.
    print("\n--- Full Transcript Text ---")
    print(transcript.text)
    print("----------------------------\n")
    
    # Check if word-level data (with speaker or channel labels) is available.
    if not hasattr(transcript, "words") or not transcript.words:
        print("No word-level data available. Speaker diarization may not be enabled in this result.")
        return

    # We'll build segments based on either the "channel" attribute (if available) or "speaker"
    segments = []
    current_label = None
    current_segment = []

    # Simple mapping if using channel info:
    def map_channel(ch):
        if ch == 0:
            return "Agent"
        elif ch == 1:
            return "Customer"
        else:
            return f"Channel {ch}"

    # Otherwise, use a simple speaker mapping
    speaker_mapping = {}

    for word in transcript.words:
        # First try to use the channel attribute
        channel_attr = getattr(word, "channel", None)
        if channel_attr is not None:
            label = map_channel(channel_attr)
        else:
            # Fall back to using the speaker attribute
            spk = getattr(word, "speaker", None)
            if spk is None:
                continue
            if spk not in speaker_mapping:
                if len(speaker_mapping) == 0:
                    speaker_mapping[spk] = "Agent"
                elif len(speaker_mapping) == 1:
                    speaker_mapping[spk] = "Customer"
                else:
                    speaker_mapping[spk] = f"Speaker {spk}"
            label = speaker_mapping[spk]
        
        # Get the word text – prefer punctuated_word if available.
        word_text = getattr(word, "punctuated_word", None)
        if not word_text:
            # Fallback: convert the word object to string
            word_text = str(word)
        
        # If the label changes, store the current segment.
        if label != current_label:
            if current_segment:
                segments.append((current_label, " ".join(current_segment)))
            current_label = label
            current_segment = [word_text]
        else:
            current_segment.append(word_text)
    
    if current_segment:
        segments.append((current_label, " ".join(current_segment)))
    
    # Print the speaker-labeled transcript.
    print("\n--- Speaker-Labeled Transcript ---")
    for label, text in segments:
        print(f"{label}: {text}")
    print("------------------------------------\n")

if __name__ == "__main__":
    main()
