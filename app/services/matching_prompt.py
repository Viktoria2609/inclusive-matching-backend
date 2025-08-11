from typing import List, Dict, Any
import json

SYSTEM_PROMPT = """
Role: Inclusive Matching Assistant
Goal: Help match children/families to foster inclusion, friendship, and shared growth.

Match modes:
- similarity: match by similar age/city/strengths/interests.
- complementarity: one child’s strengths cover the other’s needs.
- goal_alignment: shared goals/notes (e.g., practice social skills).

Safety & constraints:
- Mind age gaps: up to 3 years difference for ages <=12; up to 4 years for ages 13–18.
- For in-person suggestions prefer same city (or explicit nearby radius if available).
- Flag any potential risks (allergies, sensory triggers, behavioral notes) if present.
- Output must be valid JSON only (no extra text).

Scoring rubric (0–100 total):
- age_fit (0–20)
- location_fit (0–15)
- strengths_overlap (0–15)
- needs_complement (0–25)
- goal_alignment (0–15)
- practicality (0–10)

You must rank top_k best candidates by overall_score and provide short rationale and a suggested first message the parent could send.
"""

def build_user_prompt(
    target: Dict[str, Any],
    candidates: List[Dict[str, Any]],
    mode: str = "complementarity",
    top_k: int = 5,
    online_radius_km: int = 50,
    language: str = "en",   
) -> str:
    target_json = json.dumps(target, ensure_ascii=False)
    candidates_json = json.dumps(candidates, ensure_ascii=False)
    params_json = json.dumps(
        {"mode": mode, "top_k": top_k, "online_radius_km": online_radius_km, "language": language},
        ensure_ascii=False,
    )

    return (
        "You are given:\n"
        f'LANGUAGE: "{language}"\n'
        "TARGET_PROFILE:\n"
        f"{target_json}\n\n"
        "CANDIDATE_PROFILES:\n"
        f"{candidates_json}\n\n"
        "PARAMS:\n"
        f"{params_json}\n\n"
        "TASK:\n"
        "Use LANGUAGE for all natural-language fields (rationale, suggested_first_message). "
        "Keep answers concise. Do not use any other language than LANGUAGE.\n"
        "1) Score each candidate by the rubric.\n"
        "2) Return JSON ONLY, following the schema below.\n"
        "3) Do not include any text outside of the JSON object.\n\n"
        "OUTPUT_JSON_SCHEMA:\n"
        "{\n"
        '  "target_id": number,\n'
        '  "mode": "similarity" | "complementarity" | "goal_alignment",\n'
        '  "results": [\n'
        "    {\n"
        '      "candidate_id": number,\n'
        '      "overall_score": number,\n'
        '      "scores": {\n'
        '        "age_fit": number,\n'
        '        "location_fit": number,\n'
        '        "strengths_overlap": number,\n'
        '        "needs_complement": number,\n'
        '        "goal_alignment": number,\n'
        '        "practicality": number\n'
        "      },\n"
        '      "shared_strengths": [string],\n'
        '      "complementary_pairs": [ { "from": "target|candidate", "strength": string, "covers_need": string } ],\n'
        '      "matched_goals": [string],\n'
        '      "red_flags": [string],\n'
        '      "rationale": string,\n'
        '      "suggested_first_message": string\n'
        "    }\n"
        "  ]\n"
        "}\n"
        "Return ONLY valid JSON. No extra text.\n"
    )
