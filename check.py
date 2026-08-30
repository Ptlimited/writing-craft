#!/usr/bin/env python3
"""Mechanical checks for the writing-craft gate.

Thresholds are calibrated against a 50-file blind corpus, scored by three
independent judges. See SKILL.md for where the rules and the numbers come from.

Usage:
    python3 check.py draft.md
    python3 check.py draft.md --hooks     # zero-tolerance hedging
    cat draft.md | python3 check.py -
    python3 check.py draft.md --json

Exit code 0 = all mechanical checks pass. 1 = at least one fails.
The judgment rules (2, 3, 4, 6) are not checked here. They are listed in the
output as a reminder, because a passing score on the mechanical checks is not
the same as a finished draft.

One check sits outside the nine: em and en dashes, at zero tolerance. It is not
one of the judged signals and carries no corpus number. See the note above the
thresholds.
"""
import argparse
import json
import re
import statistics
import sys
from pathlib import Path

# --- calibrated thresholds -------------------------------------------------
# Firing rates on the calibration corpus, HIGH = mean Human >= 4.0 (n=19),
# LOW = mean Human <= 2.33 (n=12):
#   hedges  > 0.5 per 100w   fires HIGH  4/19   LOW  9/12
#   contraction ratio < 0.7  fires HIGH  2/19   LOW  8/12
#   sentence CV < 0.45       fires HIGH  2/19   LOW 10/12
# Together they catch 12/12 of the LOW files.
#
# The dash check is NOT one of the nine and carries no corpus number. Em and en
# dashes were stripped from all 50 files before judging, so no scored file was
# ever left to fit a threshold against.
#
# It is here because of why they were stripped: "Models have a telltale sign when
# it comes to em dashes and en dashes." Stripping them kept the test neutral. In
# a draft that ships, the tell is the problem, and none of the nine catch it.
# Zero tolerance, no threshold to fit.
HEDGE_PER_100W = 0.5
CONTRACTION_RATIO = 0.7
SENTENCE_CV = 0.45

HEDGES = [
    "might", "may", "often", "sometimes", "probably", "tends to", "tend to",
    "arguably", "perhaps", "somewhat", "generally", "typically", "fairly",
    "quite", "relatively", "usually", "can be", "could be", "seems", "appears",
    "a bit", "rather", "possibly", "likely", "in some cases", "for the most part",
    "in many ways", "more or less", "to some extent",
]

EXPANDED = [
    "it is", "do not", "does not", "did not", "you are", "i am", "that is",
    "cannot", "can not", "will not", "there is", "they are", "we are", "is not",
    "are not", "was not", "were not", "would not", "should not", "could not",
    "you will", "it will", "i have", "you have", "let us", "here is", "what is",
    "who is", "he is", "she is", "i will", "we will", "they will", "you would",
]
CONTRACTED = re.compile(r"\b\w+'(?:s|t|re|ve|ll|d|m)\b", re.I)

# Rule 9: claims a reader would have to verify before publishing.
CLAIM_PATTERNS = [
    (re.compile(r"\b\d+(?:\.\d+)?\s*%"), "percentage"),
    (re.compile(r"\b\d[\d,]{2,}\b"), "large number"),
    (re.compile(r"\b(?:19|20)\d{2}\b"), "year"),
    (re.compile(r"\b\d+\s*(?:x|times)\b", re.I), "multiplier"),
    (re.compile(r"\b\d+\s*(?:seconds?|minutes?|hours?|days?|weeks?|months?|years?)\b", re.I), "duration"),
    (re.compile(r"\b(?:I|we)\s+(?:tested|measured|ran|tried|found|built|spent|shipped|counted)\b"), "first-person claim"),
    (re.compile(r"\b(?:studies|research|data)\s+(?:show|shows|suggest|suggests)\b", re.I), "appeal to research"),
]

JUDGMENT_RULES = [
    ("2. Argue with the brief",
     "Name in one line what this adds that the brief did not contain. If you cannot, it has not departed."),
    ("3. One load-bearing analogy",
     "Count the analogies. Keep one. Could it be swapped for another with nothing lost? Then cut it."),
    ("4. No stacked template shapes",
     "Stacked single-sentence paragraphs, a litany opener, an aphorism couplet close, a question "
     "aimed at the reader, a tidy three-part list. Two or more together and the shape arrived "
     "before the thinking did."),
    ("6. N options means N different options",
     "If the brief asked for several, does each change what the finished piece would be? Give each "
     "a one-line reason it works on a reader."),
]


def strip_markup(text):
    body = re.sub(r"^#.*$", "", text, flags=re.M)
    body = re.sub(r"^\s*>\s?", "", body, flags=re.M)
    return body


def sentences(text):
    body = re.sub(r"^\s*(?:[-*]|\d+[.)])\s+", "", strip_markup(text), flags=re.M)
    parts = re.split(r"(?<=[.!?])\s+", body)
    return [p.strip() for p in parts if len(p.strip().split()) >= 2]


def count_phrases(low, phrases):
    hits = {}
    for p in phrases:
        n = len(re.findall(r"\b" + re.escape(p) + r"\b", low))
        if n:
            hits[p] = n
    return hits


def analyse(text, hooks=False):
    body = strip_markup(text)
    low = body.lower()
    words = len(low.split())
    sents = sentences(text)

    hedge_hits = count_phrases(low, HEDGES)
    hedge_n = sum(hedge_hits.values())
    hedge_rate = 100 * hedge_n / words if words else 0.0

    expanded_hits = count_phrases(low, EXPANDED)
    expanded_n = sum(expanded_hits.values())
    contracted_n = len(CONTRACTED.findall(body))
    total_c = contracted_n + expanded_n
    ratio = contracted_n / total_c if total_c else 1.0

    lens = [len(s.split()) for s in sents]
    if len(lens) > 1:
        mean_len = statistics.mean(lens)
        cv = statistics.pstdev(lens) / mean_len if mean_len else 0.0
    else:
        mean_len, cv = (lens[0] if lens else 0), 0.0

    claims = []
    for pattern, label in CLAIM_PATTERNS:
        for m in pattern.finditer(body):
            line = body[:m.start()].count("\n") + 1
            claims.append({"kind": label, "text": m.group(0).strip(), "line": line})

    checks = []
    hedge_limit = 0.0 if hooks else HEDGE_PER_100W
    checks.append({
        "rule": "5. Cut the hedges",
        "pass": hedge_rate <= hedge_limit,
        "value": round(hedge_rate, 2),
        "limit": hedge_limit,
        "unit": "per 100 words",
        "detail": ", ".join(f"{k} x{v}" for k, v in sorted(hedge_hits.items(), key=lambda i: -i[1])) or "none",
        "fix": ("A hedged hook is not a hook. Cut every one." if hooks else
                "Cut them, or commit to the claim. Keep one only if you can say why it is load-bearing."),
    })
    checks.append({
        "rule": "7. Contractions",
        "pass": ratio >= CONTRACTION_RATIO,
        "value": round(ratio, 2),
        "limit": CONTRACTION_RATIO,
        "unit": "contracted / (contracted + expanded)",
        "detail": ", ".join(f"{k} x{v}" for k, v in sorted(expanded_hits.items(), key=lambda i: -i[1])[:8]) or "none",
        "fix": "Expanded forms mean the piece is being narrated, not said. Contract them.",
    })
    checks.append({
        "rule": "8. Vary the rhythm",
        "pass": cv >= SENTENCE_CV,
        "value": round(cv, 2),
        "limit": SENTENCE_CV,
        "unit": "coefficient of variation, sentence length",
        "detail": f"{len(sents)} sentences, mean {mean_len:.1f} words",
        "fix": "Sentences are too close to the same length. Let one run on because the thought does, then stop one short.",
    })

    em_n = body.count("—")
    en_n = body.count("–")
    dash_hits = {}
    if em_n:
        dash_hits["em dash"] = em_n
    if en_n:
        dash_hits["en dash"] = en_n
    checks.append({
        "rule": "Dashes (outside the nine)",
        "pass": (em_n + en_n) == 0,
        "value": em_n + en_n,
        "limit": 0,
        "unit": "em or en dashes, zero tolerance",
        "detail": ", ".join(f"{k} x{v}" for k, v in dash_hits.items()) or "none",
        "fix": "Rewrite around it. A period, a comma, a colon, or a semicolon does the job a dash was doing. "
               "An en dash inside a number range counts too. Write \"2020 to 2024\" instead.",
    })

    return {
        "words": words,
        "sentences": len(sents),
        "checks": checks,
        "claims": claims,
        "passed": all(c["pass"] for c in checks),
    }


def render(result, hooks):
    out = []
    status = "PASS" if result["passed"] else "FAIL"
    out.append(f"writing-craft mechanical checks: {status}"
               f"  ({result['words']} words, {result['sentences']} sentences"
               f"{', hooks mode' if hooks else ''})")
    out.append("")
    for c in result["checks"]:
        mark = "ok  " if c["pass"] else "FAIL"
        out.append(f"  [{mark}] {c['rule']}")
        out.append(f"         {c['value']} against {c['limit']} {c['unit']}")
        out.append(f"         found: {c['detail']}")
        if not c["pass"]:
            out.append(f"         fix:   {c['fix']}")
        out.append("")

    out.append("  Rule 9. Claims needing a source before this ships:")
    if result["claims"]:
        for c in result["claims"]:
            out.append(f"         line {c['line']}: {c['kind']} - \"{c['text']}\"")
        out.append("         Each is either sourced or marked for the writer. Never invent one to satisfy rule 1.")
    else:
        out.append("         none found. Rule 1 wants at least one concrete detail, so this is")
        out.append("         usually a sign the draft is speaking in categories.")
    out.append("")

    out.append("  Judgment rules, not checkable here:")
    for name, prompt in JUDGMENT_RULES:
        out.append(f"    {name}")
        out.append(f"        {prompt}")
    out.append("")
    out.append("  Rule 1. Specificity: does the draft carry at least one detail that would be")
    out.append("          pointless to invent? Counting numbers does not answer this. In the corpus")
    out.append("          the weak files carried MORE numbers than the strong ones, because they")
    out.append("          invented them. Judge the detail, not the digit count.")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", help="path to the draft, or - for stdin")
    ap.add_argument("--hooks", action="store_true", help="zero-tolerance hedging, for hook lists")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    text = sys.stdin.read() if args.file == "-" else Path(args.file).read_text()
    result = analyse(text, hooks=args.hooks)

    print(json.dumps(result, indent=2) if args.json else render(result, args.hooks))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
