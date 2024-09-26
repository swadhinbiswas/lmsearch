from apps.ingest.normalizers import normalize_cpu, normalize_ram_gb, normalize_specs, normalize_storage_gb


def test_ram():
    assert normalize_ram_gb("32GB RAM laptop") == 32
    assert normalize_ram_gb("16gb") is None  # bare 16gb without ram context -> None by design
    assert normalize_ram_gb("Ryzen laptop with 32GB RAM") == 32


def test_storage():
    gb, kind = normalize_storage_gb("512GB SSD")
    assert gb == 512
    gb, _ = normalize_storage_gb("1TB SSD")
    assert gb == 1024


def test_cpu_ryzen():
    out = normalize_cpu("AMD Ryzen 7 7730U laptop")
    assert out["cpu_brand"] == "AMD"
    assert out["cpu_series"] == "ryzen7"


def test_cpu_intel():
    out = normalize_cpu("Intel Core i7-13700H")
    assert out["cpu_brand"] == "Intel"
    assert out["cpu_series"] == "i7"


def test_specs_blob():
    s = normalize_specs("Lenovo Ryzen 7 32GB RAM 1TB SSD 120Hz", category="laptop")
    assert s["ram_gb"] == 32
    assert s["storage_gb"] == 1024
    assert s["refresh_hz"] == 120
