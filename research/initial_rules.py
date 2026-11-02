"""Frozen v1 feature rules. No litigation or enforceability predictions.

Offsets are Python Unicode character offsets in the original input, [start, end).
All evidence is a literal input slice; matching only folds whitespace/case.
"""
import re

TASKS = {
    "forward_looking": "MAE Forward looking standard (Y/N)",
    "consummation": "MAE definition includes adverse impact on Target's ability to consummate (Y/N)",
    "shareholder_litigation": "Target stockholder proceedings-Answer (Y/N)",
    "buyer_actions": "Actions taken by Buyer-Answer (Y/N)",
}

# Deliberately transparent and conservative in complexity, not in legal effect.
PATTERNS = {
    "forward_looking": r"\b(?:would|could|may|will)(?:\s+\w+){0,4}\s+(?:expected|likely)\b|\breasonably\s+likely\b",
    "consummation": r"\b(?:prevent|impair|impede|delay|hinder|interfere)(?:\s+\w+|[^\w\s]){0,24}\b(?:consummat\w*|complet\w*)\b|\bability\s+to\s+(?:consummate|complete)\b",
    "shareholder_litigation": r"\b(?:stockholder|shareholder)s?\b[\s\S]{0,220}\b(?:litigation|lawsuits?|suits?|proceedings?|actions?|claims?)\b|\b(?:litigation|lawsuits?|proceedings?|claims?)\b[\s\S]{0,220}\b(?:stockholder|shareholder)s?\b",
    "buyer_actions": r"\b(?:actions?|omissions?|conduct)\b[\s\S]{0,100}\b(?:by|of)\s+(?:the\s+)?(?:Buyer|Parent|Merger\s+Sub|Acquiror|Acquirer)\b",
}

def hit(text, pattern, start=0, end=None):
    m = re.search(pattern, text[start:end], re.I)
    if not m:
        return None
    a, b = start + m.start(), start + m.end()
    return {"start": a, "end": b, "quote": text[a:b]}

def boundary(text):
    """First exclusion marker; heuristic, not a parse tree."""
    m = re.search(r"\bprovided\s*,?\s*however\b|\bexcluding\b|\bexcept\s+(?:that|for)\b", text, re.I)
    return m.start() if m else len(text)

def features(text):
    cutoff = boundary(text)
    result = {}
    for task, pattern in PATTERNS.items():
        # Forward-looking boilerplate in an exclusion does not establish the core trigger.
        ev = hit(text, pattern, end=cutoff) if task in ("forward_looking", "consummation") else hit(text, pattern, start=cutoff if cutoff<len(text) else 0)
        result[task] = {"value": bool(ev), "evidence": ev,
                        "interpretation": "Textual cue found; verify scope" if ev else "No matching cue found; absence is not established"}
    return result

def analyze(text):
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Paste an extracted target MAE definition, including its exclusions and provisos.")
    if len(text)>100_000:
        raise ValueError("Input exceeds 100,000 characters. Supply the MAE definition rather than the full agreement.")
    fs = features(text)
    flags = []
    def flag(code, title, pattern, why, action):
        ev=hit(text,pattern)
        if ev:
            flags.append({"id":code,"title":title,"evidence":ev,"reason":why,"drafting_question":action})
    flag("D1", "Define the comparison group", r"\bdisproportionat\w*\b",
         "A disproportionate-effect exception requires a factual comparison. A generic industry reference may leave the relevant peers contested.",
         "Identify the relevant businesses, geography, comparison period and measurement approach; verify which exclusions the exception modifies.")
    flag("D2", "Check the reach of causal language", r"\b(?:relat(?:ed|ing)\s+to|aris(?:e|es|ing)\s+(?:from|out\s+of)|result(?:s|ed|ing)?\s+from|attributable\s+to)\b",
         "The chosen causal connector can change the reach of an exclusion when an event has several causes.",
         "Decide whether direct effects, indirect effects and mixed causes are covered, and use the intended connector consistently.")
    flag("D3", "Preserve the underlying-cause allocation", r"\b(?:fail\w*\s+to\s+meet|underlying\s+(?:caus\w*|facts?|events?|changes?))\b",
         "A missed forecast and the facts causing it are different objects of exclusion.",
         "State whether underlying causes may count toward an MAE and whether other exclusions still apply.")
    flag("D4", "Coordinate emergency exclusions with covenants", r"\b(?:pandemic\w*|epidemic\w*|COVID[-\s]?19|public\s+health)\b",
         "An MAE exclusion does not itself excuse noncompliance with a separate ordinary-course covenant.",
         "Read the ordinary-course covenant, consent procedure, notice requirement and closing conditions together; specify any emergency response permission.")
    flag("D5", "Make cross references reviewable", r"\b(?:clauses?|sections?)\s+(?:[\"\u201c\u201d']?\([a-zivx0-9]+\)|\d+(?:\.\d+)+)",
         "An exclusion or exception may apply only to selected clauses or representations.",
         "Use explicit clause lists and check each cross reference after edits; this prototype does not resolve them.")
    if fs['consummation']['value']:
        flags.append({"id":"D6","title":"Separate business effects from closing ability","evidence":fs['consummation']['evidence'],
                      "reason":"An ability-to-close prong may allocate different risks from a business deterioration prong.",
                      "drafting_question":"State which exclusions and forward-looking standards apply to each prong."})
    return {"version":"0.1.0","scope":"Extracted target MAE definition in a public-company merger agreement",
            "notice":"Research review prompts only. No litigation probability, enforceability conclusion, or clean bill of health. Human review of the entire agreement is required.",
            "characters":len(text),"features":fs,"review_prompts":flags,
            "input_checks":{"looks_like_mae_definition":bool(re.search(r'material\s+adverse\s+(?:effect|change)',text,re.I)),
                            "contains_omission_marker":'<omitted>' in text,
                            "contains_replacement_character":'\ufffd' in text}}
