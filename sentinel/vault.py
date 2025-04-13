from typing import Dict


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

    def __init__(self):
        """
        Initialize the Vault with an empty secret mapping.
        """
        self.secret_mapping: Dict[str, str] = {}

    def add_secret(self, token: str, secret: str):
        """
        Add a secret to the secret mapping.

        Parameters:
        ----------
        token : str
            The token that will be used as a placeholder for the secret.

        secret : str
            The sensitive data to be stored securely.
        """
        self.secret_mapping[token] = secret

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
