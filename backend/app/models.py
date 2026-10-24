from pydantic import BaseModel, Field
from typing import Optional

class OptimizationRequest(BaseModel):
    prompt: str = Field(..., description="The user prompt to optimize")
    system_prompt: Optional[str] = Field("", description="Optional system prompt")
    model: Optional[str] = Field("gpt-4o", description="Target LLM model")
    model_limit: Optional[int] = Field(128000, description="Max context window for the model")

class OptimizationResponse(BaseModel):
    original_tokens: int
    optimized_tokens: int
    compression_percentage: float
    estimated_cost_saved: float
    strategy_used: str
    optimized_prompt: str
    budget_allocation: dict
    routing_signals: dict = {} 