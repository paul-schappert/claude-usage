#!/usr/bin/env python3
# <swiftbar.title>Claude Usage</swiftbar.title>
# <swiftbar.version>1.0</swiftbar.version>
# <swiftbar.desc>Shows Claude.ai session and weekly usage in the macOS menu bar</swiftbar.desc>
# <swiftbar.refreshOnOpen>false</swiftbar.refreshOnOpen>
# <swiftbar.hideAbout>true</swiftbar.hideAbout>

import subprocess
import json
import os
import tempfile
from datetime import datetime, timezone

DEBUG = os.environ.get("CLAUDE_USAGE_DEBUG", "").lower() in ("1", "true", "yes")
USAGE_PAGE = "https://claude.ai/settings/usage"

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

# ── AppleScript templates ─────────────────────────────────────────────────────
# Chromium browsers all use the same AppleScript JS API as Chrome.
# Safari uses a slightly different syntax (do JavaScript ... in tab).
CHROMIUM_BROWSERS = [
    "Google Chrome",
    "Google Chrome Canary",
    "Brave Browser",
    "Microsoft Edge",
    "Arc",
    "Vivaldi",
    "Chromium",
]

def make_chromium_script(browser, js):
    safe_js = js.replace("\\", "\\\\").replace('"', '\\"')
    return f'''
tell application "{browser}"
    repeat with w in windows
        if URL of active tab of w contains "claude.ai" then
            return execute active tab of w javascript "{safe_js}"
        end if
    end repeat
    repeat with w in windows
        repeat with t in tabs of w
            if URL of t contains "claude.ai" then
                return execute t javascript "{safe_js}"
            end if
        end repeat
    end repeat
    return "__NO_TAB__"
end tell
'''

def make_safari_script(js):
    safe_js = js.replace("\\", "\\\\").replace('"', '\\"')
    return f'''
tell application "Safari"
    repeat with w in windows
        if URL of current tab of w contains "claude.ai" then
            return do JavaScript "{safe_js}" in current tab of w
        end if
    end repeat
    repeat with w in windows
        repeat with t in tabs of w
            if URL of t contains "claude.ai" then
                return do JavaScript "{safe_js}" in t
            end if
        end repeat
    end repeat
    return "__NO_TAB__"
end tell
'''

def run_applescript(script):
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.applescript', delete=False) as f:
            f.write(script)
            tmp = f.name
        r = subprocess.run(["osascript", tmp], capture_output=True, text=True, timeout=15)
        out = r.stdout.strip()
        err = r.stderr.strip()
        if "Allow JavaScript from Apple Events" in err:
            return "__JS_DISABLED__"
        return out if out else None
    except Exception:
        return None
    finally:
        if tmp and os.path.exists(tmp):
            os.unlink(tmp)

def is_running(app_name):
    r = subprocess.run(
        ["osascript", "-e", f'tell application "System Events" to return (name of processes) contains "{app_name}"'],
        capture_output=True, text=True, timeout=5
    )
    return r.stdout.strip() == "true"

def fetch_usage():
    for browser in CHROMIUM_BROWSERS:
        if not is_running(browser):
            continue
        result = run_applescript(make_chromium_script(browser, FETCH_JS))
        if result == "__JS_DISABLED__":
            return {"_error": "js_disabled"}
        if result and result != "__NO_TAB__" and result.startswith("{"):
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                continue

    if is_running("Safari"):
        result = run_applescript(make_safari_script(FETCH_JS))
        if result == "__JS_DISABLED__":
            return {"_error": "js_disabled"}
        if result and result != "__NO_TAB__" and result.startswith("{"):
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                pass

    return None

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
    raw = fetch_usage()

    if raw is None:
        print("Claude")
        print("---")
        print("Open a claude.ai tab in Chrome or Safari")
        print(f"Open Claude | href=https://claude.ai")
        return

    if "_error" in raw:
        err = raw["_error"]
        print("Claude ⚠")
        print("---")
        if err == "js_disabled":
            print("Enable: Chrome → View → Developer → Allow JavaScript from Apple Events")
        elif err == "no_org_id":
            print("Could not read org ID — are you logged in to Claude?")
        elif err == "no_endpoint_worked":
            print("Could not find usage API endpoint")
        else:
            print(f"Error: {err}")
        print(f"Open Claude Usage | href={USAGE_PAGE}")
        return

    data = raw.get("_data", raw)
    endpoint_used = raw.get("_endpoint", "?")

    if DEBUG:
        print("Claude: DEBUG")
        print("---")
        print(f"Endpoint: {endpoint_used}")
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

    has_session = sl_pct is not None
    has_weekly  = wl_pct is not None
    reset_mins  = minutes_until(reset_at)

    parts = []
    if has_session:
        parts.append(str(round(float(sl_pct))))
    if reset_mins is not None:
        parts.append(str(reset_mins))
    bar = " │ ".join(parts) if parts else "Claude"

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
