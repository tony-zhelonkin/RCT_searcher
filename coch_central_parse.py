from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

# Initialize the web driver
driver = webdriver.Chrome(executable_path='/path/to/chromedriver')

# Open Cochrane Library
driver.get('https://www.cochranelibrary.com/central')

# Wait for the page to load
time.sleep(5)

# Locate search bar and enter query
search_bar = driver.find_element_by_id('search-box-input')
search_bar.send_keys('oncology')
search_bar.send_keys(Keys.RETURN)

# Wait for search results to load
time.sleep(5)

# Example of scraping search results
from bs4 import BeautifulSoup

# Get page source and parse with BeautifulSoup
page_source = driver.page_source
soup = BeautifulSoup(page_source, 'html.parser')

# Find and print search results
results = soup.find_all('div', class_='result')
for result in results:
    title = result.find('a', class_='result-title').text
    print(title)

# Close the driver
driver.quit()
