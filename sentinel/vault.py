from typing import Dict
import uuid
import hashlib  # Add import for hashing


class Vault:
    """
    A class for managing sensitive data securely.

    The Vault class provides functionality to store, retrieve, and clear
    mappings of tokens to sensitive data (secrets). It acts as a secure
    storage mechanism for handling secrets during runtime.

    Attributes:
    ----------
    secret_mapping : Dict[str, str]
        A dictionary that maps tokens to their corresponding secrets.
    """

    def __init__(self, hash_length: int = 8):
        """
        Initialize the Vault with an empty secret mapping and a configurable hash length.

        Parameters:
        ----------
        hash_length : int, optional
            The length of the hash used for generating placeholders (default is 8).
        """
        self.secret_mapping: Dict[str, str] = {}
        self.hash_length = hash_length

    def _add_secret(self, placeholder: str, secret: str):
        """
        Add a secret to the secret mapping.

        Parameters:
        ----------
        placeholder : str
            The placeholder that will be used as a reference for the secret.

        secret : str
            The sensitive data to be stored securely.
        """
        self.secret_mapping[placeholder] = secret

    def add_secret_and_get_placeholder(self, secret: str) -> str:
        """
        Add a secret to the secret mapping and generate a shorter unique placeholder for it.

        Parameters:
        ----------
        secret : str
            The sensitive data to be stored securely.

        Returns:
        -------
        str
            The shorter placeholder that maps to the secret.
        """
        # Generate a short hash-based placeholder
        short_hash = Vault._hash_secret(secret, self.hash_length)
        self._add_secret(short_hash, secret)
        return short_hash

    @staticmethod
    def _hash_secret(txt: str, hash_length: int = 8) -> str:
        return hashlib.sha256(txt.encode()).hexdigest()[:hash_length]

    def get_secret_mapping(self) -> Dict[str, str]:
        """
        Retrieve the current secret mapping.

        Returns:
        -------
        Dict[str, str]
            A dictionary containing all token-secret mappings.
        """
        return self.secret_mapping

    def clear_secrets(self):
        """
        Clear all secrets from the secret mapping.

        This method removes all stored token-secret mappings, effectively
        resetting the Vault.
        """
        self.secret_mapping.clear()
