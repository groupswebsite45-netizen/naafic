import urllib.request
import json
import os
import sys

print("Fetching PyPI metadata for playwright...")
req = urllib.request.urlopen("https://pypi.org/pypi/playwright/json")
data = json.loads(req.read().decode("utf-8"))
urls = data["urls"]

win_whl = None
for u in urls:
    if "win_amd64.whl" in u["filename"] and "cp314" not in u["filename"]:
        if "py3-none-win_amd64.whl" in u["filename"]:
            win_whl = u
            break

if not win_whl:
    for u in urls:
        if "win_amd64.whl" in u["filename"]:
            win_whl = u
            break

print("Target wheel:", win_whl["filename"], "Size:", win_whl["size"])
download_url = win_whl["url"]
target_path = os.path.join(os.path.dirname(__file__), win_whl["filename"])

def reporthook(count, block_size, total_size):
    percent = int(count * block_size * 100 / total_size)
    sys.stdout.write(f"\rDownloading: {percent}% ({count * block_size}/{total_size} bytes)")
    sys.stdout.flush()

if not os.path.exists(target_path) or os.path.getsize(target_path) != win_whl["size"]:
    urllib.request.urlretrieve(download_url, target_path, reporthook)
    print("\nDownload complete!")
else:
    print("\nFile already downloaded!")

print("Installing wheel...")
import subprocess
subprocess.run([sys.executable, "-m", "pip", "install", target_path, "--no-index", "--find-links", "."])
print("Done!")
