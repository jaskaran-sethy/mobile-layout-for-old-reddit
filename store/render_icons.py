"""Draw the icon (same shapes as store/icon.svg, on a 96-unit grid) to the PNG sizes Firefox and AMO use.
Drawn at 8x and downsampled for smooth edges."""
from pathlib import Path
from PIL import Image, ImageDraw

OUT = Path(__file__).parent.parent / "extension" / "icons"
OUT.mkdir(exist_ok=True)
S = 8  # supersampling factor


def draw():
    img = Image.new("RGBA", (96 * S, 96 * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    box = lambda x, y, w, h: [x * S, y * S, (x + w) * S, (y + h) * S]
    d.rounded_rectangle(box(0, 0, 96, 96), radius=20 * S, fill="#cee3f8")
    # phone: blue frame, white screen, blue status bar
    d.rounded_rectangle(box(23, 7, 50, 82), radius=11 * S, fill="#5f99cf")
    d.rounded_rectangle(box(27, 11, 42, 74), radius=7 * S, fill="#ffffff")
    d.rounded_rectangle(box(27, 11, 42, 13), radius=7 * S, fill="#5f99cf")
    d.rectangle(box(27, 18, 42, 6), fill="#5f99cf")
    # upvote arrow + post lines
    d.polygon([(40 * S, 33 * S), (49 * S, 44 * S), (43.5 * S, 44 * S), (43.5 * S, 53 * S),
               (36.5 * S, 53 * S), (36.5 * S, 44 * S), (31 * S, 44 * S)], fill="#ff4500")
    for x, y, w, c in ((52, 35, 13, "#336699"), (52, 44, 9, "#9cbcdb"), (32, 61, 33, "#336699"), (32, 71, 24, "#9cbcdb")):
        d.rounded_rectangle(box(x, y, w, 5), radius=2.5 * S, fill=c)
    return img


big = draw()
for size in (32, 48, 96, 128):
    big.resize((size, size), Image.LANCZOS).save(OUT / f"icon-{size}.png")
big.resize((512, 512), Image.LANCZOS).save(Path(__file__).parent / "icon-512.png")
print(sorted(f.name for f in OUT.iterdir()))
