import csv
import time
import curl_cffi.requests as requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import List

# https://id1.iherb.com/c/sports?p=1
CATEGORY_URL = "https://id1.iherb.com/c/sports"
API_URL_TEMPLATE = "https://id1.iherb.com/ugc/api/product/v2/{}"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
}

@dataclass
class Product:
    product_id: int
    display_name: str
    is_available: bool
    part_number: str
    root_category_name: str
    product_url: str
    discount_price: str
    list_price: str
    brand_name: str
    brand_url: str
    brand_logo_url: str
    primary_image_index: int

def fetch_category_page(url):
    """Fetch the category page HTML with error handling."""
    try:
        response = requests.get(url, headers=HEADERS, impersonate="chrome110", timeout=10)

        if response.status_code == 200:
            return response.text
        elif response.status_code == 403:
            print("[❌] Blocked! Try changing IP or use a proxy.")
        elif response.status_code == 429:
            print("[⏳] Rate limit hit! Please wait...")
            time.sleep(10)  # Wait before retrying
            return fetch_category_page(url)  # Try again
        else:
            print(f"[⚠] Error {response.status_code} when fetching category page.")

    except requests.exceptions.Timeout:
        print("[⏳] Timeout! Server too slow.")
    except requests.exceptions.RequestException as e:
        print(f"[❌] Request error: {e}")

    return None

def extract_product_ids(html_content):
    """Extract product IDs from the category page."""
    soup = BeautifulSoup(html_content, "html.parser")
    product_cards = soup.find_all("a", class_="product-link")

    product_ids = set()
    for card in product_cards:
        product_id = card.get("data-product-id")
        if product_id:
            product_ids.add(product_id)

    return list(product_ids)

def fetch_product_details(product_id):
    """Fetch complete product details from the API based on product ID with error handling."""
    url = API_URL_TEMPLATE.format(product_id)

    try:
        response = requests.get(url, headers=HEADERS, impersonate="chrome110", timeout=10)

        if response.status_code == 200:
            try:
                return response.json()
            except ValueError:
                print(f"[⚠] Failed to parse JSON for product {product_id}")
                return None

        elif response.status_code == 404:
            print(f"[⚠] Product {product_id} not found (404).")
        elif response.status_code == 429:
            print("[⏳] Rate limit hit! Please wait...")
            time.sleep(10)
            return fetch_product_details(product_id)  # Try again
        else:
            print(f"[⚠] Error {response.status_code} for product {product_id}")

    except requests.exceptions.Timeout:
        print(f"[⏳] Timeout when fetching product {product_id}.")
    except requests.exceptions.RequestException as e:
        print(f"[❌] Request error for product {product_id}: {e}")

    return None

def save_to_csv(products: List[Product], filename="products.csv"):
    """Save product data to a CSV file."""
    with open(filename, mode="w", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            "Product ID", "Display Name", "Available", "Part Number", "Category", 
            "Product URL", "Discount Price", "List Price", "Brand Name", "Brand URL", 
            "Brand Logo URL", "Primary Image Index"
        ])
        for product in products:
            writer.writerow([
                product.product_id, product.display_name, product.is_available, product.part_number, 
                product.root_category_name, product.product_url, product.discount_price, 
                product.list_price, product.brand_name, product.brand_url, 
                product.brand_logo_url, product.primary_image_index
            ])

# 1. Fetch the category page HTML
html_content = fetch_category_page(CATEGORY_URL)

# 2. Extract product IDs from the category page
if html_content:
    product_ids = extract_product_ids(html_content)
    print(f"Found {len(product_ids)} products.")

# 3. Fetch detailed product data (with rate limit)
product_data_list = []
if product_ids:
    for index, product_id in enumerate(product_ids, start=1):
        print(f"[📦] Scraping product {index} (ID: {product_id})...")  # Progress log
        product_data = fetch_product_details(product_id)
        if product_data:
            try:
                product = Product(
                    product_id=product_data['id'],
                    display_name=product_data['displayName'],
                    is_available=product_data['isAvailableToPurchase'],
                    part_number=product_data['partNumber'],
                    root_category_name=product_data['rootCategoryName'],
                    product_url=product_data['url'],
                    discount_price=product_data['discountPrice'],
                    list_price=product_data['listPrice'],
                    brand_name=product_data['brandName'],
                    brand_url=product_data['brandUrl'],
                    brand_logo_url=product_data['brandLogoUrl'],
                    primary_image_index=product_data['primaryImageIndex']
                )
                product_data_list.append(product)
            except KeyError as e:
                print(f"[⚠] Missing key {e} for product {product_id}. Skipping this product.")
                continue  # Skip to the next product if key error occurs

        time.sleep(3)  # Rate limit to avoid being blocked

# 4. Save results to CSV
save_to_csv(product_data_list)
print(f"Successfully saved {len(product_data_list)} products to CSV.")
