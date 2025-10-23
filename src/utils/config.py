import os
import yaml
from dotenv import load_dotenv

load_dotenv()

def load_config(path="config.yaml"):
    with open(path, "r") as f:
        cfg = yaml.safe_load(f)
    
    cfg['env'] = os.getenv("ENV", "local")
    
    # Override with Docker environment variables if available
    if os.getenv("HTTPBIN_URL"):
        cfg['base_url'] = os.getenv("HTTPBIN_URL")
    
    if os.getenv("RABBITMQ_URL"):
        cfg['rabbitmq']['url'] = os.getenv("RABBITMQ_URL")
    
    if os.getenv("PROMETHEUS_URL"):
        cfg['prometheus_url'] = os.getenv("PROMETHEUS_URL")
    
    return cfg
