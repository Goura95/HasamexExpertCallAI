from app.models.transcript import TranscriptSegment
from app.services.runtime_data import get_active_segments


INTERVIEW_GUIDE = [
    {
        "id": "q1",
        "question": (
            "How would you describe current adoption of robotic "
            "surgery in your market?"
        ),
    },
    {
        "id": "q2",
        "question": "What are the main barriers to adoption?",
    },
    {
        "id": "q3",
        "question": (
            "How important are hospital budgets and ROI in "
            "purchasing decisions?"
        ),
    },
    {
        "id": "q4",
        "question": (
            "How important are surgeon training and clinical "
            "outcomes?"
        ),
    },
    {
        "id": "q5",
        "question": (
            "What adoption trend do you expect over the next "
            "3–5 years?"
        ),
    },
    {
        "id": "q6",
        "question": (
            "What is the typical hospital decision-making "
            "timeline for purchasing a new robotic system?"
        ),
    },
]


GUIDE_EVIDENCE_MAP = {
    "q1": {
        "France": ["fr_002"],
        "Germany": ["de_002"],
        "United Kingdom": ["uk_002"],
    },
    "q2": {
        "France": ["fr_004"],
        "Germany": ["de_004"],
        "United Kingdom": ["uk_004"],
    },
    "q3": {
        "France": ["fr_006"],
        "Germany": ["de_006"],
        "United Kingdom": ["uk_006", "uk_008"],
    },
    "q4": {
        "France": ["fr_008", "fr_010"],
        "Germany": ["de_006"],
        "United Kingdom": ["uk_004", "uk_006"],
    },
    "q5": {
        "France": ["fr_012"],
        "Germany": ["de_012"],
        "United Kingdom": ["uk_010"],
    },
    "q6": {
        "France": ["fr_014"],
        "Germany": ["de_014"],
        "United Kingdom": ["uk_012"],
    },
}


def get_segment_lookup() -> dict[str, TranscriptSegment]:
    """
    Build a lookup from the currently active transcript dataset.

    This ensures the Interview Guide uses the same active
    dataset as the rest of the application.
    """
    segments = get_active_segments()

    return {
        segment.id: segment
        for segment in segments
    }


def build_evidence(
    segment_ids: list[str],
) -> list[dict]:
    """
    Return only the exact transcript segments explicitly
    mapped to the interview-guide question.

    No semantic retrieval is performed here.
    The guide therefore cannot accidentally include
    evidence belonging to another question.
    """
    segment_lookup = get_segment_lookup()

    evidence = []

    for segment_id in segment_ids:
        segment = segment_lookup.get(segment_id)

        if segment is None:
            continue

        evidence.append(
            {
                "segment_id": segment.id,
                "expert": segment.expert,
                "role": segment.role,
                "market": segment.market,
                "speaker": segment.speaker,
                "timestamp": segment.timestamp,
                "quote": segment.text,
            }
        )

    return evidence


def get_guide_data() -> list[dict]:
    """
    Build the complete Interview Guide using the active
    transcript dataset.
    """
    guide_results = []

    markets = [
        "France",
        "Germany",
        "United Kingdom",
    ]

    for guide_item in INTERVIEW_GUIDE:
        question_id = guide_item["id"]

        expert_answers = []

        for market in markets:
            segment_ids = GUIDE_EVIDENCE_MAP[
                question_id
            ][market]

            evidence = build_evidence(
                segment_ids
            )

            expert_answers.append(
                {
                    "market": market,
                    "evidence": evidence,
                }
            )

        guide_results.append(
            {
                "id": question_id,
                "question": guide_item["question"],
                "answers": expert_answers,
            }
        )

    return guide_results