# YouTube LLM Edit Tool

**Automatically cut YouTube videos to their main points using AI**

Feed a YouTube link to an LLM, get a DaVinci Resolve timeline that's already cut. Remove fluff, redundancy, intros, outros, and tangents—keep only the valuable content.

## How It Works

1. **Provide a YouTube URL** with your editing instructions
2. **Extract transcript** with precise timestamps
3. **LLM analyzes** the content and selects segments to keep
4. **Generate FCPXML** timeline file for DaVinci Resolve
5. **Download video** locally
6. **Import into Resolve** → your cuts appear automatically

## What This Does (And What It Doesn't)

This is **NOT** "AI edits your video inside Resolve."

This **IS** "AI produces an edit-decision timeline file that Resolve can import."

The LLM decides what's important based on the transcript. DaVinci Resolve simply imports a pre-cut timeline.

**Works best for:**
- Talking-head videos
- Tutorials and educational content
- Interviews and podcasts
- Lectures

**Less reliable for:**
- Purely visual content without narration
- Videos with important on-screen text that isn't read aloud
- Music videos or visual montages

## Installation

### 1. Clone and install dependencies

```bash
git clone <repo-url>
cd python-cheatsheet
pip install -r requirements.txt
```

### 2. Set up API keys

Create a `.env` file in the project root:

```bash
# For OpenAI (GPT-4, etc.)
OPENAI_API_KEY=your_openai_api_key_here

# For Anthropic (Claude)
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

You only need one API key (either OpenAI or Anthropic).

Get your API keys:
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/

## Usage

### Basic Usage

```bash
python main.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

This will:
- Use OpenAI GPT-4 by default
- Target ~35% of original video length
- Remove fluff and redundancy
- Save everything to `output/` directory

### Advanced Options

**Use Anthropic Claude instead:**
```bash
python main.py "URL" --provider anthropic
```

**Custom editing instructions:**
```bash
python main.py "URL" --instructions "Keep only actionable steps, remove theory and examples"
```

**Target specific compression ratio:**
```bash
python main.py "URL" --target 25  # Keep 25% of original
```

**Specify a model:**
```bash
python main.py "URL" --provider openai --model gpt-4-turbo
python main.py "URL" --provider anthropic --model claude-3-5-sonnet-20241022
```

**Custom output directory:**
```bash
python main.py "URL" --output-dir my_project
```

**Skip video download (if you already have it):**
```bash
python main.py "URL" --no-download
```

### Full Command Reference

```
python main.py URL [OPTIONS]

Required:
  URL                    YouTube video URL

Options:
  --instructions TEXT    What to keep/remove (default: "Keep main points, remove fluff")
  --target INT          Target % of original length (default: 35)
  --provider TEXT       LLM provider: "openai" or "anthropic" (default: openai)
  --model TEXT          Specific model to use
  --output-dir TEXT     Output directory (default: output)
  --no-download         Skip video download
  -h, --help            Show help
```

## Output Files

After running, you'll get:

```
output/
├── timeline.fcpxml    # Import this into DaVinci Resolve
├── cutlist.json       # Human-readable segment list
├── source.mp4         # Downloaded YouTube video
└── transcript.txt     # Full transcript with timestamps
```

## Importing into DaVinci Resolve

1. **Open DaVinci Resolve**

2. **Import the source video:**
   - `File → Import Media`
   - Select `output/source.mp4`
   - Drag it to your Media Pool

3. **Import the timeline:**
   - `File → Import → Timeline`
   - Select `output/timeline.fcpxml`

4. **Relink media if prompted:**
   - Point to `source.mp4` in the output folder

5. **Done!** Your cut-down timeline is ready to review, adjust, and export.

## Examples

### Example 1: Tutorial video, keep only steps
```bash
python main.py "https://youtube.com/watch?v=abc123" \
  --instructions "Keep only step-by-step instructions, remove explanations" \
  --target 20
```

### Example 2: Podcast, remove intro/outro
```bash
python main.py "https://youtube.com/watch?v=xyz789" \
  --instructions "Remove intro, outro, and sponsor reads. Keep main discussion" \
  --provider anthropic
```

### Example 3: Lecture, keep examples
```bash
python main.py "https://youtube.com/watch?v=def456" \
  --instructions "Keep definitions and examples, remove tangents" \
  --target 40
```

## Troubleshooting

### "Could not fetch transcript"
- The video may not have captions/subtitles available
- Try a different video or manually add captions on YouTube first

### "API key not set"
- Make sure you created a `.env` file with your API key
- Check that the key is valid and has credits

### "Media relinking" in Resolve
- Make sure both `source.mp4` and `timeline.fcpxml` are in the same folder
- Import `source.mp4` into Media Pool before importing the timeline

### Cuts seem wrong
- Try different `--instructions` to guide the LLM better
- Adjust `--target` percentage
- Try a different `--provider` (OpenAI vs Anthropic)
- Review `cutlist.json` to see what was selected

## Architecture

```
src/
├── video/
│   ├── transcript.py        # YouTube transcript extraction
│   ├── downloader.py        # Video download with yt-dlp
│   └── fcpxml_generator.py  # FCPXML timeline creation
├── llm/
│   └── analyzer.py          # LLM-based segment selection
└── utils/
    └── __init__.py
```

## Requirements

- Python 3.8+
- OpenAI API key OR Anthropic API key
- Internet connection for YouTube access and API calls
- DaVinci Resolve (free or Studio version)

## Cost Estimate

Typical cost per video:
- **OpenAI GPT-4:** $0.10 - $0.50 per video (depending on length)
- **Anthropic Claude:** $0.05 - $0.30 per video

Longer videos with longer transcripts cost more. The LLM analyzes the full transcript text.

## License

MIT License

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## Credits

Built with:
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube video download
- [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api) - Transcript extraction
- [OpenAI API](https://openai.com/) - GPT models
- [Anthropic API](https://anthropic.com/) - Claude models
