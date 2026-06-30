"""Simple numerology / rashi / nakshatra calculation helpers.

These provide deterministic, formula-based approximations suitable for a
marriage-bureau biodata (Mulank, Bhagyank, and a Rashi/Nakshatra lookup based
on the birth date). They are NOT a substitute for a licensed astrologer but
give consistent, explainable values for matching purposes.
"""

RASHI_LIST = [
    "Mesh (Aries)", "Vrishabh (Taurus)", "Mithun (Gemini)", "Kark (Cancer)",
    "Singh (Leo)", "Kanya (Virgo)", "Tula (Libra)", "Vrishchik (Scorpio)",
    "Dhanu (Sagittarius)", "Makar (Capricorn)", "Kumbh (Aquarius)", "Meen (Pisces)",
]

NAKSHATRA_LIST = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta",
    "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]


def digit_sum(n: int) -> int:
    while n > 9:
        n = sum(int(d) for d in str(n))
    return n


def calculate_mulank(dob) -> int:
    """Mulank = reduced sum of the day of birth."""
    if not dob:
        return None
    return digit_sum(dob.day) or 9


def calculate_bhagyank(dob) -> int:
    """Bhagyank = reduced sum of the full date of birth (DDMMYYYY)."""
    if not dob:
        return None
    total = dob.day + dob.month + dob.year
    return digit_sum(total)


def estimate_rashi(dob) -> str:
    """Deterministic placeholder Rashi based on day-of-year, evenly split
    into 12 segments approximating zodiac sun-sign date ranges."""
    if not dob:
        return None
    sign_ranges = [
        (3, 21, 4, 19), (4, 20, 5, 20), (5, 21, 6, 20), (6, 21, 7, 22),
        (7, 23, 8, 22), (8, 23, 9, 22), (9, 23, 10, 22), (10, 23, 11, 21),
        (11, 22, 12, 21), (12, 22, 1, 19), (1, 20, 2, 18), (2, 19, 3, 20),
    ]
    m, d = dob.month, dob.day
    for idx, (sm, sd, em, ed) in enumerate(sign_ranges):
        if (m == sm and d >= sd) or (m == em and d <= ed):
            return RASHI_LIST[idx]
    return RASHI_LIST[0]


def estimate_nakshatra(dob) -> str:
    """Deterministic placeholder using day-of-year modulo 27 nakshatras."""
    if not dob:
        return None
    day_of_year = dob.timetuple().tm_yday
    return NAKSHATRA_LIST[day_of_year % 27]
