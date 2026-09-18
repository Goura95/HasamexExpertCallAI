from app.models.transcript import TranscriptSegment
from app.services.runtime_data import get_active_segments


def evidence_dict(
    segment: TranscriptSegment,
) -> dict:
    return {
        "segment_id": segment.id,
        "expert": segment.expert,
        "role": segment.role,
        "market": segment.market,
        "speaker": segment.speaker,
        "timestamp": segment.timestamp,
        "quote": segment.text,
    }


def find_segments(
    keywords: list[str],
    limit: int = 6,
) -> list[TranscriptSegment]:
    results = []

    for segment in get_active_segments():
        if segment.speaker == "Interviewer":
            continue

        text = segment.text.lower()

        if any(
            keyword in text
            for keyword in keywords
        ):
            results.append(segment)

    return results[:limit]


def get_differences() -> list[dict]:
    definitions = [
        {
            "id": "difference-outlook",
            "topic": "Different expectations for future growth",
            "summary": (
                "The experts all expect continued growth, "
                "but their stated expectations differ. France "
                "describes steady rather than explosive growth, "
                "Germany describes gradual growth, while the UK "
                "expert expresses a more positive view and says "
                "growth could accelerate in some areas."
            ),
            "keywords": [
                "expect",
                "growth",
                "accelerate",
                "annually",
            ],
        },
        {
            "id": "difference-economics",
            "topic": "Different emphasis on the purchasing decision",
            "summary": (
                "France and Germany place strong emphasis on "
                "the economic case and utilisation. The UK expert "
                "describes economics as balanced with clinical "
                "strategy and other organisational considerations."
            ),
            "keywords": [
                "economic",
                "economics",
                "roi",
                "finance",
                "clinical strategy",
                "outcomes",
            ],
        },
        {
            "id": "difference-timeline",
            "topic": "Purchase timelines vary by market context",
            "summary": (
                "The experts report different typical purchasing "
                "windows and emphasise that capital or budget "
                "cycles can extend the process."
            ),
            "keywords": [
                "months",
                "purchase",
                "capital cycle",
                "budget cycle",
            ],
        },
    ]

    results = []

    for definition in definitions:
        segments = find_segments(
            definition["keywords"]
        )

        evidence = [
            evidence_dict(segment)
            for segment in segments
        ]

        markets = {
            item["market"]
            for item in evidence
        }

        if len(markets) < 2:
            continue

        results.append(
            {
                "id": definition["id"],
                "topic": definition["topic"],
                "summary": definition["summary"],
                "evidence": evidence,
            }
        )

    return results