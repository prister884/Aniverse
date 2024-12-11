# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# import time

# # Base URL for Telegram link
# base_url = "https://t.me/mifikianivers/1894/"

# # Starting message ID (the part that increases)
# start_message_id = 270232

# # Number of iterations (how many messages you want to capture)
# num_loops = 10

# def capture_screenshot(driver, message_id):
#     """
#     Capture a screenshot of the page after scaling it to 75%.
#     """
#     # Scale the browser window to 75%
#     driver.execute_script("document.body.style.zoom='75%'")
    
#     # Take a screenshot of the page immediately
#     screenshot_path = f"screenshot_{message_id}.png"
#     driver.save_screenshot(screenshot_path)
#     print(f"Captured screenshot for message {message_id}: {screenshot_path}")

# def fetch_telegram_data():
#     # Setup Selenium WebDriver
#     driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
#     driver.maximize_window()  # Optional: maximize window for better visibility

#     for i in range(num_loops):
#         # Dynamically generate the URL by incrementing the message ID
#         message_id = start_message_id + i
#         telegram_web_url = f"{base_url}{message_id}"

#         print(f"Fetching data from: {telegram_web_url}")
#         driver.get(telegram_web_url)

#         # Capture a screenshot of the page with scaling
#         capture_screenshot(driver, message_id)

#         # Move on to the next message
#         time.sleep(1)  # Optional: give a small delay between loading pages

#     # Close the browser
#     driver.quit()

# # Run the function to load pages, scale the browser, and take screenshots
# fetch_telegram_data()



