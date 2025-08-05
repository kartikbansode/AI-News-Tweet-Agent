from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

TYPEFULLY_EMAIL = os.getenv("TYPEFULLY_EMAIL")
TYPEFULLY_PASSWORD = os.getenv("TYPEFULLY_PASSWORD")

def post_to_typefully(tweet_text):
    print("🔁 Launching headless browser...")
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    try:
        driver.get("https://typefully.com/login")
        time.sleep(3)

        # Email input
        email_input = driver.find_element(By.NAME, "email")
        email_input.send_keys(TYPEFULLY_EMAIL)

        driver.find_element(By.XPATH, "//button[contains(text(),'Continue')]").click()
        time.sleep(2)

        # Password input
        password_input = driver.find_element(By.NAME, "password")
        password_input.send_keys(TYPEFULLY_PASSWORD)

        driver.find_element(By.XPATH, "//button[contains(text(),'Log in')]").click()
        time.sleep(5)

        # Compose new post
        driver.get(f"https://typefully.com/new?text={tweet_text}")
        time.sleep(3)

        # Publish the tweet
        publish_btn = driver.find_element(By.XPATH, "//button[contains(text(),'Publish now')]")
        publish_btn.click()
        time.sleep(2)

        print("✅ Tweet published successfully on Typefully.")
    except Exception as e:
        print(f"❌ Error posting to Typefully: {e}")
    finally:
        driver.quit()
