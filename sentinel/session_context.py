from typing import Dict
from sentinel.vault import Vault
import requests
import uuid


class SessionContext:
    """
    A singleton class for managing session-specific context, including secrets and reporting.

    The `SessionContext` class provides functionality to manage sensitive data securely
    using the `Vault` class, and to report detected secrets to a server. It ensures that
    only one instance of the class exists during the application's lifecycle.

    Attributes:
    ----------
    project_token : str
        A unique token identifying the project.

    server_url : str
        The URL of the server to which reports are sent.

    session_id : str
        A unique identifier for the session. If not provided, a UUID is generated.

    vault : Vault
        An instance of the `Vault` class for managing secrets.
    """

    _instance = None  # Singleton instance

    def __new__(cls, *args, **kwargs):
        """
        Ensure that only one instance of the class is created (singleton pattern).
        """
        if cls._instance is None:
            cls._instance = super(SessionContext, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, app_token: str, server_url: str = None, session_id: str = None):
        """
        Initialize the SessionContext instance.

        Parameters:
        ----------
        app_token : str
            A unique token identifying the application.

        server_url : str, optional
            The URL of the server to which reports are sent. If not provided, reporting is disabled.

        session_id : str, optional
            A unique identifier for the session. If not provided, a UUID is generated.
        """
        if self._initialized:
            return  # Avoid reinitializing the singleton instance
        self.project_token = app_token
        self.server_url = server_url  # Allow server_url to be None
        self.vault = Vault()  # Use Vault for secret management
        self.session_id = session_id or str(uuid.uuid4())
        self._initialized = True

    def add_secret(self, placeholder: str, secret: str):
        """
        Add a secret to the vault.

        Parameters:
        ----------
        placeholder : str
            The placeholder that will be used as a reference for the secret.

        secret : str
            The sensitive data to be stored securely.
        """
        self.vault.add_secret(placeholder, secret)

    def get_secret_mapping(self) -> Dict[str, str]:
        """
        Retrieve the current secret mapping from the vault.

        Returns:
        -------
        Dict[str, str]
            A dictionary containing all placeholder-secret mappings.
        """
        return self.vault.get_secret_mapping()

    def clear_secrets(self):
        """
        Clear all secrets from the vault.

        This method removes all stored token-secret mappings, effectively
        resetting the vault.
        """
        self.vault.clear_secrets()

    def report_to_server(self, prompt: str, secrets: list, sanitized_output: str, timestamp: str):
        """
        Sends a report about the detected secrets to the server.

        Parameters:
        ----------
        prompt : str
            The original prompt containing sensitive data.

        secrets : list
            A list of detected secrets.

        sanitized_output : str
            The sanitized version of the prompt with secrets replaced by tokens.

        timestamp : str
            The timestamp of when the secrets were detected.
        """
        if not self.server_url:
            print("Server URL is not defined. Reporting functionality is disabled.")
            return

        url = f"{self.server_url}/api/report"
        payload = {
            "project_token": self.project_token,
            "session_id": self.session_id,
            "prompt": prompt,
            "secrets": secrets,
            "sanitized_output": sanitized_output,
            "timestamp": timestamp
        }
        try:
            requests.post(url, json=payload)
        except Exception:
            print("Could not send data to the server")


