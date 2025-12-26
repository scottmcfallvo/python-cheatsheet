#!/usr/bin/env python3
"""
YouTube LLM Edit Tool
Main entry point for the application

Workflow:
1. Provide YouTube URL
2. Extract transcript with timestamps
3. LLM analyzes and selects segments to keep
4. Generate FCPXML timeline file
5. Download video
6. Import into DaVinci Resolve
"""

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

from src.video.transcript import (
    get_transcript_with_timestamps,
    format_transcript_for_llm,
    get_video_duration
)
from src.video.downloader import download_youtube_video, get_video_info
from src.llm.analyzer import analyze_transcript
from src.video.fcpxml_generator import (
    create_fcpxml_timeline,
    save_cutlist_json
)


def main():
    """Main function"""
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="YouTube LLM Edit Tool - Automatically cut YouTube videos to main points",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with OpenAI
  python main.py "https://www.youtube.com/watch?v=VIDEO_ID"

  # Use Anthropic Claude instead
  python main.py "URL" --provider anthropic

  # Custom instructions
  python main.py "URL" --instructions "Keep only actionable steps, remove theory"

  # Target specific compression
  python main.py "URL" --target 25

  # Skip video download (if you already have it)
  python main.py "URL" --no-download
        """
    )

    parser.add_argument(
        "url",
        help="YouTube URL to process"
    )

    parser.add_argument(
        "--instructions",
        default="Keep only main points, remove fluff and redundancy",
        help="Instructions for what content to keep (default: keep main points)"
    )

    parser.add_argument(
        "--target",
        type=int,
        default=35,
        help="Target percentage of original length to keep (default: 35)"
    )

    parser.add_argument(
        "--provider",
        choices=["openai", "anthropic"],
        default="openai",
        help="LLM provider to use (default: openai)"
    )

    parser.add_argument(
        "--model",
        help="Specific model to use (e.g., gpt-4, claude-3-5-sonnet-20241022)"
    )

    parser.add_argument(
        "--output-dir",
        default="output",
        help="Directory for output files (default: output)"
    )

    parser.add_argument(
        "--no-download",
        action="store_true",
        help="Skip video download (assumes source.mp4 already exists)"
    )

    args = parser.parse_args()

    # Create output directory
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("YouTube LLM Edit Tool")
    print("=" * 70)
    print(f"\nYouTube URL: {args.url}")
    print(f"LLM Provider: {args.provider}")
    print(f"Target Length: {args.target}% of original")
    print(f"Instructions: {args.instructions}")
    print()

    try:
        # Step 1: Get video info
        print("\n[Step 1/5] Fetching video information...")
        video_info = get_video_info(args.url)
        print(f"  Title: {video_info['title']}")
        print(f"  Duration: {video_info['duration']} seconds")
        print(f"  Uploader: {video_info['uploader']}")

        # Step 2: Get transcript
        print("\n[Step 2/5] Extracting transcript with timestamps...")
        transcript_segments = get_transcript_with_timestamps(args.url)
        print(f"  Retrieved {len(transcript_segments)} transcript segments")

        video_duration = get_video_duration(transcript_segments)
        print(f"  Total duration: {video_duration:.1f} seconds")

        # Format transcript for LLM
        formatted_transcript = format_transcript_for_llm(transcript_segments)

        # Save full transcript for reference
        transcript_path = os.path.join(args.output_dir, "transcript.txt")
        with open(transcript_path, 'w', encoding='utf-8') as f:
            f.write(formatted_transcript)
        print(f"  Saved transcript to: {transcript_path}")

        # Step 3: LLM Analysis
        print(f"\n[Step 3/5] Analyzing transcript with {args.provider.upper()} LLM...")
        segments = analyze_transcript(
            formatted_transcript,
            instructions=args.instructions,
            target_percentage=args.target,
            provider=args.provider,
            model=args.model
        )

        if not segments:
            print("  ERROR: No segments selected by LLM")
            return 1

        total_kept = sum(seg['end'] - seg['start'] for seg in segments)
        compression_ratio = (total_kept / video_duration) * 100
        print(f"  Selected {len(segments)} segments")
        print(f"  Total kept: {total_kept:.1f}s ({compression_ratio:.1f}% of original)")

        # Step 4: Generate FCPXML
        print("\n[Step 4/5] Generating FCPXML timeline...")
        fcpxml_path = os.path.join(args.output_dir, "timeline.fcpxml")
        cutlist_path = os.path.join(args.output_dir, "cutlist.json")

        create_fcpxml_timeline(
            segments=segments,
            source_filename="source.mp4",
            output_path=fcpxml_path,
            video_duration=video_duration,
            timeline_name=f"AI Edit - {video_info['title'][:50]}"
        )

        save_cutlist_json(segments, cutlist_path)

        # Step 5: Download video
        if not args.no_download:
            print("\n[Step 5/5] Downloading video...")
            video_path = download_youtube_video(
                args.url,
                output_dir=args.output_dir,
                filename="source"
            )
        else:
            print("\n[Step 5/5] Skipping video download (--no-download flag)")
            video_path = os.path.join(args.output_dir, "source.mp4")
            if not os.path.exists(video_path):
                print(f"  WARNING: {video_path} does not exist!")

        # Final instructions
        print("\n" + "=" * 70)
        print("SUCCESS! Timeline created.")
        print("=" * 70)
        print("\nGenerated files:")
        print(f"  1. {fcpxml_path} - Import this into DaVinci Resolve")
        print(f"  2. {cutlist_path} - Human-readable segment list")
        print(f"  3. {video_path} - Source video file")
        print(f"  4. {transcript_path} - Full transcript")

        print("\n" + "=" * 70)
        print("NEXT STEPS - Import into DaVinci Resolve:")
        print("=" * 70)
        print("1. Open DaVinci Resolve")
        print("2. Import the source video into your Media Pool:")
        print(f"   File → Import Media → {video_path}")
        print("3. Import the timeline:")
        print(f"   File → Import Timeline → {fcpxml_path}")
        print("4. If prompted, relink media to source.mp4")
        print("5. Your cut-down timeline is now ready to review and export!")
        print()

        return 0

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
