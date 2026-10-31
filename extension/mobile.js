// Mobile Layout for Old Reddit: runs at document_start on old.reddit.com, and on www.reddit.com when it serves the old design.
(() => {
  "use strict";

  const root = document.documentElement;
  // Shows which build is running: document.documentElement.dataset.ormVersion in the console.
  if (typeof browser !== "undefined" && browser.runtime) root.dataset.ormVersion = browser.runtime.getManifest().version;

  // Re-checked on resize, so desktop Responsive Design Mode switches it on and off without a reload.
  // The window-width check covers RDM, where screen.* can still report the laptop's screen.
  function isPhone() {
    return (
      root.dataset.ormForce === "1" ||
      Math.min(screen.width, screen.height) <= 600 ||
      innerWidth <= 600 ||
      (screen.width <= 1024 && matchMedia("(pointer: coarse)").matches)
    );
  }
  // www.reddit.com serves the old design only to accounts that chose it; until old reddit's top bar shows up there,
  // the page is left completely alone (no class, no viewport change).
  let oldReddit = location.hostname === "old.reddit.com" || root.dataset.ormForce === "1";
  function detectOldReddit() {
    if (!oldReddit && document.getElementById("sr-header-area")) {
      oldReddit = true;
      active = isActive();
    }
    return oldReddit;
  }
  function isActive() {
    return oldReddit && isPhone();
  }
  let active = isActive();
  root.classList.toggle("orm", active);

  const store = typeof browser !== "undefined" && browser.storage ? browser.storage.local : null;
  const settings = { subStyles: false };
  const SUB_CSS = 'link[title="applied_subreddit_stylesheet"], style[title="applied_subreddit_stylesheet"]';
  const LINE_COLORS = ["#e57373", "#64b5f6", "#81c784", "#ffb74d", "#ba68c8", "#4dd0e1", "#f06292", "#a1887f"];

  // Without a viewport meta, phones lay old.reddit out at ~980px and shrink it.
  // Keep exactly one viewport meta (ours, in <head>): if the page ships its own, the browser may use that one.
  const VIEWPORT = "width=device-width, initial-scale=1";
  function setViewport() {
    const metas = [...document.querySelectorAll('meta[name="viewport"]')];
    let meta = metas.find((m) => m.dataset.orm);
    for (const m of metas) if (m !== meta) m.remove();
    if (!meta) {
      meta = document.createElement("meta");
      meta.name = "viewport";
      meta.dataset.orm = "1";
    }
    if (meta.content !== VIEWPORT) meta.content = VIEWPORT;
    if (document.head) {
      if (meta.parentNode !== document.head) document.head.prepend(meta);
    } else if (!meta.parentNode) {
      root.prepend(meta);
    }
  }

  function applySubStyles() {
    for (const el of document.querySelectorAll(SUB_CSS)) el.disabled = active && !settings.subStyles;
  }

  function onResize() {
    const now = isActive();
    if (now === active) return;
    active = now;
    root.classList.toggle("orm", active);
    if (!active) root.classList.remove("orm-side-open");
    applySubStyles();
    if (document.body) {
      placeBorrowed();
      hideNags();
    }
  }

  // Reddit's scripts overwrite <html class> (Modernizr) and can put their width=1024 viewport back,
  // so both are re-applied whenever they change, for the life of the page.
  function enforce() {
    if (!detectOldReddit()) return;
    if (active && !root.classList.contains("orm")) root.classList.add("orm");
    setViewport();
  }

  // Until the DOM is ready, watch everything: also catches the subreddit stylesheet before it paints.
  enforce();
  const earlyObserver = new MutationObserver(() => {
    enforce();
    applySubStyles();
  });
  earlyObserver.observe(root, { childList: true, subtree: true, attributes: true, attributeFilter: ["class"] });

  if (store) {
    store.get("subStyles").then((r) => {
      settings.subStyles = !!r.subStyles;
      applySubStyles();
      const box = document.getElementById("orm-substyles");
      if (box) box.checked = settings.subStyles;
    });
  }

  // Returns scope itself (if it matches) plus matching descendants.
  function all(scope, selector) {
    const found = [...scope.querySelectorAll(selector)];
    if (scope.matches && scope.matches(selector)) found.unshift(scope);
    return found;
  }

  function depthOf(comment) {
    let depth = 0;
    let el = comment;
    while ((el = el.parentElement && el.parentElement.closest(".comment"))) depth++;
    return depth;
  }

  function isReplyItem(li) {
    return (
      li.classList.contains("reply-button") ||
      !!li.querySelector('.reply-button, a[onclick*="reply"]') ||
      li.textContent.trim().toLowerCase() === "reply"
    );
  }

  // Keep the one action people use (comments link on posts, reply on comments); hide the rest behind "⋯".
  function setupButtons(ul) {
    if (ul.dataset.orm) return;
    ul.dataset.orm = "1";
    const inComment = !!ul.closest(".comment");
    const items = [...ul.children].filter((el) => el.tagName === "LI");
    for (const li of items) {
      const keep = inComment ? isReplyItem(li) : li.classList.contains("first");
      if (keep) li.classList.add("orm-keep");
    }
    if (items.filter((li) => !li.classList.contains("orm-keep")).length < 2) return;
    const li = document.createElement("li");
    li.className = "orm-more-li";
    const a = document.createElement("a");
    a.href = "#";
    a.className = "orm-more";
    a.textContent = "⋯";
    a.setAttribute("aria-label", "More actions");
    li.append(a);
    ul.append(li);
    ul.classList.add("orm-collapsible");
  }

  function colorThreadLines(scope) {
    for (const child of all(scope, ".comment > .child")) {
      if (child.style.getPropertyValue("--orm-line")) continue;
      const depth = depthOf(child.parentElement);
      child.style.setProperty("--orm-line", LINE_COLORS[depth % LINE_COLORS.length]);
    }
  }

  function collapse(comment) {
    if (!comment.classList.contains("collapsed")) {
      const toggle = comment.querySelector(":scope > .entry .tagline .expand");
      if (toggle) toggle.click();
    }
    if (comment.getBoundingClientRect().top < 0) comment.scrollIntoView({ block: "start" });
  }

  function collapseAutoModerator() {
    for (const comment of document.querySelectorAll(".commentarea .nestedlisting > .comment.stickied")) {
      const author = comment.dataset.author || comment.querySelector(":scope > .entry .author")?.textContent;
      if (author === "AutoModerator") collapse(comment);
    }
  }

  function process(scope) {
    for (const ul of all(scope, ".flat-list.buttons")) setupButtons(ul);
    colorThreadLines(scope);
  }

  function el(tag, props = {}, ...children) {
    const node = Object.assign(document.createElement(tag), props);
    node.append(...children);
    return node;
  }

  function section(title, ...children) {
    return el("section", { className: "orm-section" }, el("h3", { textContent: title }), ...children);
  }

  // Copies of reddit's own links, so the header markup stays intact for desktop.
  function linkCopy(a, className) {
    const copy = el("a", { href: a.href, textContent: a.textContent.trim(), className });
    const here = location.pathname.replace(/\/$/, "") || "/";
    let path = "";
    try {
      path = new URL(a.href).pathname.replace(/\/$/, "") || "/";
    } catch (e) {}
    if (a.closest(".selected") || path === here) copy.classList.add("orm-current");
    return copy;
  }

  function feedLinks() {
    const bar = document.querySelector("#sr-header-area .sr-list ul.flat-list");
    return bar ? [...bar.querySelectorAll("a")] : [];
  }

  function subredditLinks() {
    const drop = [...document.querySelectorAll("#sr-header-area .drop-choices a.choice:not(.bottom-option)")];
    if (drop.length) return drop;
    const bars = document.querySelectorAll("#sr-header-area .sr-list ul.flat-list");
    return bars.length > 1 ? [...bars[1].querySelectorAll("a")] : [];
  }

  // Elements moved into the drawer on phones and put back on desktop, each remembered by a marker comment.
  const moved = [];
  function borrow(node, into) {
    if (!node) return;
    const marker = document.createComment("orm");
    node.before(marker);
    moved.push({ node, marker, into });
  }

  function placeBorrowed() {
    for (const { node, marker, into } of moved) {
      if (active) into.append(node);
      else marker.after(node);
    }
  }

  // Our own top row (home link, page name, ☰); reddit's logo and page name are hidden on phones.
  function addHeaderBar(header) {
    const name = header.querySelector(".pagename a");
    let title = "reddit";
    let href = "/";
    if (name) {
      title = name.textContent.trim();
      href = name.href;
      try {
        if (/^\/r\//.test(new URL(href).pathname)) title = "r/" + title;
      } catch (e) {}
    }
    const btn = el("button", { id: "orm-menu-btn", type: "button", textContent: "☰" });
    btn.setAttribute("aria-label", "Open menu");
    // Outside #header, as the first thing in <body>, so it can stick to the top of the screen.
    document.body.prepend(
      el("div", { id: "orm-bar" },
        el("a", { id: "orm-home", href: "/", textContent: "reddit" }),
        el("a", { id: "orm-title", href, textContent: title }),
        btn)
    );
  }

  // Home / Popular / All, always at the top of the drawer.
  const MAIN_FEEDS = [["Home", "/"], ["Popular", "/r/popular/"], ["All", "/r/all/"]];
  function mainFeeds() {
    const here = location.pathname.replace(/\/$/, "") || "/";
    return el("nav", { className: "orm-main-feeds" }, ...MAIN_FEEDS.map(([label, path]) => {
      const a = el("a", { href: path, textContent: label });
      if ((path.replace(/\/$/, "") || "/") === here) a.classList.add("orm-current");
      return a;
    }));
  }

  function addDrawer() {
    const header = document.getElementById("header");
    if (!header) return;
    addHeaderBar(header);

    document.body.append(el("div", { id: "orm-backdrop" }));
    const drawer = el("div", { id: "orm-drawer" });
    drawer.setAttribute("role", "dialog");
    drawer.setAttribute("aria-label", "Menu");

    const account = el("div", { className: "orm-account" });
    borrow(document.getElementById("header-bottom-right"), account);

    const body = el("div", { className: "orm-drawer-body" });
    // The rest of reddit's feed bar (mod, users, friends, ...) as small chips.
    const mainPaths = new Set(MAIN_FEEDS.map(([, p]) => p.replace(/\/$/, "") || "/"));
    const feeds = feedLinks().filter((a) => {
      try {
        return !mainPaths.has(new URL(a.href).pathname.replace(/\/$/, "") || "/");
      } catch (e) {
        return true;
      }
    });
    if (feeds.length) body.append(section("More feeds", el("div", { className: "orm-chips" }, ...feeds.map((a) => linkCopy(a, "orm-chip")))));

    const subs = subredditLinks();
    if (subs.length) {
      const list = el("ul", { className: "orm-subs" }, ...subs.map((a) => el("li", {}, linkCopy(a, ""))));
      const edit = document.querySelector("#sr-header-area .drop-choices a.bottom-option, #sr-more-link");
      body.append(section("My subreddits", list, ...(edit ? [linkCopy(edit, "orm-edit-subs")] : [])));
    }

    const panel = el("div", { id: "orm-settings" });
    body.append(panel);

    const side = document.querySelector("body > .side") || document.querySelector(".side");
    if (side) {
      const holder = el("div");
      body.append(section("This subreddit", holder));
      borrow(side, holder);
    }

    drawer.append(mainFeeds(), account, body);
    document.body.append(drawer);
    placeBorrowed();
    const label = document.createElement("label");
    const box = document.createElement("input");
    box.type = "checkbox";
    box.id = "orm-substyles";
    box.checked = settings.subStyles;
    box.addEventListener("change", () => {
      settings.subStyles = box.checked;
      applySubStyles();
      if (store) store.set({ subStyles: settings.subStyles });
    });
    label.append(box, " Use subreddit styles");
    panel.append(label);
  }

  // Reddit's "add your email" nag is a fixed banner with no stable class name; match it by its text.
  const NAG = /verify your (reddit account|email)|add your email/i;
  function hideNags() {
    if (!active) return;
    for (const node of document.querySelectorAll("body > *, body > * > *")) {
      if (node.classList.contains("orm-nag") || node.closest("#orm-drawer, .content, #header")) continue;
      if (!NAG.test(node.textContent)) continue;
      const pos = getComputedStyle(node).position;
      if (pos === "fixed" || pos === "sticky") node.classList.add("orm-nag");
    }
  }

  function addComposeButton() {
    const form = document.querySelector(".commentarea > form.usertext");
    if (!form) return;
    const btn = document.createElement("button");
    btn.id = "orm-compose-btn";
    btn.type = "button";
    btn.textContent = "Add a comment…";
    form.before(btn);
  }

  function onClick(e) {
    const t = e.target;
    if (!(t instanceof Element)) return;

    const more = t.closest(".orm-more");
    if (more) {
      e.preventDefault();
      more.closest("ul").classList.toggle("orm-open");
      return;
    }
    if (t.id === "orm-menu-btn") {
      root.classList.add("orm-side-open");
      return;
    }
    if (t.id === "orm-backdrop") {
      root.classList.remove("orm-side-open");
      return;
    }
    if (t.id === "orm-compose-btn") {
      const area = t.closest(".commentarea");
      area.classList.add("orm-compose");
      area.querySelector(":scope > form.usertext textarea")?.focus();
      return;
    }
    // A tap on the coloured thread line (the .child's own left padding) collapses the parent comment.
    if (t.classList.contains("child") && t.parentElement?.classList.contains("comment")) {
      if (e.clientX - t.getBoundingClientRect().left <= 18) {
        e.preventDefault();
        collapse(t.parentElement);
      }
    }
  }

  function init() {
    earlyObserver.disconnect();
    if (!detectOldReddit()) return; // new design on www.reddit.com: nothing to do
    enforce();
    applySubStyles();
    const guard = new MutationObserver(enforce);
    guard.observe(root, { attributes: true, attributeFilter: ["class"] });
    if (document.head) guard.observe(document.head, { childList: true, subtree: true, attributes: true, attributeFilter: ["content"] });
    addDrawer();
    addComposeButton();
    process(document.body);
    hideNags();
    if (active) collapseAutoModerator();
    document.addEventListener("click", onClick);
    addEventListener("resize", onResize);

    // "load more comments", reply forms, late banners: process whatever gets added.
    new MutationObserver((records) => {
      let nag = false;
      for (const r of records) {
        if (r.target === document.body || r.target.parentElement === document.body) nag = true;
        for (const node of r.addedNodes) if (node.nodeType === 1) process(node);
      }
      if (nag) hideNags();
      applySubStyles();
    }).observe(document.body, { childList: true, subtree: true });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init, { once: true });
  else init();
})();
