import csv
from typing import List
from app import Product, ProductModel 
import time
from app.scraper import ProductScraper
from sqlalchemy.exc import IntegrityError
from app.database import SessionLocal

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


def save_to_db(product_data):
    """Menyimpan data produk ke database."""
    session = SessionLocal()
    try:
        product = ProductModel(
            product_id=product_data.product_id,
            display_name=product_data.display_name,
            is_available=product_data.is_available,
            part_number=product_data.part_number,
            root_category_name=product_data.root_category_name,
            product_url=product_data.product_url,
            discount_price=product_data.discount_price,
            list_price=product_data.list_price,
            brand_name=product_data.brand_name,
            brand_url=product_data.brand_url,
            brand_logo_url=product_data.brand_logo_url,
            primary_image_index=product_data.primary_image_index
        )

        session.add(product)
        session.commit()
        print(f"[✅] Product {product_data.display_name} saved to database.")
    except IntegrityError:
        session.rollback()
        print(f"[⚠] Product {product_data.product_id} already exists in the database. Skipping.")
    except Exception as e:
        session.rollback()
        print(f"[❌] Error saving product {product_data.display_name}: {e}")
    finally:
        session.close()
