import os
import yaml
from dotenv import load_dotenv

load_dotenv()

def load_config(path="config.yaml"):
    with open(path, "r") as f:
        cfg = yaml.safe_load(f)
    cfg['env'] = os.getenv("ENV", "local")
    return cfg
