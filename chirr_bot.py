import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

def post_to_twitter_via_chirr(tweet):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        print("🔁 Opening Chirr App...")
        driver.get("https://chirr.app/editor")
        time.sleep(5)

        print("✍️ Typing tweet...")
        textarea = driver.find_element(By.CSS_SELECTOR, "textarea")
        textarea.send_keys(tweet)
        time.sleep(2)

        print("✅ Click 'Tweet All'")
        tweet_all = driver.find_element(By.XPATH, "//button[contains(text(),'Tweet all')]")
        tweet_all.click()
        time.sleep(3)

        print("✅ Tweet sent successfully via Chirr!")

    except Exception as e:
        print("❌ Failed to post tweet:", e)

    finally:
        driver.quit()
