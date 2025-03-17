import csv
from typing import List
from app import Product
import time
from app.scraper import ProductScraper

def get_all_products():
    """Scrape all products from the category page."""
    scraper = ProductScraper(ProductScraper.CATEGORY_URL)

    # 1. Ambil halaman kategori
    html_content = scraper.fetch_category_page()

    if not html_content:
        print("[❌] Failed to fetch category page.")
        return []  # Return list kosong jika gagal ambil kategori

    # 2. Ekstrak semua product_id dari halaman kategori
    product_ids = scraper.extract_product_ids()
    print(f"[🔍] Found {len(product_ids)} products.")

    # 3. Scrape setiap produk berdasarkan product_id
    all_products = []
    for index, product_id in enumerate(product_ids, start=1):
        print(f"[📦] Scraping product {index}/{len(product_ids)} (ID: {product_id})...")
        
        product = scraper.scrape_one_product(product_id)
        if product:
            all_products.append(product)

        time.sleep(3)  # Delay untuk menghindari blokir

    print(f"[✅] Successfully scraped {len(all_products)} products.")
    return all_products  # Return list produk yang berhasil di-scrape



def save_to_csv(products: List[Product], filename="data/products.csv"):
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