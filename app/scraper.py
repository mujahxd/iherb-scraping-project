
import curl_cffi.requests as requests
from bs4 import BeautifulSoup
import time
from app import Product

class ProductScraper(BeautifulSoup):
    CATEGORY_URL = "https://id1.iherb.com/c/sports"
    API_URL_TEMPLATE = "https://id1.iherb.com/ugc/api/product/v2/{}"
    HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    }

    def __init__(self, url):
        """Initialize and fetch HTML content from the given URL."""
        self.url = url
        self.html_content = self.fetch_category_page()
        super().__init__(self.html_content, "html.parser")

    
    def fetch_category_page(self):
        """Fetch the category page HTML with error handling."""
        try:
            response = requests.get(self.url, headers=self.HEADERS, impersonate="chrome110", timeout=10)

            if response.status_code == 200:
                return response.text
            elif response.status_code == 403:
                print("[❌] Blocked! Try changing IP or use a proxy.")
            elif response.status_code == 429:
                print("[⏳] Rate limit hit! Please wait...")
                time.sleep(10)  # Wait before retrying
                return self.fetch_category_page()  # Try again
            else:
                print(f"[⚠] Error {response.status_code} when fetching category page.")

        except requests.exceptions.Timeout:
            print("[⏳] Timeout! Server too slow.")
        except requests.exceptions.RequestException as e:
            print(f"[❌] Request error: {e}")

        return None
    
    def extract_product_ids(self):
        """Extract product IDs from the category page."""
        product_cards = self.find_all("a", class_="product-link")
        product_ids = set()
        for card in product_cards:
            product_id = card.get("data-product-id")
            if product_id:
                product_ids.add(product_id)

        return list(product_ids)
    
    def fetch_product_details(self, product_id):
        """Fetch complete product details from the API based on product ID with error handling."""
        url = self.API_URL_TEMPLATE.format(product_id)

        try:
            response = requests.get(url, headers=self.HEADERS, impersonate="chrome110", timeout=10)

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
                return self.fetch_product_details(product_id)  # Try again
            else:
                print(f"[⚠] Error {response.status_code} for product {product_id}")

        except requests.exceptions.Timeout:
            print(f"[⏳] Timeout when fetching product {product_id}.")
        except requests.exceptions.RequestException as e:
            print(f"[❌] Request error for product {product_id}: {e}")

        return None
    

    def scrape_one_product(self, product_id):
        """Scrape a single product's details based on product ID."""
        print(f"[📦] Scraping product ID: {product_id}...")  # Progress log

        product_data = self.fetch_product_details(product_id)

        if product_data:
            try:
                return Product(
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
            except KeyError as e:
                print(f"[⚠] Missing key {e} for product {product_id}. Skipping this product.")
                return None  # Return None jika ada key yang hilang

        return None  # Return None jika request gagal atau produk tidak ditemukan

    