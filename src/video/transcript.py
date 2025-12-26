"""
YouTube transcript extraction with timestamps
"""

import re
from typing import List, Dict
from youtube_transcript_api import YouTubeTranscriptApi


def extract_video_id(url: str) -> str:
    """
    Extract video ID from various YouTube URL formats

    Args:
        url: YouTube URL (e.g., https://www.youtube.com/watch?v=VIDEO_ID)

    Returns:
        Video ID string
    """
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'^([0-9A-Za-z_-]{11})$'
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    raise ValueError(f"Could not extract video ID from URL: {url}")


def get_transcript_with_timestamps(url: str) -> List[Dict[str, any]]:
    """
    Get YouTube transcript with timestamps

    Args:
        url: YouTube URL

    Returns:
        List of segments with 'text', 'start', 'duration' keys
        Example: [{'text': 'Hello', 'start': 0.0, 'duration': 1.5}, ...]
    """
    video_id = extract_video_id(url)

    try:
        # Get transcript (automatically selects best available language)
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return transcript
    except Exception as e:
        # Try manually generated transcript if auto-generated fails
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            transcript = transcript_list.find_transcript(['en']).fetch()
            return transcript
        except Exception as e2:
            raise ValueError(
                f"Could not fetch transcript for video {video_id}. "
                f"Error: {e2}. Make sure the video has captions available."
            )


def format_transcript_for_llm(segments: List[Dict[str, any]]) -> str:
    """
    Format transcript segments into a readable text format for LLM analysis

    Args:
        segments: List of transcript segments with timing info

    Returns:
        Formatted transcript string with timestamps
    """
    lines = []
    for seg in segments:
        start_time = seg['start']
        end_time = start_time + seg['duration']

        # Format times as MM:SS
        start_str = format_timestamp(start_time)
        end_str = format_timestamp(end_time)

        lines.append(f"[{start_str} - {end_str}] {seg['text']}")

    return "\n".join(lines)


def format_timestamp(seconds: float) -> str:
    """
    Convert seconds to HH:MM:SS format

    Args:
        seconds: Time in seconds

    Returns:
        Formatted timestamp string
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"


def get_video_duration(segments: List[Dict[str, any]]) -> float:
    """
    Calculate total video duration from transcript segments

    Args:
        segments: List of transcript segments

    Returns:
        Total duration in seconds
    """
    if not segments:
        return 0.0

    last_segment = segments[-1]
    return last_segment['start'] + last_segment['duration']
