# Frontend Development Server Stability Report

**Date:** 2026-09-19  
**Application:** Hawlwadaag Primary and Secondary School Portal (Frontend)  
**Host Environment:** Windows (Node.js `v24.18.0`, Vite `v6.4.3`, Vue `v3.5.13`, TypeScript `v5.7.3`)  
**Status:** **RESOLVED & VERIFIED RESILIENT**

---

## 1. Root Cause Analysis

### What Was Happening
Whenever a developer modified source code and then refreshed the browser (or rapidly navigated between views), Vite was unexpectedly crashing with:
```text
node:events:487
      throw er; // Unhandled 'error' event
      ^

Error: read ECONNRESET
    at TCP.onStreamRead (node:internal/stream_base_commons:216:20)
Emitted 'error' event on Socket instance at:
    at emitErrorNT (node:internal/streams/destroy:170:8)
    at emitErrorCloseNT (node:internal/streams/destroy:129:3)
    at process.processTicksAndRejections (node:internal/process/task_queues:90:21) {
  errno: -4077,
  code: 'ECONNRESET',
  syscall: 'read'
}

Node.js v24.18.0
```

### Technical Explanation
1. **Node 24 Strict Error Handling on Windows:**
   In modern Node.js (`v24.18.0`), any unhandled `'error'` event emitted on a `net.Socket` or `EventEmitter` is fatal and aborts the Node process with exit code 1 (`throw er; // Unhandled 'error' event`).
2. **Browser Refresh Socket Teardown (`RST`):**
   When code is changed, Vite sends HMR update notifications to the browser over WebSocket, and the browser simultaneously fetches updated module scripts over HTTP. When the user hits browser reload (F5 / Ctrl+R) during this exchange, the browser abruptly closes both the pending HTTP keep-alive sockets and the HMR WebSocket connection by sending a TCP `RST` packet.
3. **Missing Socket Error Trap in Default Vite Configuration:**
   Windows Winsock reports this as `WSAECONNRESET` (-4077). Because the raw underlying TCP client sockets lacked explicit individual error listeners, the socket error bubbled up as an unhandled exception to the Node event loop, immediately killing the Vite development server process.
4. **Subsequent Refresh Failure:**
   With the Vite process dead, any subsequent browser request to `http://localhost:5173` resulted in `ERR_CONNECTION_REFUSED`.
5. **Secondary Risk Factor (Port Drift):**
   When `strictPort` was unset (defaulting to `false`), any transient socket cleanup delay could cause Vite to silently bind to port `5174` instead of `5173`, also presenting as connection refusal on port 5173.

---

## 2. Fix Implementation

### File Changed: `frontend/vite.config.ts`

The Vite configuration was upgraded with a multi-layered resilience architecture:

1. **Process-Level Unhandled Socket Exception Guard:**
   Catches transient network disconnect exceptions (`ECONNRESET`, `EPIPE`, `ECONNABORTED`, `ETIMEDOUT`, `HPE_INVALID_EOF_STATE`) at the Node process level, preventing fatal process termination while preserving logging for real application exceptions.

2. **Custom Dev Server Resilience Plugin (`devServerResiliencePlugin`):**
   - **Client Socket Interception:** Listens to `server.httpServer.on('connection')` and attaches error listeners directly to client sockets, cleanly destroying aborted sockets without re-throwing.
   - **Protocol Client Error Interception:** Listens to `server.httpServer.on('clientError')` to safely destroy sockets on malformed or aborted HTTP header requests.
   - **WebSocket HMR Resilience:** Intercepts `server.ws.on('error')` to absorb WebSocket disconnection spikes.

3. **Backend Proxy Fault Tolerance:**
   Configured the `/api` proxy target with custom `onError` handling: if the FastAPI backend (`http://127.0.0.1:8000`) is temporarily down, restarting, or slow, the proxy returns a clean `503 Service Unavailable` JSON response instead of killing the Vite process.

4. **Port Stability (`strictPort: true`):**
   Prevents Vite from silently shifting to alternative ports (`5174`, `5175`).

5. **Watcher Scoping:**
   Configured `server.watch.ignored` to ignore `**/dist/**`, `**/.git/**`, `**/backend/**`, and Windows temporary editor files.

---

## 3. Verification & Stability Test Results

### A. TypeScript Check (`vue-tsc --noEmit`)
- **Status:** **PASSED (0 Errors)**
- All types, views, stores, and services pass strict TypeScript validation.

### B. Production Build (`vue-tsc && vite build`)
- **Status:** **PASSED (Exit Code 0)**
- Production bundle compiled in 9.86s without errors.

### C. Direct Route Refresh & SPA Fallback Test
Each of the following routes was loaded and refreshed directly via HTTP:
- `http://localhost:5173/admin/students` -> **[PASS] 200 OK**
- `http://localhost:5173/admin/fees` -> **[PASS] 200 OK**
- `http://localhost:5173/admin/results` -> **[PASS] 200 OK**
- `http://localhost:5173/teacher/exams` -> **[PASS] 200 OK**
- `http://localhost:5173/teacher/classes` -> **[PASS] 200 OK**

### D. 20-Cycle Edit / HMR / Refresh Stability Test (`test_dev_server_stability.py`)
Executed an automated 20-cycle test against the live running Vite server:
- **Cycle Action:** Edit file -> Wait for HMR -> Simulate browser refresh with abrupt TCP `RST` socket close -> Navigate to `/admin/students` -> Navigate to `/admin/results` -> Navigate to `/teacher/exams` -> Return to `/admin/fees`.
- **Result:** **20 / 20 CYCLES PASSED (100% Availability)**
- **Connection Refusals:** **0**
- The server process remained active and responsive throughout all 20 cycles.

### E. Backend Unit Tests
- **Command:** `python -m pytest tests/test_fee_management_system.py -q`
- **Result:** **16 passed in 1.11s**

---

## 4. Summary Table

| Check / Requirement | Result | Notes |
| :--- | :--- | :--- |
| **Vite Dev Server Startup** | **PASS** | Running stably on `http://localhost:5173` |
| **HMR Functional** | **PASS** | HMR updates detected and delivered |
| **Socket RST / Browser Reload Immunity** | **PASS** | `ECONNRESET` cleanly absorbed; no crash |
| **Direct Route Refresh (SPA Fallback)** | **PASS** | All required admin/teacher routes return 200 |
| **Backend Proxy Error Resilience** | **PASS** | Proxy returns 503 if backend unreachable; Vite stays up |
| **TypeScript Typecheck** | **PASS** | 0 errors (`vue-tsc --noEmit`) |
| **Production Build** | **PASS** | Succeeded in 9.86s (`vite build`) |
| **20 Edit / Refresh Cycles** | **PASS** | 20 / 20 passed with 0 crashes |
| **Remaining Warnings** | None blocking | Vite chunk size recommendation (production bundle optimization) |
