from shop.scripts.utils import get_or_upload_photo_id

def main():
    for name in ["start.png", "profile.png", "catalog.png", "support.png"]:
        file_path = f"shop/media/{name}"
        photo_id = get_or_upload_photo_id(file_path)
        print(f"{name} => {photo_id}")

if __name__ == "__main__":
    main()