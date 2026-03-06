# upload_assets.py — jalankan sekali dari terminal
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
import os

load_dotenv()
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

# Upload gambar dari URL publik langsung ke Cloudinary
assets = [
    ("https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=1200", "nutriapp/landing/hero"),
    ("https://images.unsplash.com/photo-1490645935967-10de6ba17061?w=800", "nutriapp/landing/food1"),
    ("https://images.unsplash.com/photo-1547592180-85f173990554?w=800", "nutriapp/landing/food2"),
    ("https://images.unsplash.com/photo-1498837167922-ddd27525d352?w=800", "nutriapp/landing/food3"),
]

for url, public_id in assets:
    result = cloudinary.uploader.upload(url, public_id=public_id, overwrite=True)
    print(f"{public_id}: {result['secure_url']}")