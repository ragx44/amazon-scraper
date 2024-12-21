import time
import csv
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# Configuration
AMAZON_EMAIL = 'your_email@example.com'  # Replace with your Amazon email
AMAZON_PASSWORD = 'your_password'          # Replace with your Amazon password
CATEGORIES = [
    'kitchen', 'shoes', 'computers', 'electronics', 'books',
    'clothing', 'toys', 'home_improvement', 'sports', 'health'
]
OUTPUT_FILE = 'amazon_best_sellers.json'  # Output file name

# Initialize WebDriver
options = Options()
options.add_argument('--headless')  # Run in headless mode
service = Service('path/to/chromedriver')  # Update with your chromedriver path
driver = webdriver.Chrome(service=service, options=options)

def login():
    driver.get('https://www.amazon.in/ap/signin')
    time.sleep(2)
    email_input = driver.find_element(By.ID, 'ap_email')
    email_input.send_keys(AMAZON_EMAIL)
    email_input.send_keys(Keys.RETURN)
    time.sleep(2)
    password_input = driver.find_element(By.ID, 'ap_password')
    password_input.send_keys(AMAZON_PASSWORD)
    password_input.send_keys(Keys.RETURN)
    time.sleep(5)

def scrape_category(category):
    driver.get(f'https://www.amazon.in/gp/bestsellers/{category}/ref=zg_bs_nav_{category}_0')
    time.sleep(3)
    
    products = []
    product_elements = driver.find_elements(By.CSS_SELECTOR, '.zg-item-immersion')
    
    for product in product_elements[:150]:  # Limit to top 150 products
        try:
            name = product.find_element(By.CSS_SELECTOR, 'div.p13n-sc-truncate').text
            price = product.find_element(By.CSS_SELECTOR, '.p13n-sc-price').text
            discount = product.find_element(By.CSS_SELECTOR, '.p13n-sc-price').get_attribute('innerText')
            rating = product.find_element(By.CSS_SELECTOR, 'span.a-icon-alt').text
            ship_from = product.find_element(By.CSS_SELECTOR, '.a-size-small.a-color-secondary').text
            sold_by = product.find_element(By.CSS_SELECTOR, '.a-size-small.a-color-secondary').text
            description = product.find_element(By.CSS_SELECTOR, '.a-size-small.a-color-secondary').text
            images = [img.get_attribute('src') for img in product.find_elements(By.CSS_SELECTOR, 'img')]
            
            # Check for discount
            if float(discount.strip('%')) > 50:
                products.append({
                    'Product Name': name,
                    'Product Price': price,
                    'Sale Discount': discount,
                    'Best Seller Rating': rating,
                    'Ship From': ship_from,
                    'Sold By': sold_by,
                    'Rating': rating,
                    'Product Description': description,
                    'Category Name': category,
                    'All Available Images': images
                })
        except NoSuchElementException:
            continue

    return products

def main():
    login()
    all_products = []

    for category in CATEGORIES:
        print(f'Scraping category: {category}')
        products = scrape_category(category)
        all_products.extend(products)

    # Save to JSON
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(all_products, f, indent=4)

    print(f'Scraped {len(all_products)} products. Data saved to {OUTPUT_FILE}.')
    driver.quit()

if __name__ == '__main__':
    main()