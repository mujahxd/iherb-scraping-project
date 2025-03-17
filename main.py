from app import save_to_csv, get_all_products

# https://id1.iherb.com/c/sports?p=1
def main():
    all_products = get_all_products()
    save_to_csv(all_products)
    print(f"Successfully saved to CSV.")

if __name__ == "__main__":
    main()
