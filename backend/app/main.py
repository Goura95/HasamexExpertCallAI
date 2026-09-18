from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.services.guide import get_guide_data
from app.services.rag import answer_question
from app.services.runtime_data import (
    get_active_experts,
    get_active_retriever,
    get_active_segments,
    set_active_data,
)
from app.services.themes import get_themes
from app.services.transcript_data import (
    get_all_segments,
    get_experts,
)
from app.services.retrieval import TranscriptRetriever
from app.services.upload import (
    parse_transcript_file,
    validate_uploaded_dataset,
)


# ============================================================
# APPLICATION
# ============================================================

app = FastAPI(
    title="ExpertCall AI",
    description=(
        "Evidence-grounded transcript intelligence "
        "for the Hasamex technical case."
    ),
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST MODELS
# ============================================================

class AskRequest(BaseModel):
    question: str
    top_k: int = 6


# ============================================================
# STARTUP / RUNTIME DATA
# ============================================================

def build_runtime_dataset():
    """
    Load the bundled Hasamex case transcripts at startup,
    build the FAISS retrieval index, and activate the dataset.
    """

    segments = get_all_segments()
    experts = get_experts()

    retriever = TranscriptRetriever(segments)
    retriever.build_index()

    set_active_data(
        segments,
        experts,
        retriever,
    )

    print(
        f"Loaded {len(segments)} transcript segments."
    )

    print(
        "Searchable expert segments:",
        len(retriever.searchable_segments),
    )


@app.on_event("startup")
def startup_event():
    build_runtime_dataset()


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "name": "ExpertCall AI",
        "status": "online",
        "service": "Evidence-grounded transcript intelligence",
    }


# ============================================================
# EXPERTS
# ============================================================

@app.get("/api/experts")
def experts():
    """
    Return the currently active experts.
    """

    return get_active_experts()


# ============================================================
# TRANSCRIPTS / EVIDENCE
# ============================================================

@app.get("/api/transcripts")
def transcripts():
    """
    Return all expert statements from the currently active
    transcript dataset.

    Interviewer questions are excluded because the evidence
    layer should contain source statements from the experts.
    """

    return [
        {
            "segment_id": segment.id,
            "expert": segment.expert,
            "role": segment.role,
            "market": segment.market,
            "speaker": segment.speaker,
            "timestamp": segment.timestamp,
            "quote": segment.text,
        }
        for segment in get_active_segments()
        if segment.speaker != "Interviewer"
    ]


# ============================================================
# INTERVIEW GUIDE
# ============================================================

@app.get("/api/guide")
def guide():
    """
    Return the six interview-guide questions with
    evidence-backed answers for each expert.
    """

    return get_guide_data()


# ============================================================
# THEMES
# ============================================================

@app.get("/api/themes")
def themes():
    """
    Return common themes identified across the active
    transcripts.
    """

    return get_themes()


# ============================================================
# DIFFERENCES / MARKET COMPARISON
# ============================================================

@app.get("/api/differences")
def differences():
    """
    Compare the three experts across the main interview topics.

    Evidence is selected using explicit transcript segment IDs
    rather than broad keyword matching.

    This is important for evidence grounding because a keyword
    such as "utilisation", "cost", or "growth" can appear in
    multiple topics. Explicit segment selection prevents an
    unrelated transcript statement from being displayed as
    evidence for another comparison topic.

    The original transcript text, speaker, market, expert and
    timestamp are always returned directly from the transcript
    records.
    """

    segments = get_active_segments()

    # --------------------------------------------------------
    # Build lookup of expert statements
    # --------------------------------------------------------

    segment_lookup = {
        segment.id: segment
        for segment in segments
        if segment.speaker != "Interviewer"
    }

    # --------------------------------------------------------
    # Convert original transcript segment into evidence object
    # --------------------------------------------------------

    def evidence_dict(
        segment_id: str,
    ) -> dict | None:
        segment = segment_lookup.get(segment_id)

        if segment is None:
            return None

        return {
            "segment_id": segment.id,
            "expert": segment.expert,
            "role": segment.role,
            "market": segment.market,
            "speaker": segment.speaker,
            "timestamp": segment.timestamp,
            "quote": segment.text,
        }

    # --------------------------------------------------------
    # Build evidence from explicit segment IDs
    # --------------------------------------------------------

    def build_evidence(
        segment_ids: list[str],
    ) -> list[dict]:
        evidence = []

        for segment_id in segment_ids:
            item = evidence_dict(segment_id)

            if item is not None:
                evidence.append(item)

        return evidence

    # --------------------------------------------------------
    # Explicit comparison definitions
    # --------------------------------------------------------

    comparison_definitions = [
        {
            "id": "comparison-economics",
            "topic": "Economic decision-making",
            "summary": (
                "France and Germany place strong emphasis on "
                "capital budgets, utilisation and the economic "
                "case. The UK describes economics as balanced "
                "with clinical strategy rather than finance alone."
            ),
            "evidence_ids": [
                # France
                "fr_004",
                "fr_006",

                # Germany
                "de_004",
                "de_006",

                # United Kingdom
                "uk_008",
            ],
        },
        {
            "id": "comparison-training",
            "topic": "Training and utilisation",
            "summary": (
                "All three experts connect training capacity "
                "with successful adoption and system utilisation. "
                "The UK additionally highlights theatre staff "
                "training capacity."
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
            "id": "comparison-trend",
            "topic": "Expected adoption trend",
            "summary": (
                "All three experts expect continued growth, "
                "but their expectations differ in emphasis. "
                "France describes steady growth, Germany expects "
                "gradual growth, while the UK describes a more "
                "positive possibility of acceleration."
            ),
            "evidence_ids": [
                # France
                "fr_012",

                # Germany
                "de_012",

                # United Kingdom
                "uk_010",
            ],
        },
        {
            "id": "comparison-timeline",
            "topic": "Purchase decision timeline",
            "summary": (
                "The experts report different typical timelines "
                "and all note that funding or capital-cycle "
                "constraints can extend the process."
            ),
            "evidence_ids": [
                # France
                "fr_014",

                # Germany
                "de_014",

                # United Kingdom
                "uk_012",
            ],
        },
    ]

    # --------------------------------------------------------
    # Build final comparison response
    # --------------------------------------------------------

    results = []

    for definition in comparison_definitions:
        evidence = build_evidence(
            definition["evidence_ids"]
        )

        # If no valid evidence exists, do not display the
        # comparison as if it were supported.
        if not evidence:
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


# ============================================================
# ASK THE CALLS
# ============================================================

@app.post("/api/ask")
def ask(request: AskRequest):
    """
    Answer a question across all active transcripts using
    retrieval-augmented generation.

    The retriever provides transcript evidence.
    The RAG layer is responsible for grounded synthesis.
    """

    retriever = get_active_retriever()

    if retriever is None:
        return {
            "question": request.question,
            "answer": (
                "The transcript retrieval engine is not "
                "ready yet."
            ),
            "evidence": [],
        }

    return answer_question(
        request.question,
        retriever,
        top_k=request.top_k,
    )


# ============================================================
# UPLOAD TRANSCRIPTS
# ============================================================

@app.post("/api/upload")
async def upload_transcripts(
    files: list[UploadFile] = File(...),
):
    """
    Upload exactly three .txt expert transcripts.

    The uploaded dataset replaces the bundled default dataset
    after validation and a new FAISS index is successfully built.
    """

    # --------------------------------------------------------
    # Validate number of files
    # --------------------------------------------------------

    if len(files) != 3:
        return {
            "message": (
                "Please upload exactly 3 transcript files."
            )
        }

    experts = []
    segments = []

    # --------------------------------------------------------
    # Parse every uploaded transcript
    # --------------------------------------------------------

    for index, uploaded_file in enumerate(
        files,
        start=1,
    ):
        filename = uploaded_file.filename or (
            f"transcript_{index}.txt"
        )

        # ----------------------------------------------------
        # Validate extension
        # ----------------------------------------------------

        if not filename.lower().endswith(".txt"):
            return {
                "message": (
                    f"{filename}: only .txt files "
                    "are supported."
                )
            }

        # ----------------------------------------------------
        # Read file
        # ----------------------------------------------------

        content = await uploaded_file.read()

        # ----------------------------------------------------
        # Parse transcript
        # ----------------------------------------------------

        try:
            expert, parsed_segments = (
                parse_transcript_file(
                    filename,
                    content,
                    index,
                )
            )

        except ValueError as error:
            return {
                "message": str(error)
            }

        experts.append(expert)
        segments.extend(parsed_segments)

    # --------------------------------------------------------
    # Validate complete uploaded dataset
    # --------------------------------------------------------

    try:
        validate_uploaded_dataset(
            experts,
            segments,
        )

    except ValueError as error:
        return {
            "message": str(error)
        }

    # --------------------------------------------------------
    # Build new retrieval index
    # --------------------------------------------------------

    try:
        retriever = TranscriptRetriever(segments)
        retriever.build_index()

    except Exception as error:
        return {
            "message": (
                "The transcripts were parsed successfully, "
                "but the retrieval index could not be built: "
                f"{error}"
            )
        }

    # --------------------------------------------------------
    # Activate uploaded dataset
    # --------------------------------------------------------

    set_active_data(
        segments,
        experts,
        retriever,
    )

    # --------------------------------------------------------
    # Backend logging
    # --------------------------------------------------------

    print(
        "Uploaded dataset activated:"
    )

    print(
        "Experts:",
        len(experts),
    )

    print(
        "Segments:",
        len(segments),
    )

    print(
        "Searchable expert segments:",
        len(retriever.searchable_segments),
    )

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {
        "message": (
            "Successfully uploaded and activated "
            "3 expert transcripts."
        ),
        "experts": len(experts),
        "segments": len(segments),
        "searchable_expert_segments": len(
            retriever.searchable_segments
        ),
        "markets": [
            expert.market
            for expert in experts
        ],
    }