import os
import json
import aiohttp
from dotenv import load_dotenv

load_dotenv()

# --- Provider Configuration ---
# Set LLM_PROVIDER=anthropic in .env to use Claude instead of local Ollama
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()

OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434") + "/api/generate"
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = "claude-sonnet-4-20250514"
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"


async def call_llm(prompt: str, system: str = "") -> str:
    """
    Unified LLM caller. Dispatches to Ollama or Anthropic based on LLM_PROVIDER env var.
    """
    if LLM_PROVIDER == "anthropic":
        return await _call_anthropic(prompt, system)
    else:
        return await _call_ollama(prompt)


async def _call_ollama(prompt: str) -> str:
    """Call local Ollama instance."""
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
                    print(f"--- RAW OLLAMA RESPONSE ---\n{response[:300]}...\n--------------------------")
                    return response
                else:
                    print(f"Ollama error: {resp.status}")
                    return ""
    except Exception as e:
        print(f"Failed to call Ollama: {e}")
        return ""


async def _call_anthropic(prompt: str, system: str = "") -> str:
    """Call Anthropic Claude API."""
    if not ANTHROPIC_API_KEY:
        print("ANTHROPIC_API_KEY not set in .env")
        return ""
    try:
        headers = {
            "Content-Type": "application/json",
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01"
        }
        body = {
            "model": ANTHROPIC_MODEL,
            "max_tokens": 2000,
            "messages": [{"role": "user", "content": prompt}]
        }
        if system:
            body["system"] = system

        async with aiohttp.ClientSession() as session:
            async with session.post(ANTHROPIC_URL, headers=headers, json=body) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    response = data["content"][0]["text"]
                    print(f"--- RAW ANTHROPIC RESPONSE ---\n{response[:300]}...\n-----------------------------")
                    return response
                else:
                    err = await resp.text()
                    print(f"Anthropic error {resp.status}: {err}")
                    return ""
    except Exception as e:
        print(f"Failed to call Anthropic: {e}")
        return ""


def _safe_parse_json(text: str) -> dict | list | None:
    """Extract and parse the first valid JSON object or array from a string."""
    text = text.strip()
    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Strip markdown fences
    cleaned = text.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    # Try extracting by brace/bracket boundaries
    for start_char, end_char in [('{', '}'), ('[', ']')]:
        start = cleaned.find(start_char)
        end = cleaned.rfind(end_char)
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(cleaned[start:end+1])
            except json.JSONDecodeError:
                pass
    return None


async def parse_jd_with_llm(jd_text: str) -> dict:
    prompt = f"""Parse the following Job Description and extract key information as JSON.

Return ONLY a valid JSON object with these fields:
- role_title (string)
- required_skills (array of strings)
- experience_years_required (integer or null)
- role_type (string, e.g. "Full-time", "Contract")
- location_preference (string)
- nice_to_haves (array of strings)
- summary (string, 1-2 sentences)

No markdown, no backticks, no explanation. Just the raw JSON object.

Job Description:
{jd_text}"""

    response_text = await call_llm(prompt)
    if not response_text:
        return {"error": "LLM failed to respond"}

    parsed = _safe_parse_json(response_text)
    if parsed and isinstance(parsed, dict):
        return parsed

    print(f"--- PARSE FAILURE ---\n{response_text}\n--------------------")
    return {"error": "Failed to parse JD — LLM did not return valid JSON"}


async def simulate_outreach(candidate_profile: dict, jd_summary: str) -> dict:
    # Build a clean candidate description (no raw dict dumps in the prompt)
    skills_str = ", ".join(candidate_profile.get("skills", []))
    name = candidate_profile.get("name", "Candidate")
    role = candidate_profile.get("current_role", "Engineer")
    exp = candidate_profile.get("experience_years", 0)
    location = candidate_profile.get("location", "India")
    ctc = candidate_profile.get("expected_ctc", "not specified")
    open_to = candidate_profile.get("open_to_work", True)

    prompt = f"""You are simulating a recruiter reaching out to a candidate about a job opportunity.

Candidate Profile:
- Name: {name}
- Role: {role} ({exp} years experience)
- Skills: {skills_str}
- Location: {location}
- Expected CTC: {ctc}
- Currently open to work: {open_to}

Job Summary: {jd_summary}

Simulate a natural 4-turn conversation (2 from recruiter, 2 from candidate) where:
1. Recruiter introduces the opportunity
2. Candidate responds naturally based on their profile and open_to_work status
3. Recruiter follows up with role specifics
4. Candidate gives a final response indicating their level of interest

Then return a JSON object with:
- "conversation": array of objects with "speaker" (string) and "text" (string)
- "interest_score": integer 0-100 (based on how enthusiastic and engaged the candidate is)
- "summary": string (1-2 sentences explaining the interest score)

Return ONLY valid JSON. No markdown, no backticks, no preamble."""

    response_text = await call_llm(prompt)
    if not response_text:
        return {"error": "LLM failed", "interest_score": 0, "conversation": [], "summary": ""}

    parsed = _safe_parse_json(response_text)
    if parsed and isinstance(parsed, dict) and "conversation" in parsed:
        return parsed

    print(f"--- OUTREACH PARSE FAILURE ---\n{response_text}\n------------------------------")
    return {
        "error": "Failed to simulate outreach",
        "interest_score": 0,
        "conversation": [],
        "summary": "Simulation failed — LLM did not return valid JSON"
    }
