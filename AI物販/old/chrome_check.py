from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import subprocess

chrome_driver_path = r"C:\Users\SOICHIRO SAHARA\Documents\BizBright\04 Script\99 temp\chromedriver-win64\chromedriver-win64\chromedriver.exe"

# ChromeDriverのバージョン確認
version_info = subprocess.run(
    [chrome_driver_path, "--version"],
    capture_output=True,
    text=True
)

print("現在のChromeDriverバージョン:")
print(version_info.stdout)
