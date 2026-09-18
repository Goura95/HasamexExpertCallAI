import re
from pathlib import Path

from app.models.transcript import (
    Expert,
    TranscriptSegment,
)


# ============================================================
# HEADER PATTERNS
# ============================================================

HEADER_EXPERT = re.compile(
    r"^Expert:\s*(.+)$",
    re.IGNORECASE,
)

HEADER_ROLE = re.compile(
    r"^Role:\s*(.+)$",
    re.IGNORECASE,
)

HEADER_MARKET = re.compile(
    r"^Market:\s*(.+)$",
    re.IGNORECASE,
)


# ============================================================
# TRANSCRIPT SEGMENT PATTERN
# ============================================================

SEGMENT_PATTERN = re.compile(
    r"^(\d{2}:\d{2})\s+([^:]+):\s*(.+)$"
)


# ============================================================
# REQUIRED HASAMEX MARKETS
# ============================================================

REQUIRED_MARKETS = {
    "France",
    "Germany",
    "United Kingdom",
}


# ============================================================
# PARSE TRANSCRIPT
# ============================================================

def parse_transcript_file(
    filename: str,
    content: bytes,
    transcript_number: int,
) -> tuple[Expert, list[TranscriptSegment]]:
    """
    Parse a .txt expert transcript.

    Expected format:

    Expert: Dr. Jean Martin
    Role: Head of Urology
    Market: France

    00:00 Interviewer: ...
    00:18 Dr. Jean Martin: ...

    The parser preserves:
    - expert
    - role
    - market
    - speaker
    - timestamp
    - original transcript text
    """

    text = content.decode(
        "utf-8",
        errors="replace",
    )

    lines = [
        line.strip()
        for line in text.splitlines()
    ]

    expert_name = None
    role = None
    market = None

    # --------------------------------------------------------
    # Read metadata from the header
    # --------------------------------------------------------

    for line in lines[:10]:

        match = HEADER_EXPERT.match(line)

        if match:
            expert_name = match.group(1).strip()
            continue

        match = HEADER_ROLE.match(line)

        if match:
            role = match.group(1).strip()
            continue

        match = HEADER_MARKET.match(line)

        if match:
            market = match.group(1).strip()
            continue

    # --------------------------------------------------------
    # Validate metadata
    # --------------------------------------------------------

    if not expert_name:
        raise ValueError(
            f"{filename}: missing 'Expert:' header."
        )

    if not role:
        raise ValueError(
            f"{filename}: missing 'Role:' header."
        )

    if not market:
        raise ValueError(
            f"{filename}: missing 'Market:' header."
        )

    # --------------------------------------------------------
    # Parse timestamped transcript segments
    # --------------------------------------------------------

    segments = []

    # Segment ID prefix is based on the market.
    prefix = {
        "France": "fr",
        "Germany": "de",
        "United Kingdom": "uk",
    }.get(
        market,
        f"t{transcript_number}",
    )

    for line in lines:

        match = SEGMENT_PATTERN.match(line)

        if not match:
            continue

        timestamp = match.group(1)
        speaker = match.group(2).strip()
        segment_text = match.group(3).strip()

        if not segment_text:
            continue

        segment_id = (
            f"{prefix}_{len(segments) + 1:03d}"
        )

        segments.append(
            TranscriptSegment(
                id=segment_id,
                expert=expert_name,
                role=role,
                market=market,
                speaker=speaker,
                timestamp=timestamp,
                text=segment_text,
            )
        )

    # --------------------------------------------------------
    # Ensure transcript contains timestamped segments
    # --------------------------------------------------------

    if not segments:
        raise ValueError(
            f"{filename}: no timestamped transcript "
            "segments were found."
        )

    # --------------------------------------------------------
    # Build expert metadata
    # --------------------------------------------------------

    expert = Expert(
        name=expert_name,
        role=role,
        market=market,
        transcript_id=Path(filename).stem,
    )

    return expert, segments


# ============================================================
# VALIDATE UPLOADED DATASET
# ============================================================

def validate_uploaded_dataset(
    experts: list[Expert],
    segments: list[TranscriptSegment],
) -> None:
    """
    Validate the uploaded Hasamex transcript dataset.

    Requirements:
    - Exactly 3 expert transcripts
    - France, Germany and United Kingdom must be represented
    - No unexpected markets
    - Every expert must have transcript segments
    - Every required market must have expert evidence
    """

    # --------------------------------------------------------
    # Exactly three experts
    # --------------------------------------------------------

    if len(experts) != 3:
        raise ValueError(
            "Exactly 3 expert transcripts are required."
        )

    # --------------------------------------------------------
    # Validate markets
    # --------------------------------------------------------

    markets = {
        expert.market.strip()
        for expert in experts
    }

    missing_markets = (
        REQUIRED_MARKETS - markets
    )

    unexpected_markets = (
        markets - REQUIRED_MARKETS
    )

    if missing_markets or unexpected_markets:

        message_parts = [
            "The uploaded dataset must contain "
            "France, Germany and United Kingdom."
        ]

        if missing_markets:
            message_parts.append(
                "Missing markets: "
                + ", ".join(
                    sorted(missing_markets)
                )
                + "."
            )

        if unexpected_markets:
            message_parts.append(
                "Unexpected markets: "
                + ", ".join(
                    sorted(unexpected_markets)
                )
                + "."
            )

        raise ValueError(
            " ".join(message_parts)
        )

    # --------------------------------------------------------
    # Ensure every expert has transcript segments
    # --------------------------------------------------------

    for expert in experts:

        expert_segment_count = sum(
            1
            for segment in segments
            if segment.expert == expert.name
        )

        if expert_segment_count == 0:
            raise ValueError(
                f"No transcript segments found for "
                f"{expert.name}."
            )

    # --------------------------------------------------------
    # Ensure every required market has expert evidence
    # --------------------------------------------------------

    segment_markets = {
        segment.market.strip()
        for segment in segments
        if segment.speaker != "Interviewer"
    }

    missing_evidence_markets = (
        REQUIRED_MARKETS - segment_markets
    )

    unexpected_evidence_markets = (
        segment_markets - REQUIRED_MARKETS
    )

    if (
        missing_evidence_markets
        or unexpected_evidence_markets
    ):

        message_parts = [
            "Transcript evidence must contain expert "
            "statements from France, Germany and "
            "United Kingdom."
        ]

        if missing_evidence_markets:
            message_parts.append(
                "Missing evidence markets: "
                + ", ".join(
                    sorted(missing_evidence_markets)
                )
                + "."
            )

        if unexpected_evidence_markets:
            message_parts.append(
                "Unexpected evidence markets: "
                + ", ".join(
                    sorted(unexpected_evidence_markets)
                )
                + "."
            )

        raise ValueError(
            " ".join(message_parts)
        )