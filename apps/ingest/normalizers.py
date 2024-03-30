"""Deterministic spec normalizers shared by ingest + API."""
from __future__ import annotations

import re

RAM_RE = re.compile(r"(\d+(?:\.\d+)?)\s*gb\s*ram", re.I)
RAM_RE2 = re.compile(r"ram\s*(\d+(?:\.\d+)?)\s*gb?", re.I)
RAM_SHORT = re.compile(r"(?<![\d.])(\d{1,3})\s*gb(?![a-z])", re.I)
STORAGE_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(tb|gb)\s*(ssd|hdd|nvme|emmc|ufs)?", re.I)
CPU_RYZEN = re.compile(r"ryzen\s*([3579])(?:\s*(\d{4}[a-z]*))?", re.I)
CPU_INTEL = re.compile(r"(?:intel\s*)?(?:core\s*)?i([3579])(?:[\s\-_]*(\d{2,5}[a-z]*))?", re.I)
CPU_APPLE = re.compile(r"\b(M1|M2|M3)(?:\s*(Pro|Max|Ultra))?", re.I)
REFRESH_RE = re.compile(r"(\d{2,3})\s*hz", re.I)
SCREEN_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(?:inch|in|\"|”)", re.I)
BATTERY_MAH = re.compile(r"(\d{3,5})\s*mah", re.I)
BATTERY_WH = re.compile(r"(\d+(?:\.\d+)?)\s*wh", re.I)
CAMERA_RE = re.compile(r"(\d{2,3})\s*mp", re.I)


def normalize_ram_gb(text: str) -> int | None:
    if not text:
        return None
    for rx in (RAM_RE, RAM_RE2):
        m = rx.search(text)
        if m:
            v = float(m.group(1))
            if 2 <= v <= 256:
                return int(v)
    return None


def normalize_storage_gb(text: str) -> tuple[int | None, str]:
    if not text:
        return None, ""
    m = STORAGE_RE.search(text)
    if not m:
        return None, ""
    val, unit, stype = float(m.group(1)), m.group(2).lower(), (m.group(3) or "SSD").upper()
    gb = int(val * 1024) if unit == "tb" else int(val)
    if gb < 8 or gb > 16384:
        return None, ""
    return gb, stype


def normalize_cpu(text: str) -> dict:
    t = text or ""
    m = CPU_RYZEN.search(t)
    if m:
        series = f"ryzen{m.group(1)}"
        model = f"Ryzen {m.group(1)} {m.group(2)}".strip() if m.group(2) else f"Ryzen {m.group(1)}"
        return {"cpu_brand": "AMD", "cpu_model": model, "cpu_series": series}
    m = CPU_INTEL.search(t)
    if m:
        series = f"i{m.group(1)}"
        model = f"Core i{m.group(1)} {m.group(2)}".strip() if m.group(2) else f"Core i{m.group(1)}"
        return {"cpu_brand": "Intel", "cpu_model": model, "cpu_series": series}
    m = CPU_APPLE.search(t)
    if m:
        chip = m.group(1).upper()
        return {"cpu_brand": "Apple", "cpu_model": chip, "cpu_series": chip.lower()}
    return {}


def normalize_refresh_hz(text: str) -> int | None:
    m = REFRESH_RE.search(text or "")
    if m:
        v = int(m.group(1))
        if 30 <= v <= 360:
            return v
    return None


def normalize_battery(text: str, category: str = "phone") -> dict:
    t = text or ""
    m = BATTERY_MAH.search(t)
    if m:
        return {"battery_mah": int(m.group(1))}
    m = BATTERY_WH.search(t)
    if m:
        return {"battery_wh": float(m.group(1))}
    return {}


def normalize_specs(title: str, description: str = "", category: str = "laptop") -> dict:
    blob = f"{title} {description}"
    specs: dict = {}
    ram = normalize_ram_gb(blob)
    if ram:
        specs["ram_gb"] = ram
    storage, stype = normalize_storage_gb(blob)
    if storage:
        specs["storage_gb"] = storage
        specs["storage_type"] = stype
    specs.update(normalize_cpu(blob))
    hz = normalize_refresh_hz(blob)
    if hz:
        specs["refresh_hz"] = hz
    m = SCREEN_RE.search(blob)
    if m:
        specs["screen_inch"] = float(m.group(1))
    specs.update(normalize_battery(blob, category))
    m = CAMERA_RE.search(blob)
    if m and category == "phone":
        specs["camera_mp"] = int(m.group(1))
    low = blob.lower()
    if "5g" in low:
        specs["5g"] = "yes"
    if "rtx 4070" in low:
        specs["gpu"] = "RTX 4070"
    elif "rtx 4060" in low:
        specs["gpu"] = "RTX 4060"
    elif "rtx 4050" in low:
        specs["gpu"] = "RTX 4050"
    return specs
