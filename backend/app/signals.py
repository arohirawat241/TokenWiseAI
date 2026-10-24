import re
from app.tokenizer import count_tokens
from app.compressor import compress_prompt

def calculate_budget_pressure(total_tokens: int, model_limit: int, reserved_output: int = 1000, safety_margin: int = 500) -> float:
    usable_budget = model_limit - reserved_output - safety_margin
    if usable_budget <= 0: return 1.0
    pressure = total_tokens / usable_budget
    return round(pressure, 4)

def estimate_savings(original_text: str) -> float:
    To = count_tokens(original_text)
    if To == 0: return 0.0
    
    estimated_compressed_text = compress_prompt(original_text)
    Te = count_tokens(estimated_compressed_text)
    
    # ADD THIS PRINT TO SEE EXACTLY WHAT HAPPENED:
    print(f"   [Heuristic Check] Original tokens: {To} -> Regex estimate: {Te} tokens.")
    
    savings = (To - Te) / To
    return round(savings, 4)

def calculate_constraint_risk(text: str) -> float:
    """Smart risk calculation: only flags strict OUTPUT constraints, not mere mentions."""
    risk_score = 0.0
    lower_text = text.lower()
    
    # 1. JSON: Only flag if explicitly asking for JSON output or contains actual JSON syntax
    if re.search(r'(output|return|respond with|format as)\s+(valid\s+)?json', lower_text) or re.search(r'\{\s*".*"\s*:', text):
        risk_score += 0.4
        
    # 2. SQL: Only flag if asking to write/generate SQL code
    if re.search(r'(write|generate|provide)\s+(a\s+)?sql\s+(query|statement|code)', lower_text):
        risk_score += 0.3
        
    # 3. Code Blocks
    if '```' in text: 
        risk_score += 0.3
        
    # 4. Strict negative constraints
    if 'do not' in lower_text or 'must not' in lower_text or 'exactly' in lower_text: 
        risk_score += 0.2
        
    # 5. High density of strict commands
    if lower_text.count('please') + lower_text.count('ensure') + lower_text.count('must') > 5: 
        risk_score += 0.1
        
    return min(round(risk_score, 2), 1.0)