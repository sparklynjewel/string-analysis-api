import hashlib
from collections import Counter

def analyze_string(value):

    raw = value.strip()
    hash_id = hashlib.sha256(raw.encode('utf-8')).hexdigest()

    properties = {
        "length": len(value),
        "is_palindrome": value.lower() == value.lower()[::-1],
        "unique_characters": len(set(value)),
        "word_count": len(value.strip().split()),
        "sha256_hash": hash_id,
        "character_frequency_map": dict(Counter(value)),
    }

    return hash_id, properties
