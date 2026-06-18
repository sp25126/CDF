import re

def decompose_query(text: str) -> list[str]:
    """
    Decomposes a compound user query into sub-questions.
    
    Rules:
    - Split on: "and", "also", "plus", "aur", "bhi" (case-insensitive)
    - Only split if both parts are valid questions (length >= 4 and contains characters)
    - Max 2 sub-questions to keep response size manageable
    """
    if not text:
        return []

    # Regex split on: "and", "also", "plus", "aur", "bhi"
    split_pattern = r'\b(and|also|plus|aur|bhi)\b'
    parts = re.split(split_pattern, text, flags=re.IGNORECASE)
    
    sub_queries = []
    delimiters = {"and", "also", "plus", "aur", "bhi"}
    
    for part in parts:
        p_clean = part.strip()
        if not p_clean:
            continue
        if p_clean.lower() in delimiters:
            continue
        sub_queries.append(p_clean)
        
    # Validation: only keep non-trivial parts
    valid_queries = []
    for q in sub_queries:
        # Check if it has at least 4 chars and contains alphanumeric content
        if len(q) >= 4 and re.search(r'[a-zA-Z0-9\u0900-\u097F]', q):
            valid_queries.append(q)
            
    # If we split but ended up with only 1 valid question, return the original
    if len(valid_queries) <= 1:
        return [text]

    # Limit to max 2 sub-questions
    return valid_queries[:2]
