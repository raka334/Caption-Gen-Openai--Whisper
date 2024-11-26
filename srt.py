import re


def parse_srt(file_path):
    """
    Parse an SRT file into a list of segments.
    Each segment is a dictionary with keys: index, start, end, and text.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    pattern = re.compile(r"(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.*?)(?=\n\n|\Z)", re.DOTALL)
    matches = pattern.findall(content)
    segments = []
    for match in matches:
        index, start, end, text = match
        segments.append({
            "index": int(index),
            "start": time_to_seconds(start),
            "end": time_to_seconds(end),
            "text": text.replace("\n", " ").strip()
        })
    return segments


def time_to_seconds(timestamp):
    """
    Convert an SRT timestamp (HH:MM:SS,mmm) to seconds.
    """
    hours, minutes, seconds_ms = timestamp.split(":")
    seconds, milliseconds = map(float, seconds_ms.split(","))
    hours, minutes = map(float, [hours, minutes])
    return hours * 3600 + minutes * 60 + seconds + milliseconds / 1000


def seconds_to_time(seconds):
    """
    Convert seconds to SRT timestamp format.
    """
    ms = int((seconds % 1) * 1000)
    seconds = int(seconds)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02},{ms:03}"


def split_segment(segment, max_duration):
    """
    Split a single segment into smaller segments based on max duration.
    """
    duration = segment["end"] - segment["start"]
    words = segment["text"].split()
    if duration <= max_duration or len(words) <= 1:
        return [segment]

    split_segments = []
    num_splits = int(duration // max_duration) + 1
    words_per_split = max(1, len(words) // num_splits)

    start_time = segment["start"]
    for i in range(num_splits):
        end_time = min(segment["end"], start_time + max_duration)
        split_text = " ".join(words[i * words_per_split:(i + 1) * words_per_split])
        split_segments.append({
            "index": len(split_segments) + 1,
            "start": start_time,
            "end": end_time,
            "text": split_text.strip()
        })
        start_time = end_time

    return split_segments


def split_segments(segments, max_duration):
    """
    Split segments that exceed the max duration into smaller chunks.
    """
    new_segments = []
    for segment in segments:
        new_segments.extend(split_segment(segment, max_duration))
    return new_segments


def write_srt(segments, output_file):
    """
    Write segments to an SRT file.
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        for i, segment in enumerate(segments, 1):
            f.write(f"{i}\n")
            f.write(f"{seconds_to_time(segment['start'])} --> {seconds_to_time(segment['end'])}\n")
            f.write(f"{segment['text']}\n\n")


def process_srt(input_srt, output_srt, max_duration):
    """
    Process an SRT file to split segments based on max duration.
    """
    segments = parse_srt(input_srt)
    new_segments = split_segments(segments, max_duration)
    for i, segment in enumerate(new_segments):
        segment["index"] = i + 1
    write_srt(new_segments, output_srt)
    print(f"Processed SRT file saved as: {output_srt}")


# Main script
if __name__ == "__main__":
    input_srt = "transcription.srt"
    output_srt = "reduced_timestamps.srt"
    max_duration = 3.0
    process_srt(input_srt, output_srt, max_duration)
