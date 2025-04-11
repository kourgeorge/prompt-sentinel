from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

text = "My name is John and my phone is 555-123-4567. My password for gmail is gkgkgk"
results = analyzer.analyze(text=text, language="en")
anonymized = anonymizer.anonymize(text=text, analyzer_results=results)
print(anonymized.text)
# Output: "My name is <PERSON> and my phone is <PHONE_NUMBER>"
