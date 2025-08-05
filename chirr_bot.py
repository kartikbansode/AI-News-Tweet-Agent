import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

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

        # Wait for textarea to load
        wait = WebDriverWait(driver, 20)
        textarea = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[placeholder='Start typing your thread...']")))

        print("✍️ Typing tweet...")
        textarea.send_keys(tweet)
        time.sleep(2)

        print("✅ Click 'Tweet All'")
        tweet_all = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Tweet all')]")))
        tweet_all.click()
        time.sleep(3)

        print("✅ Tweet sent successfully via Chirr!")

    except Exception as e:
        print("❌ Failed to post tweet:", e)

    finally:
        driver.quit()
