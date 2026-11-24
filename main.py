#!/usr/bin/env python3
"""Seventeen Syllables of Debugging entry (make.fun, program/v1).

Writes one original haiku about debugging to /output/entry.txt
(or $MAKEFUN_OUTPUT_DIR). Pure stdlib only (os, re). The haiku is
three lines in the 5-7-5 syllable shape, at most 200 characters,
byte-identical on every run.
"""

import os
import re

HAIKU = (
    "Breakpoint set at dawn\n"
    "the log scrolls past, still no clue\n"
    "it was a typo"
)

EXPECTED_SYLLABLES = (5, 7, 5)

# Syllable counts for the words this haiku uses. Every word here is
# one syllable except "breakpoint" (2) and "typo" (2). Verified line
# by line against the 5-7-5 shape:
#   "Breakpoint set at dawn"              -> 2+1+1+1 = 5
#   "the log scrolls past, still no clue" -> 1+1+1+1+1+1+1 = 7
#   "it was a typo"                       -> 1+1+1+2 = 5
# Total 72 characters, well under the 200-character gate.
SYLLABLES = {
    "breakpoint": 2,
    "typo": 2,
}


def count_syllables(word):
    """Count syllables in one word: known words from the table,
    otherwise a vowel-group heuristic (each run of vowels counts once,
    a trailing silent 'e' drops one)."""
    w = word.strip(".,;:!?\"'").lower()
    if not w:
        return 0
    if w in SYLLABLES:
        return SYLLABLES[w]
    groups = re.findall(r"[aeiouy]+", w)
    count = len(groups)
    if w.endswith("e") and count > 1:
        count -= 1
    return max(count, 1)


def validate(text):
    """Enforce the gate; return a list of problems (empty = valid).

    Gate: UTF-8, 1-200 chars, not only whitespace; plus the haiku
    shape: exactly 3 lines in the 5-7-5 syllable shape.
    """
    problems = []
    if not isinstance(text, str):
        return ["not a string"]
    if not 1 <= len(text) <= 200:
        problems.append("length %d outside 1-200" % len(text))
    if not text.strip():
        problems.append("only whitespace")
    try:
        text.encode("utf-8")
    except UnicodeEncodeError as exc:
        problems.append("not UTF-8 encodable: %s" % exc)
    lines = text.split("\n")
    if len(lines) != 3:
        problems.append("expected 3 lines, got %d" % len(lines))
    else:
        for i, line in enumerate(lines):
            got = sum(count_syllables(w) for w in line.split())
            if got != EXPECTED_SYLLABLES[i]:
                problems.append(
                    "line %d has %d syllables, expected %d"
                    % (i + 1, got, EXPECTED_SYLLABLES[i])
                )
    return problems


def main():
    problems = validate(HAIKU)
    if problems:
        raise SystemExit("haiku failed validation: " + "; ".join(problems))
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.txt")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(HAIKU)
    print("wrote %d chars to %s" % (len(HAIKU), path))


if __name__ == "__main__":
    main()
