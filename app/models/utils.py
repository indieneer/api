import re


def slugify(text):
    # Convert to lowercase and strip whitespace at the ends
    text = text.lower().strip()
    # Replace all non-word characters (except '-') with '-'
    text = re.sub(r'[^\w\s-]', '-', text)
    # Replace any whitespace or repeated hyphens with a single hyphen
    text = re.sub(r'[-\s]+', '-', text)
    return text
