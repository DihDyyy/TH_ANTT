"""Remove only the three throwaway browser profiles created for the capture probe."""

from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[1]
ASSETS = (ROOT / "report-assets").resolve()
assert ASSETS.is_relative_to(ROOT.resolve())
for name in ["browser-profile", "capture-profile", "edge-capture-profile"]:
    target = ASSETS / name
    if not target.exists():
        continue
    assert not target.is_symlink()
    assert target.resolve().parent == ASSETS
    assert target.resolve().name == name
    shutil.rmtree(target)
for name in ["capture-test.html", "capture-test.png"]:
    target = ASSETS / name
    if target.is_file():
        target.unlink()
print("Removed the known browser probe profiles and capture-test files only.")
