import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

def post_to_typefully(tweet):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    try:
        driver.get("https://typefully.com/new")
        time.sleep(5)

        # Type tweet
        tweet_box = driver.find_element(By.CSS_SELECTOR, "div[contenteditable='true']")
        tweet_box.send_keys(tweet)
        time.sleep(2)

        # Click tweet button
        tweet_button = driver.find_element(By.XPATH, "//button[contains(text(),'Tweet now')]")
        tweet_button.click()
        time.sleep(3)
        print("✅ Tweet posted successfully!")

    except Exception as e:
        print("❌ Failed to post:", e)
    finally:
        driver.quit()
