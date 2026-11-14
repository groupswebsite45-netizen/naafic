import re
from pathlib import Path

ROOT = Path(r"d:\documents\GitHub\sms\backend\app")
pattern = re.compile(r"academic_year|academic_years", re.IGNORECASE)

matching_functions = []

for py_file in ROOT.rglob("*.py"):
    content = py_file.read_text(encoding="utf-8")
    for i, line in enumerate(content.splitlines(), start=1):
        if "academic_years" in line or "academic_year_current" in line or "def get_academic_years" in line or "filter_options" in line:
            matching_functions.append((str(py_file.relative_to(ROOT)), i, line.strip()))

for f, i, l in matching_functions:
    print(f"{f}:{i} -> {l}")
