---
name: browser-triage
description: Diagnose and surgically remediate Chromium and Brave UI freezes, event hijacking, and storage corruption without user data loss. Scans extensions for capture-phase listeners, repairs LevelDB and GPU shader caches, and verifies fixes with physical OS pointer events. Use when browser dropdowns fail, web actions freeze, or suspect extensions hijack pointer events.
---

# Browser Triage: Autonomous Chromium & Brave Remediation Engine

A systems-level diagnostic and surgical remediation suite for Chromium-based browsers (Brave, Google Chrome, Microsoft Edge, Chromium). Resolves UI freezes, dead dropdowns, broken action bars, and unresponsive web controls caused by extension capture-phase event hijacking, DirectComposition surface desync, and LevelDB storage corruption—with **absolute zero user data loss**.

---

## 1. Core Principles & Iron Invariants

### Zero User Data Loss (Non-Negotiable)
Under no circumstances may user data be wiped, deleted, or reset. The following files and directories are completely immutable and must remain 100% intact:
- `Bookmarks` (Saved bookmarks and folders)
- `Login Data` & `Login Data For Account` (Saved credentials and passwords)
- `History` & `Favicons` (Browsing history and page favicons)
- `Web Data` (Autofill data, addresses, payment cards)
- `Sessions/` & `Current Session` / `Current Tabs` (Active browser tabs and windows)
- `Preferences` (Must only be modified surgically via in-memory JSON parsing; never wiped)

### Physical Verification (Anti-Sycophancy)
Never claim that an issue is resolved using synthetic JavaScript (`element.click()`, `dispatchEvent()`, or `location.hash = ...`). Synthetic events bypass Windows OS message pumps, Chromium's `RenderWidgetHostInputEventRouter`, and extension capture listeners. All empirical verification must use physical OS-level pointer dispatch (e.g., Chrome DevTools Protocol `Input.dispatchMouseEvent` with `mousePressed` and `mouseReleased` at exact physical coordinates).

---

## 2. Common Failure Modes & Mechanisms

### A. Capture-Phase Event Hijacking
Extensions running in `<all_urls>` with `"run_at": "document_start"` can attach capture-phase listeners:
```javascript
window.addEventListener('mousedown', (e) => {
  e.stopImmediatePropagation();
  e.preventDefault();
}, true); // true = CAPTURE PHASE
```
Because capture listeners fire from the window down through the DOM hierarchy before target listeners execute, calling `stopImmediatePropagation()` silently snuffs out all clicks before they reach web app buttons (such as Gmail's Closure action buttons or account flyouts). In addition, extensions often nullify native handlers (`document.onmousedown = null`), destroying custom framework event buses.

### B. DirectComposition & GPU Shader Cache Desync
On Windows systems with integrated graphics (e.g., Intel Iris Xe), ANGLE (Direct3D 11/12) renders secondary dropdown popups (`<select>` menus, Google Account switcher iframes, extension flyouts) to independent DirectComposition surfaces. Corrupted shader caches (`GPUCache`, `GrShaderCache`, `DawnGraphiteCache`) cause hit-testing failure in the Desktop Window Manager (DWM). Physical mouse clicks pass straight through the popup surface to the underlying page.

### C. LevelDB Uncompacted Write-Ahead Log Deadlocks
IndexedDB and LocalStorage rely on Google's LevelDB engine. If the browser exits abruptly or an extension floods storage transactions, LevelDB log files (`.log`) fail to compact into immutable `.ldb` SSTables. On launch, the storage thread hangs while attempting WAL replay, deadlocking web applications that await `indexedDB.open()`.

---

## 3. Toolkit Reference

The `browser-triage` skill bundles four purpose-built diagnostic and repair tools in `scripts/`:

| Script | Purpose |
| :--- | :--- |
| `scripts/scan_extensions.py` | AST/regex static analysis of all installed extensions to identify capture listeners, `stopImmediatePropagation`, and handler nulling. Outputs blast-radius risk scores (0-100). |
| `scripts/remediate_storage.py` | Performs atomic backup of user SQLite databases and surgically purges uncompacted LevelDB logs, ServiceWorker caches, and GPU shader caches. |
| `scripts/manage_extension.py` | Queries, disables, enables, or quarantines extensions in `Preferences` and `Secure Preferences` by modifying Chromium state flags without touching user profiles. |
| `scripts/verify_pointer.js` | Dispatches real CDP `Input.dispatchMouseEvent` (`mousePressed`/`mouseReleased`) to verify that buttons trigger physical DOM updates and network requests. |

---

## 4. Remediation Workflow

When a user reports UI non-responsiveness, dropdown menu failures, or unresponsive buttons:

### Step 1: Identify Browser & Active Processes
Locate the user data directory (see `references/browser-paths.md`) and inspect running processes:
```powershell
Get-Process brave, chrome, msedge -ErrorAction SilentlyContinue | Select-Object Id, ProcessName, CommandLine
```

### Step 2: Audit Installed Extensions
Execute `scan_extensions.py` against the browser's profile directory to identify suspect extensions:
```powershell
python scripts/scan_extensions.py --profile "$env:LOCALAPPDATA\BraveSoftware\Brave-Browser\User Data\Default"
```
The scanner inspects background workers and content scripts, reporting:
- Capture-phase event listeners (`addEventListener(..., true)`)
- Propagation cancellations (`stopPropagation`, `stopImmediatePropagation`)
- Direct property wipes (`onmousedown = null`, `onclick = null`)
- High-risk permission scopes (`<all_urls>`, `webNavigation`, `debugger`)

### Step 3: Surgically Disable Suspect Extensions
Disable identified culprits without deleting them using `manage_extension.py`:
```powershell
python scripts/manage_extension.py --profile "$env:LOCALAPPDATA\BraveSoftware\Brave-Browser\User Data\Default" --disable <extension_id>
```
To restore or quarantine:
```powershell
# Restore extension
python scripts/manage_extension.py --profile "$env:LOCALAPPDATA\BraveSoftware\Brave-Browser\User Data\Default" --enable <extension_id>

# Move extension folder to a quarantine location outside User Data
python scripts/manage_extension.py --profile "$env:LOCALAPPDATA\BraveSoftware\Brave-Browser\User Data\Default" --quarantine <extension_id>
```

### Step 4: Storage & Shader Cache Cleanup
If the issue involves rendering anomalies, dead dropdown surfaces, or database stalls, run `remediate_storage.py`:
```powershell
python scripts/remediate_storage.py --user-data "$env:LOCALAPPDATA\BraveSoftware\Brave-Browser\User Data"
```
This utility:
1. Creates a timestamped `.backup` of `Bookmarks`, `Login Data`, `History`, `Web Data`, and `Preferences`.
2. Purges stale DirectComposition / GPU shader caches (`GPUCache`, `GrShaderCache`, `DawnGraphiteCache`).
3. Purges ephemeral ServiceWorker script caches (`Service Worker/CacheStorage`).
4. Compacts LevelDB stores by removing dead uncompacted `.log` files while preserving `.ldb` data tables.
5. If GPU hit-testing continues to fail, configures software rasterization fallback in `Local State` (`hardware_acceleration_mode.enabled = false`).

### Step 5: Empirical Pointer Verification
Launch the browser with remote debugging enabled or attach to the active instance, then run `verify_pointer.js`:
```powershell
node scripts/verify_pointer.js --port 9222 --url "https://mail.google.com" --selector "div[role='button'][aria-label*='Refresh']"
```
The verification script:
1. Queries the target element's bounding box using CDP `DOM.getBoxModel`.
2. Computes the exact center coordinate `(x, y)`.
3. Dispatches physical `Input.dispatchMouseEvent` with `mousePressed` followed by `mouseReleased`.
4. Listens for resulting network requests (`Network.requestWillBeSent`) or DOM attribute mutations.
5. Emits strict pass/fail telemetry with raw exit codes.

---

## 5. Architectural References
- Consult `references/chromium-architecture.md` for in-depth details on `HWNDMessageHandler`, `RenderWidgetHostInputEventRouter`, and DWM multi-surface composition.
- Consult `references/browser-paths.md` for standard directory layouts across Windows, macOS, and Linux.
