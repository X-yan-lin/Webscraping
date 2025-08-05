import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ---- SETTINGS ----
collection_url = "https://goodr.com/collections/best-sellers"
driver_path = "/usr/local/bin/chromedriver"
csv_filename = "goodr_products_final.csv"

# ---- Set up Selenium ----
service = Service(driver_path)
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=service, options=options)
driver.get(collection_url)
time.sleep(2)  # Wait for JS rendering

# ---- Use BeautifulSoup to Extract Info from List Page ----
soup = BeautifulSoup(driver.page_source, "html.parser")
cards = soup.select('a.ns-product.ns-border-box.ns-clickable.ns-text-undecorated.goodr-product-grid-item')

product_rows = []
product_urls = []
brand = "Goodr" #Hard code for brand as it is consistent across the website

for idx, card in enumerate(cards[:10], 1):
    title_elem = card.select_one("h4.goodr-product-grid-item-title")
    product_name = title_elem.text.strip() if title_elem else ""
    product_url = card.get("href")
    # If the URL is relative, make it absolute:
    if product_url.startswith("/"):
        product_url = "https://goodr.com" + product_url
    price_elem = card.select_one("p.title2")
    price = price_elem.text.strip() if price_elem else ""
    discount_elem = card.select_one("p.body1.compare_at_price")
    discounted_price = discount_elem.text.strip() if discount_elem else "No Discount"
    product_urls.append(product_url)
    product_rows.append([
        collection_url,
        "list",
        product_name,
        brand,
        price,
        discounted_price,
        idx,                 # position (1-based)
        "",                  # number of photos (blank)
        "",                  # number of colors (blank)
        ""                   # product description (blank)
    ])

# ---- Scrape Product Detail Pages with Selenium ----
for url in product_urls:
    driver.get(url)
    time.sleep(1.5)  # Wait for product page to load

    # Brand
    brand = "Goodr"

    # Number of photos
    media_buttons = driver.find_elements(By.CSS_SELECTOR, "button.goodr-product-media-item")
    num_photos = len(media_buttons)

    # Number of visible colors
    num_colors = len(driver.find_elements(By.CSS_SELECTOR, 'div.swatch:not(.extra-swatch):not(.hidden)'))

    # Product description
    description = ""  # Default value to avoid NameError
    try:
        box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div.goodr-product-description div.product-description-box"))
        )
        raw_text = box.text.strip()
        lines = raw_text.splitlines()
        if lines and lines[0].strip().upper() == "DESCRIPTION":
            lines = lines[1:]
        description = " ".join(lines).strip()
    except Exception as e:
        print(f"[{url}] Description extraction error: {e}")
        description = ""

    # Product name (from detail page)
    try:
        name_elem = driver.find_element(By.CSS_SELECTOR, "h1.goodr-product-title")
        product_name = name_elem.text.strip()
    except:
        product_name = ""

    # Price
    try:
        price_elem = driver.find_element(By.CSS_SELECTOR, "span.product-price")
        price = price_elem.text.strip()
    except:
        price = ""

    # Discounted price
    try:
        discounted_elem = driver.find_element(By.CSS_SELECTOR, "span.product-compare-at-price")
        discounted_price = discounted_elem.text.strip()
    except:
        discounted_price = ""

    product_rows.append([
        url,                 # URL (product page)
        "product",           # list/product page
        product_name,
        brand,
        price,
        discounted_price,
        "",                  # position (blank for product page)
        num_photos,
        num_colors,
        description
    ])

driver.quit()

# ---- Write to CSV ----
csv_abspath = os.path.abspath(csv_filename)
print("Your CSV will be saved to:", csv_abspath)

with open(csv_abspath, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow([
        "URL",
        "list/product page",
        "product name",
        "brand",
        "price",
        "discounted price",
        "position",
        "number of photos",
        "number of colors",
        "description"
    ])
    writer.writerows(product_rows)

print("CSV saved as", csv_abspath)
