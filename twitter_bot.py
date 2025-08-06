from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

def post_to_twitter(tweet):
    print("🔁 Launching browser...")

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    try:
        driver.get("https://twitter.com/login")
        time.sleep(5)

        # Enter email
        email_input = driver.find_element(By.NAME, "text")
        email_input.send_keys(os.environ["TWITTER_EMAIL"])
        email_input.send_keys(Keys.RETURN)
        time.sleep(3)

        # Check for possible username screen
        try:
            username_input = driver.find_element(By.NAME, "text")
            username_input.send_keys(Keys.RETURN)
            time.sleep(3)
        except:
            pass

        # Enter password
        password_input = driver.find_element(By.NAME, "password")
        password_input.send_keys(os.environ["TWITTER_PASSWORD"])
        password_input.send_keys(Keys.RETURN)
        time.sleep(5)

        # Post tweet
        tweet_box = driver.find_element(By.CSS_SELECTOR, "div[aria-label='Tweet text']")
        tweet_box.send_keys(tweet)
        time.sleep(2)

        tweet_button = driver.find_element(By.XPATH, "//div[@data-testid='tweetButtonInline']")
        tweet_button.click()
        time.sleep(5)

        print("✅ Tweet posted!")

    except Exception as e:
        print("❌ Failed to post:", e)

    finally:
        driver.quit()
