import os
import sys
import subprocess
import json

def run_browser_tests():
    print("==================================================")
    print("RUNNING BROWSER E2E + RESPONSIVE SUITE VIA PLAYWRIGHT")
    print("==================================================")
    
    script_path = os.path.join(os.path.dirname(__file__), 'browser_runner.cjs')
    proc = subprocess.run(['node', script_path], capture_output=True, text=True, encoding='utf-8')
    print(proc.stdout)
    if proc.stderr:
        print("STDERR:", proc.stderr)
        
    raw_path = os.path.join(os.path.dirname(__file__), 'browser_audit_raw.json')
    if os.path.exists(raw_path):
        with open(raw_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    return None

if __name__ == "__main__":
    run_browser_tests()
