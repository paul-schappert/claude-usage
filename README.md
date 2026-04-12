# Claude Usage

A [SwiftBar](https://swiftbar.app) plugin that shows your Claude.ai usage in the macOS menu bar.

```
32 │ 58      ← session % used │ minutes until session reset
```

Click to see the full breakdown and open your usage page:

```
Session (5h):  32%
Resets in 58m
──────────────
Weekly (7d):   22%
Resets in 3d 15h 58m
──────────────
Refresh
```

## How it works

Injects a small JavaScript snippet into an existing browser tab on claude.ai via AppleScript, making an authenticated API call using your existing browser session. No API keys, no cookie extraction, no pip dependencies - just Python 3 standard library.

**Note:** This uses Claude.ai's internal API, which could change without notice.

## Setup

**Prerequisites:** macOS, Python 3.7+, a Claude.ai account (Pro/Team/Enterprise).

1. Install SwiftBar:
   ```bash
   brew install --cask swiftbar
   ```

2. Clone this repo:
   ```bash
   git clone https://github.com/paul-schappert/claude-usage.git ~/claude-usage
   ```

3. Make the plugin executable:
   ```bash
   chmod +x ~/claude-usage/claude_usage.10s.py
   ```

4. Enable JavaScript from Apple Events in your browser:

   **Chrome/Chromium:** View → Developer → Allow JavaScript from Apple Events

   **Safari:** Develop → Allow JavaScript from Apple Events (enable the Develop menu in Safari → Settings → Advanced first)

5. Open SwiftBar and set the plugin directory to `~/claude-usage`.

That's it. Keep a claude.ai tab open in your browser and your usage will appear in the menu bar.

## Configuration

| What | How |
|------|-----|
| Refresh interval | Rename the file - the `10s` in `claude_usage.10s.py` controls it (e.g., `30s`, `1m`, `5m`) |
| Debug mode | `CLAUDE_USAGE_DEBUG=1 python3 claude_usage.10s.py` - dumps raw API response |

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| "Claude" with no numbers | Open a claude.ai tab in your browser |
| "Claude ⚠" with JS error | Enable JavaScript from Apple Events in your browser (step 4) |
| Nothing in menu bar | Make sure SwiftBar is running and pointed at the right plugin folder |
| Numbers look stale | Click the dropdown → Refresh |

## Supported browsers

Chrome, Brave, Arc, Edge, Vivaldi, Chromium, Safari.

## Requirements

macOS only - uses AppleScript and SwiftBar, which are macOS-specific.

## License

MIT
