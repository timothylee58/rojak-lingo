import re
import unicodedata
import zlib

# CJK characters carry no spaces, so each one is its own token; otherwise n-grams
# over mixed English/Mandarin text would collapse into a few giant tokens.
_TOKEN = re.compile(r"[一-鿿]|[^\s\W一-鿿]+")


def tokens(text: str) -> list[str]:
    return _TOKEN.findall(unicodedata.normalize("NFKC", text).lower())


def norm(text: str) -> str:
    return " ".join(tokens(text))


def ngrams(toks: list[str], n: int) -> set[tuple[str, ...]]:
    if not toks:
        return set()
    if len(toks) <= n:
        return {tuple(toks)}
    return {tuple(toks[i : i + n]) for i in range(len(toks) - n + 1)}


def stable_hash(gram: tuple[str, ...]) -> int:
    # builtin hash() is salted per process, which would make dedupe non-reproducible
    return zlib.crc32(" ".join(gram).encode("utf-8"))


def jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)
