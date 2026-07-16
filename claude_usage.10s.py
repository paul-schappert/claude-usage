#!/usr/bin/env python3
# <swiftbar.title>Claude Usage</swiftbar.title>
# <swiftbar.version>1.2</swiftbar.version>
# <swiftbar.desc>Shows Claude.ai session and weekly usage in the macOS menu bar</swiftbar.desc>
# <swiftbar.refreshOnOpen>false</swiftbar.refreshOnOpen>
# <swiftbar.hideAbout>true</swiftbar.hideAbout>

import subprocess
import json
import os
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

DEBUG = os.environ.get("CLAUDE_USAGE_DEBUG", "").lower() in ("1", "true", "yes")
USAGE_PAGE = "https://claude.ai/settings/usage"
HINT_TIMEOUT = 2   # seconds for the known-good tab hint
DISCOVERY_TIMEOUT = 8  # seconds per tab during parallel fallback discovery
CACHE_FILE = os.path.expanduser("~/.claude-usage-tab-hint.json")

# ── JavaScript to run inside the browser tab ──────────────────────────────────
FETCH_JS = r"""
(function() {
    var cookies = {};
    document.cookie.split(';').forEach(function(c) {
        var parts = c.trim().split('=');
        var key = parts.shift().trim();
        cookies[key] = parts.join('=');
    });
    var orgId = cookies['lastActiveOrg'];
    if (!orgId) return JSON.stringify({_error: 'no_org_id'});
    var endpoints = [
        '/api/organizations/' + orgId + '/usage',
        '/api/organizations/' + orgId + '/rate_limits',
    ];
    for (var i = 0; i < endpoints.length; i++) {
        try {
            var xhr = new XMLHttpRequest();
            xhr.open('GET', endpoints[i], false);
            xhr.setRequestHeader('Accept', 'application/json');
            xhr.send();
            if (xhr.status === 200) {
                return JSON.stringify({_endpoint: endpoints[i], _data: JSON.parse(xhr.responseText)});
            }
        } catch(e) {}
    }
    return JSON.stringify({_error: 'no_endpoint_worked', _orgId: orgId});
})()
"""

# ── Browser support ──────────────────────────────────────────────────────────
CHROMIUM_BROWSERS = [
    "Google Chrome",
    "Google Chrome Canary",
    "Brave Browser",
    "Microsoft Edge",
    "Arc",
    "Vivaldi",
    "Chromium",
]

# ── Cache ────────────────────────────────────────────────────────────────────

def load_tab_hint():
    try:
        with open(CACHE_FILE) as f:
            return json.load(f)
    except Exception:
        return None

def save_tab_hint(tab_info):
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(tab_info, f)
    except Exception:
        pass

# ── AppleScript helpers ──────────────────────────────────────────────────────

def run_applescript(script, timeout=60):
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.applescript', delete=False) as f:
            f.write(script)
            tmp = f.name
        r = subprocess.run(["osascript", tmp], capture_output=True, text=True, timeout=timeout)
        out = r.stdout.strip()
        err = r.stderr.strip()
        if "Allow JavaScript from Apple Events" in err:
            return "__JS_DISABLED__"
        if "-1712" in err or "AppleEvent timed out" in err:
            return "__APPLEEVENT_TIMEOUT__"
        if err and not out:
            return f"__ERR__:{err.splitlines()[-1][:200]}"
        return out if out else None
    except subprocess.TimeoutExpired:
        return "__SUBPROCESS_TIMEOUT__"
    except Exception as e:
        return f"__ERR__:{type(e).__name__}: {str(e)[:200]}"
    finally:
        if tmp and os.path.exists(tmp):
            os.unlink(tmp)

def is_running(app_name):
    r = subprocess.run(
        ["osascript", "-e", f'tell application "System Events" to return (name of processes) contains "{app_name}"'],
        capture_output=True, text=True, timeout=5
    )
    return r.stdout.strip() == "true"

# ── Tab discovery (single fast AppleEvent per browser) ───────────────────────

def find_claude_tabs_chromium(browser):
    """Returns (active_tabs, inactive_tabs) where each is a list of (wi, ti).
    Uses a single bulk call to get all URLs + active tab indices."""
    script = f'''
tell application "{browser}"
    set allUrls to URL of every tab of every window
    set activeIdxs to active tab index of every window
    set out to ""
    set wi to 0
    repeat with winUrls in allUrls
        set wi to wi + 1
        set ai to item wi of activeIdxs
        set ti to 0
        repeat with u in winUrls
            set ti to ti + 1
            if (u as text) contains "claude.ai" then
                if ti = ai then
                    set out to out & "A:" & wi & ":" & ti & linefeed
                else
                    set out to out & "I:" & wi & ":" & ti & linefeed
                end if
            end if
        end repeat
    end repeat
    return out
end tell
'''
    raw = run_applescript(script, timeout=10)
    if isinstance(raw, str) and raw.startswith("__"):
        return raw, []
    if not raw:
        return [], []
    active, inactive = [], []
    for line in raw.strip().splitlines():
        parts = line.split(":")
        if len(parts) == 3:
            try:
                loc = (int(parts[1]), int(parts[2]))
                (active if parts[0] == "A" else inactive).append(loc)
            except ValueError:
                continue
    return active, inactive

def find_claude_tabs_safari():
    """Same as chromium variant but for Safari."""
    script = '''
tell application "Safari"
    set out to ""
    set wi to 0
    repeat with w in windows
        set wi to wi + 1
        try
            set ci to index of current tab of w
            set tabList to tabs of w
            set ti to 0
            repeat with t in tabList
                set ti to ti + 1
                try
                    if URL of t contains "claude.ai" then
                        if ti = ci then
                            set out to out & "A:" & wi & ":" & ti & linefeed
                        else
                            set out to out & "I:" & wi & ":" & ti & linefeed
                        end if
                    end if
                end try
            end repeat
        end try
    end repeat
    return out
end tell
'''
    raw = run_applescript(script, timeout=10)
    if isinstance(raw, str) and raw.startswith("__"):
        return raw, []
    if not raw:
        return [], []
    active, inactive = [], []
    for line in raw.strip().splitlines():
        parts = line.split(":")
        if len(parts) == 3:
            try:
                loc = (int(parts[1]), int(parts[2]))
                (active if parts[0] == "A" else inactive).append(loc)
            except ValueError:
                continue
    return active, inactive

# ── JS execution on a specific tab ───────────────────────────────────────────

def make_exec_script_chromium(browser, wi, ti, js):
    safe_js = js.replace("\\", "\\\\").replace('"', '\\"')
    return f'''
tell application "{browser}"
    return execute tab {ti} of window {wi} javascript "{safe_js}"
end tell
'''

def make_exec_script_safari(wi, ti, js):
    safe_js = js.replace("\\", "\\\\").replace('"', '\\"')
    return f'''
tell application "Safari"
    return do JavaScript "{safe_js}" in tab {ti} of window {wi}
end tell
'''

# ── Parallel tab execution ───────────────────────────────────────────────────

def parse_js_result(raw):
    """Parse a JS execution result. Returns dict on success, None on failure."""
    if not raw or not isinstance(raw, str):
        return None
    if raw.startswith("__"):
        if raw == "__JS_DISABLED__":
            return {"_error": "js_disabled"}
        return None  # timeout/error — tab is discarded
    if raw.startswith("{"):
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return None
    return None

def try_single_tab(browser_type, browser_name, wi, ti, js, timeout=HINT_TIMEOUT):
    """Execute JS on one tab. Returns (result_dict, tab_info) or (None, None)."""
    if browser_type == "chromium":
        script = make_exec_script_chromium(browser_name, wi, ti, js)
    else:
        script = make_exec_script_safari(wi, ti, js)
    raw = run_applescript(script, timeout=timeout)
    parsed = parse_js_result(raw)
    if parsed is not None:
        return parsed, {"browser_type": browser_type, "browser": browser_name, "wi": wi, "ti": ti}
    return None, None

def try_tabs_parallel(tab_specs, js, timeout=DISCOVERY_TIMEOUT):
    """Try multiple tabs in parallel, return first success.
    tab_specs: list of (browser_type, browser_name, wi, ti)"""
    if not tab_specs:
        return None, None
    # For a single tab, just run it directly
    if len(tab_specs) == 1:
        bt, bn, wi, ti = tab_specs[0]
        return try_single_tab(bt, bn, wi, ti, js, timeout=timeout)
    with ThreadPoolExecutor(max_workers=min(len(tab_specs), 8)) as pool:
        futures = {}
        for bt, bn, wi, ti in tab_specs:
            f = pool.submit(try_single_tab, bt, bn, wi, ti, js, timeout=timeout)
            futures[f] = (bt, bn, wi, ti)
        for f in as_completed(futures):
            result, tab_info = f.result()
            if result is not None:
                # Cancel remaining futures (they'll hit timeout anyway)
                for other in futures:
                    if other is not f:
                        other.cancel()
                return result, tab_info
    return None, None

# ── Main fetch logic ─────────────────────────────────────────────────────────

def fetch_usage():
    # 1. If we have a tab hint from last time, try it first (fast single attempt)
    hint = load_tab_hint()
    if hint:
        result, tab_info = try_single_tab(
            hint["browser_type"], hint["browser"],
            hint["wi"], hint["ti"], FETCH_JS
        )
        if result is not None and "_error" not in result:
            save_tab_hint(tab_info)
            return result, "hint"

    # 3. Full discovery: find all claude.ai tabs across browsers
    all_active = []   # (browser_type, browser_name, wi, ti)
    all_inactive = []
    any_browser = False
    last_err = None

    for browser in CHROMIUM_BROWSERS:
        if not is_running(browser):
            continue
        any_browser = True
        found = find_claude_tabs_chromium(browser)
        if isinstance(found[0], str) and found[0].startswith("__"):
            if found[0] == "__JS_DISABLED__":
                return {"_error": "js_disabled"}, None
            last_err = found[0]
            continue
        active, inactive = found
        for wi, ti in active:
            all_active.append(("chromium", browser, wi, ti))
        for wi, ti in inactive:
            all_inactive.append(("chromium", browser, wi, ti))

    if is_running("Safari"):
        any_browser = True
        found = find_claude_tabs_safari()
        if isinstance(found[0], str) and found[0].startswith("__"):
            if found[0] == "__JS_DISABLED__":
                return {"_error": "js_disabled"}, None
            last_err = found[0]
        else:
            active, inactive = found
            for wi, ti in active:
                all_active.append(("safari", "Safari", wi, ti))
            for wi, ti in inactive:
                all_inactive.append(("safari", "Safari", wi, ti))

    any_claude_tab = bool(all_active or all_inactive)

    # 4. Try active tabs first (instant), then inactive tabs in parallel
    if all_active:
        result, tab_info = try_tabs_parallel(all_active, FETCH_JS)
        if result is not None and "_error" not in result:
            save_tab_hint(tab_info)
            return result, "active"
        if result is not None:
            return result, None

    if all_inactive:
        result, tab_info = try_tabs_parallel(all_inactive, FETCH_JS)
        if result is not None and "_error" not in result:
            save_tab_hint(tab_info)
            return result, "inactive"
        if result is not None:
            return result, None

    # 5. Nothing worked
    if last_err:
        return {"_error": last_err}, None
    if any_claude_tab:
        return {"_error": "all_tabs_discarded"}, None
    if any_browser:
        return {"_error": "no_tab"}, None
    return {"_error": "no_browser"}, None

# ── helpers ───────────────────────────────────────────────────────────────────
def flatten(data, prefix="", out=None):
    if out is None:
        out = {}
    if isinstance(data, dict):
        for k, v in data.items():
            flatten(v, f"{prefix}.{k}" if prefix else str(k), out)
    elif isinstance(data, list):
        for i, v in enumerate(data[:10]):
            flatten(v, f"{prefix}[{i}]", out)
    else:
        out[prefix] = data
    return out

def dhm(val):
    if val is None:
        return None
    try:
        dt = datetime.fromisoformat(str(val))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        secs = (dt - datetime.now(timezone.utc)).total_seconds()
        if secs <= 0:
            return "soon"
        d = int(secs // 86400)
        h = int((secs % 86400) // 3600)
        m = int((secs % 3600) // 60)
        parts = []
        if d: parts.append(f"{d}d")
        if h: parts.append(f"{h}h")
        if m: parts.append(f"{m}m")
        return " ".join(parts) if parts else "soon"
    except Exception:
        return None

def minutes_until(val):
    if val is None:
        return None
    try:
        dt = datetime.fromisoformat(str(val))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        secs = (dt - datetime.now(timezone.utc)).total_seconds()
        return int(secs // 60) if secs > 0 else 0
    except Exception:
        return None

# ── main ──────────────────────────────────────────────────────────────────────
def main():
    raw, source = fetch_usage()

    if raw is None or "_error" in raw:
        err = (raw or {}).get("_error", "unknown")
        print("Claude \u26a0 | color=#FF6B6B darkColor=#FF6B6B")
        print("---")
        if err == "js_disabled":
            print("Enable: Chrome \u2192 View \u2192 Developer \u2192 Allow JavaScript from Apple Events")
        elif err == "no_org_id":
            print("Could not read org ID \u2014 are you logged in to Claude?")
        elif err == "no_endpoint_worked":
            print("Could not find usage API endpoint")
        elif err == "no_tab":
            print("No claude.ai tab found in any browser")
        elif err == "all_tabs_discarded":
            print("All claude.ai tabs are suspended by Chrome")
            print("Visit any claude.ai tab to wake it up")
        elif err == "no_browser":
            print("No supported browser is running")
        elif err == "applescript_timeout":
            print("AppleEvent timed out talking to the browser")
        elif err == "subprocess_timeout":
            print("osascript timed out \u2014 browser is unresponsive")
        else:
            print(f"Error: {err}")
        print("---")
        print(f"Open Claude Usage | href={USAGE_PAGE}")
        print("Refresh | refresh=true")
        return

    data = raw.get("_data", raw)
    endpoint_used = raw.get("_endpoint", "?")

    if DEBUG:
        print("Claude: DEBUG")
        print("---")
        print(f"Endpoint: {endpoint_used}")
        print(f"Source: {source}")
        print("---")
        flat = flatten(data)
        for k, v in sorted(flat.items()):
            print(f"{k}: {v}")
        return

    flat = flatten(data)

    sl_pct      = flat.get("five_hour.utilization")
    wl_pct      = flat.get("seven_day.utilization")
    reset_at    = flat.get("five_hour.resets_at")
    wl_reset_at = flat.get("seven_day.resets_at")

    # Publish the account-wide usage for the Claude Code status line
    # (~/.claude/scripts/statusline.sh reads ~/.claude/cache/ratelimits.tsv,
    # newest epoch wins). This catches usage from claude.ai chats too, which
    # idle Claude Code windows can't see.
    if sl_pct is not None and wl_pct is not None:
        try:
            import time as _time
            _dir = os.path.expanduser("~/.claude/cache")
            os.makedirs(_dir, exist_ok=True)
            _tmp = os.path.join(_dir, ".ratelimits.tsv.tmp")
            with open(_tmp, "w") as _fh:
                _fh.write(f"{int(_time.time())}\t{round(float(sl_pct))}\t{round(float(wl_pct))}\n")
            os.replace(_tmp, os.path.join(_dir, "ratelimits.tsv"))
        except Exception:
            pass  # never break the menu bar over the status-line cache

    has_session = sl_pct is not None
    has_weekly  = wl_pct is not None
    reset_mins  = minutes_until(reset_at)

    parts = []
    if has_session:
        parts.append(str(round(float(sl_pct))))
    if reset_mins is not None:
        parts.append(str(reset_mins))
    bar = " \u2502 ".join(parts) if parts else "Claude"

    print(f"{bar} | color=#FFFFFF darkColor=#FFFFFF")
    link = f"href={USAGE_PAGE}"
    print("---")
    if has_session:
        print(f"Session (5h):  {round(float(sl_pct))}% | {link}")
    if reset_at:
        print(f"Resets in {dhm(reset_at)} | {link}")
    print("---")
    if has_weekly:
        print(f"Weekly (7d):   {round(float(wl_pct))}% | {link}")
    if wl_reset_at:
        print(f"Resets in {dhm(wl_reset_at)} | {link}")
    print("---")
    print("Refresh | refresh=true")


if __name__ == "__main__":
    main()
