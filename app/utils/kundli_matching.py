"""Kundli Matching Engine.

Implements a simplified Ashtakoot (8-fold) Gun Milan scoring system based on
Rashi and Nakshatra of the two profiles, plus a Manglik compatibility check.
Total score out of 36, like traditional Gun Milan.
"""
from app.utils.astrology import RASHI_LIST, NAKSHATRA_LIST

GUNS = [
    ("Varna", 1), ("Vashya", 2), ("Tara", 3), ("Yoni", 4),
    ("Graha Maitri", 5), ("Gana", 6), ("Bhakoot", 7), ("Nadi", 8),
]
MAX_SCORE = sum(w for _, w in GUNS)  # 36


def _index_or(value, lst):
    try:
        return lst.index(value)
    except (ValueError, TypeError):
        return None


def calculate_gun_milan(profile_a, profile_b):
    """Returns dict with per-gun scores, total, percentage and manglik status."""
    rashi_a = _index_or(profile_a.rashi, RASHI_LIST)
    rashi_b = _index_or(profile_b.rashi, RASHI_LIST)
    nak_a = _index_or(profile_a.nakshatra, NAKSHATRA_LIST)
    nak_b = _index_or(profile_b.nakshatra, NAKSHATRA_LIST)

    scores = {}

    # Deterministic pseudo-scoring derived from the difference between
    # rashi/nakshatra indices -- gives consistent, explainable results.
    def score_from_diff(diff, max_points, mod):
        if diff is None:
            return round(max_points * 0.5, 1)
        diff = diff % mod
        # closer signs score higher, opposite-ish score lower, using a smooth curve
        ratio = 1 - (abs(diff - mod / 2) / (mod / 2))
        return round(max_points * max(0.2, ratio), 1)

    rashi_diff = None if rashi_a is None or rashi_b is None else abs(rashi_a - rashi_b)
    nak_diff = None if nak_a is None or nak_b is None else abs(nak_a - nak_b)

    scores["Varna"] = score_from_diff(rashi_diff, 1, 12)
    scores["Vashya"] = score_from_diff(rashi_diff, 2, 12)
    scores["Tara"] = score_from_diff(nak_diff, 3, 27)
    scores["Yoni"] = score_from_diff(nak_diff, 4, 27)
    scores["Graha Maitri"] = score_from_diff(rashi_diff, 5, 12)
    scores["Gana"] = score_from_diff(nak_diff, 6, 27)
    scores["Bhakoot"] = score_from_diff(rashi_diff, 7, 12)
    scores["Nadi"] = score_from_diff(nak_diff, 8, 27)

    total = round(sum(scores.values()), 1)
    percentage = round((total / MAX_SCORE) * 100, 1)

    manglik_a = (profile_a.manglik or "No")
    manglik_b = (profile_b.manglik or "No")
    if manglik_a == manglik_b:
        manglik_status = "Compatible"
    elif "Anshik" in (manglik_a, manglik_b):
        manglik_status = "Partially Compatible"
    else:
        manglik_status = "Caution: Manglik Dosh Mismatch"

    verdict = "Excellent Match" if percentage >= 75 else \
        "Good Match" if percentage >= 60 else \
        "Average Match" if percentage >= 40 else "Not Recommended"

    return {
        "scores": scores,
        "total": total,
        "max_score": MAX_SCORE,
        "percentage": percentage,
        "manglik_status": manglik_status,
        "verdict": verdict,
    }


def find_best_matches(profile, candidates, limit=10):
    """candidates: iterable of Profile objects of opposite gender.
    Returns list of (profile, match_result) sorted by percentage desc."""
    results = []
    for c in candidates:
        if c.id == profile.id:
            continue
        result = calculate_gun_milan(profile, c)
        results.append((c, result))
    results.sort(key=lambda x: x[1]["percentage"], reverse=True)
    return results[:limit]
