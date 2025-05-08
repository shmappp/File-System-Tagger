import os
import json

def load_data(json_path):
    if os.path.exists(json_path):
        with open(json_path, 'r') as f:
            return json.load(f)
    else:
        return {}

def save_data(data, json_path):
    with open(json_path, 'w') as f:
        json.dump(data, f, indent=2)