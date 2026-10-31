"""End-to-end in Chrome: load dist/chrome/ (run build.py first) into Playwright's Chromium as an unpacked extension,
like chrome://extensions → "Load unpacked", and serve the fixtures as old.reddit.com / www.reddit.com."""
import json, sys, tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).parent
EXT = (HERE.parent / (sys.argv[1] if len(sys.argv) > 1 else "dist/chrome")).resolve()
FIX = HERE / "fixtures"

ROUTES = {"/r/all/": "listing.html", "/r/Frugal/comments/abc/beans/": "thread.html"}


def serve(route):
    url = route.request.url
    path = "/" + url.split("reddit.com/", 1)[1]
    if "www.reddit.com/r/new-design/" in url:
        return route.fulfill(status=200, body=(FIX / "newreddit.html").read_bytes(), headers={"content-type": "text/html; charset=utf-8"})
    name = ROUTES.get(path.split("?")[0]) or path.rsplit("/", 1)[-1]
    f = FIX / name
    if not f.exists():
        return route.fulfill(status=404, body="")
    ctype = "text/css" if f.suffix == ".css" else "text/html; charset=utf-8"
    route.fulfill(status=200, body=f.read_bytes(), headers={"content-type": ctype})


failures = []
def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + (f"  ({detail})" if detail else ""))
    if not cond:
        failures.append(name)

if not (EXT / "manifest.json").exists():
    sys.exit(f"{EXT} has no manifest.json: run python build.py first")

with sync_playwright() as p, tempfile.TemporaryDirectory() as profile:
    # Extensions need the full Chromium build ("chromium" channel), not the headless shell.
    ctx = p.chromium.launch_persistent_context(
        profile,
        channel="chromium",
        headless=True,
        args=[f"--disable-extensions-except={EXT}", f"--load-extension={EXT}"],
        viewport={"width": 412, "height": 915},
        screen={"width": 412, "height": 915},
    )
    ctx.route("**/old.reddit.com/**", serve)
    ctx.route("**/www.reddit.com/**", serve)
    pg = ctx.new_page()
    logs = []
    pg.on("console", lambda m: logs.append(f"{m.type}: {m.text}"))
    pg.on("pageerror", lambda e: logs.append(f"pageerror: {e}"))

    for host, path, shot in (("old", "/r/all/", "chrome_listing.png"), ("old", "/r/Frugal/comments/abc/beans/", "chrome_thread.png"), ("www", "/r/all/", "chrome_www_listing.png")):
        pg.goto(f"https://{host}.reddit.com{path}")
        pg.wait_for_timeout(1500)
        path = host + ":" + path
        state = pg.evaluate("""[document.documentElement.className,
            [...document.querySelectorAll('meta[name=viewport]')].map(m => m.outerHTML),
            !!document.querySelector("#orm-drawer"), document.documentElement.scrollWidth, document.documentElement.dataset.ormVersion || null]""")
        check(f"{path}: extension active", "orm" in state[0].split() and state[2], json.dumps(state))
        check(f"{path}: our viewport meta only", state[1] == ['<meta name="viewport" data-orm="1" content="width=device-width, initial-scale=1">'], json.dumps(state[1]))
        check(f"{path}: fits 412px", state[3] <= 412, str(state[3]))
        check(f"{path}: chrome.runtime reachable", state[4] is not None, str(state[4]))
        pg.screenshot(path=str(HERE / "shots" / shot))

    # The "Use subreddit styles" switch persists through chrome.storage.local.
    pg.goto("https://old.reddit.com/r/all/")
    pg.wait_for_timeout(1000)
    pg.evaluate("""() => { const b = document.getElementById('orm-substyles'); b.checked = !b.checked; b.dispatchEvent(new Event('change', {bubbles: true})); }""")
    pg.wait_for_timeout(300)
    pg.reload()
    pg.wait_for_timeout(1000)
    check("subreddit-styles setting survives reload", pg.evaluate("document.getElementById('orm-substyles').checked") is True)

    pg.goto("https://www.reddit.com/r/new-design/")
    pg.wait_for_timeout(1000)
    state = pg.evaluate("[document.documentElement.className, [...document.querySelectorAll('meta[name=viewport]')].map(m => m.outerHTML), !!document.querySelector('#orm-drawer, #orm-bar')]")
    check("www new design: left alone", state == ["", ['<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'], False], json.dumps(state))
    ctx.close()

for line in logs:
    print("  console", line)
print(f"\n{len(failures)} failure(s)" if failures else "\nall chrome e2e checks passed")
sys.exit(1 if failures else 0)
