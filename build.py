"""Package extension/ for both stores (each a zip with manifest.json at the root):
  dist/mobile-layout-for-old-reddit-<version>.xpi         Firefox (addons.mozilla.org), manifest as written
  dist/mobile-layout-for-old-reddit-<version>-chrome.zip  Chrome Web Store, with a Manifest V3 manifest
  dist/chrome/                                            the same Chrome build unpacked, for "Load unpacked"
"""
import json, shutil, zipfile
from pathlib import Path

HERE = Path(__file__).parent
SRC = HERE / "extension"
DIST = HERE / "dist"
manifest = json.loads((SRC / "manifest.json").read_text(encoding="utf-8"))
version = manifest["version"]


def chrome_manifest(m):
    """Chrome only accepts Manifest V3; the content-script keys are the same, so only the Firefox-only keys go."""
    m = dict(m, manifest_version=3)
    m.pop("browser_specific_settings", None)
    m.pop("author", None)  # Chrome expects {"email": ...} here; the store takes the developer name from the account
    return m


def files():
    return [f for f in sorted(SRC.rglob("*")) if f.is_file() and f.name != "manifest.json"]


def write_zip(out, manifest_text):
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("manifest.json", manifest_text)
        for f in files():
            z.write(f, f.relative_to(SRC).as_posix())
    print(out.relative_to(HERE))


DIST.mkdir(exist_ok=True)
chrome_text = json.dumps(chrome_manifest(manifest), indent=2) + "\n"
write_zip(DIST / f"mobile-layout-for-old-reddit-{version}.xpi", (SRC / "manifest.json").read_text(encoding="utf-8"))
write_zip(DIST / f"mobile-layout-for-old-reddit-{version}-chrome.zip", chrome_text)

unpacked = DIST / "chrome"
shutil.rmtree(unpacked, ignore_errors=True)
for f in files():
    (unpacked / f.relative_to(SRC)).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(f, unpacked / f.relative_to(SRC))
(unpacked / "manifest.json").write_text(chrome_text, encoding="utf-8", newline="\n")
print(unpacked.relative_to(HERE))
