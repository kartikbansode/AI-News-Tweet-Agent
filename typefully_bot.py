import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def post_to_typefully(tweet):
    print("✅ Post generated successfully.")
    print("🔁 Launching headless browser...")

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    driver.get("https://typefully.com/login")

    time.sleep(3)

    email = os.getenv("TYPEFULLY_EMAIL")
    password = os.getenv("TYPEFULLY_PASSWORD")

    # Fill in email
    email_input = driver.find_element(By.NAME, "email")
    email_input.send_keys(email)
    email_input.send_keys(Keys.RETURN)

    time.sleep(3)

    # Fill in password (this only works if password auth is enabled on your account)
    password_input = driver.find_element(By.NAME, "password")
    password_input.send_keys(password)
    password_input.send_keys(Keys.RETURN)

    time.sleep(5)

    # Go to new tweet page
    driver.get(f"https://typefully.com/new?text={tweet}")

    time.sleep(5)

    # Click the tweet/send button (if available)
    try:
        tweet_button = driver.find_element(By.XPATH, "//button[contains(., 'Post') or contains(., 'Tweet')]")
        tweet_button.click()
        print("✅ Tweet posted via Typefully.")
    except:
        print("⚠️ Could not find 'Post' button. Manual confirmation may be required.")

    driver.quit()
