import re

def extract_emails(text):

    pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]+"

    emails = re.findall(pattern, text)

    return list(set(emails))


def extract_links(text):

    import re

    pattern = r"https?://[^\s]+|www\.[^\s]+"

    links = re.findall(pattern, text)

    return list(set(links))

from extractor import extract_emails

import re

def extract_links(text):
    pattern = r'https?://[^\s]+|www\.[^\s]+'
    links = re.findall(pattern, text)

    return list(set(links))

import re

def extract_phones(text):

    pattern = r'\+?\d[\d\s\-\(\)]{8,}\d'

    phones = re.findall(pattern, text)

    return list(set(phones))

text = """
info@gmail.com
test@yahoo.com
info@gmail.com
"""

print(extract_emails(text))