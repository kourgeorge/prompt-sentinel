import re
from sentinel.prompt_sentinel import sentinel
from sentinel.session_context import SessionContext

# Initialize the singleton SessionContext
session = SessionContext(app_token='42215214', server_url='http://ps.example.com')


# A dummy detector for demonstration
class DummyDetector:
    def detect(self, text):
        pattern = re.compile(r'AKIA[A-Z0-9]{16}')
        results = []
        for match in pattern.finditer(text):
            results.append({'start': match.start(), 'end': match.end(), 'secret': match.group()})
        return results


detector = DummyDetector()


# Use the sentinel decorator with the default session context
@sentinel(detector, session_context=session)
def process_message(message):
    # Process the input message and return it as is
    return message


if __name__ == '__main__':
    sample_message = "This is a sample message with AWS key: AKIAABCDEFGHIJKLMN"
    output = process_message(sample_message)
    print("Processed message:")
    print(output)
