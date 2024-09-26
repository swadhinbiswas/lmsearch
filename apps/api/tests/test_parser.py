from apps.api.app.services import currency as cur
from apps.api.app.services.query_parser import parse_query_rule
from apps.api.app.services.query_parser_bn import parse_query_multilingual


def test_ryzen_32gb_under_1200():
    p = parse_query_multilingual("I need a Ryzen laptop with 32GB RAM under $1200 for programming")
    assert p["category"] == "laptop"
    assert p["must"].get("ram_gb_min") == 32
    assert any("ryzen" in c for c in p["must"].get("cpu_series", []))
    assert p["price"]["max"] == 1200
    assert "programming" in p["use_case"]


def test_phone_bdt():
    p = parse_query_multilingual("gaming phone, 120Hz screen, 5000mAh battery, below 40k BDT")
    assert p["category"] == "phone"
    assert p["must"].get("refresh_hz_min") == 120
    assert p["must"].get("battery_mah_min") == 5000
    # 40k BDT -> ~341 USD
    assert abs(p["price"]["max"] - 40000 / 117.0) < 1.0


def test_taka_symbol():
    price = cur.parse_price("below ৳50000")
    assert price["currency"] == "BDT"
    assert price["max"] == 50000


def test_lakh():
    price = cur.parse_price("under 1.2 lakh BDT")
    assert price["max"] == 120000


def test_between():
    price = cur.parse_price("between $800 and $1200")
    assert price["min"] == 800 and price["max"] == 1200


def test_bangla_mixed():
    p = parse_query_multilingual("ল্যাপটপ Ryzen 16GB RAM দাম ১ লাখ টাকা")
    # transliterated laptop + lakh BDT path should not crash and keeps ram
    assert p["must"].get("ram_gb_min") == 16


def test_rule_base():
    p = parse_query_rule("HP laptop i7 16GB RAM 512GB SSD")
    assert "HP" in p["brands"]
    assert p["must"]["ram_gb_min"] == 16
