import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def post_to_chirr(tweet_text):
    print("🔁 Launching headless browser...")

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        print("🔁 Opening Chirr App...")
        driver.get("https://getchirrapp.com")

        wait = WebDriverWait(driver, 20)

        # Wait for email input to be visible and interactable
        email_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="email"]')))
        email_input.send_keys(os.environ["CHIRR_EMAIL"])

        # Click Continue button
        continue_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Continue')]")))
        continue_btn.click()

        # Wait for manual OTP entry (can't bypass via code)
        print("⚠️ OTP login required. Please complete OTP manually (1 minute timeout)...")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "textarea")))

        # Wait for tweet box to become clickable
        textarea = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "textarea")))
        print("✍️ Typing tweet...")
        textarea.send_keys(tweet_text)

        # Post button click
        post_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Post')]")))
        post_button.click()

        print("✅ Tweet posted successfully on Chirr!")

    except Exception as e:
        print("❌ Failed to post tweet:", e)

    finally:
        driver.quit()
