"""
FCPXML timeline generator for DaVinci Resolve

Creates FCPXML files that describe a cut-down timeline with selected segments
"""

from typing import List, Dict
from xml.etree.ElementTree import Element, SubElement, tostring, ElementTree
from xml.dom import minidom
import os


def seconds_to_framerate_string(seconds: float, framerate: int = 30) -> str:
    """
    Convert seconds to FCPXML time format (frames/framerate)

    Args:
        seconds: Time in seconds
        framerate: Video framerate (default 30fps)

    Returns:
        String like "900/30s" for 30 seconds at 30fps
    """
    frames = int(seconds * framerate)
    return f"{frames}/{framerate}s"


def create_fcpxml_timeline(
    segments: List[Dict[str, float]],
    source_filename: str,
    output_path: str,
    video_duration: float,
    framerate: int = 30,
    timeline_name: str = "AI Edited Timeline"
) -> str:
    """
    Create an FCPXML file with selected segments

    Args:
        segments: List of dicts with 'start' and 'end' keys (in seconds)
                  Example: [{'start': 10.5, 'end': 25.3}, ...]
        source_filename: Name of source video file (e.g., "source.mp4")
        output_path: Where to save the FCPXML file
        video_duration: Total duration of source video in seconds
        framerate: Video framerate (default 30fps)
        timeline_name: Name for the timeline in Resolve

    Returns:
        Path to created FCPXML file
    """
    # Create root element
    fcpxml = Element('fcpxml', version="1.9")

    # Add resources section
    resources = SubElement(fcpxml, 'resources')

    # Format element for the video format
    format_elem = SubElement(
        resources,
        'format',
        id="r1",
        name="FFVideoFormat1080p30",
        frameDuration=f"1/{framerate}s",
        width="1920",
        height="1080"
    )

    # Asset element for source video
    asset = SubElement(
        resources,
        'asset',
        id="r2",
        name=source_filename,
        src=source_filename,
        start="0s",
        duration=seconds_to_framerate_string(video_duration, framerate),
        hasVideo="1",
        hasAudio="1",
        format="r1"
    )

    # Create library and event
    library = SubElement(fcpxml, 'library')
    event = SubElement(library, 'event', name="AI Edit")

    # Create project (timeline)
    project = SubElement(
        event,
        'project',
        name=timeline_name
    )

    # Create sequence
    sequence = SubElement(
        project,
        'sequence',
        format="r1",
        duration=seconds_to_framerate_string(
            sum(seg['end'] - seg['start'] for seg in segments),
            framerate
        )
    )

    # Create spine (main timeline track)
    spine = SubElement(sequence, 'spine')

    # Add each segment as a clip
    timeline_offset = 0.0

    for i, seg in enumerate(segments):
        start_time = seg['start']
        end_time = seg['end']
        duration = end_time - start_time

        # Create asset-clip element
        clip = SubElement(
            spine,
            'asset-clip',
            name=f"Segment {i+1}",
            ref="r2",
            offset=seconds_to_framerate_string(timeline_offset, framerate),
            duration=seconds_to_framerate_string(duration, framerate),
            start=seconds_to_framerate_string(start_time, framerate),
            tcFormat="NDF"
        )

        timeline_offset += duration

    # Write to file with pretty formatting
    xml_string = minidom.parseString(tostring(fcpxml)).toprettyxml(indent="  ")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(xml_string)

    print(f"FCPXML timeline created: {output_path}")
    print(f"  - {len(segments)} segments")
    print(f"  - Original duration: {format_time(video_duration)}")
    print(f"  - Edited duration: {format_time(timeline_offset)}")
    print(f"  - Compression: {(timeline_offset/video_duration)*100:.1f}%")

    return output_path


def format_time(seconds: float) -> str:
    """Format seconds as HH:MM:SS"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"


def save_cutlist_json(segments: List[Dict[str, float]], output_path: str) -> str:
    """
    Save human-readable cutlist as JSON for auditing

    Args:
        segments: List of segment dicts with 'start' and 'end'
        output_path: Where to save JSON file

    Returns:
        Path to created JSON file
    """
    import json

    formatted_segments = []
    for i, seg in enumerate(segments):
        formatted_segments.append({
            'segment': i + 1,
            'start': seg['start'],
            'end': seg['end'],
            'duration': seg['end'] - seg['start'],
            'start_formatted': format_time(seg['start']),
            'end_formatted': format_time(seg['end'])
        })

    cutlist = {
        'total_segments': len(segments),
        'total_duration': sum(seg['end'] - seg['start'] for seg in segments),
        'segments': formatted_segments
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(cutlist, f, indent=2)

    print(f"Cutlist saved: {output_path}")
    return output_path
