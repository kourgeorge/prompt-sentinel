import re
from sentinel.prompt_sentinel import sentinel
from sentinel.session_context import SessionContext

# Initialize the singleton SessionContext with provided APP_ID and URL.
session = SessionContext(app_id='42215214', server_url='http://ps.example.com')


# DummyDetector uses a regex to detect AWS keys.
class DummyDetector:
    def detect(self, text):
        # Pattern expects "AKIA" followed by exactly 16 uppercase letters or digits.
        pattern = re.compile(r'AKIA[A-Z0-9]{16}')
        results = []
        for match in pattern.finditer(text):
            results.append({'start': match.start(), 'end': match.end(), 'secret': match.group()})
        return results


detector = DummyDetector()


# The sentinel decorator sanitizes input and reports detected secrets.
@sentinel(detector)
def process_message(message):
    return message


if __name__ == '__main__':
    # Process 50 messages, each with a different AWS secret key.
    for i in range(50):
        # Generate a unique AWS key for each iteration.
        secret = f"AKIA{'A' * 15}{chr(65 + (i % 26))}"
        message = f"This is message {i + 1} with secret: {secret}"
        output = process_message(message)
        print(f"Processed message {i + 1}: {output}")
