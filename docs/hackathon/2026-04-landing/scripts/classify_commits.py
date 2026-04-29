#!/usr/bin/env python3
"""Classify commits as AI-driven, AI-co-authored, or human-only.

Reads commit dump produced by:
  git log <range> --pretty=format:"===%H===%n%an%n%B%n---"
"""
import re
import sys
from collections import Counter
from pathlib import Path


def parse_commits(text):
    """Yield (sha, author, body) tuples."""
    blocks = re.split(r"^===([0-9a-f]{40})===$", text, flags=re.MULTILINE)
    # blocks[0] is empty/junk before first match; then alternating sha, body
    i = 1
    while i < len(blocks) - 1:
        sha = blocks[i]
        rest = blocks[i + 1]
        # rest is "\n<author>\n<body>\n---\n"
        lines = rest.lstrip("\n").split("\n", 1)
        author = lines[0] if lines else ""
        body_part = lines[1] if len(lines) > 1 else ""
        # strip trailing "---\n"
        body = re.sub(r"\n---\s*$", "", body_part)
        yield sha, author, body
        i += 2


# AI signature patterns (case-insensitive)
AI_PATTERNS = [
    re.compile(r"co-authored-by:\s*claude", re.IGNORECASE),
    re.compile(r"co-authored-by:\s*codex", re.IGNORECASE),
    re.compile(r"generated with claude code", re.IGNORECASE),
    re.compile(r"claude\.ai/code", re.IGNORECASE),
    re.compile(r"\bcodex\b.*@users\.noreply", re.IGNORECASE),
]

AI_AUTHORS = {"claude", "codex"}
BOT_AUTHORS = {"github-actions[bot]"}


def classify(author, body):
    """Return one of:
    - 'ai_solo'       : author is AI itself
    - 'ai_coauthored' : human author but AI in body
    - 'bot'           : automation bot (release, CI)
    - 'human_only'    : no AI signal anywhere
    """
    a_low = author.lower().strip()
    if a_low in AI_AUTHORS:
        return "ai_solo"
    if author in BOT_AUTHORS:
        return "bot"
    for pat in AI_PATTERNS:
        if pat.search(body):
            return "ai_coauthored"
    return "human_only"


def main():
    path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8")
    commits = list(parse_commits(text))
    print(f"Total commits parsed: {len(commits)}")
    print()

    counts = Counter()
    by_author = Counter()
    samples = {"ai_solo": [], "ai_coauthored": [], "bot": [], "human_only": []}

    for sha, author, body in commits:
        cls = classify(author, body)
        counts[cls] += 1
        by_author[(author, cls)] += 1
        if len(samples[cls]) < 3:
            first_line = body.split("\n", 1)[0]
            samples[cls].append(f"  {sha[:8]} [{author}] {first_line[:80]}")

    print("=== Classification breakdown ===")
    total = sum(counts.values())
    for cls in ["ai_solo", "ai_coauthored", "bot", "human_only"]:
        n = counts[cls]
        pct = 100 * n / total if total else 0
        print(f"  {cls:18s}: {n:4d}  ({pct:5.1f}%)")
    ai_total = counts["ai_solo"] + counts["ai_coauthored"]
    print(f"  {'AI involved':18s}: {ai_total:4d}  ({100*ai_total/total:5.1f}%)")
    print()

    print("=== By author × classification ===")
    for (author, cls), n in sorted(by_author.items(), key=lambda x: -x[1]):
        print(f"  {author:25s} {cls:18s} {n:4d}")
    print()

    print("=== Samples ===")
    for cls, lines in samples.items():
        print(f"--- {cls} ---")
        for line in lines:
            print(line)
        print()


if __name__ == "__main__":
    main()
