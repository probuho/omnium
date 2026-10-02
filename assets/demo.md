# Demo GIF Placeholder

This is a placeholder for the demo GIF. To create a real demo:

1. Run the TUI: `omnium`
2. Record with a tool like:
   - `ffmpeg -f gdigest -framerate 10 -i desktop -vf "scale=800:-1" demo.gif` (Windows)
   - `peek` or `byzanz` (Linux)
   - ScreenToGif (Windows)
2. Save as `assets/demo.gif` (max 2MB recommended)

Or use a static SVG as fallback:
```markdown
![Omnium Suite Demo](assets/demo.svg)
```