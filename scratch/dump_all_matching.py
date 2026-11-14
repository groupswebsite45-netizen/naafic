import re
from pathlib import Path

ROOT = Path(r"d:\documents\GitHub\sms")
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".pytest_cache", "dist", "uploads", "backups"}
PATTERNS = [
    re.compile(r"202[4578][/-]202[5689]"),
    re.compile(r"2026-2027"),
    re.compile(r"['\"]2025/2026['\"]|['\"]2024/2025['\"]|['\"]2027/2028['\"]")
]

results = {}

for folder in ["frontend/src", "backend/app"]:
    dir_path = ROOT / folder
    for p in dir_path.rglob("*"):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.suffix in [".ts", ".vue", ".py", ".json", ".html"]:
            try:
                content = p.read_text(encoding="utf-8")
                matches = []
                for line_no, line in enumerate(content.splitlines(), start=1):
                    for pat in PATTERNS:
                        m = pat.findall(line)
                        if m:
                            matches.append((line_no, line.strip(), m))
                if matches:
                    results[str(p.relative_to(ROOT))] = matches
            except Exception as e:
                pass

with open("scratch/all_matching_files.txt", "w", encoding="utf-8") as out:
    for f in sorted(results.keys()):
        out.write(f"{f}\n")
        for line_no, text, matched in results[f]:
            out.write(f"  L{line_no}: {text}\n")
print(f"Wrote {len(results)} files to scratch/all_matching_files.txt")
