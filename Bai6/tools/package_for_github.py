"""Copy only the new lab artifacts into the prepared local repository clone."""

from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT / "github-repo"
TARGET = REPO / "Bai6"
assert REPO.resolve().is_relative_to(ROOT.resolve())
assert (REPO / ".git").is_dir(), "Prepare the local clone before packaging"
TARGET.mkdir(exist_ok=True)

for name in ["REPORT_Bai6_LeDinhDuy_2387700102.md", "README_GITHUB.md", "requirements.txt", ".gitignore", ".gitattributes"]:
    shutil.copy2(ROOT / name, TARGET / name)

for name in ["tools", "github-workflows", "evidence", "lab06-devsecops"]:
    shutil.copytree(
        ROOT / name, TARGET / name, dirs_exist_ok=True,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".npm-cache", "node_modules", ".docusaurus", "build", "public", ".git"),
    )

assets = TARGET / "report-assets"
assets.mkdir(exist_ok=True)
for path in (ROOT / "report-assets").iterdir():
    if path.is_file() and path.name[:2].isdigit() and path.suffix in [".png", ".html"]:
        shutil.copy2(path, assets / path.name)

workflows = REPO / ".github" / "workflows"
workflows.mkdir(parents=True, exist_ok=True)
for path in (ROOT / "github-workflows").glob("*.yml"):
    shutil.copy2(path, workflows / path.name)

print("Prepared " + str(TARGET))
