"""Seed 600 realistic products (laptops + phones). Idempotent, no network needed."""

from __future__ import annotations

import json
import random

random.seed(42)

LAPTOP_CPUS = [
    ("AMD", "Ryzen 5 7530U", "ryzen5", "integrated"),
    ("AMD", "Ryzen 7 7730U", "ryzen7", "integrated"),
    ("AMD", "Ryzen 7 7840HS", "ryzen7", "RTX 4050"),
    ("AMD", "Ryzen 9 7940HS", "ryzen9", "RTX 4070"),
    ("Intel", "Core i5-1335U", "i5", "integrated"),
    ("Intel", "Core i7-1360P", "i7", "integrated"),
    ("Intel", "Core i7-13700H", "i7", "RTX 4060"),
    ("Apple", "M2", "m2", "integrated"),
    ("Apple", "M3", "m3", "integrated"),
]
PHONE_CHIPS = [
    "Snapdragon 8 Gen 2",
    "Snapdragon 7 Gen 1",
    "Dimensity 8200",
    "Exynos 2200",
    "Tensor G3",
    "Helio G99",
]
BRANDS_LAPTOP = ["Lenovo", "HP", "Dell", "Asus", "Acer", "MSI", "Apple", "Samsung"]
BRANDS_PHONE = ["Samsung", "Xiaomi", "Realme", "OnePlus", "Vivo", "Oppo", "Google", "Motorola"]


def gen_products(n: int = 600) -> list[dict]:
    out = []
    for i in range(n):
        if i % 2 == 0:
            brand = BRANDS_LAPTOP[i % len(BRANDS_LAPTOP)]
            cpu_brand, cpu_model, cpu_series, gpu = LAPTOP_CPUS[i % len(LAPTOP_CPUS)]
            ram = [8, 16, 16, 32, 32, 64][i % 6]
            storage = [256, 512, 512, 1024, 1024, 2048][i % 6]
            price = 450 + (i * 37) % 2100
            kind = "ThinkPad" if brand == "Lenovo" else "Laptop"
            p = {
                "id": i + 1,
                "source": "seed",
                "source_id": f"laptop-{i+1}",
                "title": f"{brand} {kind} {cpu_model} {ram}GB/{storage}GB",
                "brand": brand,
                "category": "laptop",
                "price": float(price),
                "currency": "USD",
                "url": f"https://example.com/laptop-{i+1}",
                "image_urls": [f"https://example.com/img/laptop-{i+1}.jpg"],
                "description": (
                    f"{cpu_brand} {cpu_model} laptop with {ram}GB RAM "
                    f"and {storage}GB SSD for programming and office work."
                ),
                "rating": round(3.5 + (i % 15) / 10, 1),
                "in_stock": i % 11 != 0,
                "specs": {
                    "cpu_brand": cpu_brand,
                    "cpu_model": cpu_model,
                    "cpu_series": cpu_series,
                    "ram_gb": ram,
                    "storage_gb": storage,
                    "storage_type": "SSD",
                    "gpu": gpu,
                    "screen_inch": 14.0 + (i % 4),
                    "refresh_hz": 60 if i % 3 else 120,
                    "os": "Windows 11",
                },
            }
        else:
            brand = BRANDS_PHONE[i % len(BRANDS_PHONE)]
            ram = [4, 6, 8, 8, 12, 12][i % 6]
            storage = [64, 128, 128, 256, 256, 512][i % 6]
            battery = [4000, 4500, 5000, 5000, 5500, 6000][i % 6]
            refresh = [60, 90, 120, 120, 144, 120][i % 6]
            price_bdt = 15000 + (i * 911) % 90000
            chip = PHONE_CHIPS[i % len(PHONE_CHIPS)]
            p = {
                "id": i + 1,
                "source": "seed",
                "source_id": f"phone-{i+1}",
                "title": f"{brand} Phone {chip} {ram}GB/{storage}GB {battery}mAh",
                "brand": brand,
                "category": "phone",
                "price": float(price_bdt / 117.0),
                "currency": "USD",
                "price_bdt": float(price_bdt),
                "url": f"https://example.com/phone-{i+1}",
                "image_urls": [f"https://example.com/img/phone-{i+1}.jpg"],
                "description": (
                    f"{brand} gaming phone with {refresh}Hz screen " f"and {battery}mAh battery."
                ),
                "rating": round(3.6 + (i % 13) / 10, 1),
                "in_stock": i % 9 != 0,
                "specs": {
                    "chipset": PHONE_CHIPS[i % len(PHONE_CHIPS)],
                    "ram_gb": ram,
                    "storage_gb": storage,
                    "battery_mah": battery,
                    "screen_inch": 6.5 + (i % 3) * 0.2,
                    "refresh_hz": refresh,
                    "camera_mp": 50 + (i % 4) * 12,
                    "5g": "yes" if i % 2 == 0 else "no",
                },
            }
        out.append(p)
    return out


def main() -> None:
    products = gen_products()
    with open("data_seed.json", "w") as f:
        json.dump(products, f, indent=1)
    print(f"seeded {len(products)} products -> data_seed.json")


if __name__ == "__main__":
    main()
