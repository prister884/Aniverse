import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
import time

# Base URL for Telegram link
base_url = "https://t.me/mifikianivers/3502/"

# Starting message ID (the part that increases)
start_message_id = 3907

# Number of iterations (how many messages you want to capture)
num_loops = 15

# Directory for saving screenshots
screenshot_directory = "screenshots"

# Ensure the screenshot directory exists
if not os.path.exists(screenshot_directory):
    os.makedirs(screenshot_directory)

def capture_and_crop_screenshot(driver, message_id):
    """
    Capture a screenshot of the page, scale it to 75%, and then crop the central bottom part.
    The bottom will be cropped to remove Telegram's embed and "view in Telegram" buttons.
    """
    # Scale the browser window to 75%
    driver.execute_script("document.body.style.zoom='75%'")
    
    # Screenshot path
    screenshot_path = os.path.join(screenshot_directory, f"screenshot_{message_id}.png")
    
    # Take a screenshot of the page immediately
    driver.save_screenshot(screenshot_path)
    print(f"Captured screenshot for message {message_id}: {screenshot_path}")

    # Open the screenshot using Pillow
    img = Image.open(screenshot_path)

    # Get the dimensions of the image
    width, height = img.size

    # Define the coordinates for cropping (central bottom part)
    left = 1.2 * width // 3  # 25% from the left
    top = 1.4 * height // 2  # Start from the middle of the image
    right = 2.5 * width // 4  # 25% from the right
    bottom = height - 190  # Crop 100px from the bottom to exclude footer elements

    # Crop the image to keep only the central bottom part
    cropped_img = img.crop((left, top, right, bottom))

    # Cropped screenshot path
    cropped_screenshot_path = os.path.join(screenshot_directory, f"screenshot_{message_id}.png")
    
    # Save the cropped image
    cropped_img.save(cropped_screenshot_path)
    print(f"Cropped screenshot for message {message_id}: {cropped_screenshot_path}")

    # Return the path of the cropped image
    return cropped_screenshot_path


def fetch_telegram_data():
    # Setup Selenium WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()  # Optional: maximize window for better visibility

    for i in range(num_loops):
        # Dynamically generate the URL by incrementing the message ID
        message_id = start_message_id + i
        telegram_web_url = f"{base_url}{message_id}"

        print(f"Fetching data from: {telegram_web_url}")
        driver.get(telegram_web_url)

        # Capture and crop the screenshot of the page
        capture_and_crop_screenshot(driver, message_id)

        # Move on to the next message
        time.sleep(1)  # Optional: give a small delay between loading pages

    # Close the browser
    driver.quit()

# Run the function to load pages, scale the browser, take screenshots, and crop them
fetch_telegram_data()
