import os
import json
import aiohttp
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.1"

async def call_llm(prompt: str) -> str:
    try:
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            }
            async with session.post(OLLAMA_URL, json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    response = data.get("response", "")
                    print(f"--- RAW LLM RESPONSE ---\n{response}\n-------------------------")
                    return response
                else:
                    print(f"Ollama error: {resp.status}")
                    return ""
    except Exception as e:
        print(f"Failed to call Ollama: {e}")
        return ""

async def parse_jd_with_llm(jd_text: str) -> dict:
    prompt = f"""
    Parse the following Job Description (JD) and extract key information in JSON format.
    The JSON should have:
    - role_title
    - required_skills (list)
    - experience_years_required (int or null)
    - role_type (e.g., Full-time, Contract)
    - location_preference
    - nice_to_haves (list)
    - summary (short paragraph)

    JD Text:
    {jd_text}

    Return ONLY a valid JSON object. Do NOT include markdown code blocks, backticks, or any preamble. Your entire response must be a single JSON object.
    
    CRITICAL: Your life depends on returning nothing but a clean, valid JSON block.
    """
    response_text = await call_llm(prompt)
    if not response_text:
        return {"error": "LLM failed"}

    try:
        start = response_text.find("{")
        end = response_text.rfind("}")
        if start != -1 and end != -1:
            json_str = response_text[start:end+1]
            return json.loads(json_str)
    except Exception as e:
        print(f"--- DEBUG: RAW LLM OUTPUT START ---")
        print(response_text)
        print(f"--- DEBUG: RAW LLM OUTPUT END ---")
        print(f"Failed to parse JSON: {e}")
    
    return {"error": "Failed to parse JD JSON"}

async def simulate_outreach(candidate_profile: dict, jd_summary: str) -> dict:
    prompt = f"""
    You are a candidate named {candidate_profile['name']}. 
    Your profile: {candidate_profile}
    
    A recruiter is reaching out about this job: {jd_summary}
    
    Simulate a conversation where the recruiter asks:
    1. Are you currently open to new opportunities?
    2. Does this role interest you? Why/why not?
    3. What's your expected CTC?
    4. What's your notice period?
    
    IMPORTANT: Do NOT include raw JSON data, profile dictionaries, or technical field names in the conversation text. Speak naturally like a human candidate.
    
    Return the response in JSON format:
    {{
        "conversation": [
            {{"speaker": "Recruiter", "text": "..."}},
            {{"speaker": "{candidate_profile['name']}", "text": "..."}}
        ],
        "interest_score": int,
        "summary": "Short explanation of interest level"
    }}
    
    Return ONLY a valid JSON object. Do NOT include markdown code blocks, backticks, or any conversational filler. Your entire response must be a single JSON object.
    
    CRITICAL: Your life depends on returning nothing but a clean, valid JSON block.
    """
    response_text = await call_llm(prompt)
    if not response_text:
        return {"error": "LLM failed", "interest_score": 0, "conversation": []}

    try:
        start = response_text.find("{")
        end = response_text.rfind("}")
        if start != -1 and end != -1:
            json_str = response_text[start:end+1]
            return json.loads(json_str)
    except Exception as e:
        print(f"--- DEBUG: RAW OUTREACH OUTPUT START ---")
        print(response_text)
        print(f"--- DEBUG: RAW OUTREACH OUTPUT END ---")
        print(f"Failed to parse Outreach JSON: {e}")
        
    return {"error": "Failed to simulate outreach", "interest_score": 0, "conversation": []}
