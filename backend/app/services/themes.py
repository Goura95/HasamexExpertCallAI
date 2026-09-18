from app.models.transcript import TranscriptSegment
from app.services.runtime_data import get_active_segments


# ============================================================
# EVIDENCE FORMATTER
# ============================================================

def evidence_dict(
    segment: TranscriptSegment,
) -> dict:
    """
    Convert an original transcript segment into the
    evidence format returned to the frontend.

    Quotes and timestamps always come directly from the
    transcript segment. Nothing is generated here.
    """

    return {
        "segment_id": segment.id,
        "expert": segment.expert,
        "role": segment.role,
        "market": segment.market,
        "speaker": segment.speaker,
        "timestamp": segment.timestamp,
        "quote": segment.text,
    }


# ============================================================
# THEME DEFINITIONS
# ============================================================

THEME_DEFINITIONS = [
    {
        "id": "theme-adoption",
        "theme": "Growing but uneven adoption",
        "description": (
            "All three experts describe robotic surgery "
            "adoption as increasing, while noting that "
            "access or adoption varies across hospitals."
        ),
        "evidence_ids": [
            # France
            "fr_002",

            # Germany
            "de_002",

            # United Kingdom
            "uk_002",
        ],
    },
    {
        "id": "theme-economics",
        "theme": "Economics and capital approval",
        "description": (
            "Capital budgets, cost, ROI, utilisation and "
            "the economic case are recurring considerations "
            "in purchasing decisions."
        ),
        "evidence_ids": [
            # France
            "fr_004",
            "fr_006",

            # Germany
            "de_004",
            "de_006",

            # United Kingdom
            "uk_006",
            "uk_008",
        ],
    },
    {
        "id": "theme-training",
        "theme": "Training and utilisation",
        "description": (
            "Experts connect training capacity with the "
            "ability to use a robotic system sufficiently."
        ),
        "evidence_ids": [
            # France
            "fr_008",

            # Germany
            "de_006",
            "de_008",

            # United Kingdom
            "uk_004",
        ],
    },
    {
        "id": "theme-volume",
        "theme": "Procedure volume and programme sustainability",
        "description": (
            "Procedure volume and system utilisation are "
            "linked to whether a robotic surgery programme "
            "can operate sustainably."
        ),
        "evidence_ids": [
            # France
            "fr_006",
            "fr_008",

            # Germany
            "de_004",

            # United Kingdom
            "uk_014",
        ],
    },
]


# ============================================================
# SEGMENT LOOKUP
# ============================================================

def get_segment_lookup() -> dict[str, TranscriptSegment]:
    """
    Build a lookup of expert transcript segments.

    Interviewer questions are excluded because they are not
    considered source evidence.
    """

    segments = get_active_segments()

    return {
        segment.id: segment
        for segment in segments
        if segment.speaker != "Interviewer"
    }


# ============================================================
# BUILD THEME EVIDENCE
# ============================================================

def build_theme_evidence(
    segment_ids: list[str],
) -> list[dict]:
    """
    Retrieve evidence using explicit transcript segment IDs.

    This prevents broad keyword matching from attaching
    unrelated transcript statements to a theme.
    """

    segment_lookup = get_segment_lookup()

    evidence = []

    for segment_id in segment_ids:
        segment = segment_lookup.get(segment_id)

        if segment is None:
            continue

        evidence.append(
            evidence_dict(segment)
        )

    return evidence


# ============================================================
# GET THEMES
# ============================================================

def get_themes() -> list[dict]:
    """
    Return evidence-grounded themes across the active
    transcript dataset.

    A theme is returned only when supporting evidence exists
    from at least two different markets.
    """

    results = []

    for definition in THEME_DEFINITIONS:
        evidence = build_theme_evidence(
            definition["evidence_ids"]
        )

        # ----------------------------------------------------
        # Require cross-market evidence
        # ----------------------------------------------------

        markets = {
            item["market"]
            for item in evidence
        }

        if len(markets) < 2:
            continue

        # ----------------------------------------------------
        # Return theme with original transcript evidence
        # ----------------------------------------------------

        results.append(
            {
                "id": definition["id"],
                "theme": definition["theme"],
                "description": definition["description"],
                "evidence": evidence,
            }
        )

    return results