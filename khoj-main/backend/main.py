from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import asyncio
from services.llm_service import parse_jd_with_llm, simulate_outreach
from typing import List, Optional

app = FastAPI(title="Talent Scout AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class JDRequest(BaseModel):
    jd_text: str

class Candidate(BaseModel):
    id: int
    name: str
    skills: List[str]
    experience_years: int
    current_role: str
    location: str
    open_to_work: bool
    expected_ctc: str
    email: str
    bio: str
    match_score: Optional[float] = 0
    match_explanation: Optional[str] = ""
    interest_score: Optional[float] = 0
    interest_summary: Optional[str] = ""
    conversation: Optional[List[dict]] = []

def load_candidates():
    with open("data/candidates.json", "r") as f:
        return json.load(f)

def calculate_match_score(candidate: dict, parsed_jd: dict):
    score = 0
    explanation = []
    
    # Skills overlap (40%)
    required_skills = [s.lower() for s in parsed_jd.get("required_skills", [])]
    candidate_skills = [s.lower() for s in candidate.get("skills", [])]
    
    if not required_skills:
        skill_score = 100
    else:
        matched_skills = set(required_skills).intersection(set(candidate_skills))
        skill_score = (len(matched_skills) / len(required_skills)) * 100
        explanation.append(f"Matched {len(matched_skills)}/{len(required_skills)} required skills.")
    
    # Experience fit (30%)
    req_exp = parsed_jd.get("experience_years_required")
    cand_exp = candidate.get("experience_years", 0)
    if req_exp is None:
        exp_score = 100
    else:
        if cand_exp >= req_exp:
            exp_score = 100
            explanation.append(f"Experience ({cand_exp} yrs) meets or exceeds requirement ({req_exp} yrs).")
        else:
            exp_score = (cand_exp / req_exp) * 100
            explanation.append(f"Experience ({cand_exp} yrs) is less than required ({req_exp} yrs).")
            
    # Role alignment (30%)
    req_role = parsed_jd.get("role_title", "").lower()
    cand_role = candidate.get("current_role", "").lower()
    if req_role in cand_role or cand_role in req_role:
        role_score = 100
        explanation.append("Current role aligns well with the target role.")
    else:
        role_score = 50
        explanation.append("Role alignment is moderate.")
        
    final_score = (skill_score * 0.4) + (exp_score * 0.3) + (role_score * 0.3)
    return round(final_score, 2), " ".join(explanation)

@app.post("/api/run")
async def run_pipeline(request: JDRequest):
    print(f"Received JD: {request.jd_text[:100]}...")
    # 1. Parse JD
    print("\n" + "="*50)
    print("🚀 STAGE 1: PARSING JOB DESCRIPTION")
    print("="*50)
    parsed_jd = await parse_jd_with_llm(request.jd_text)
    if "error" in parsed_jd:
        print(f"❌ PARSING ERROR: {parsed_jd['error']}")
        raise HTTPException(status_code=400, detail=parsed_jd["error"])
    print(f"✅ Extracted Role: {parsed_jd.get('role_title')}")
    print(f"✅ Skills Identified: {', '.join(parsed_jd.get('required_skills', []))}")
    print(f"✅ Exp Required: {parsed_jd.get('experience_years_required')} yrs")
        
    # 2. Match Candidates
    print("\n" + "="*50)
    print("🔍 STAGE 2: MATCHING 50 CANDIDATES")
    print("="*50)
    candidates = load_candidates()
    scored_candidates = []
    for cand in candidates:
        score, explanation = calculate_match_score(cand, parsed_jd)
        cand["match_score"] = score
        cand["match_explanation"] = explanation
        cand["interest_score"] = 0  # Default value
        cand["interest_summary"] = ""
        cand["conversation"] = []
        scored_candidates.append(cand)
        
    # Sort and take top 5 for outreach simulation
    scored_candidates.sort(key=lambda x: x["match_score"], reverse=True)
    top_candidates = scored_candidates[:5]
    print(f"✅ Top Matches identified: {', '.join([c['name'] for c in top_candidates])}")
    
    # 3. Simulated Outreach
    print("\n" + "="*50)
    print("💬 STAGE 3: SIMULATING AI OUTREACH (TOP 5)")
    print("="*50)
    outreach_tasks = []
    for cand in top_candidates:
        print(f"📡 Sending outreach to {cand['name']}...")
        outreach_tasks.append(simulate_outreach(cand, parsed_jd.get("summary", "New role")))
        
    outreach_results = await asyncio.gather(*outreach_tasks)
    
    for i, result in enumerate(outreach_results):
        cand_name = top_candidates[i]["name"]
        if "error" not in result:
            top_candidates[i]["interest_score"] = result.get("interest_score", 0)
            top_candidates[i]["interest_summary"] = result.get("summary", "")
            top_candidates[i]["conversation"] = result.get("conversation", [])
            
            print(f"\n✅ SUCCESS: {cand_name} ({top_candidates[i]['interest_score']}% Interest)")
            # Log the last message from the candidate as a preview
            conv = top_candidates[i]["conversation"]
            if conv:
                last_msg = conv[-1]
                print(f"   💬 Last Word: {last_msg['speaker']}: \"{last_msg['text'][:80]}...\"")
        else:
            top_candidates[i]["interest_summary"] = f"Simulation failed: {result['error']}"
            print(f"⚠️ FAILED: {cand_name} - {result['error']}")
        
    # Combine back
    final_list = top_candidates + scored_candidates[5:]
    final_list.sort(key=lambda x: (x["match_score"] * 0.6 + x["interest_score"] * 0.4), reverse=True)

    print("\n" + "="*50)
    print("🏆 FINAL RANKING (COMBINED SCORE)")
    print("="*50)
    for i, c in enumerate(final_list[:5]):
        combined = round(c['match_score'] * 0.6 + c['interest_score'] * 0.4, 2)
        print(f"RANK #{i+1}: {c['name'].ljust(15)} | Combined: {str(combined).ljust(5)}% | Match: {str(c['match_score']).ljust(5)}% | Interest: {str(c['interest_score']).ljust(5)}%")
    print("="*50 + "\n")
    
    return {
        "parsed_jd": parsed_jd,
        "shortlist": final_list
    }

@app.get("/api/candidates")
async def get_candidates():
    return load_candidates()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
