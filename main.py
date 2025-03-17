from app import init_db, save_to_csv, get_all_products, save_to_db

# https://id1.iherb.com/c/sports?p=1
def main():
    all_products = get_all_products()
    save_to_csv(all_products)
    print(f"Successfully saved to CSV.")
    for product in all_products:
        save_to_db(product)
    

if __name__ == "__main__":
    init_db()
    main()
