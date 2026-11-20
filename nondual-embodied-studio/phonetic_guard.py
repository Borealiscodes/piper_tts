import re

LEXICON = [
    ("Flyxion", "FLIK-shun"),
    ("rasa-darśan", "RAH-sah DAR-shahn"),
    ("Rasa-Darśan", "RAH-sah DAR-shahn"),
    ("Tōrō", "TOH-roh"),
    ("Bonshō", "BON-shoh"),
    ("Tsukubai", "TSOO-koo-bye"),
    ("Iwakura", "ee-WAH-koo-rah"),
    ("Hakuin", "HAH-koo-een"),
    ("Huineng", "HWAY-nung"),
    ("sumi-e", "SOO-mee-eh"),
    ("koan", "KOH-ahn"),
]

def normalize_for_speech(text: str, lexicon=LEXICON) -> str:
    out = str(text or "")
    for term, spoken in lexicon:
        pattern = re.compile(rf"(?<![\w]){re.escape(term)}(?![\w])", re.UNICODE)
        out = pattern.sub(spoken, out)
    return out
