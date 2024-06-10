from pydantic import BaseModel, Field


class PriceFilter(BaseModel):
    min: float | None = None
    max: float | None = None
    currency: str = "USD"


class MustFilters(BaseModel):
    ram_gb_min: int | None = None
    storage_gb_min: int | None = None
    cpu_series: list[str] = Field(default_factory=list)
    gpu_keywords: list[str] = Field(default_factory=list)
    refresh_hz_min: int | None = None
    battery_mah_min: int | None = None
    screen_inch_min: float | None = None
    screen_inch_max: float | None = None
    camera_mp_min: int | None = None


class StructuredQuery(BaseModel):
    category: str | None = None
    brands: list[str] = Field(default_factory=list)
    must: MustFilters = Field(default_factory=MustFilters)
    price: PriceFilter = Field(default_factory=PriceFilter)
    use_case: list[str] = Field(default_factory=list)
    soft_preferences: list[str] = Field(default_factory=list)
    exclude: list[str] = Field(default_factory=list)
    semantic_query: str = ""
