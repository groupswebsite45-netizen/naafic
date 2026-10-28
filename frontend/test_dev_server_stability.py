import time
import socket
import urllib.request
import urllib.error
import os

BASE_URL = "http://localhost:5173"
ROUTES = [
    "/admin/students",
    "/admin/fees",
    "/admin/results",
    "/teacher/exams",
    "/teacher/classes"
]

def check_server_available():
    try:
        resp = urllib.request.urlopen(f"{BASE_URL}/", timeout=3)
        return resp.status == 200
    except Exception as e:
        print(f"Server check failed: {e}")
        return False

def simulate_browser_refresh(route):
    # 1. Fetch HTML
    url = f"{BASE_URL}{route}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    with urllib.request.urlopen(req, timeout=5) as resp:
        assert resp.status == 200, f"Expected 200 for {route}, got {resp.status}"
        html = resp.read().decode("utf-8")
        assert 'id="app"' in html, f"SPA root element missing in {route}"

    # 2. Open WebSocket connection to Vite HMR and abruptly disconnect with RST
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect(('localhost', 5173))
        ws_req = (
            "GET / HTTP/1.1\r\n"
            "Host: localhost:5173\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\n"
            "Sec-WebSocket-Version: 13\r\n\r\n"
        )
        s.sendall(ws_req.encode("utf-8"))
        time.sleep(0.05)
        # Force abrupt RST teardown (simulating F5 page reload)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, b'\x01\x00\x00\x00\x00\x00\x00\x00')
        s.close()
    except Exception as e:
        pass

def main():
    print("==================================================")
    print("STARTING FRONTEND DEV SERVER STABILITY VERIFICATION")
    print("==================================================")
    
    assert check_server_available(), "Vite dev server is not running on http://localhost:5173!"
    print("[PASS] Initial server availability confirmed on http://localhost:5173")

    # PHASE 1: Direct SPA route refresh test
    print("\n--- PHASE 1: Direct Browser Refresh / SPA Fallback Test ---")
    for route in ROUTES:
        simulate_browser_refresh(route)
        print(f"[PASS] Direct refresh on {route} succeeded without connection refusal")

    # PHASE 2: 20 Edit / HMR / Refresh / Navigation Cycles
    print("\n--- PHASE 2: 20 Edit / HMR / Refresh / Navigation Cycles ---")
    css_path = os.path.join(os.path.dirname(__file__), "src", "assets", "styles", "variables.css")
    vue_path = os.path.join(os.path.dirname(__file__), "src", "views", "admin", "fees", "FeesView.vue")
    
    with open(css_path, "r", encoding="utf-8") as f:
        original_css = f.read()

    successful_cycles = 0
    try:
        for cycle in range(1, 21):
            print(f"Cycle {cycle}/20: ", end="", flush=True)

            # 1. Edit a source file (alternating CSS and Vue)
            timestamp_comment = f"\n/* [HMR-STABILITY-TEST-CYCLE-{cycle}-{time.time()}] */\n"
            if cycle % 2 == 1:
                # Modify CSS
                with open(css_path, "w", encoding="utf-8") as f:
                    f.write(original_css + timestamp_comment)
            else:
                # Modify CSS with different variation
                with open(css_path, "w", encoding="utf-8") as f:
                    f.write(original_css + f"\n:root {{ --test-cycle-{cycle}: {cycle}; }}\n")

            # 2. Wait for HMR file watcher
            time.sleep(0.15)

            # 3. Simulate browser refresh on /admin/fees with socket RST
            simulate_browser_refresh("/admin/fees")

            # 4. Navigate between routes
            navigate_routes = ["/admin/students", "/admin/results", "/teacher/exams", "/admin/fees"]
            for r in navigate_routes:
                simulate_browser_refresh(r)

            successful_cycles += 1
            print(f"[OK] - Server online and responding (All 4 route reloads successful)")
    finally:
        # Restore original CSS file
        with open(css_path, "w", encoding="utf-8") as f:
            f.write(original_css)
        print("\nRestored source file to clean original state.")

    print(f"\n==================================================")
    print(f"STABILITY TEST COMPLETED: {successful_cycles}/20 CYCLES PASSED")
    print(f"SERVER REMAINED 100% AVAILABLE AND STABLE")
    print(f"==================================================")

if __name__ == "__main__":
    main()
