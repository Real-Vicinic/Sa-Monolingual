import numpy as np

import process
from aws.generate_pairs import build
from config import LANGS, SOURCES


def test_normalize_strips_urls_and_whitespace():
    out = process.normalize("Visit  https://example.com\u00a0now\u200b please")
    assert "http" not in out
    assert "  " not in out
    assert out == "Visit now please"


def test_dedup_key_ignores_case_and_punctuation():
    a = process.dedup_key("Hello, World!")
    b = process.dedup_key("hello   world")
    assert a == b


def test_hash_is_stable():
    assert process.hash64("abc") == process.hash64("abc")
    assert process.hash64("abc") != process.hash64("abd")


def test_split_sentences():
    parts = list(process.split_sentences("Yebo ngiyaphila. Wena unjani?\nNgiyabonga kakhulu."))
    assert len(parts) == 3


def test_quality_rejects_bad_input():
    assert not process.quality_ok("too short")
    assert not process.quality_ok("word " * 200)
    assert not process.quality_ok("<div>this is html markup content</div>")
    assert not process.quality_ok("1234 5678 9012 3456 7890 1234 5678")
    assert not process.quality_ok("spam spam spam spam spam spam spam spam spam")


def test_quality_accepts_normal_sentence():
    assert process.quality_ok("Ngiyabonga kakhulu ngosizo lwakho namuhla ekuseni")


def test_exclusion_lookup():
    arr = np.array(sorted([5, 10, 99]), dtype=np.uint64)
    assert process.in_exclusion(arr, 10)
    assert not process.in_exclusion(arr, 11)
    assert not process.in_exclusion(np.array([], dtype=np.uint64), 10)


def test_every_language_has_labels_and_a_source():
    from config import GLOTLID, LANG_NAMES

    for lang in LANGS:
        assert lang in GLOTLID and lang in LANG_NAMES
        assert any(lang in s["configs"] for s in SOURCES)


def test_pairs_cover_all_sources():
    data = build(["zu"])
    assert data["langs"] == ["zu"]
    assert all(p["lang"] == "zu" for p in data["pairs"])
    assert len(data["pairs"]) == sum("zu" in s["configs"] for s in SOURCES)
