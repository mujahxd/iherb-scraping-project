from dataclasses import dataclass
from app.database import Base
from sqlalchemy import Column, Integer, String, Boolean

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

class ProductModel(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, unique=True, nullable=False)  # ID dari API
    display_name = Column(String, nullable=False)
    is_available = Column(Boolean, nullable=False)
    part_number = Column(String, nullable=False)
    root_category_name = Column(String, nullable=False)
    product_url = Column(String, nullable=False)
    discount_price = Column(String, nullable=False)
    list_price = Column(String, nullable=False)
    brand_name = Column(String, nullable=False)
    brand_url = Column(String, nullable=False)
    brand_logo_url = Column(String)
    primary_image_index = Column(Integer)