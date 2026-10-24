import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

def get_llm_response(prompt: str, system_prompt: str = "You are a helpful assistant.") -> str:
    try:
        response = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}],
            temperature=0.7, max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating response: {e}"

def evaluate_quality(original_prompt: str, response_a: str, response_b: str) -> dict:
    judge_prompt = f"""
    Original User Prompt: "{original_prompt}"
    Response A (from Original Prompt): {response_a}
    Response B (from Optimized Prompt): {response_b}
    
    Task: Compare Response A and Response B. Rate Response B compared to Response A on a scale of 1-10 for:
    1. Accuracy, 2. Completeness, 3. Instruction Following.
    Output MUST be a valid JSON object with these exact keys: "score_accuracy", "score_completeness", "score_instruction_following", "average_score", "justification".
    """
    try:
        response = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[{"role": "system", "content": "You are an expert AI evaluator. Output ONLY valid JSON. Do not include markdown formatting."}, {"role": "user", "content": judge_prompt}],
            response_format={"type": "json_object"}, temperature=0.2
        )
        result = response.choices[0].message.content.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(result)
    except Exception as e:
        return {"error": str(e), "average_score": 0, "justification": "Evaluation failed."}