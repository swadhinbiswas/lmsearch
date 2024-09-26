from apps.api.app.services.catalog import load_catalog
from apps.api.app.services.filters import apply_filters
from apps.api.app.services.hybrid import rrf_fuse
from apps.api.app.services.query_parser_bn import parse_query_multilingual


def test_rrf():
    fused = rrf_fuse([[(1, 1.0), (2, 0.5)], [(2, 1.0), (1, 0.5)]], k=60)
    ids = [pid for pid, _ in fused]
    assert set(ids) == {1, 2}


def test_relaxation_reports():
    catalog = load_catalog()
    parsed = parse_query_multilingual("Ryzen laptop 64GB RAM under $100 impossiblebrandxyz")
    filtered, relaxed = apply_filters(catalog, parsed)
    assert isinstance(relaxed, list)
