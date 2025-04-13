# Vault: Secure Storage for Sensitive Data

The Vault is a feature in Prompt Sentinel designed to securely store and manage sensitive data, such as API keys, tokens, and credentials. It ensures that sensitive information is protected during interactions with language models (LLMs) and provides a centralized mechanism for managing secrets.

## Purpose of the Vault

The Vault serves the following purposes:
- **Secure Storage**: Safely store sensitive data in memory or an external secure storage system.
- **Controlled Access**: Provide controlled access to sensitive data during LLM interactions.
- **Seamless Integration**: Integrate with Prompt Sentinel's detection and sanitization mechanisms to ensure secure and transparent workflows.

## Using the Vault

The Vault can be used to store and retrieve sensitive data during LLM interactions. Below is an example of how to use the Vault in your application.

### Example Usage

```python
from sentinel import Vault

# Initialize the Vault
vault = Vault()

# Store sensitive data in the Vault
vault.store("api_key", "hf-mfehcnsjk8")
vault.store("db_password", "securepassword123")

# Retrieve sensitive data from the Vault
api_key = vault.retrieve("api_key")
db_password = vault.retrieve("db_password")

# Use the sensitive data securely
print(f"API Key: {api_key}")
print(f"Database Password: {db_password}")
```

## Features of the Vault

- **In-Memory Storage**: By default, the Vault stores sensitive data in memory, ensuring fast access and secure handling.
- **Custom Backends**: The Vault can be configured to use custom storage backends, such as encrypted files or external secret management systems.
- **Integration with Detectors**: The Vault integrates seamlessly with Prompt Sentinel's detectors to ensure sensitive data is sanitized and restored during LLM interactions.

## Customizing the Vault

You can customize the Vault to use a different storage backend or encryption mechanism. For example, you can implement a custom backend that stores secrets in an encrypted file.

### Example: Custom Backend

```python
from sentinel import Vault

class EncryptedFileBackend:
    def __init__(self, file_path):
        self.file_path = file_path

    def store(self, key, value):
        # Implement encryption and file storage logic
        pass

    def retrieve(self, key):
        # Implement decryption and file retrieval logic
        pass

# Initialize the Vault with a custom backend
vault = Vault(backend=EncryptedFileBackend("secrets.enc"))
```

## Best Practices

- **Limit Access**: Restrict access to the Vault to only the components that require sensitive data.
- **Use Encryption**: Always use encryption for storing sensitive data, especially when using custom backends.
- **Regularly Rotate Secrets**: Periodically update and rotate sensitive data to minimize security risks.

The Vault is a powerful tool for managing sensitive data securely and efficiently. By integrating it into your Prompt Sentinel workflows, you can ensure that your applications handle sensitive information with the highest level of security.
