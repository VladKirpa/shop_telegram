import json
import os
import sqlite3

CONFIG_PATH = "payment_config.json"

DEFAULT_CONFIG = {
    "enabled_methods": ["crypto"],
    "card_details": {
        "number": "0000 0000 0000 0000",
        "bank": "Your Bank",
        "receiver": "Name Surname"
    }
}

def load_config():
    if not os.path.exists(CONFIG_PATH):
        save_config(DEFAULT_CONFIG)
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)

def is_method_enabled(method: str) -> bool:
    config = load_config()
    return method in config.get("enabled_methods", [])

def enable_method(method: str):
    config = load_config()
    if method not in config["enabled_methods"]:
        config["enabled_methods"].append(method)
    save_config(config)

def disable_method(method: str):
    config = load_config()
    config["enabled_methods"] = [m for m in config["enabled_methods"] if m != method]
    save_config(config)

def get_card_details():
    config = load_config()
    return config.get("card_details", {})

def update_card_details(number: str, bank: str, receiver: str):
    config = load_config()
    config["card_details"] = {
        "number": number,
        "bank": bank,
        "receiver": receiver
    }
    save_config(config)

def get_payment_config():
    config = load_config()
    methods = config.get("enabled_methods", [])
    if "crypto" in methods and "card" in methods:
        return "both"
    elif "crypto" in methods:
        return "crypto"
    elif "card" in methods:
        return "card"
    else:
        return "none"
    
