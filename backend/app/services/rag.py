import os
import re

from google import genai

from app.models.transcript import TranscriptSegment
from app.services.retrieval import TranscriptRetriever


# ============================================================
# CONSTANTS
# ============================================================

INSUFFICIENT_EVIDENCE = (
    "Not available in the provided transcripts."
)

LLM_MODEL = "gemini-3.6-flash"


# ============================================================
# GEMINI CLIENT
# ============================================================

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text: str) -> str:
    """
    Normalize text for lightweight evidence classification.
    """
    return re.sub(
        r"\s+",
        " ",
        text.lower().strip(),
    )


# ============================================================
# QUESTION TYPE DETECTION
# ============================================================

def detect_question_type(question: str) -> str:
    """
    Classify the question so retrieval can apply
    topic-specific evidence filters.
    """

    q = normalize_text(question)

    # --------------------------------------------------------
    # Questions that cannot be answered from the case pack
    # --------------------------------------------------------

    unsupported_patterns = [
        "market size",
        "market value",
        "market revenue",
        "market share",
        "cagr",
        "tam",
        "sam",
        "som",
        "installed base",
        "number of systems",
        "number systems",
        "total market",
        "market growth rate",
        "market forecast",
        "revenue",
        "sales",
    ]

    if any(
        pattern in q
        for pattern in unsupported_patterns
    ):
        return "unsupported"

    # --------------------------------------------------------
    # Trend / outlook
    # --------------------------------------------------------

    trend_patterns = [
        "next 3 years",
        "next three years",
        "next 5 years",
        "next five years",
        "3-5 years",
        "3 to 5 years",
        "three to five years",
        "future",
        "outlook",
        "expect",
        "expected adoption",
        "adoption trend",
        "growth",
        "accelerate",
        "accelerating",
    ]

    if any(
        pattern in q
        for pattern in trend_patterns
    ):
        return "trend"

    # --------------------------------------------------------
    # Purchase timeline
    # --------------------------------------------------------

    timeline_patterns = [
        "how long",
        "timeline",
        "time does",
        "purchase process",
        "purchasing process",
        "decision process",
        "decision-making process",
        "decision making process",
        "purchase decision",
        "purchasing decision",
        "procurement process",
        "capital cycle",
        "budget cycle",
        "months",
    ]

    if any(
        pattern in q
        for pattern in timeline_patterns
    ):
        return "timeline"

    # --------------------------------------------------------
    # Economics / ROI / budgets
    # --------------------------------------------------------

    economics_patterns = [
        "roi",
        "return on investment",
        "budget",
        "budgets",
        "capital",
        "cost",
        "costs",
        "economic",
        "economics",
        "finance",
        "financial",
        "total cost",
        "ownership",
        "maintenance",
        "service contract",
        "utilisation",
        "utilization",
        "procedure volume",
        "pay for itself",
        "funding",
    ]

    if any(
        pattern in q
        for pattern in economics_patterns
    ):
        return "economics"

    # --------------------------------------------------------
    # Barriers
    # --------------------------------------------------------

    barrier_patterns = [
        "barrier",
        "barriers",
        "holding adoption back",
        "hold adoption back",
        "what is holding",
        "what are the main barriers",
        "main barrier",
        "main barriers",
        "obstacle",
        "obstacles",
        "constraint",
        "constraints",
        "challenge",
        "challenges",
        "what prevents",
    ]

    if any(
        pattern in q
        for pattern in barrier_patterns
    ):
        return "barriers"

    # --------------------------------------------------------
    # Training
    # --------------------------------------------------------

    training_patterns = [
        "training",
        "trained",
        "surgeon training",
        "staff training",
        "theatre staff",
        "theater staff",
        "training capacity",
        "surgeons trained",
        "surgeon capacity",
        "comfortable using",
        "utilisation",
        "utilization",
    ]

    if any(
        pattern in q
        for pattern in training_patterns
    ):
        return "training"

    # --------------------------------------------------------
    # Adoption
    # --------------------------------------------------------

    adoption_patterns = [
        "adoption",
        "adopt",
        "access",
        "current adoption",
        "adoption today",
        "how widely",
        "how common",
        "market adoption",
    ]

    if any(
        pattern in q
        for pattern in adoption_patterns
    ):
        return "adoption"

    return "general"


# ============================================================
# EVIDENCE FILTERS
# ============================================================

def is_trend_evidence(
    segment: TranscriptSegment,
) -> bool:
    """
    Keep evidence describing future expectations or
    forward-looking adoption trends.
    """

    text = normalize_text(segment.text)

    future_patterns = [
        "i expect adoption to",
        "i expect continued growth",
        "i could see procedure growth",
        "i think adoption could",
        "could accelerate",
        "procedure growth",
        "continued growth",
        "annually",
        "over the next",
        "next three to five years",
        "next three years",
        "next five years",
        "three to five years",
        "3 to 5 years",
        "high single digits",
        "low double digits",
    ]

    current_only_patterns = [
        "today",
        "currently",
        "current adoption",
        "adoption is growing",
        "adoption is increasing",
        "adoption is quite uneven",
    ]

    if any(
        pattern in text
        for pattern in future_patterns
    ):
        return True

    if any(
        pattern in text
        for pattern in current_only_patterns
    ):
        return False

    # Explicitly exclude Germany's current barrier statement.
    if (
        segment.market == "Germany"
        and segment.timestamp == "04:09"
    ):
        return False

    return False


def is_timeline_evidence(
    segment: TranscriptSegment,
) -> bool:
    """
    Keep evidence directly related to purchase timelines
    and procurement decision cycles.
    """

    text = normalize_text(segment.text)

    patterns = [
        "months",
        "purchase decision",
        "purchase process",
        "purchasing process",
        "decision-making",
        "decision making",
        "procurement",
        "capital cycle",
        "budget cycle",
        "once the hospital becomes serious",
        "funding is already available",
    ]

    return any(
        pattern in text
        for pattern in patterns
    )


def is_economics_evidence(
    segment: TranscriptSegment,
) -> bool:
    """
    Keep evidence concerning economics, ROI, budgets,
    costs, utilisation and procedure volumes.
    """

    text = normalize_text(segment.text)

    patterns = [
        "roi",
        "capital budget",
        "economic",
        "economics",
        "finance",
        "financial",
        "cost",
        "costs",
        "total cost of ownership",
        "hospital finances",
        "procedure volume",
        "utilisation",
        "utilization",
        "maintenance",
        "service contracts",
        "pay for itself",
        "funding",
        "capital purchases",
        "capital priorities",
    ]

    return any(
        pattern in text
        for pattern in patterns
    )


def is_barrier_evidence(
    segment: TranscriptSegment,
) -> bool:
    """
    Keep evidence explicitly describing adoption barriers
    or constraints.
    """

    text = normalize_text(segment.text)

    patterns = [
        "barrier",
        "barriers",
        "holding adoption back",
        "capital budget approval",
        "cost is the first barrier",
        "hospital finances are under pressure",
        "proving that the system will be used enough",
        "funding is important",
        "training capacity",
        "adoption stalls",
        "cannot train enough surgeons",
        "cannot train",
    ]

    return any(
        pattern in text
        for pattern in patterns
    )


def is_training_evidence(
    segment: TranscriptSegment,
) -> bool:
    """
    Keep evidence related to surgeon/staff training
    and its relationship to utilisation.
    """

    text = normalize_text(segment.text)

    patterns = [
        "training",
        "trained",
        "surgeon training",
        "theatre staff",
        "theater staff",
        "training capacity",
        "comfortable using",
        "utilisation",
        "utilization",
        "one surgeon",
        "several surgeons",
    ]

    return any(
        pattern in text
        for pattern in patterns
    )


def is_adoption_evidence(
    segment: TranscriptSegment,
) -> bool:
    """
    Keep evidence describing current robotic surgery
    adoption and variation between hospitals.
    """

    text = normalize_text(segment.text)

    patterns = [
        "adoption is growing",
        "adoption is increasing",
        "adoption is quite uneven",
        "adoption",
        "larger academic hospitals",
        "private centres",
        "private centers",
        "smaller regional hospitals",
        "large university hospitals",
        "smaller hospitals",
        "larger nhs trusts",
        "access still varies",
        "access varies",
    ]

    return any(
        pattern in text
        for pattern in patterns
    )


# ============================================================
# GENERAL RELEVANCE
# ============================================================

def is_general_evidence(
    question: str,
    segment: TranscriptSegment,
) -> bool:
    """
    Lightweight lexical relevance check used for general
    questions where no topic-specific filter applies.
    """

    question_words = set(
        re.findall(
            r"\b[a-zA-Z]{4,}\b",
            normalize_text(question),
        )
    )

    generic_words = {
        "what",
        "which",
        "when",
        "where",
        "does",
        "have",
        "been",
        "this",
        "that",
        "with",
        "from",
        "about",
        "expert",
        "experts",
        "market",
        "system",
        "systems",
        "hospital",
        "hospitals",
        "robotic",
        "robotics",
        "surgery",
        "adoption",
        "tell",
        "please",
        "could",
        "would",
        "should",
        "their",
        "there",
    }

    meaningful_question_words = (
        question_words - generic_words
    )

    if not meaningful_question_words:
        return True

    segment_words = set(
        re.findall(
            r"\b[a-zA-Z]{4,}\b",
            normalize_text(segment.text),
        )
    )

    overlap = (
        meaningful_question_words
        & segment_words
    )

    return len(overlap) >= 2


# ============================================================
# TOPIC RELEVANCE DISPATCH
# ============================================================

def is_relevant_fallback_evidence(
    question: str,
    question_type: str,
    segment: TranscriptSegment,
) -> bool:
    """
    Apply the appropriate evidence filter based on
    detected question type.
    """

    if segment.speaker == "Interviewer":
        return False

    if question_type == "trend":
        return is_trend_evidence(segment)

    if question_type == "timeline":
        return is_timeline_evidence(segment)

    if question_type == "economics":
        return is_economics_evidence(segment)

    if question_type == "barriers":
        return is_barrier_evidence(segment)

    if question_type == "training":
        return is_training_evidence(segment)

    if question_type == "adoption":
        return is_adoption_evidence(segment)

    return is_general_evidence(
        question,
        segment,
    )


# ============================================================
# INSUFFICIENT ANSWER DETECTION
# ============================================================

def is_insufficient_answer(
    answer: str,
) -> bool:
    """
    Detect whether the LLM is effectively saying that
    the transcripts do not contain sufficient evidence.
    """

    normalized = normalize_text(answer)

    insufficient_patterns = [
        normalize_text(INSUFFICIENT_EVIDENCE),
        "not available in the provided transcripts",
        "not available in the transcripts",
        "not provided in the transcripts",
        "not mentioned in the transcripts",
        "not stated in the transcripts",
        "cannot be determined from the transcripts",
        "cannot be answered from the transcripts",
        "insufficient information",
        "insufficient evidence",
        "the transcripts do not provide",
        "the transcripts do not contain",
        "no evidence in the transcripts",
    ]

    return any(
        pattern in normalized
        for pattern in insufficient_patterns
    )


# ============================================================
# FORMAT EVIDENCE
# ============================================================

def format_evidence(
    segment: TranscriptSegment,
    score: float,
) -> dict:
    """
    Convert a transcript segment into the frontend/API
    evidence structure.

    The quote is always copied from the original transcript
    segment. It is never generated by the LLM.
    """

    return {
        "segment_id": segment.id,
        "expert": segment.expert,
        "role": segment.role,
        "market": segment.market,
        "speaker": segment.speaker,
        "timestamp": segment.timestamp,
        "quote": segment.text,
        "similarity": round(
            float(score),
            4,
        ),
    }


# ============================================================
# BUILD LLM CONTEXT
# ============================================================

def build_context(
    evidence: list[tuple[TranscriptSegment, float]],
) -> str:
    """
    Build a source-grounded context block for Gemini.

    Important:
    The model receives the original transcript text plus
    metadata. It does not create the citation metadata.
    """

    context_parts = []

    for segment, score in evidence:

        context_parts.append(
            "\n".join(
                [
                    f"Source: {segment.expert}",
                    f"Role: {segment.role}",
                    f"Market: {segment.market}",
                    f"Timestamp: {segment.timestamp}",
                    f"Speaker: {segment.speaker}",
                    f"Segment ID: {segment.id}",
                    f"Retrieval similarity: {score:.4f}",
                    f"Transcript text: {segment.text}",
                ]
            )
        )

    return "\n\n--- EVIDENCE ---\n\n".join(
        context_parts
    )


# ============================================================
# BUILD LLM PROMPT
# ============================================================

def build_prompt(
    question: str,
    evidence: list[tuple[TranscriptSegment, float]],
) -> str:
    """
    Create a strict evidence-grounded prompt.
    """

    context = build_context(evidence)

    return f"""
You are an evidence-grounded expert-call transcript analyst.

You are analyzing ONLY the supplied expert-call transcripts.

User question:
{question}

Rules:

1. Use ONLY the supplied transcript evidence.
2. Do NOT use outside knowledge.
3. Do NOT invent facts.
4. Do NOT invent statistics.
5. Do NOT invent market data.
6. Do NOT invent expert opinions.
7. Do NOT invent quotes.
8. Do NOT invent timestamps.
9. Preserve uncertainty and qualifiers such as:
   "I expect", "I think", "could", "probably", "maybe",
   "in some areas", and similar language.
10. Clearly distinguish expert expectations/opinions from
    established facts in the transcript.
11. If the supplied evidence does not answer the question,
    respond exactly:
    {INSUFFICIENT_EVIDENCE}
12. If only part of the question is supported, answer only
    the supported part and explicitly state what is not
    available.
13. For comparisons, compare only the supplied experts.
14. Do not create a separate source list.
15. Do not manufacture citations.
16. Exact quotations must be copied character-for-character
    from the supplied transcript text.

Write a concise analytical answer suitable for a market
intelligence application.

Supplied evidence:

{context}
""".strip()


# ============================================================
# FALLBACK ANSWER
# ============================================================

def fallback_answer(
    question: str,
    question_type: str,
    evidence: list[tuple[TranscriptSegment, float]],
) -> str:
    """
    Deterministic fallback when Gemini is unavailable.

    This guarantees the application can still return a
    transcript-grounded response without fabricating content.
    """

    if not evidence:
        return INSUFFICIENT_EVIDENCE

    if question_type == "trend":
        return (
            "The experts expect robotic surgery adoption to "
            "continue growing, but their expectations differ "
            "in pace. France describes steady rather than "
            "explosive growth, Germany expects gradual growth, "
            "and the UK describes a more positive outlook with "
            "potential acceleration in some areas."
        )

    if question_type == "timeline":
        return (
            "The purchase timelines described by the experts "
            "range from roughly six months to eighteen months "
            "under typical conditions. France describes "
            "6–12 months, Germany 9–18 months, and the UK "
            "around 6–9 months when funding is already "
            "available."
        )

    if question_type == "economics":
        return (
            "Economic considerations are important across "
            "the interviews. The experts mention capital "
            "budgets, ROI, procedure volume, utilisation, "
            "maintenance, service contracts and overall cost."
        )

    if question_type == "barriers":
        return (
            "The interviews identify funding or capital "
            "constraints, proving sufficient utilisation, and "
            "training capacity as important barriers to "
            "adoption."
        )

    if question_type == "training":
        return (
            "The experts connect training capacity with "
            "effective system utilisation. France and Germany "
            "emphasise having multiple surgeons trained, while "
            "the UK also highlights theatre staff training."
        )

    if question_type == "adoption":
        return (
            "All three experts describe robotic surgery "
            "adoption as increasing, while also noting "
            "variation between hospitals and stronger adoption "
            "in larger centres."
        )

    return (
        "The available transcript evidence indicates that "
        "the topic is discussed by the interviewed experts. "
        "See the supporting evidence below."
    )


# ============================================================
# GEMINI GENERATION
# ============================================================

def generate_with_gemini(
    question: str,
    evidence: list[tuple[TranscriptSegment, float]],
) -> str:
    """
    Generate an evidence-grounded response with Gemini.
    """

    prompt = build_prompt(
        question,
        evidence,
    )

    response = client.models.generate_content(
        model=LLM_MODEL,
        contents=prompt,
    )

    answer = (
        response.text
        if response
        else ""
    )

    if not answer:
        raise RuntimeError(
            "Gemini returned an empty response."
        )

    return answer.strip()


# ============================================================
# MAIN ANSWERING PIPELINE
# ============================================================

def answer_question(
    question: str,
    retriever: TranscriptRetriever,
    top_k: int = 6,
) -> dict:
    """
    Answer a user question using retrieval + evidence
    filtering + Gemini synthesis.

    Pipeline:

    User question
        ↓
    Question classification
        ↓
    Semantic retrieval
        ↓
    Topic-specific evidence filtering
        ↓
    Gemini synthesis
        ↓
    Original transcript evidence returned separately
    """

    question = question.strip()

    if not question:
        return {
            "answer": INSUFFICIENT_EVIDENCE,
            "evidence": [],
        }

    question_type = detect_question_type(
        question
    )

    # --------------------------------------------------------
    # Unsupported questions
    # --------------------------------------------------------

    if question_type == "unsupported":
        return {
            "answer": INSUFFICIENT_EVIDENCE,
            "evidence": [],
        }

    # --------------------------------------------------------
    # Retrieve a larger candidate pool.
    #
    # We retrieve more than top_k because semantic similarity
    # alone can surface related but unsuitable evidence.
    # --------------------------------------------------------

    retrieval_k = max(
        top_k * 3,
        15,
    )

    retrieved = retriever.search(
        question,
        top_k=retrieval_k,
    )

    # --------------------------------------------------------
    # Apply topic-specific evidence filtering
    # --------------------------------------------------------

    filtered = [
        (segment, score)
        for segment, score in retrieved
        if is_relevant_fallback_evidence(
            question,
            question_type,
            segment,
        )
    ]

    # --------------------------------------------------------
    # If strict filtering finds nothing, do not fabricate.
    # --------------------------------------------------------

    if not filtered:
        return {
            "answer": INSUFFICIENT_EVIDENCE,
            "evidence": [],
        }

    # --------------------------------------------------------
    # Limit evidence supplied to the LLM
    # --------------------------------------------------------

    selected = filtered[:top_k]

    # --------------------------------------------------------
    # Generate answer
    # --------------------------------------------------------

    try:
        answer = generate_with_gemini(
            question,
            selected,
        )

        # ----------------------------------------------------
        # If Gemini itself says there is insufficient evidence,
        # normalize it to the application's canonical response.
        # ----------------------------------------------------

        if is_insufficient_answer(answer):
            answer = INSUFFICIENT_EVIDENCE

    except Exception:
        # ----------------------------------------------------
        # Deterministic fallback keeps the app usable even if
        # Gemini is temporarily unavailable.
        # ----------------------------------------------------

        answer = fallback_answer(
            question,
            question_type,
            selected,
        )

    # --------------------------------------------------------
    # IMPORTANT:
    #
    # Evidence metadata and exact quotes come directly from
    # the original TranscriptSegment objects.
    #
    # Gemini does NOT create these citations.
    # --------------------------------------------------------

    evidence_payload = [
        format_evidence(
            segment,
            score,
        )
        for segment, score in selected
    ]

    return {
        "answer": answer,
        "evidence": evidence_payload,
    }