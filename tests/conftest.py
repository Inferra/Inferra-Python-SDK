import pytest
import os
import json
from pathlib import Path
from inferra import InferraClient

@pytest.fixture
def test_api_key():
    return "test-key-12345"

@pytest.fixture
def client(test_api_key):
    return InferraClient(api_key=test_api_key)

@pytest.fixture
def sample_responses():
    path = Path(__file__).parent / "data" / "sample_responses.json"
    with open(path) as f:
        return json.load(f)
