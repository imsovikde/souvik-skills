# Chromium Core Architecture & Event Routing Forensics

## 1. Chromium Multi-Process Architecture

Chromium executes across strictly isolated processes connected by Mojo IPC channels:

1. **Browser Process (`BrowserProcess`)**:
   - Manages top-level OS windows, native menus, bookmarks, passwords, and sessions.
   - Owns the native Win32 `HWND` and receives raw OS window messages (`WM_LBUTTONDOWN`, `WM_MOUSEMOVE`, `WM_LBUTTONUP`) via `HWNDMessageHandler`.
2. **GPU Process (`GpuProcess` / `Viz`)**:
   - Rasterizes visual primitives and composites surface layers via DirectComposition on Windows.
   - Interacts with display drivers via ANGLE (translating OpenGL ES / WebGL to Direct3D 11/12).
   - Manages compiled shader disk caches (`GrShaderCache`, `GPUCache`, `DawnGraphiteCache`).
3. **Renderer Process (`RenderProcessHost` / Blink)**:
   - Executes HTML parsing, layout, CSS style recalculations, and V8 JavaScript engines.
   - Hosts isolated extension content scripts in separate isolated worlds.
4. **Storage Service (`StorageService`)**:
   - Owns LevelDB databases (`IndexedDB`, `Service Worker\Database`, `Session Storage`) and SQLite databases (`Login Data`, `History`, `Web Data`).

---

## 2. Windows Pointer Input Event Pipeline

When a user clicks on an element in the browser, the event traverses this exact chain:

```
[Windows OS Mouse Hardware]
           │
           ▼
[Desktop Window Manager (DWM)]
           │
           ▼
[WM_LBUTTONDOWN -> HWNDMessageHandler]
           │
           ▼
[RenderWidgetHostViewAura (Top-level Window)]
           │
           ▼
[RenderWidgetHostInputEventRouter (Hit-testing across frames & sub-surfaces)]
           │
           ▼ (Mojo IPC)
[Blink InputHandlerProxy in Renderer Process]
           │
           ▼
[DOM Event Dispatcher]
           │
           ├─► Phase 1: CAPTURE PHASE (window -> document -> html -> body -> ... -> target)
           │     * Any extension listener with { capture: true } executes here!
           │     * If it calls e.stopPropagation() or stopImmediatePropagation(),
           │       the event NEVER reaches the target element or bubbling listeners!
           │
           ├─► Phase 2: TARGET PHASE (target element)
           │     * Native in-page event handlers execute.
           │
           └─► Phase 3: BUBBLE PHASE (target -> ... -> body -> html -> document -> window)
```

### Why Synthetic `element.click()` Fails as a Test:
Calling `element.click()` in V8 synchronously creates a synthetic DOM click event starting directly at the target element. It completely bypasses:
1. The OS window message pump (`WM_LBUTTONDOWN`).
2. `HWNDMessageHandler` and `RenderWidgetHostInputEventRouter`.
3. DWM DirectComposition hit-testing across secondary popup surfaces.
4. Top-level window capture listeners that intercept `mousedown` and `mouseup`.
Only true physical pointer dispatch via Chrome DevTools Protocol (`Input.dispatchMouseEvent` with `mousePressed` and `mouseReleased` at physical screen coordinates) traverses the full OS-to-DOM pipeline.

---

## 3. Extension Capture-Phase Event Hijacking

Extensions that bypass site copy-paste restrictions or implement page blocking often register:
```javascript
document.addEventListener('mousedown', (e) => e.stopPropagation(), true);
document.addEventListener('mouseup', (e) => e.stopPropagation(), true);
```
Or nullify inline handlers:
```javascript
document.body.onmousedown = null;
document.onmousedown = null;
```
Because dropdown menus (HTML `<select>` and Google Account flyouts) and action bars (Gmail Refresh, Back button) rely on `mousedown` to trigger popup widgets and commit action closures, this capture interception freezes UI interaction across entire domains.

---

## 4. Intel Iris Xe DirectComposition Surface Desync

On Windows 11 with Intel Iris Xe Graphics drivers, stale precompiled shaders in `GrShaderCache` and `GPUCache` can cause sub-surfaces (dropdown listboxes, autocomplete popups, and iframe flyouts) to fail DWM hit-testing. 

**Mechanistic Failure**: Pointer clicks hit the parent background layer instead of the foreground dropdown surface.
**Surgical Fix**: Enforce software composition fallback in `Local State` and `Preferences`:
```json
"hardware_acceleration_mode": { "enabled": false }
```
This forces Chromium to use software rasterization for popups, instantly restoring 100% reliable hit-testing without display driver desync.

---

## 5. Storage Engine Deadlocks

Gmail's Closure compiler relies on IndexedDB LevelDB transaction logs (`https_mail.google.com_0.indexeddb.leveldb`) and Blink `ServiceWorker\CacheStorage`. When uncompacted `.log` files or locked transaction states accumulate, asynchronous storage callbacks deadlock. The UI event dispatcher hangs waiting for storage completion callbacks, locking buttons in a non-responsive state. Purging ephemeral LevelDB and Service Worker caches cleanly resets the pipeline without losing saved credentials or history.
