"""Load the fixtures in Playwright Firefox at phone width with the extension injected at document start,
check for horizontal overflow and exercise the interactions, and save screenshots to test/shots/."""
import json, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).parent
EXT = HERE.parent / "extension"
SHOTS = HERE / "shots"
SHOTS.mkdir(exist_ok=True)

css = (EXT / "mobile.css").read_text(encoding="utf-8")
js = (EXT / "mobile.js").read_text(encoding="utf-8")
INIT = (
    "document.documentElement.dataset.ormForce = '1';"
    f"(() => {{ const s = document.createElement('style'); s.textContent = {json.dumps(css)}; document.documentElement.append(s); }})();"
    + js
)

OVERFLOW_JS = """() => {
  const w = innerWidth, bad = [];
  for (const el of document.querySelectorAll('body *')) {
    const r = el.getBoundingClientRect();
    if (r.width && r.height && r.right > w + 1 && getComputedStyle(el).position !== 'fixed' && !el.closest('.side, pre, #sr-header-area, .tabmenu, #header-bottom-right'))
      bad.push(el.tagName.toLowerCase() + '.' + [...el.classList].join('.') + ' right=' + Math.round(r.right));
  }
  return { scrollWidth: document.documentElement.scrollWidth, innerWidth: w, overflowing: bad.slice(0, 10) };
}"""

failures = []

def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + (f"  ({detail})" if detail else ""))
    if not cond:
        failures.append(name)

with sync_playwright() as p:
    b = p.firefox.launch()
    fx = (HERE / "fixtures").resolve().as_uri()

    before = b.new_context(viewport={"width": 412, "height": 915})
    pg = before.new_page()
    for name in ("listing", "thread"):
        pg.goto(f"{fx}/{name}.html")
        pg.screenshot(path=str(SHOTS / f"before_{name}.png"))
    before.close()

    ctx = b.new_context(viewport={"width": 412, "height": 915}, screen={"width": 412, "height": 915})
    ctx.add_init_script(INIT)
    pg = ctx.new_page()
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))

    # ---- listing ----
    pg.goto(f"{fx}/listing.html")
    pg.wait_for_timeout(300)
    ov = pg.evaluate(OVERFLOW_JS)
    check("listing: no horizontal overflow", ov["scrollWidth"] <= 412 and not ov["overflowing"], json.dumps(ov))
    check("listing: html.orm set again after reddit-style class overwrite", pg.evaluate("['js', 'orm'].every(c => document.documentElement.classList.contains(c))"))
    metas = pg.evaluate("[...document.querySelectorAll('meta[name=viewport]')].map(m => [m.content, m.parentNode.tagName])")
    check("listing: single viewport meta (ours, in head), page's own removed", metas == [["width=device-width, initial-scale=1", "HEAD"]], str(metas))
    check("listing: subreddit style disabled", pg.evaluate("document.querySelector('link[title=applied_subreddit_stylesheet]').disabled"))
    check("listing: chooser hidden", pg.evaluate("getComputedStyle(document.querySelector('.listing-chooser')).display") == "none")
    check("listing: drawer closed", pg.evaluate("getComputedStyle(document.querySelector('#orm-drawer')).display") == "none")
    check("listing: subreddit bar hidden", pg.evaluate("getComputedStyle(document.querySelector('#sr-header-area')).display") == "none")
    check("listing: get-new-reddit hidden", pg.evaluate("getComputedStyle(document.querySelector('.redesign-beta-optin')).display") == "none")
    check("listing: email banner hidden", pg.evaluate("[...document.querySelectorAll('.verify-nag-wrapper, .verify-nag-wrapper > div')].some(e => getComputedStyle(e).display === 'none')"))
    check("listing: account row + sidebar moved into drawer", pg.evaluate("!!document.querySelector('#orm-drawer #header-bottom-right') && !!document.querySelector('#orm-drawer .side')"))
    feeds = pg.evaluate("[...document.querySelectorAll('#orm-drawer .orm-main-feeds a')].map(a => a.textContent + ' ' + new URL(a.href).pathname)")
    check("drawer: Home / Popular / All at the top", feeds == ["Home /", "Popular /r/popular/", "All /r/all/"] and pg.evaluate("document.querySelector('#orm-drawer').firstElementChild.className") == "orm-main-feeds", str(feeds))
    chips = pg.evaluate("[...document.querySelectorAll('#orm-drawer .orm-chip')].map(a => a.textContent)")
    check("drawer: other feeds as chips, main three not repeated", chips == ["mod", "users"], str(chips))
    subs = pg.evaluate("[...document.querySelectorAll('#orm-drawer .orm-subs a')].map(a => a.textContent)")
    check("drawer: subscriptions from the my-subreddits menu", subs == ["AskReddit", "pics", "news", "thegrandtour", "technology"], str(subs))
    check("drawer: edit subscriptions link", pg.evaluate("document.querySelector('#orm-drawer .orm-edit-subs')?.textContent") == "edit subscriptions")
    bar = pg.evaluate("""(() => { const r = s => document.querySelector(s).getBoundingClientRect(), b = r('#orm-menu-btn'), t = r('#orm-title'), h = r('#header');
        const hidden = ['#header-img', '#header .pagename'].map(s => getComputedStyle(document.querySelector(s)).display);
        return [document.querySelector('#orm-title').textContent, Math.round(b.right), Math.round(b.top), Math.round(t.top), Math.round(h.height), hidden]; })()""")
    check("header: bar with title r/all, ☰ top-right, reddit logo/pagename hidden", bar[0] == "r/all" and bar[1] == 412 and bar[2] == 0 and bar[3] < 30 and bar[4] < 60 and bar[5] == ["none", "none"], str(bar))
    visible = pg.evaluate("[...document.querySelector('.thing.link .buttons').children].filter(li => getComputedStyle(li).display !== 'none').map(li => li.textContent.trim())")
    check("listing: only comments + ⋯ visible", visible == ["98 comments", "⋯"], str(visible))
    title_box = pg.evaluate("(() => { const r = document.querySelector('a.title').getBoundingClientRect(); return [r.right, r.height]; })()")
    check("listing: title wraps within screen", title_box[0] <= 412 and title_box[1] > 30, str(title_box))
    arrow = pg.evaluate("(() => { const r = document.querySelector('.arrow.up').getBoundingClientRect(); return [Math.round(r.width), Math.round(r.height)]; })()")
    check("listing: vote arrow enlarged", arrow[0] >= 20, str(arrow))
    pg.screenshot(path=str(SHOTS / "after_listing.png"))
    pg.evaluate("scrollTo(0, 1500)")
    pg.wait_for_timeout(100)
    stuck = pg.evaluate("(() => { const b = document.querySelector('#orm-bar').getBoundingClientRect(); return [scrollY, Math.round(b.top), Math.round(b.right), getComputedStyle(document.body).overflowX]; })()")
    check("top bar sticks to the top while scrolling", stuck[0] > 200 and stuck[1] == 0 and stuck[2] == 412, str(stuck))
    pg.screenshot(path=str(SHOTS / "after_listing_scrolled.png"))
    ov = pg.evaluate(OVERFLOW_JS)
    check("listing: still no sideways scrolling with overflow clip", ov["scrollWidth"] <= 412, json.dumps(ov))
    pg.evaluate("scrollTo(0, 0)")
    pg.screenshot(path=str(SHOTS / "after_listing_full.png"), full_page=True)

    pg.click(".thing.link .orm-more")
    visible = pg.evaluate("[...document.querySelector('.thing.link .buttons').children].filter(li => getComputedStyle(li).display !== 'none').length")
    check("listing: ⋯ reveals all actions", visible == 7, str(visible))
    pg.screenshot(path=str(SHOTS / "after_listing_more.png"), clip={"x": 0, "y": 0, "width": 412, "height": 400})

    pg.evaluate("document.querySelectorAll('.expando')[3].style.display = 'block'")  # simulate opening a preview
    ov = pg.evaluate(OVERFLOW_JS)
    check("listing: open preview fits", ov["scrollWidth"] <= 412 and not ov["overflowing"], json.dumps(ov))
    pg.evaluate("document.querySelectorAll('.thing.link')[3].scrollIntoView()")
    pg.screenshot(path=str(SHOTS / "after_listing_expando.png"))
    pg.evaluate("scrollTo(0, 0)")

    pg.click("#orm-menu-btn")
    side = pg.evaluate("(() => { const r = document.querySelector('#orm-drawer').getBoundingClientRect(); return [Math.round(r.left), Math.round(r.right)]; })()")
    check("drawer opens on the right", side[1] == 412 and side[0] > 0, str(side))
    pg.screenshot(path=str(SHOTS / "after_drawer.png"))
    pg.click("#orm-substyles")
    check("drawer: toggle re-enables subreddit style", not pg.evaluate("document.querySelector('link[title=applied_subreddit_stylesheet]').disabled"))
    pg.click("#orm-substyles")
    pg.mouse.click(20, 400)
    check("drawer closes on backdrop tap", not pg.evaluate("document.documentElement.classList.contains('orm-side-open')"))

    # ---- thread ----
    pg.goto(f"{fx}/thread.html")
    pg.wait_for_timeout(300)
    ov = pg.evaluate(OVERFLOW_JS)
    check("thread: no horizontal overflow", ov["scrollWidth"] <= 412 and not ov["overflowing"], json.dumps(ov))
    check("thread: AutoModerator collapsed", pg.evaluate("document.querySelector('.comment.stickied').classList.contains('collapsed')"))
    check("thread: top reply box hidden", pg.evaluate("getComputedStyle(document.querySelector('#form-main')).display") == "none")
    visible = pg.evaluate("[...document.querySelectorAll('.comment .buttons')[1].children].filter(li => getComputedStyle(li).display !== 'none').map(li => li.textContent.trim())")
    check("thread: comment shows reply + ⋯", visible == ["reply", "⋯"], str(visible))
    deepest = pg.evaluate("""(() => { let best = null, bd = -1; for (const c of document.querySelectorAll('.comment')) { let d = 0, p = c; while ((p = p.parentElement.closest('.comment'))) d++; if (d > bd) { bd = d; best = c; } }
        const r = best.querySelector('.md').getBoundingClientRect(); return [bd, Math.round(r.left), Math.round(r.width)]; })()""")
    check("thread: depth-7 comment still has >= 250px of text width", deepest[2] >= 250, f"depth={deepest[0]} left={deepest[1]} width={deepest[2]}")
    colors = pg.evaluate("[...document.querySelectorAll('.comment > .child')].slice(0, 4).map(c => getComputedStyle(c).borderLeftColor)")
    check("thread: lines colored by depth", len(set(colors)) >= 3, str(colors))
    pg.screenshot(path=str(SHOTS / "after_thread.png"))
    pg.evaluate("document.querySelector('[data-fullname=t1_axxxx]').scrollIntoView({block: 'start'})")
    pg.screenshot(path=str(SHOTS / "after_thread_deep.png"))

    pg.click("#orm-compose-btn")
    check("thread: compose button shows reply box", pg.evaluate("getComputedStyle(document.querySelector('#form-main')).display") != "none")

    # Tap the thread line of comment "a" (its .child's left padding).
    box = pg.evaluate("(() => { const r = document.querySelector('[data-fullname=t1_a] > .child').getBoundingClientRect(); return [r.left, r.top, r.height]; })()")
    pg.evaluate("document.querySelector('[data-fullname=t1_a] > .child').scrollIntoView({block: 'center'})")
    box = pg.evaluate("(() => { const r = document.querySelector('[data-fullname=t1_a] > .child').getBoundingClientRect(); return [r.left, r.top, r.height]; })()")
    pg.mouse.click(box[0] + 5, min(box[1] + box[2] / 2, 900))
    check("thread: tapping thread line collapses parent", pg.evaluate("document.querySelector('[data-fullname=t1_a]').classList.contains('collapsed')"))
    pg.screenshot(path=str(SHOTS / "after_thread_collapsed.png"))

    # Comments added later (load more) get processed too.
    pg.evaluate("""(() => { const c = document.querySelector('[data-fullname=t1_b]').cloneNode(true);
        c.querySelectorAll('[data-orm]').forEach(u => { delete u.dataset.orm; u.classList.remove('orm-collapsible'); u.querySelector('.orm-more-li')?.remove(); });
        c.querySelectorAll('.child').forEach(ch => ch.style.removeProperty('--orm-line'));
        c.dataset.fullname = 't1_new'; document.querySelector('.nestedlisting').append(c); })()""")
    pg.wait_for_timeout(100)
    check("thread: dynamically added comments processed", pg.evaluate("!!document.querySelector('[data-fullname=t1_new] .orm-more') && !!document.querySelector('[data-fullname=t1_new] > .child').style.getPropertyValue('--orm-line')"))

    check("no page errors", not errors, str(errors))

    # Laptop screen with a phone-sized window (desktop Responsive Design Mode), no force flag.
    rdm = b.new_context(viewport={"width": 412, "height": 915}, screen={"width": 1920, "height": 1080})
    rdm.add_init_script(INIT.replace("document.documentElement.dataset.ormForce = '1';", ""))
    rp = rdm.new_page()
    rp.goto(f"{fx}/listing.html")
    check("laptop screen + phone viewport activates", rp.evaluate("document.documentElement.classList.contains('orm')"))
    rdm.close()

    # Laptop screen and a normal desktop window: stays off.
    desk = b.new_context(viewport={"width": 1400, "height": 900}, screen={"width": 1920, "height": 1080})
    desk.add_init_script(INIT.replace("document.documentElement.dataset.ormForce = '1';", ""))
    dp = desk.new_page()
    dp.goto(f"{fx}/listing.html")
    check("desktop window stays untouched", not dp.evaluate("document.documentElement.classList.contains('orm')"))
    check("desktop: ⋯ hidden", dp.evaluate("getComputedStyle(document.querySelector('.orm-more-li')).display") == "none")
    check("desktop: subreddit style kept", not dp.evaluate("document.querySelector('link[title=applied_subreddit_stylesheet]').disabled"))
    dp.set_viewport_size({"width": 412, "height": 915})
    dp.wait_for_timeout(300)
    check("resize to phone width switches on", dp.evaluate("document.documentElement.classList.contains('orm')"))
    check("resize to phone width disables subreddit style", dp.evaluate("document.querySelector('link[title=applied_subreddit_stylesheet]').disabled"))
    ov = dp.evaluate(OVERFLOW_JS)
    check("resize to phone width: no overflow", ov["scrollWidth"] <= 412 and not ov["overflowing"], json.dumps(ov))
    dp.set_viewport_size({"width": 1400, "height": 900})
    dp.wait_for_timeout(300)
    check("resize back to desktop switches off", not dp.evaluate("document.documentElement.classList.contains('orm')"))
    check("desktop: account row and sidebar back in place", dp.evaluate("document.querySelector('#header-bottom-right').parentElement.id === 'header' && document.querySelector('.side').parentElement === document.body"))
    desk.close()
    b.close()

print(f"\n{len(failures)} failure(s)" if failures else "\nall checks passed")
sys.exit(1 if failures else 0)
