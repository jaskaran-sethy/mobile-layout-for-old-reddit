"""Compose the Chrome Web Store images from the mockups in design/ and store/icon-512.png into store/chrome/:
  screenshot-1..4.png   1280x800 (the store takes 1280x800 or 640x400, 24-bit PNG without alpha)
  promo-small.png       440x280 small promo tile (required)
  promo-marquee.png     1400x560 marquee tile (optional, used if the store features the extension)
The listing's 128x128 icon is extension/icons/icon-128.png. Uses Windows' Segoe UI; falls back to DejaVu Sans."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).parent
DESIGN = HERE.parent / "design"
OUT = HERE / "chrome"
OUT.mkdir(exist_ok=True)

BG = "#e9f1fa"  # lighter than the icon's own #cee3f8 tile, so the tile stands out
INK = "#1a1a1b"
BLUE = "#336699"
FRAME = "#1f2328"
LISTING, THREAD, DRAWER = "t8mLa6.png", "ZMmZU.png", "zUUFZ.png"


def font(size, bold=False):
    for name in (("segoeuib.ttf", "DejaVuSans-Bold.ttf") if bold else ("segoeui.ttf", "DejaVuSans.ttf")):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default(size)


def rounded_mask(size, radius, s=4):
    """Anti-aliased rounded-rectangle mask, drawn at s-times size and downsampled."""
    m = Image.new("L", (size[0] * s, size[1] * s), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, m.width - 1, m.height - 1), radius=radius * s, fill=255)
    return m.resize(size, Image.LANCZOS)


def phone(name, height):
    """A mockup in a dark phone frame; `height` is the screen height in pixels (the frame adds a bezel)."""
    shot = Image.open(DESIGN / name).convert("RGB")
    shot = shot.crop((0, 0, shot.width, min(shot.height, round(shot.width * 1.86))))  # all three at one aspect
    w = round(shot.width * height / shot.height)
    shot = shot.resize((w, height), Image.LANCZOS)
    bezel, r = max(8, height // 60), max(20, height // 18)
    body = Image.new("RGBA", (w + 2 * bezel, height + 2 * bezel), (0, 0, 0, 0))
    body.paste(FRAME, (0, 0), rounded_mask(body.size, r + bezel))
    body.paste(shot, (bezel, bezel), rounded_mask(shot.size, r))
    return body


def place(canvas, img, xy, shadow=True):
    if shadow:
        sh = Image.new("RGBA", (img.width + 80, img.height + 80), (0, 0, 0, 0))
        sh.paste((20, 40, 70, 90), (40, 40), img.split()[3])
        sh = sh.filter(ImageFilter.GaussianBlur(18))
        canvas.alpha_composite(sh, (xy[0] - 40, xy[1] - 28))
    canvas.alpha_composite(img, xy)


def text_block(d, x, y, title, lines, width):
    """Bold title (wrapped to `width`) then one line per point; returns the y below it."""
    tf, bf = font(52, True), font(28)
    words, row = title.split(), ""
    for word in words:
        if row and d.textlength(row + " " + word, font=tf) > width:
            d.text((x, y), row, font=tf, fill=INK)
            y, row = y + 66, word
        else:
            row = (row + " " + word).strip()
    d.text((x, y), row, font=tf, fill=INK)
    y += 96
    for line in lines:
        d.ellipse((x, y + 14, x + 10, y + 24), fill="#ff4500")
        d.text((x + 26, y), line, font=bf, fill=BLUE)
        y += 50
    return y


def canvas(w, h):
    return Image.new("RGBA", (w, h), BG)


def save(img, name):
    img.convert("RGB").save(OUT / name, optimize=True)
    print((OUT / name).relative_to(HERE.parent))


# 1. Overview: headline over three phones running off the bottom edge.
c = canvas(1280, 800)
d = ImageDraw.Draw(c)
for text, f, y, fill in (("Old Reddit, made for your phone", font(54, True), 46, INK),
                         ("Fits the screen  ·  menu always at hand  ·  readable comment threads", font(28), 122, BLUE)):
    d.text(((1280 - d.textlength(text, font=f)) // 2, y), text, font=f, fill=fill)
phones = [phone(n, 700) for n in (LISTING, THREAD, DRAWER)]
gap = 56
x = (1280 - sum(p.width for p in phones) - gap * 2) // 2
for p in phones:
    place(c, p, (x, 200))
    x += p.width + gap
save(c, "screenshot-1.png")

# 2-4. One feature each: text on the left, a large phone on the right.
FEATURES = (
    (LISTING, "Every post fits the screen", ["No sideways scrolling or zooming", "Big vote arrows and thumbnails", "Swipe through hot, new, top…"]),
    (THREAD, "Comment threads you can follow", ["A coloured line for each reply level", "Tap a line to collapse that thread", "Extra actions tucked behind •••"]),
    (DRAWER, "Everything one tap away", ["Home, Popular and All", "Your subreddits and account", "Subreddit styles off by default"]),
)
for i, (shot, title, lines) in enumerate(FEATURES, start=2):
    c = canvas(1280, 800)
    d = ImageDraw.Draw(c)
    text_block(d, 96, 210, title, lines, 560)
    p = phone(shot, 900)
    place(c, p, (1280 - 96 - p.width, 64))
    save(c, f"screenshot-{i}.png")

icon = Image.open(HERE / "icon-512.png").convert("RGBA")

# Small promo tile: icon and name only (small tiles are shown at thumbnail size).
c = canvas(440, 280)
d = ImageDraw.Draw(c)
c.alpha_composite(icon.resize((136, 136), Image.LANCZOS), (34, 72))
for i, line in enumerate(("Mobile Layout", "for Old Reddit")):
    d.text((190, 92 + i * 46), line, font=font(34, True), fill=INK)
save(c, "promo-small.png")

# Marquee: icon, name and tagline on the left, two phones on the right.
c = canvas(1400, 560)
d = ImageDraw.Draw(c)
c.alpha_composite(icon.resize((130, 130), Image.LANCZOS), (96, 72))
for i, line in enumerate(("Mobile Layout", "for Old Reddit")):
    d.text((96, 228 + i * 68), line, font=font(56, True), fill=INK)
d.text((96, 390), "Old Reddit, made for your phone.", font=font(28), fill=BLUE)
for j, name in enumerate((THREAD, LISTING)):
    p = phone(name, 640)
    place(c, p, (1400 - 64 - (j + 1) * p.width - j * 36, 60))
save(c, "promo-marquee.png")
