# 📸 Instagram Follower Tracker

An automated Python Playwright script to compare your Instagram followers and following lists and identify accounts that you follow but do not follow you back.

Built using the same persistent session and stealth architecture used in production browser automations.

---

## ✨ Features

- **Real Browser Automation**: Uses your installed Google Chrome (`channel="chrome"`).
- **Persistent Session**: Logs in once and stores the authenticated session locally in `browser_session/`—no need to re-login or re-enter 2FA on future runs.
- **Zero Credential Exposure**: Never requires passwords in code; support for manual login or optional `.env` auto-fill.
- **Anti-Bot Stealth**: Clears `navigator.webdriver` flags, applies realistic User-Agent headers, and includes human-like scroll intervals to avoid rate limits.
- **Accurate Profile Inspection**: Automatically navigates to profile, opens `followers` and `following` modals, and scrolls to dynamically load all users.
- **Export Formats**:
  - Detailed CLI summary report with counts of followers, following, mutual friends, and non-followers.
  - Plain text list of profile URLs in `output/<username>_not_following_back.txt`.
  - Structured JSON data in `output/<username>_report.json`.

---

## 🚀 Getting Started

### 1. Prerequisites

- Python 3.8+
- Google Chrome installed

### 2. Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/HarshadHindlekar/instagram-follower-tracker.git
cd instagram-follower-tracker
pip install -r requirements.txt
playwright install chromium
```

### 3. Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and set your Instagram handle:

```env
INSTAGRAM_USERNAME=your_username
```

---

## 🏃 Running the Script

### Windows (1-Click Batch Runner)

Simply double-click:
```cmd
run_tracker.bat
```

### Or via Terminal

```bash
python instagram_tracker.py
```

### First-Time Flow:
1. Google Chrome opens to `https://www.instagram.com/`.
2. Log in manually (supports 2FA / checkpoints).
3. The session is saved to `browser_session/`.
4. The script opens your profile, scrolls through both lists, and generates the report.
5. On all subsequent runs, it runs automatically without prompting for login.

---

## 📁 Output

Results are saved in the `output/` directory (git-ignored for privacy):
- `output/<username>_not_following_back.txt`
- `output/<username>_report.json`

---

## 🛡️ Privacy & Security

- All session data (`browser_session/`), environment credentials (`.env`), logs, and follower lists are excluded from Git via `.gitignore`.
- Your credentials and session tokens never leave your local machine.

---

## 📄 License

MIT License. For educational and personal use only.
