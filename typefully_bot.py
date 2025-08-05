import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def post_to_typefully(tweet):
    print("✅ Post generated successfully.")
    print("🔁 Launching headless browser...")

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=options)

    try:
        driver.get("https://typefully.com/login")

        # Log in with email
        email = os.getenv("TYPEFULLY_EMAIL")
        password = os.getenv("TYPEFULLY_PASSWORD")

        time.sleep(5)
        email_input = driver.find_element(By.NAME, "email")
        email_input.send_keys(email)
        email_input.submit()

        time.sleep(5)
        password_input = driver.find_element(By.NAME, "password")
        password_input.send_keys(password)
        password_input.submit()

        time.sleep(10)
        driver.get(f"https://typefully.com/new?text={tweet}")

        time.sleep(10)

        # Click publish
        publish_button = driver.find_element(By.XPATH, "//button[contains(text(),'Publish')]")
        publish_button.click()

        print("✅ Tweet published successfully via Typefully.")
    except Exception as e:
        print(f"❌ Failed to publish tweet: {e}")
    finally:
        driver.quit()
