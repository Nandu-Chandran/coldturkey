from faker import faker

def random_user():
    return{
            "name": _fake.name(),
            "email": _fake.email(),
            "address": _fake.address(),
            "sentence": _fake.sentence(),
            }

def random_query_params(n=3):
    return {_fake.word():_fake.word() for _ in range(n)}

