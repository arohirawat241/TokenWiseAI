import os
import re
from dotenv import load_dotenv
from openai import OpenAI
from app.tokenizer import count_tokens
load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

def normalize_whitespace(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def remove_filler_phrases(text: str) -> str:
    fillers = [
        r"\bplease note that\b", r"\bi would like you to\b", r"\bin order to\b",
        r"\bas an ai language model\b", r"\bkindly\b", r"\bi want you to act as\b",
        r"\bplease answer this question in a detailed and comprehensive manner\b"
    ]
    for filler in fillers:
        text = re.sub(filler, "", text, flags=re.IGNORECASE)
    return normalize_whitespace(text)

def remove_duplicate_lines(text: str) -> str:
    lines = text.split('\n')
    seen = set()
    unique_lines = []
    for line in lines:
        cleaned_line = line.strip()
        if cleaned_line and cleaned_line not in seen:
            seen.add(cleaned_line)
            unique_lines.append(line)
    return '\n'.join(unique_lines)

def compress_prompt(text: str) -> str:
    if not text: return ""
    compressed = remove_duplicate_lines(text)
    compressed = remove_filler_phrases(compressed)
    compressed = normalize_whitespace(compressed)
    return compressed

def extract_json_schema(text: str) -> tuple[str, str]:
    """
    Finds a large JSON block at the end of the prompt and splits it from the instructions.
    Returns (instructions, json_schema). If no JSON found, returns (text, "").
    """
    # Regex to find the last JSON object in the text
    match = re.search(r'(\{[\s\S]*\})\s*$', text)
    
    if match:
        json_block = match.group(1)
        # Heuristic: Only treat it as a schema if it's substantial (over 100 chars)
        if len(json_block) > 100:
            instructions = text[:match.start()].strip()
            return instructions, json_block
            
    return text, ""
def semantic_compress(text: str) -> str:
    """Compresses instructions while mathematically guaranteeing the JSON schema is untouched AND preventing the AI from answering the prompt."""
    
    # 1. Physically separate the JSON schema from the text
    instructions, json_schema = extract_json_schema(text)
    
    # 2. Define the ultimate system prompt that prevents "answering"
    system_prompt = (
        "You are compressing a set of instructions for an AI. \n"
        "CRITICAL RULES:\n"
        "1. DO NOT answer the questions or generate the requested content.\n"
        "2. Your output must remain a concise list of instructions (e.g., 'Explain X, Y, and Z'), NOT the actual explanations or definitions.\n"
        "3. Preserve all constraints, formatting rules, and the exact order of topics.\n"
        "4. If there is a JSON schema, it will be appended automatically. Do not touch it."
    )
    
    try:
        response = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Compress these instructions into a concise prompt for an AI:\n\n{instructions}"}
            ],
            temperature=0.1,
            max_tokens=800
        )
        compressed_instructions = response.choices[0].message.content.strip()
        
        # 3. Staple the ORIGINAL, UNTOUCHED JSON schema back onto the end
        final_prompt = f"{compressed_instructions}\n\n{json_schema}" if json_schema else compressed_instructions
        # Replace the old print statement with this:
        orig_tokens = count_tokens(text)
        new_tokens = count_tokens(final_prompt)
        print(f"✅ AI Compression Successful. Original tokens: {orig_tokens}, New tokens: {new_tokens} (Saved: {orig_tokens - new_tokens})")
        return final_prompt
        
    except Exception as e:
        print(f"❌ LLM Compression FAILED: {e}")
        return text # Fallback