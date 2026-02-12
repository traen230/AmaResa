from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def search_google_news(keyword):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = "/usr/bin/chromium"

    driver = webdriver.Chrome(executable_path="/usr/bin/chromedriver", options=options)

    try:
        query = f"https://www.google.com/search?q={keyword}&tbm=nws"
        driver.get(query)
        time.sleep(2)

        results = []
        elements = driver.find_elements(By.CSS_SELECTOR, "div.dbsr")
        for el in elements[:3]:
            title = el.find_element(By.TAG_NAME, "div").text
            url = el.find_element(By.TAG_NAME, "a").get_attribute("href")
            results.append((title, url))

        return results
    finally:
        driver.quit()
