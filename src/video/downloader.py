"""
YouTube video downloader using yt-dlp
"""

import os
from pathlib import Path
import yt_dlp


def download_youtube_video(url: str, output_dir: str = "downloads", filename: str = "source") -> str:
    """
    Download YouTube video to local file

    Args:
        url: YouTube URL
        output_dir: Directory to save video
        filename: Output filename (without extension)

    Returns:
        Path to downloaded video file
    """
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    output_path = os.path.join(output_dir, f"{filename}.mp4")

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': output_path,
        'quiet': False,
        'no_warnings': False,
        'merge_output_format': 'mp4',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Downloading video from: {url}")
            ydl.download([url])
            print(f"Video downloaded to: {output_path}")
            return output_path
    except Exception as e:
        raise ValueError(f"Failed to download video: {e}")


def get_video_info(url: str) -> dict:
    """
    Get video metadata without downloading

    Args:
        url: YouTube URL

    Returns:
        Dictionary with video info (title, duration, etc.)
    """
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0),
                'uploader': info.get('uploader', 'Unknown'),
                'description': info.get('description', ''),
            }
    except Exception as e:
        raise ValueError(f"Failed to get video info: {e}")
