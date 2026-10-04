import os
import sys
import time
import json
import random
import logging
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

LOG_DIR = os.path.join(BASE_DIR, "logs")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
SESSION_DIR = os.path.join(BASE_DIR, "browser_session")

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(SESSION_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "instagram_tracker.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("InstagramTracker")

IG_USERNAME = (os.getenv("INSTAGRAM_USERNAME") or "").strip() or "hind_harshad"

def scrape_list(page, list_type: str) -> set:
    """Clicks the followers or following button in the profile header and scrolls the modal."""
    logger.info(f"Opening '{list_type}' modal on profile header...")

    # Accurate selector matching Instagram's profile header (e.g. '842 followers', '661 following')
    button = page.locator(f'header a:has-text("{list_type}")').first
    try:
        button.wait_for(state="visible", timeout=15000)
        button_text = button.text_content().strip()
        logger.info(f"Found button: '{button_text}'. Clicking to open modal...")
        button.click()
    except Exception as e:
        logger.error(f"Could not find or click '{list_type}' button: {e}")
        return set()

    dialog_selector = 'div[role="dialog"]'
    try:
        dialog = page.locator(dialog_selector).first
        dialog.wait_for(state="visible", timeout=12000)
    except Exception as e:
        logger.error(f"Dialog for {list_type} not found: {e}")
        return set()

    logger.info(f"Scrolling through {list_type} to load all accounts...")
    collected = set()
    last_count = 0
    stagnant_iterations = 0

    time.sleep(2)

    while True:
        # Extract usernames from links inside dialog
        anchors = dialog.locator('a[role="link"]').all()
        for a in anchors:
            try:
                href = a.get_attribute("href")
                if href:
                    parts = [p for p in href.strip("/").split("/") if p]
                    if len(parts) == 1 and parts[0] not in ["explore", "reels", "stories", "direct", "settings", IG_USERNAME]:
                        collected.add(parts[0])
            except Exception:
                pass

        curr_count = len(collected)
        print(f"   Collected {curr_count} {list_type}...", end="\r", flush=True)

        if curr_count == last_count:
            stagnant_iterations += 1
            if stagnant_iterations >= 6:
                break
        else:
            stagnant_iterations = 0
            last_count = curr_count

        # Scroll the modal container
        page.evaluate("""
            () => {
                const dialog = document.querySelector('div[role="dialog"]');
                if (!dialog) return;
                const scrollable = Array.from(dialog.querySelectorAll('div')).find(
                    d => d.scrollHeight > d.clientHeight && d.clientHeight > 150
                );
                if (scrollable) {
                    scrollable.scrollTop = scrollable.scrollHeight;
                }
            }
        """)
        time.sleep(random.uniform(1.2, 1.8))

    print()
    logger.info(f"Retrieved {len(collected)} {list_type} in total.")

    # Close modal
    try:
        page.keyboard.press("Escape")
    except Exception:
        pass
    time.sleep(2)
    return collected

def run_tracker():
    logger.info("=" * 60)
    logger.info(f"Starting Instagram Follower Tracker for @{IG_USERNAME}")
    logger.info("=" * 60)

    with sync_playwright() as p:
        launch_kwargs = {
            "user_data_dir": SESSION_DIR,
            "headless": False,
            "channel": "chrome",  # Real Google Chrome
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "viewport": {"width": 1366, "height": 850},
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-infobars"
            ]
        }

        browser_context = p.chromium.launch_persistent_context(**launch_kwargs)
        page = browser_context.pages[0] if browser_context.pages else browser_context.new_page()
        page.set_default_timeout(40000)

        # Stealth: remove navigator.webdriver flag
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        profile_url = f"https://www.instagram.com/{IG_USERNAME}/"
        logger.info(f"Opening your profile: {profile_url}")
        page.goto(profile_url, wait_until="domcontentloaded")
        time.sleep(3)

        # 1. Scrape Following
        following = scrape_list(page, "following")

        # 2. Scrape Followers
        followers = scrape_list(page, "followers")

        browser_context.close()

    # 3. Compare
    not_following_back = sorted(list(following - followers))
    fans = sorted(list(followers - following))
    mutuals = sorted(list(following & followers))

    logger.info("=" * 60)
    logger.info(f"📊 REPORT FOR @{IG_USERNAME}")
    logger.info("=" * 60)
    logger.info(f"Followers count : {len(followers)}")
    logger.info(f"Following count : {len(following)}")
    logger.info(f"Mutual friends  : {len(mutuals)}")
    logger.info(f"🚨 Users who DO NOT follow you back: {len(not_following_back)}")
    logger.info("=" * 60)

    if not_following_back:
        print("\nAccounts you follow who DO NOT follow you back:")
        for idx, u in enumerate(not_following_back, 1):
            print(f"  {idx:3d}. @{u:<25} (https://instagram.com/{u})")
    else:
        print("\n🎉 Everyone you follow follows you back!")

    # Save to files
    out_txt = os.path.join(OUTPUT_DIR, f"{IG_USERNAME}_not_following_back.txt")
    with open(out_txt, "w", encoding="utf-8") as f:
        for u in not_following_back:
            f.write(f"https://instagram.com/{u}\n")

    out_json = os.path.join(OUTPUT_DIR, f"{IG_USERNAME}_report.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump({
            "target": IG_USERNAME,
            "followers_count": len(followers),
            "following_count": len(following),
            "not_following_back_count": len(not_following_back),
            "not_following_back": not_following_back,
            "fans_count": len(fans),
            "fans": fans,
            "mutuals_count": len(mutuals),
            "mutuals": mutuals
        }, f, indent=2)

    logger.info(f"Saved non-followers list to: {out_txt}")
    logger.info(f"Saved full JSON report to: {out_json}")
    logger.info("✨ Done!")

if __name__ == "__main__":
    try:
        run_tracker()
    except KeyboardInterrupt:
        print("\nAborted by user.")
