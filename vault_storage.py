import json
import os

VAULT_FILE = "vault.json"


def vault_exists(filepath: str = VAULT_FILE) -> bool:
    """Checks if the vault JSON file exists on disk."""
    return os.path.exists(filepath)


def save_vault_data(data: dict, filepath: str = VAULT_FILE) -> None:
    """Writes a dictionary to the vault JSON file."""
    with open(filepath, "w") as file:
        json.dump(data, file, indent=4)


def load_vault_data(filepath: str = VAULT_FILE) -> dict:
    """Loads and returns the dictionary from the vault JSON file."""
    if not vault_exists(filepath):
        raise FileNotFoundError(f"Vault file '{filepath}' not found.")

    with open(filepath, "r") as file:
        return json.load(file)