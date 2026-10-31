# AMO listing: Mobile Layout for Old Reddit

Copy each field into the matching box on addons.mozilla.org (Developer Hub → your add-on → Edit Product Page).

## Name

Mobile Layout for Old Reddit

## Add-on URL slug

mobile-layout-for-old-reddit

## Summary (max 250 characters)

Makes old Reddit comfortable on a phone. The page fits your screen, the top bar stays put with a menu for Home, Popular, All and your subreddits, posts are easy to tap, and comment threads stay readable however deep they go.

## Description

Old Reddit was built for desktop screens. On a phone you get tiny text, sideways scrolling, and comment threads that disappear off the right edge. This add-on gives old Reddit a proper phone layout while keeping its look: same colours, same pages, nothing new to learn.

What it changes on phone-sized screens:

• The page fits your screen. No zooming, no sideways scrolling; titles and comments wrap.
• A sticky top bar with the page name and a ☰ menu. The menu has Home, Popular and All one tap away, your subscribed subreddits, your account links, and the subreddit's sidebar.
• Posts: bigger vote arrows and thumbnails, full titles, and just the "comments" link up front. Share, save, hide and report are behind "⋯".
• Comment threads: small indents with a coloured line per level, so deep replies keep most of the screen. Tap a line to collapse that whole thread. "Reply" stays visible; the rest is behind "⋯".
• Less clutter: the "Get new Reddit" button and the email-verification banner are hidden, the empty reply box becomes an "Add a comment…" button, and AutoModerator's pinned comment starts collapsed.
• Subreddit custom styles are off by default, since most aren't built for phones. Turn them back on from the menu.

It works on old.reddit.com, and on www.reddit.com if your account is set to the old design. On desktop-sized windows nothing changes.

Privacy: the add-on collects no data and makes no network requests. Its only stored setting (whether to use subreddit styles) stays on your device.

Not affiliated with or endorsed by Reddit, Inc.

## Categories

- Firefox for Android: Experimental (or "Other" if offered)
- Firefox: Appearance

## Tags

reddit, old reddit, mobile, android, layout

## Support

- Support email: (your email)
- Support website: (optional; add a GitHub repo link once it's public)

## License

MIT License (choose "MIT/X11 License" in the form; the text is in LICENSE)

## Privacy policy

Not needed: the manifest declares no data collection.

## Notes to reviewer

Test account (old.reddit.com now requires signing in):
  Username: <throwaway test account username>
  Password: <its password>
This is a dedicated test account with no personal data. Please don't change its settings.

How to test:
1. Sign in at https://old.reddit.com with the account above.
2. Press Ctrl+Shift+M (Responsive Design Mode) and pick a phone preset, e.g. 412×915. The layout switches on in windows 600px wide or narrower and switches off when wider. On desktop-sized windows the add-on changes nothing.
3. Check a listing (https://old.reddit.com/r/all/), a comment thread (open any post's comments), and the ☰ menu at the top right.

About the code: there is no build step and nothing is minified or bundled, so the uploaded files are the source. mobile.js and mobile.css are injected into old.reddit.com and www.reddit.com pages. On www.reddit.com the script does nothing unless the page is the old design (it checks for old Reddit's #sr-header-area element). It makes no network requests. The only permission is "storage", which holds the "Use subreddit styles" switch.

## Screenshots (take these yourself on the real site)

In Firefox's Responsive Design Mode with a phone preset (e.g. 412×915), signed in, on old.reddit.com:

1. A busy listing such as r/all: the sticky top bar, tabs and posts.
2. A post with a deep comment thread: the coloured thread lines.
3. The ☰ menu open: Home / Popular / All, subreddits, account links.
4. Optional: the same thread with the "⋯" actions opened.

Use the camera button in the Responsive Design Mode toolbar. AMO accepts PNG or JPG, ideally 1280×800 or the phone's own aspect ratio.

## Version notes for 1.0.0

First public release. On phone-sized screens (600px wide or narrower) on old.reddit.com, and on www.reddit.com when the account uses the old design:

- Fits the page to the screen width: no sideways scrolling, and titles and comments wrap.
- Sticky top bar with the page name and a ☰ menu: Home / Popular / All, account links, other feeds, subscribed subreddits, a "Use subreddit styles" switch, and the subreddit sidebar.
- Sort tabs in one row you can swipe sideways.
- Posts: larger vote arrows, 64px thumbnails and full titles. Secondary actions are behind "⋯".
- Comments: compact indents with a coloured line per level; tap a line to collapse the thread. "Reply" stays visible and the other actions are behind "⋯".
- Hides the "Get new Reddit" button and the email-verification banner. The top reply box becomes an "Add a comment…" button, and AutoModerator's pinned comment starts collapsed.
- Subreddit custom styles are off by default (switch them on in the menu).
- No data collection, no network requests. The only stored setting stays on the device.
