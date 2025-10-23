def test_post_inspection_echoes_json(client, fake_user):
    payload = fake_user
    r = client.post("/post", json=payload)
    body = r.json()
    # httpbin echoes back under 'json'
    assert body["json"] == payload
    assert "headers" in body
    assert body["headers"]["Content-Type"] in (None, "application/json")
    
def test_anything_endpoint(client):
    r = client.post("/anything/this/path?x=1", data={"a":"b"})
    b = r.json()
    assert b["method"] == "POST"
    assert "/anything/this/path" in b["url"]
    assert b["data"] == "a=b" or b["form"] == {"a": "b"}

