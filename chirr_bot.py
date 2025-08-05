import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def post_to_chirr(tweet_text):
    print("🔁 Launching headless browser...")

    # Set up headless Chrome
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")

    # Launch Chrome
    driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=options)

    try:
        print("🔁 Opening Chirr App...")
        driver.get("https://getchirrapp.com")
        time.sleep(4)

        # Enter email
        email_input = driver.find_element(By.CSS_SELECTOR, 'input[type="email"]')
        email_input.send_keys(os.environ["CHIRR_EMAIL"])
        driver.find_element(By.XPATH, "//button[contains(., 'Continue')]").click()
        time.sleep(3)

        # 🚨 OTP WARNING
        print("⚠️ OTP sent to email. This login step cannot be automated unless cookies are reused.")
        print("❌ Tweet not posted. You must log in manually once to save session cookies if you want full automation.")
        return

        # 🔒 --- BELOW CODE ONLY WORKS AFTER LOGIN / COOKIE STORAGE SETUP ---
        # If logged in, locate the textarea
        textarea = driver.find_element(By.CSS_SELECTOR, "textarea")
        print("✍️ Typing tweet...")
        textarea.send_keys(tweet_text)

        time.sleep(2)
        post_button = driver.find_element(By.XPATH, "//button[contains(., 'Post')]")
        post_button.click()

        print("✅ Tweet posted successfully on Chirr!")

    except Exception as e:
        print("❌ Failed to post tweet:", e)

    finally:
        driver.quit()
