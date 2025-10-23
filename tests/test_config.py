from utils.config import load_config


def test_load():
    cfg = load_config("config.yaml")
    assert "base_url" in cfg
    assert isinstance(cfg["timeout"],int)
