import sys

sys.path.insert(0, ".")
sys.path.insert(0, "apps/api")

import pytest
from apps.api.app.main import create_app
from fastapi.testclient import TestClient


@pytest.fixture()
def client():
    app = create_app()
    return TestClient(app)
