import whisperx
import torch
from datetime import datetime

def main():
    audio_path = "/Users/apple/Desktop/test2.m4a"
    
    # Choose device: "cuda" if available; otherwise "cpu"
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    # Load the Whisper model via WhisperX. You can choose "base", "small", etc.
    print(f"{datetime.now().strftime('%H:%M:%S')} - Loading Whisper model on {device}...")
    model = whisperx.load_model("base", device=device)
    
    # Transcribe the audio file with language set to Hindi ("hi")
    print("Transcribing audio...")
    result = model.transcribe(audio_path, language="hi")
    
    # Run alignment to refine timestamps
    print("Running alignment...")
    result_aligned = whisperx.align(result, model, audio_path)
    
    # Perform diarization; here we assume 2 speakers (adjust if necessary)
    print("Running diarization...")
    diarization = whisperx.diarize(audio_path, num_speakers=2)
    
    # Merge diarization with the aligned transcript
    print("Merging diarization with transcript...")
    final_result = whisperx.merge_diarization(result_aligned, diarization)
    
    # Map speaker numbers to roles:
    # We assume the first encountered speaker is "Agent" and the second "Customer"
    speaker_mapping = {}
    for segment in final_result["segments"]:
        spk = segment.get("speaker")
        if spk is None:
            continue
        if spk not in speaker_mapping:
            if len(speaker_mapping) == 0:
                speaker_mapping[spk] = "Agent"
            elif len(speaker_mapping) == 1:
                speaker_mapping[spk] = "Customer"
            else:
                speaker_mapping[spk] = f"Speaker {spk}"
    
    # Print the final transcript with speaker labels
    print("\n--- Final Speaker-Labeled Transcript ---\n")
    for segment in final_result["segments"]:
        spk = segment.get("speaker")
        speaker_name = speaker_mapping.get(spk, f"Speaker {spk}")
        start = segment.get("start", 0)
        end = segment.get("end", 0)
        text = segment.get("text", "")
        print(f"[{start:.2f} - {end:.2f}] {speaker_name}: {text}")
    print("\n-----------------------------------------\n")

if __name__ == "__main__":
    main()
