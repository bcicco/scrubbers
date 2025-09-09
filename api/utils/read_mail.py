import imaplib
import email
import re
def extract_email(email_string: str) -> str:
    """Extract email from string like 'Name <email@domain.com>' or return as-is if just email"""
    # Look for email in angle brackets
    match = re.search(r'<([^>]+)>', email_string)
    if match:
        return match.group(1)