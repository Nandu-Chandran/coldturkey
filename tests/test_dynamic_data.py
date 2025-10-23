def test_get_with_random_query_params(client, random_params=None):
    # or use fake generator
    from src.utils.faker_utils import random_query_params
    params = random_query_params(4)
    r = client.get("/get", params=params)
    body = r.json()
    # httpbin returns args as strings
    for k, v in params.items():
        assert body["args"].get(k) == v

