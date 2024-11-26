import whisper
import ffmpeg
from tkinter import Tk
from tkinter.filedialog import askopenfilename

def extract_audio_from_video(video_file, audio_file="output_audio.wav"):
    """
    Extract audio from a video file and save it as a WAV file.
    """
    try:
        (
            ffmpeg
            .input(video_file)
            .output(audio_file, format='wav', acodec='pcm_s16le', ac=1, ar='16000')
            .run(overwrite_output=True)
        )
        print(f"Audio extracted and saved to {audio_file}")
        return audio_file
    except ffmpeg._run.Error as e:
        print("Error in audio extraction:", e)
        return None

def transcribe_audio_to_srt(audio_file, srt_file="transcription.srt"):
    """
    Transcribe the audio using OpenAI's Whisper model and save it as an SRT file.
    """
    model = whisper.load_model("base") 
    print("Transcribing audio...")
    result = model.transcribe(audio_file)

    print("\nRaw Transcription Result:")
    print(result)

    print("Writing to SRT file...")
    if "segments" not in result or not result["segments"]:
        print("No segments found in transcription. Exiting.")
        return None

    with open(srt_file, "w", encoding="utf-8") as f:
        for i, segment in enumerate(result["segments"]):
            print(f"Processing segment {i + 1}: {segment['text']}")  # Debug: Print each segment

            f.write(f"{i + 1}\n")
            
            start_time = format_timestamp(segment["start"])
            end_time = format_timestamp(segment["end"])
            f.write(f"{start_time} --> {end_time}\n")
            
            formatted_text = break_text_by_words(segment["text"], 5)
            f.write(f"{formatted_text}\n\n")
    
    print(f"SRT file saved as {srt_file}")
    return srt_file

def format_timestamp(seconds):
    """
    Format a timestamp in seconds to the SRT format: HH:MM:SS,ms
    """
    milliseconds = int((seconds % 1) * 1000)
    seconds = int(seconds)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

def break_text_by_words(text, word_limit):
    """
    Break text into lines with a maximum of 'word_limit' words per line.
    """
    words = text.split()
    lines = [" ".join(words[i:i + word_limit]) for i in range(0, len(words), word_limit)]
    return "\n".join(lines)

def select_video_file():
    """
    Open a file dialog to select the video file.
    """
    Tk().withdraw()  
    video_file = askopenfilename(
        title="Select a Video File",
        filetypes=[("Video Files", "*.mp4 *.mkv *.avi *.mov")]
    )
    return video_file

# Main script
if __name__ == "__main__":
    print("Please select the video file.")
    video_file = select_video_file()

    if video_file:
        print(f"Selected video file: {video_file}")
        
        audio_file = extract_audio_from_video(video_file)

        if audio_file:

            srt_file = transcribe_audio_to_srt(audio_file)
            if srt_file:
                print(f"\nSubtitle file generated: {srt_file}")
            else:
                print("No subtitles generated.")
        else:
            print("Failed to process the video.")
    else:
        print("No video file selected.")
