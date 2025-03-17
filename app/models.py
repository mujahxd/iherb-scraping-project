from dataclasses import dataclass

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