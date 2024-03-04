from pydantic import BaseModel


class ProductCard(BaseModel):
    id: int
    title: str
    brand: str = ""
    category: str = ""
    price: float = 0
    currency: str = "USD"
    url: str = ""
    image: str = ""
    rating: float = 0.0
    in_stock: bool = True
    specs: dict = {}
    match_score: float = 0.0
    explanation: dict = {}
