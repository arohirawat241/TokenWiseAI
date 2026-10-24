from enum import Enum
from app.signals import calculate_budget_pressure, estimate_savings, calculate_constraint_risk

class OptimizationStrategy(str, Enum):
    PASSTHROUGH = "passthrough"
    HOT_PATH_DETERMINISTIC = "hot_path_deterministic"
    COLD_PATH_SEMANTIC = "cold_path_semantic"
    AGGRESSIVE_REDUCTION = "aggressive_reduction"
def decide_routing_strategy(original_text: str, total_tokens: int, model_limit: int) -> dict:
    budget_pressure = calculate_budget_pressure(total_tokens, model_limit)
    estimated_savings = estimate_savings(original_text)
    constraint_risk = calculate_constraint_risk(original_text)
    
    strategy = OptimizationStrategy.PASSTHROUGH
    reason = ""
    
    # 1. Critical: Budget exceeded
    if budget_pressure > 1.0:
        strategy = OptimizationStrategy.AGGRESSIVE_REDUCTION
        reason = "Budget exceeded. Must reduce context."
        
    # 2. VERBOSE PROMPTS: Trust the AI, even if there is a JSON schema. 
    # (The AI system prompt is now trained to preserve schemas verbatim).
    elif total_tokens > 250: 
        strategy = OptimizationStrategy.COLD_PATH_SEMANTIC
        reason = "Verbose prompt. Using AI for deep semantic compression."
        
    # 3. High structural risk on SHORT prompts -> Safe Hot Path
    elif constraint_risk > 0.50:
        strategy = OptimizationStrategy.HOT_PATH_DETERMINISTIC
        reason = "High structural risk on short prompt. Using safe deterministic rules."
        
    # 4. Good estimated savings from rules
    elif estimated_savings >= 0.15:
        strategy = OptimizationStrategy.COLD_PATH_SEMANTIC
        reason = "Good estimated savings. Using AI."
        
    # 5. Tiny prompts, low pressure
    elif estimated_savings < 0.10 and budget_pressure < 0.80:
        strategy = OptimizationStrategy.PASSTHROUGH
        reason = "Negligible savings, low pressure."
        
    # Fallback
    else:
        strategy = OptimizationStrategy.HOT_PATH_DETERMINISTIC
        reason = "Moderate savings. Using deterministic rules."

    return {
        "strategy": strategy.value,
        "reason": reason,
        "signals": {
            "budget_pressure": budget_pressure,
            "estimated_savings": estimated_savings,
            "constraint_risk": constraint_risk
        }
    }