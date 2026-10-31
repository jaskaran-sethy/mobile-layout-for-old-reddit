"""End-to-end: load extension/ into Playwright's Firefox as a temporary add-on (like about:debugging does)
and serve the fixtures as old.reddit.com, so the content script runs exactly as it does for a real user."""
import json, socket, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).parent
EXT = (HERE.parent / (sys.argv[1] if len(sys.argv) > 1 else "extension")).resolve()
FIX = HERE / "fixtures"
PORT = 6111

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


def install_temporary_addon(path):
    """Firefox Remote Debugging Protocol: packets are '<length>:<json>'."""
    s = None
    for _ in range(50):
        try:
            s = socket.create_connection(("127.0.0.1", PORT), timeout=10)
            break
        except OSError:
            time.sleep(0.2)
    buf = b""

    def recv():
        nonlocal buf
        while b":" not in buf:
            buf += s.recv(65536)
        n, rest = buf.split(b":", 1)
        n = int(n)
        while len(rest) < n:
            rest += s.recv(65536)
        buf = rest[n:]
        return json.loads(rest[:n])

    def send(msg):
        data = json.dumps(msg).encode()
        s.sendall(str(len(data)).encode() + b":" + data)

    recv()  # greeting
    send({"to": "root", "type": "getRoot"})
    root = recv()
    while "addonsActor" not in root:
        root = recv()
    send({"to": root["addonsActor"], "type": "installTemporaryAddon", "addonPath": str(path)})
    reply = recv()
    s.close()
    return reply


failures = []
def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + (f"  ({detail})" if detail else ""))
    if not cond:
        failures.append(name)

with sync_playwright() as p:
    browser = p.firefox.launch(
        headless=True,
        args=["-start-debugger-server", str(PORT)],
        firefox_user_prefs={
            "devtools.debugger.remote-enabled": True,
            "devtools.debugger.prompt-connection": False,
            "devtools.chrome.enabled": True,
            "xpinstall.signatures.required": False,
        },
    )
    print("install:", json.dumps(install_temporary_addon(EXT)))
    ctx = browser.new_context(viewport={"width": 412, "height": 915}, screen={"width": 412, "height": 915})
    ctx.route("**/old.reddit.com/**", serve)
    ctx.route("**/www.reddit.com/**", serve)
    pg = ctx.new_page()
    logs = []
    pg.on("console", lambda m: logs.append(f"{m.type}: {m.text}"))
    pg.on("pageerror", lambda e: logs.append(f"pageerror: {e}"))

    for host, path, shot in (("old", "/r/all/", "e2e_listing.png"), ("old", "/r/Frugal/comments/abc/beans/", "e2e_thread.png"), ("www", "/r/all/", "e2e_www_listing.png")):
        path = host + ":" + path
        pg.goto(f"https://{host}.reddit.com" + path.split(":", 1)[1])
        pg.wait_for_timeout(1500)
        state = pg.evaluate("""[document.documentElement.className,
            [...document.querySelectorAll('meta[name=viewport]')].map(m => m.outerHTML),
            !!document.querySelector("#orm-drawer"), document.documentElement.scrollWidth, document.documentElement.dataset.ormVersion || null]""")
        check(f"{path}: extension active", "orm" in state[0].split() and state[2], json.dumps(state))
        check(f"{path}: our viewport meta only", state[1] == ['<meta name="viewport" data-orm="1" content="width=device-width, initial-scale=1">'], json.dumps(state[1]))
        check(f"{path}: fits 412px", state[3] <= 412, str(state[3]))
        pg.screenshot(path=str(HERE / "shots" / shot))
    pg.goto("https://www.reddit.com/r/new-design/")
    pg.wait_for_timeout(1000)
    state = pg.evaluate("[document.documentElement.className, [...document.querySelectorAll('meta[name=viewport]')].map(m => m.outerHTML), !!document.querySelector('#orm-drawer, #orm-bar')]")
    check("www new design: left alone", state == ["", ['<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'], False], json.dumps(state))
    browser.close()

for line in logs:
    print("  console", line)
print(f"\n{len(failures)} failure(s)" if failures else "\nall e2e checks passed")
sys.exit(1 if failures else 0)
