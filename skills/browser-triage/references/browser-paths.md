# Cross-Browser User Data & Binary Paths Reference

## 1. Windows Paths

### Profile Data Directories
- **Brave Browser**:
  `%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data\<Profile>`
- **Google Chrome**:
  `%LOCALAPPDATA%\Google\Chrome\User Data\<Profile>`
- **Microsoft Edge**:
  `%LOCALAPPDATA%\Microsoft\Edge\User Data\<Profile>`
- **Chromium**:
  `%LOCALAPPDATA%\Chromium\User Data\<Profile>`

### Default Executable Paths
- **Brave Browser**:
  `C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe`
- **Google Chrome**:
  `C:\Program Files\Google\Chrome\Application\chrome.exe`
- **Microsoft Edge**:
  `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`
- **Chromium**:
  `%LOCALAPPDATA%\Chromium\Application\chrome.exe`

---

## 2. macOS Paths

### Profile Data Directories
- **Brave Browser**:
  `~/Library/Application Support/BraveSoftware/Brave-Browser/<Profile>`
- **Google Chrome**:
  `~/Library/Application Support/Google/Chrome/<Profile>`
- **Microsoft Edge**:
  `~/Library/Application Support/Microsoft Edge/<Profile>`
- **Chromium**:
  `~/Library/Application Support/Chromium/<Profile>`

---

## 3. Linux Paths

### Profile Data Directories
- **Brave Browser**:
  `~/.config/BraveSoftware/Brave-Browser/<Profile>`
- **Google Chrome**:
  `~/.config/google-chrome/<Profile>`
- **Microsoft Edge**:
  `~/.config/microsoft-edge/<Profile>`
- **Chromium**:
  `~/.config/chromium/<Profile>`

---

## 4. Immutable Profile Files (NEVER DELETE)
- `Bookmarks` & `Bookmarks.bak`: Saved bookmarks tree.
- `Login Data` & `Login Data For Account`: Saved credentials and encrypted passwords.
- `History` & `Favicons`: Browsing records and page favicons.
- `Web Data`: Autofill records, addresses, and saved payment profiles.
- `Sessions/`: Active and previous tab/window states.
- `Preferences` & `Secure Preferences`: User settings and extension configuration (modify surgically via JSON).
