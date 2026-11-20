import re

BANNED_WORDS = (
    "brilliant",
    "groundbreaking",
    "revolutionary",
    "masterpiece",
    "genius",
    "game-changing",
    "flawless",
    "unparalleled",
)

def lint_dialogue_script(doc: dict) -> dict:
    errors = []
    turns = doc.get("turns") if isinstance(doc, dict) else None
    if not isinstance(turns, list) or len(turns) == 0:
        return {"valid": False, "errors": ["Script must include a non-empty turns list."]}

    limits = doc.get("limitations") if isinstance(doc.get("limitations"), list) else []
    if len(limits) < 2:
        errors.append(f"Expected >= 2 explicit limitations; found {len(limits)}.")

    for idx, turn in enumerate(turns, start=1):
        body = str(turn.get("text", ""))
        for word in BANNED_WORDS:
            if re.search(rf"\b{re.escape(word)}\b", body, re.IGNORECASE):
                errors.append(f"Turn {idx} ({turn.get('speaker')}) uses banned flattery: '{word}'.")

    return {"valid": len(errors) == 0, "errors": errors}
