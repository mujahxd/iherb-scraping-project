from app.models import Product, ProductModel
from app.utils import save_to_csv, get_all_products, save_to_db
from app.scraper import ProductScraper
from app.database import Base, init_db, SessionLocal