import re

def detect_structure(text: str) -> list:
    """Detects if the prompt contains STRICT output format constraints."""
    structures = []
    lower_text = text.lower()
    
    # 1. JSON: Only flag if explicitly asking for JSON output or contains actual JSON syntax
    # (e.g., "output valid json", "return json", or actual {"key": "value"} syntax)
    if re.search(r'(output|return|respond with|format as)\s+(valid\s+)?json', lower_text) or re.search(r'\{\s*".*"\s*:', text):
        structures.append("JSON")
        
    # 2. SQL: Only flag if asking to write/generate SQL code
    if re.search(r'(write|generate|provide)\s+(a\s+)?sql\s+(query|statement|code)', lower_text):
        structures.append("SQL")
        
    # 3. Code Blocks: Explicit markdown code fences
    if '```' in text:
        structures.append("CODE_BLOCK")
        
    # 4. XML/HTML: Actual tags, not just the words "xml" or "html"
    if re.search(r'<[a-zA-Z]+>.*?</[a-zA-Z]+>', text, re.DOTALL):
        structures.append("XML/HTML")
        
    return structures

def validate_structure(original_text: str, compressed_text: str) -> dict:
    """Ensures the compressed text didn't destroy critical structural markers."""
    original_structures = detect_structure(original_text)
    
    # If no strict structures were demanded, it's automatically valid
    if not original_structures:
        return {"is_valid": True, "reason": "No strict output structures detected."}
    
    missing_structures = []
    for struct in original_structures:
        if struct == "JSON" and '{' not in compressed_text and 'json' not in compressed_text.lower():
            missing_structures.append("JSON")
        elif struct == "SQL" and not re.search(r'\b(SELECT|INSERT|UPDATE|DELETE)\b', compressed_text, re.IGNORECASE):
            missing_structures.append("SQL")
        elif struct == "CODE_BLOCK" and '```' not in compressed_text:
            missing_structures.append("CODE_BLOCK")
            
    if missing_structures:
        return {
            "is_valid": False, 
            "reason": f"Compression destroyed structure: {', '.join(missing_structures)}"
        }
        
    return {"is_valid": True, "reason": "All structural constraints preserved."}