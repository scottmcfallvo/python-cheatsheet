"""
LLM-based transcript analyzer for selecting video segments to keep

Uses OpenAI or Anthropic to analyze transcript and select main points
"""

import os
import json
from typing import List, Dict, Optional
import re


def analyze_transcript_with_openai(
    transcript_text: str,
    instructions: str = "Keep only main points, remove fluff and redundancy",
    target_percentage: int = 35,
    model: str = "gpt-4"
) -> List[Dict[str, float]]:
    """
    Use OpenAI to analyze transcript and select segments to keep

    Args:
        transcript_text: Formatted transcript with timestamps
        instructions: User instructions for what to keep
        target_percentage: Target percentage of original length to keep
        model: OpenAI model to use

    Returns:
        List of segments with 'start' and 'end' times in seconds
    """
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("OpenAI package not installed. Run: pip install openai")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")

    client = OpenAI(api_key=api_key)

    system_prompt = f"""You are a video editing assistant. Your job is to analyze a video transcript and select the most important segments to keep.

TASK: Review the transcript and identify segments that contain the main points, key information, and valuable content.

REMOVE:
- Introductions and outros
- Sponsor messages
- Tangents and off-topic discussions
- Repeated explanations of the same concept
- Filler words and unnecessary pauses

KEEP:
- Core concepts and definitions
- Key methods and techniques
- Important examples and demonstrations
- Actionable steps and instructions
- Novel or unique insights

TARGET: Reduce video to approximately {target_percentage}% of original length.

USER INSTRUCTIONS: {instructions}

OUTPUT FORMAT: You must respond with a valid JSON array of segments to keep. Each segment must have "start" and "end" times in seconds (as floats).

Example output:
[
  {{"start": 12.5, "end": 45.8, "reason": "Core concept introduction"}},
  {{"start": 67.2, "end": 102.4, "reason": "Key example demonstration"}},
  {{"start": 150.0, "end": 185.3, "reason": "Actionable steps"}}
]

IMPORTANT:
- Output ONLY the JSON array, nothing else
- Times must be in seconds (float numbers)
- Segments should be chronological
- Don't overlap segments
"""

    user_prompt = f"""Here is the video transcript with timestamps:

{transcript_text}

Please analyze this transcript and return a JSON array of segments to keep, following the format specified."""

    print("Analyzing transcript with OpenAI...")
    print(f"Model: {model}")

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
        )

        response_text = response.choices[0].message.content.strip()

        # Extract JSON from response (in case LLM adds extra text)
        json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(0)

        segments = json.loads(response_text)

        # Validate and clean segments
        cleaned_segments = []
        for seg in segments:
            if 'start' in seg and 'end' in seg:
                cleaned_segments.append({
                    'start': float(seg['start']),
                    'end': float(seg['end'])
                })

        print(f"LLM selected {len(cleaned_segments)} segments to keep")
        return cleaned_segments

    except Exception as e:
        raise ValueError(f"OpenAI API error: {e}")


def analyze_transcript_with_anthropic(
    transcript_text: str,
    instructions: str = "Keep only main points, remove fluff and redundancy",
    target_percentage: int = 35,
    model: str = "claude-3-5-sonnet-20241022"
) -> List[Dict[str, float]]:
    """
    Use Anthropic Claude to analyze transcript and select segments to keep

    Args:
        transcript_text: Formatted transcript with timestamps
        instructions: User instructions for what to keep
        target_percentage: Target percentage of original length to keep
        model: Anthropic model to use

    Returns:
        List of segments with 'start' and 'end' times in seconds
    """
    try:
        from anthropic import Anthropic
    except ImportError:
        raise ImportError("Anthropic package not installed. Run: pip install anthropic")

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")

    client = Anthropic(api_key=api_key)

    system_prompt = f"""You are a video editing assistant. Your job is to analyze a video transcript and select the most important segments to keep.

TASK: Review the transcript and identify segments that contain the main points, key information, and valuable content.

REMOVE:
- Introductions and outros
- Sponsor messages
- Tangents and off-topic discussions
- Repeated explanations of the same concept
- Filler words and unnecessary pauses

KEEP:
- Core concepts and definitions
- Key methods and techniques
- Important examples and demonstrations
- Actionable steps and instructions
- Novel or unique insights

TARGET: Reduce video to approximately {target_percentage}% of original length.

USER INSTRUCTIONS: {instructions}

OUTPUT FORMAT: You must respond with a valid JSON array of segments to keep. Each segment must have "start" and "end" times in seconds (as floats).

Example output:
[
  {{"start": 12.5, "end": 45.8, "reason": "Core concept introduction"}},
  {{"start": 67.2, "end": 102.4, "reason": "Key example demonstration"}},
  {{"start": 150.0, "end": 185.3, "reason": "Actionable steps"}}
]

IMPORTANT:
- Output ONLY the JSON array, nothing else
- Times must be in seconds (float numbers)
- Segments should be chronological
- Don't overlap segments"""

    user_prompt = f"""Here is the video transcript with timestamps:

{transcript_text}

Please analyze this transcript and return a JSON array of segments to keep, following the format specified."""

    print("Analyzing transcript with Anthropic Claude...")
    print(f"Model: {model}")

    try:
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
        )

        response_text = response.content[0].text.strip()

        # Extract JSON from response
        json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(0)

        segments = json.loads(response_text)

        # Validate and clean segments
        cleaned_segments = []
        for seg in segments:
            if 'start' in seg and 'end' in seg:
                cleaned_segments.append({
                    'start': float(seg['start']),
                    'end': float(seg['end'])
                })

        print(f"LLM selected {len(cleaned_segments)} segments to keep")
        return cleaned_segments

    except Exception as e:
        raise ValueError(f"Anthropic API error: {e}")


def analyze_transcript(
    transcript_text: str,
    instructions: str = "Keep only main points, remove fluff and redundancy",
    target_percentage: int = 35,
    provider: str = "openai",
    model: Optional[str] = None
) -> List[Dict[str, float]]:
    """
    Analyze transcript using specified LLM provider

    Args:
        transcript_text: Formatted transcript with timestamps
        instructions: User instructions for what to keep
        target_percentage: Target percentage of original length to keep
        provider: "openai" or "anthropic"
        model: Specific model to use (optional, uses default if not specified)

    Returns:
        List of segments with 'start' and 'end' times in seconds
    """
    if provider.lower() == "openai":
        model = model or "gpt-4"
        return analyze_transcript_with_openai(
            transcript_text, instructions, target_percentage, model
        )
    elif provider.lower() == "anthropic":
        model = model or "claude-3-5-sonnet-20241022"
        return analyze_transcript_with_anthropic(
            transcript_text, instructions, target_percentage, model
        )
    else:
        raise ValueError(f"Unknown provider: {provider}. Use 'openai' or 'anthropic'")
