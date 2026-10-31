"""Package extension/ into dist/mobile-layout-for-old-reddit-<version>.xpi (a zip with manifest.json at the root)."""
import json, zipfile
from pathlib import Path

HERE = Path(__file__).parent
SRC = HERE / "extension"
version = json.loads((SRC / "manifest.json").read_text(encoding="utf-8"))["version"]
out = HERE / "dist" / f"mobile-layout-for-old-reddit-{version}.xpi"
out.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for f in sorted(SRC.rglob("*")):
        if f.is_file():
            z.write(f, f.relative_to(SRC).as_posix())
print(out.relative_to(HERE))
