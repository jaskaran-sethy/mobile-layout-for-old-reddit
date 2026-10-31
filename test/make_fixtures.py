"""Generate fixture pages that copy old.reddit's markup (listing + comment thread)."""
from pathlib import Path

OUT = Path(__file__).parent / "fixtures"

HEAD = """<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=1024"><title>{title}</title>
<link rel="stylesheet" href="oldreddit-base.css">
<link rel="stylesheet" href="subreddit-style.css" title="applied_subreddit_stylesheet">
<script>
// Like reddit: Modernizr overwrites <html class> while parsing, and a late script restores width=1024.
document.documentElement.className = ' js cssanimations csstransforms';
window.addEventListener('load', () => setTimeout(() => {{
  document.documentElement.className = ' js cssanimations csstransforms';
  document.querySelectorAll('meta[name=viewport]').forEach(m => m.remove());
  const m = document.createElement('meta'); m.name = 'viewport'; m.content = 'width=1024'; document.head.append(m);
}}, 50));
function togglecomment(el) {{
  var t = el.closest('.thing');
  t.classList.toggle('collapsed'); t.classList.toggle('noncollapsed');
  el.textContent = t.classList.contains('collapsed') ? '[+]' : '[–]';
  return false;
}}
</script></head>
<body class="{body_class}">
<div id="header">
  <div id="sr-header-area"><div class="width-clip"><a class="redesign-beta-optin" href="#">GET NEW REDDIT</a>
    <div class="dropdown srdrop"><span class="selected title">my subreddits</span></div>
    <div class="drop-choices srdrop"><a class="choice" href="https://old.reddit.com/r/AskReddit/">AskReddit</a><a class="choice" href="https://old.reddit.com/r/pics/">pics</a><a class="choice" href="https://old.reddit.com/r/news/">news</a><a class="choice" href="https://old.reddit.com/r/thegrandtour/">thegrandtour</a><a class="choice" href="https://old.reddit.com/r/technology/">technology</a><a class="bottom-option choice" href="https://old.reddit.com/subreddits/">edit subscriptions</a></div>
    <div class="sr-list"><ul class="flat-list sr-bar hover"><li><a class="choice" href="https://old.reddit.com/">home</a></li><li><span class="separator">-</span><a class="choice" href="https://old.reddit.com/r/popular/">popular</a></li><li class="{all_sel}"><span class="separator">-</span><a class="choice" href="https://old.reddit.com/r/all/">all</a></li><li><span class="separator">-</span><a class="choice" href="https://old.reddit.com/r/mod/">mod</a></li><li><span class="separator">-</span><a class="choice" href="https://old.reddit.com/users/">users</a></li></ul><span class="separator">&nbsp;|&nbsp;</span>
    <ul class="flat-list sr-bar hover"><li><a class="choice" href="https://old.reddit.com/r/AskReddit/">AskReddit</a></li><li><span class="separator">-</span><a class="choice" href="https://old.reddit.com/r/pics/">pics</a></li></ul></div>
    <a id="sr-more-link" href="https://old.reddit.com/subreddits/">edit &raquo;</a></div></div>
  <div id="header-bottom-left"><a href="https://old.reddit.com/" id="header-img" class="default-header" title="">reddit.com</a>
    <span class="hover pagename redditname"><a href="https://old.reddit.com/r/{pagename}/">{pagename}</a></span>
    <ul class="tabmenu">{tabs}</ul></div>
  <div id="header-bottom-right"><span class="user"><a href="#">jase</a>&nbsp;(<span class="userkarma">1234</span>)</span><span class="separator">|</span><a class="havemail" id="mail" href="#">messages</a><span class="separator">|</span><ul class="flat-list hover"><li><a class="pref-lang choice" href="#">preferences</a></li></ul><span class="separator">|</span><form class="logout hover"><a href="#">logout</a></form></div>
</div>
{chooser}
<div class="side">
  <div class="spacer"><form id="search"><input name="q" placeholder="search"></form></div>
  <div class="spacer"><div class="titlebox"><h1>{pagename}</h1><span class="subscribe-button"><a class="option add" href="#">subscribe</a></span>
    <span class="subscribers"><span class="number">6,123,456</span> readers</span>
    <div class="usertext-body"><div class="md"><p>Sidebar rules and description. A long sidebar paragraph that would normally sit to the right of the posts on desktop.</p></div></div></div></div>
</div>
<a name="content"></a>
<div class="content" role="main">
{content}
</div>
<div class="verify-nag-wrapper"><div style="position:fixed;left:0;right:0;bottom:0;background:#fff;border-top:4px solid #ff4500;padding:10px;font-size:14px"><b>jase, add your email to verify your Reddit account.</b> Verify your email to prevent being locked out of your account. <button>ADD EMAIL</button></div></div>
</body></html>"""

CHOOSER = """<div class="listing-chooser"><div class="grippy"></div><ul>
<li><a href="#">home</a><br><small>the home feed</small></li><li class="intro">new! create sets of subreddits to view together.</li>
<li><a href="#">redditnews</a></li><li><a href="#">redditpets</a></li><li><a href="#">explore multis</a></li>
<li><a href="#">everything</a></li><li><a href="#">moderating</a></li><li><a href="#">saved</a></li></ul></div>"""

TITLES = [
    ("Jeremy Clarkson comments on the new season and says it will be the final one for the whole team", "theguardian.com", 13000, 98),
    ("So say we all: a long retrospective on twenty years of a TV show and its fandom", "self.television", 10500, 221),
    ("Why is the media not covering this story more widely? An investigation into newsroom priorities", "thenation.com", 13500, 723),
    ("My sister and I shaved our heads together to hopefully help her through her treatment journey", "i.redd.it", 7821, 291),
    ("OpenAI CEO says the next model will ship next spring", "tomshardware.com", 8970, 1999),
    ("Might have been a little overboard on the beans", "i.redd.it", 1780, 435),
]


def link(i, title, domain, score, ncom, stickied=False):
    thumb = f'<a class="thumbnail" href="#"><img src="data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 width=%2770%27 height=%2752%27%3E%3Crect width=%2770%27 height=%2752%27 fill=%27%23{(i * 2345) % 0xFFFFFF:06x}%27/%3E%3C/svg%3E"></a>'
    flair = '<span class="linkflairlabel">Food</span> ' if i == 5 else ""
    return f"""<div class="thing link{' stickied' if stickied else ''}" data-fullname="t3_{i}">
<p class="parent"></p><span class="rank">{i + 1}</span>
<div class="midcol unvoted"><div class="arrow up" role="button" aria-label="upvote"></div><div class="score unvoted">{score}</div><div class="arrow down" role="button" aria-label="downvote"></div></div>
{thumb}
<div class="entry unvoted"><div class="top-matter">
<p class="title">{flair}<a class="title" href="thread.html">{title}</a> <span class="domain">(<a href="#">{domain}</a>)</span></p>
<div class="expando-button collapsed"></div>
<p class="tagline">submitted <time>2 hours ago</time> by <a class="author" href="#">user{i}</a> to <a class="subreddit" href="#">r/sub{i}</a></p>
<ul class="flat-list buttons"><li class="first"><a class="comments" href="thread.html">{ncom} comments</a></li><li class="share"><a href="#">share</a></li><li class="link-save-button save-button"><a href="#">save</a></li><li><form class="hide-button"><span><a href="#">hide</a></span></form></li><li class="report-button"><a class="reportbtn" href="#">report</a></li><li class="crosspost-button"><a href="#">crosspost</a></li></ul>
</div><div class="expando expando-uninitialized"><div class="media-preview"><div class="media-preview-content" style="width:640px"><img src="data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 width=%27640%27 height=%27480%27%3E%3Crect width=%27640%27 height=%27480%27 fill=%27%23999%27/%3E%3C/svg%3E" width="640" height="480"></div></div></div></div>
<div class="child"></div><div class="clearleft"></div></div><div class="clearleft"></div>"""


LISTING_TABS = '<li class="selected"><a href="#">hot</a></li><li><a href="#">new</a></li><li><a href="#">rising</a></li><li><a href="#">controversial</a></li><li><a href="#">top</a></li><li><a href="#">gilded</a></li><li><a href="#">wiki</a></li>'

TEXT = [
    "Oh oh oh! I know this one! Because the media is owned by a handful of companies that all have the same incentives.",
    "That's part of it, but the bigger issue is that most outlets lost their local reporters a decade ago and never replaced them.",
    "I think at this point everyone sorta knows, and the people who care already care and the ones who don't won't start now.",
    "He literally campaigned on it. Sadly, that is one of the truest things anyone has said in this thread.",
    "The best part is, they think this is a compliment. Just cult things, really.",
    "Didn't expect to be jealous of a loving relationship in a thread about beans, but here I am praying I find someone like that.",
    "Here's a code block that is wider than the screen:",
    "Ok this is the deepest reply so far and it keeps going and going.",
]


def comment(id_, depth, maxdepth, author=None, stickied=False, extra=""):
    author = author or f"commenter{id_}"
    body = f"<p>{TEXT[depth % len(TEXT)]}</p>"
    if depth == 6:
        body += "<pre><code>const result = someVeryLongFunctionName(argumentNumberOne, argumentNumberTwo, argumentNumberThree);</code></pre>"
    child = ""
    if depth < maxdepth:
        child = comment(f"{id_}x", depth + 1, maxdepth)
        if depth == 2:
            child += comment(f"{id_}y", depth + 1, depth + 1)
    if depth == 3:
        child += f'<div class="thing morechildren"><span class="morecomments"><a class="button" href="#" onclick="return false">load more comments (12 replies)</a></span></div>'
    buttons = '<li class="first"><a class="bylink" href="#">permalink</a></li><li><a class="embed-comment" href="#">embed</a></li><li class="comment-save-button save-button"><a href="#">save</a></li>'
    if depth:
        buttons += '<li><a class="bylink" href="#">parent</a></li>'
    buttons += '<li class="report-button"><a class="reportbtn" href="#">report</a></li><li><a class="reply-button" href="#" onclick="return false">reply</a></li>'
    return f"""<div class="thing comment noncollapsed{' stickied' if stickied else ''}" data-fullname="t1_{id_}" data-author="{author}">
<p class="parent"><a name="{id_}"></a></p>
<div class="midcol unvoted"><div class="arrow up" role="button" aria-label="upvote"></div><div class="arrow down" role="button" aria-label="downvote"></div></div>
<div class="entry unvoted"><p class="tagline"><a href="#" class="expand" onclick="return togglecomment(this)">[&ndash;]</a><a class="author" href="#">{author}</a>{' <span class="flair">Washington</span>' if depth == 5 else ''}<span class="score unvoted"> {100 - depth * 12} points</span> <time>{depth + 1} hours ago</time>{' <span class="stickied-tagline">stickied comment</span>' if stickied else ''}</p>
<form class="usertext"><div class="usertext-body"><div class="md">{extra or body}</div></div></form>
<ul class="flat-list buttons">{buttons}</ul></div>
<div class="child"><div class="sitetable listing">{child}</div></div><div class="clearleft"></div></div><div class="clearleft"></div>"""


def build():
    listing = '<div id="siteTable" class="sitetable linklisting">' + "".join(link(i, *t) for i, t in enumerate(TITLES)) + \
        '<div class="nav-buttons"><span class="nextprev">view more: <span class="next-button"><a href="#" rel="nofollow next">next &rsaquo;</a></span></span></div></div>'
    (OUT / "listing.html").write_text(HEAD.format(title="all", body_class="listing-page with-listing-chooser", pagename="all", all_sel="selected",
                                                 tabs=LISTING_TABS, chooser=CHOOSER, content=listing), encoding="utf-8")

    automod = "<h2>Rules</h2>" + "<p>Please be civil. Hate speech, any suggestion or support of harm, or personal attacks can result in a temporary or a permanent ban.</p>" * 4 + "<p><em>I am a bot, and this action was performed automatically.</em></p>"
    thread = f"""<div id="siteTable" class="sitetable linklisting">{link(5, *TITLES[5])}</div>
<div class="commentarea"><div class="panestack-title"><span class="title">all 435 comments</span></div>
<div class="menuarea"><div class="spacer"><span class="dropdown-title lightdrop">sorted by: </span><div class="dropdown lightdrop"><span class="selected">best</span></div></div></div>
<form class="usertext cloneable" id="form-main"><div class="usertext-edit"><div><textarea name="text"></textarea></div><div class="bottom-area"><button type="submit" class="save">save</button></div></div></form>
<div id="siteTable_t3_5" class="sitetable nestedlisting">
{comment("am", 0, 0, author="AutoModerator", stickied=True, extra=automod)}
{comment("a", 0, 7)}
{comment("b", 0, 2)}
{comment("c", 0, 1)}
</div></div>"""
    (OUT / "thread.html").write_text(HEAD.format(title="Might have been a little overboard on the beans : Frugal", body_class="comments-page", pagename="Frugal", all_sel="",
                                                tabs='<li class="selected"><a href="#">comments</a></li><li><a href="#">other discussions (3)</a></li>', chooser="", content=thread), encoding="utf-8")

    # A heavy subreddit style like r/apple's: giant banner, custom notice.
    (OUT / "subreddit-style.css").write_text("""#header { height: 520px; background: linear-gradient(#ff6a3d, #42a5f5); }
#header-bottom-left { bottom: 0; background: #555; width: 100%; height: 60px; }
.content::before { content: 'You are not subscribed to this community. Please respect that by not downvoting.'; display: block; background: #555; color: #fff; padding: 10px; font-size: 14px; }
""", encoding="utf-8")


if __name__ == "__main__":
    build()
