import sys

sys.path.insert(0, ".")
sys.path.insert(0, "apps/api")

import pytest
from fastapi.testclient import TestClient

from apps.api.app.main import create_app


@pytest.fixture()
def client():
    app = create_app()
    return TestClient(app)
