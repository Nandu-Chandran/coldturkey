import pytest
import json

def test_get_returns_json(client):
    r = client.get("/get")
    assert r.headers["Content-Type"].startswith("application/json")
    body = r.json()
    assert "url" in body
    assert "headers" in body

def test_stream_bytes(client):
    # httpbin /bytes/ returns raw bytes; verify status and length
    r = client.get("/bytes/16")
    assert r.status_code == 200
    assert len(r.content) == 16

