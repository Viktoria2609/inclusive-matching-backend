from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
import json
from typing import Dict, Any, List

from app.database import get_db
from app.models import Profile
from app.services.matching_prompt import SYSTEM_PROMPT, build_user_prompt
from app.services.llm_client import llm_complete  # OpenAI client

router = APIRouter(prefix="/ai", tags=["ai-matching"])

# ----------------------------
# Utility to convert DB Profile to dict the model understands
# ----------------------------
def profile_to_dict(p: Profile) -> Dict[str, Any]:
    strengths = [s.strip() for s in (p.strengths or "").split(",") if s.strip()]
    needs = [n.strip() for n in (p.needs or "").split(",") if n.strip()]
    return {
        "id": p.id,
        "age": p.child_age,
        "city": p.city,
        "strengths": strengths,
        "needs": needs,
        "notes": p.notes or "",
        "connection_preference": "both",
    }

@router.post("/match")
def ai_match(
    target_id: int = Query(..., description="Profile ID to match from"),
    mode: str = Query("complementarity", regex="^(similarity|complementarity|goal_alignment)$"),
    top_k: int = Query(5, ge=1, le=20),
    same_city: bool = Query(True, description="Restrict candidates to the same city"),
    max_candidates: int = Query(50, ge=1, le=200, description="Max candidates passed to the LLM"),
    db: Session = Depends(get_db),
):
    # 1) load target
    target = db.get(Profile, target_id)
    if not target:
        raise HTTPException(status_code=404, detail="Target profile not found")

    # 2) prefilter candidates (age corridor + optional same city)
    age = target.child_age
    low = age - 3 if age <= 12 else age - 4
    high = age + 3 if age <= 12 else age + 4

    q = (
        db.query(Profile)
        .filter(Profile.id != target_id)
        .filter(Profile.child_age.between(low, high))
    )
    if same_city:
        q = q.filter(Profile.city == target.city)

    candidates: List[Profile] = q.limit(max_candidates).all()

    if not candidates:
        return {"target_id": target_id, "mode": mode, "results": []}

    # 3) normalize for prompt
    target_payload = profile_to_dict(target)
    candidate_payloads = [profile_to_dict(c) for c in candidates]

    # 4) build prompt
    user_prompt = build_user_prompt(
        target=target_payload,
        candidates=candidate_payloads,
        mode=mode,
        top_k=top_k,
        online_radius_km=50,
        language="ru",
    )

    # 5) call the model (OpenAI client)
    try:
        raw = llm_complete(SYSTEM_PROMPT, user_prompt)
    except Exception as e:
        # Typical causes: missing OPENAI_API_KEY, network, quota, wrong model name
        raise HTTPException(status_code=502, detail=f"LLM call failed: {e}")

    # 6) parse JSON strictly
    try:
        data = json.loads(raw)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM returned invalid JSON: {e}")

    # Minimal shape validation
    if not isinstance(data, dict) or not isinstance(data.get("results"), list):
        raise HTTPException(status_code=502, detail="Matcher returned invalid structure")

    # Enforce request values & top_k
    data["target_id"] = target_id
    data["mode"] = mode
    data["results"] = data["results"][:top_k]

    # Normalize rationale to a string (UI-friendly)
    for r in data["results"]:
        if isinstance(r.get("rationale"), list):
            r["rationale"] = " ".join(str(x) for x in r["rationale"] if x)

    return data