import yaml
import os


VNOV_DIR = os.path.dirname(os.path.abspath(__file__))

config2_dir = f"{VNOV_DIR}/config2.yaml"
if not os.path.exists(config2_dir):
    with open(f"{VNOV_DIR}/config.yaml", "r", encoding="utf-8") as f:
        CONFIG = yaml.safe_load(f)
else:
    with open(config2_dir, "r", encoding="utf-8") as f:
        CONFIG = yaml.safe_load(f)

with open(f"{VNOV_DIR}/model_config.yaml", "r", encoding="utf-8") as f:
    MODEL_CONFIG = yaml.safe_load(f)
