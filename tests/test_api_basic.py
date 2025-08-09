import os
import pytest
from fastapi.testclient import TestClient

# Ensure we import the local app
os.environ.setdefault("SPECTRA_LOG_FORMAT", "json")
os.environ.setdefault("SPECTRA_LOG_LEVEL", "WARNING")

import main  # noqa: E402

client = TestClient(main.app)


def test_root():
    r = client.get('/')
    assert r.status_code == 200
    data = r.json()
    assert data['status'] == 'running'
    assert 'available_models' in data


def test_status():
    r = client.get('/api/status')
    assert r.status_code == 200
    data = r.json()
    assert data['status'] == 'healthy'
    assert 'available_models' in data


def test_models_list():
    r = client.get('/api/models')
    assert r.status_code == 200
    data = r.json()
    assert 'current' in data
    assert 'available' in data


def test_personality_hash():
    r = client.get('/api/personality/hash')
    assert r.status_code == 200
    data = r.json()
    assert 'personality_hash' in data
    assert len(data['personality_hash']) >= 8


def test_metrics():
    r = client.get('/api/metrics')
    assert r.status_code == 200
    data = r.json()
    assert 'active_model' in data
    assert 'personality_hash' in data


@pytest.mark.parametrize("enabled", [True, False])
def test_toggle_auto_model(enabled):
    r = client.post('/api/auto-model', json={'enabled': enabled})
    assert r.status_code == 200
    data = r.json()
    assert data['auto_model_enabled'] == enabled


def test_chat_error_handling():
    # Provide a minimal message; if models missing it should still return a valid structure with error or success
    r = client.post('/api/chat', json={'message': 'Hi', 'history': []})
    # The endpoint returns 200 on success, 500 on exception; both acceptable for structure validation
    assert r.status_code in (200, 500)
    if r.status_code == 200:
        data = r.json()
        assert 'response' in data
        assert 'model_used' in data
    else:
        # 500 path structure
        detail = r.json().get('detail')
        assert 'response' in detail
        assert detail['status'] == 'error'
