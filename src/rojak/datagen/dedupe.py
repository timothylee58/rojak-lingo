from collections.abc import Callable

from ..text import jaccard, ngrams, stable_hash, tokens

SKETCH_SIZE = 6


def _sketch(shingles: set[tuple[str, ...]]) -> list[int]:
    return sorted(stable_hash(g) for g in shingles)[:SKETCH_SIZE]


def dedupe(
    rows: list[dict],
    key: Callable[[dict], str] = lambda r: r["prompt"],
    threshold: float = 0.8,
) -> tuple[list[dict], int]:
    """Drop exact and near-duplicate rows.

    A bottom-k sketch of each row's word trigrams is used as an inverted-index key, so we
    only compute Jaccard against rows that share a sketch hash instead of all pairs.
    """
    kept: list[dict] = []
    shingle_sets: list[set] = []
    index: dict[int, list[int]] = {}
    dropped = 0

    for row in rows:
        shingles = ngrams(tokens(key(row)), 3)
        sketch = _sketch(shingles)
        candidates = {i for h in sketch for i in index.get(h, [])}
        if any(jaccard(shingles, shingle_sets[i]) >= threshold for i in candidates):
            dropped += 1
            continue
        position = len(kept)
        kept.append(row)
        shingle_sets.append(shingles)
        for h in sketch:
            index.setdefault(h, []).append(position)
    return kept, dropped
