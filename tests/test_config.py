import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.config import load_config


def test_load():
    cfg = load_config("config.yaml")
    assert "base_url" in cfg
    assert isinstance(cfg["timeout"],int)
