from api import index


def test_index():
    assert index.hello() == "Hello api"
