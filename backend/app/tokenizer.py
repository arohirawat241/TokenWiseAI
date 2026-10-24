import tiktoken

PRICING = {
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "claude-3-5-sonnet": {"input": 3.00, "output": 15.00}
}

LATENCY_PER_1K_TOKENS = 50 

def count_tokens(text: str, model: str = "gpt-4o") -> int:
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))

def analyze_prompt(system_prompt: str, user_prompt: str, model: str = "gpt-4o") -> dict:
    system_tokens = count_tokens(system_prompt, model)
    user_tokens = count_tokens(user_prompt, model)
    total_input_tokens = system_tokens + user_tokens
    
    estimated_output_tokens = max(100, int(total_input_tokens * 0.2))
    
    model_pricing = PRICING.get(model, PRICING["gpt-4o"])
    input_cost = (total_input_tokens / 1_000_000) * model_pricing["input"]
    output_cost = (estimated_output_tokens / 1_000_000) * model_pricing["output"]
    total_estimated_cost = input_cost + output_cost
    
    input_latency_ms = (total_input_tokens / 1000) * LATENCY_PER_1K_TOKENS
    output_latency_ms = (estimated_output_tokens / 1000) * LATENCY_PER_1K_TOKENS
    
    return {
        "model": model,
        "system_tokens": system_tokens,
        "user_tokens": user_tokens,
        "total_input_tokens": total_input_tokens,
        "estimated_output_tokens": estimated_output_tokens,
        "estimated_total_tokens": total_input_tokens + estimated_output_tokens,
        "estimated_cost_usd": round(total_estimated_cost, 6),
        "estimated_latency_ms": round(input_latency_ms + output_latency_ms, 2)
    }