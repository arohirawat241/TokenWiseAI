from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.models import OptimizationRequest, OptimizationResponse
from app.tokenizer import analyze_prompt
from app.strategy import decide_routing_strategy, OptimizationStrategy
from app.compressor import compress_prompt, semantic_compress
from app.validator import validate_structure

app = FastAPI(
    title="LLM Token Optimization Engine",
    description="Middleware to minimize LLM costs and latency by dynamically optimizing prompts.",
    version="1.0.0"
)

# Allow the React frontend to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Optimization Engine is running"}

@app.post("/optimize", response_model=OptimizationResponse)
def optimize_prompt(request: OptimizationRequest):
    try:
        # 1. Analyze the original prompt
        original_analysis = analyze_prompt(request.system_prompt, request.prompt, request.model)
        original_tokens = original_analysis["estimated_total_tokens"]
        
        # 2. Calculate signals and decide strategy based on the Policy Router
        routing_decision = decide_routing_strategy(request.prompt, original_tokens, request.model_limit)
        strategy = OptimizationStrategy(routing_decision["strategy"])
        
        # Print signals for observability
        print(f"\n--- SIGNALS ---")
        print(f"Pressure: {routing_decision['signals']['budget_pressure']}")
        print(f"Savings:  {routing_decision['signals']['estimated_savings']}")
        print(f"Risk:     {routing_decision['signals']['constraint_risk']}")
        print(f"Decision: {routing_decision['reason']}")
        print(f"-> Executing: {strategy.value}")
        
        # 3. Execute the strategy
        if strategy == OptimizationStrategy.PASSTHROUGH:
            optimized_text = request.prompt
            validation = {"is_valid": True, "reason": "Passthrough"}
            
        elif strategy == OptimizationStrategy.HOT_PATH_DETERMINISTIC:
            optimized_text = compress_prompt(request.prompt)
            validation = validate_structure(request.prompt, optimized_text)
            if not validation["is_valid"]:
                print(f"-> Validation failed in Hot Path: {validation['reason']}. Falling back.")
                optimized_text = request.prompt
                
        elif strategy == OptimizationStrategy.COLD_PATH_SEMANTIC:
            ai_compressed = semantic_compress(request.prompt)
            optimized_text = compress_prompt(ai_compressed)
            validation = validate_structure(request.prompt, optimized_text)
            if not validation["is_valid"]:
                print(f"-> Validation failed in Cold Path: {validation['reason']}. Falling back.")
                optimized_text = request.prompt
                
        else: # AGGRESSIVE_REDUCTION
            ai_compressed = semantic_compress(request.prompt) 
            optimized_text = compress_prompt(ai_compressed)
            validation = validate_structure(request.prompt, optimized_text)
            if not validation["is_valid"]:
                print(f"-> Validation failed in Aggressive Reduction: {validation['reason']}. Falling back.")
                optimized_text = request.prompt

        print(f"Optimization Complete!\n")
            
        # 4. Analyze the optimized prompt
        optimized_analysis = analyze_prompt(request.system_prompt, optimized_text, request.model)
        optimized_tokens = optimized_analysis["estimated_total_tokens"]
        
        # 5. Calculate savings
        tokens_saved = original_tokens - optimized_tokens
        compression_pct = (tokens_saved / original_tokens * 100) if original_tokens > 0 else 0.0
        cost_saved = original_analysis["estimated_cost_usd"] - optimized_analysis["estimated_cost_usd"]
        
        # 6. Budget allocation
        budget_allocation = {
            "system_prompt": optimized_analysis["system_tokens"],
            "user_prompt": optimized_analysis["user_tokens"],
            "reserved_output": optimized_analysis["estimated_output_tokens"]
        }

        return OptimizationResponse(
            original_tokens=original_tokens,
            optimized_tokens=optimized_tokens,
            compression_percentage=round(compression_pct, 2),
            estimated_cost_saved=round(cost_saved, 6),
            strategy_used=strategy.value,
            optimized_prompt=optimized_text,
            budget_allocation=budget_allocation,
            routing_signals=routing_decision["signals"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))