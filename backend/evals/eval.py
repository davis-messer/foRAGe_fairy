"""
Run test_queries.json through the RAG chain and score responses.

Note: LLM output is non-deterministic, so instead of asserting exact equality
heuristics are used:
    - answerable=false  -> response should abstain ("not specified", "don't know")
    - answerable=true   -> response should NOT abstain, and should share
                           content words with the reference answers
"""

import json
import re
from pathlib import Path

from rag_assistant.config import SAMPLE_DOCUMENTS_DIR
from rag_assistant.generation import rag_chain
from rag_assistant.index import index_directory

ABSTAIN_MARKERS = [
    "not specified",
    "don't know",
    "do not know",
    "not mentioned",
    "cannot determine",
    "no information",
    "does not specify",
    "does not provide",
    "does not contain",
    "do not contain",
    "not provided",
    "not given",
]

STOP_WORDS = {
    "the", "a", "an", "is", "was", "were", "in", "of", "and", "to", "it",
    "her", "his", "she", "this", "that", "so", "for", "on", "by", "as",
    "at", "or", "be", "are", "did", "with",
}


def is_abstention(response: str) -> bool:
    return any(m in response.lower() for m in ABSTAIN_MARKERS)


def content_overlap(response: str, reference: str) -> float:
    """Fraction of the reference's content words present in the response."""
    ref = set(re.findall(r"[a-z0-9]+", reference.lower())) - STOP_WORDS
    resp = set(re.findall(r"[a-z0-9]+", response.lower()))
    return len(ref & resp) / len(ref) if ref else 0.0


def check(q: dict, response: str) -> tuple[bool, str]:
    """Return (passed, reason).

    Note: Answerable responses may contain abstention markers ("context does not provide X") 
    alongside real content — grounded partial answers aren't pure abstention, so check overlap first.
    """
    if not q["answerable"]:
        ok = is_abstention(response)
        return ok, "abstains" if ok else "should have abstained but answered"
    overlap = content_overlap(response, q["answer"])
    if overlap >= 0.3:
        return True, f"overlap {overlap:.0%}"
    if is_abstention(response):
        return False, "abstained on an answerable question"
    return False, f"low overlap with reference ({overlap:.0%})"


if __name__ == "__main__":
    index_directory(SAMPLE_DOCUMENTS_DIR)
    queries = json.load(open(Path(__file__).parent / "test_queries.json"))
    results = []

    for q in queries:
        response = rag_chain.invoke(q["query"])
        passed, reason = check(q, response)
        results.append(passed)
        print(f"[{'PASS' if passed else 'FAIL'}] {q['id']}: {q['query']}")
        print(f"       {reason}")
        print(f"       -> {response[:150]}")
        print()

    print(f"{sum(results)}/{len(results)} passed")
