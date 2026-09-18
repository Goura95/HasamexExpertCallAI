from app.models.transcript import Expert, TranscriptSegment


# The active dataset used by every endpoint.
#
# This starts with the bundled transcript dataset.
# /api/upload replaces these values with the uploaded transcripts.
active_segments: list[TranscriptSegment] = []
active_experts: list[Expert] = []
active_retriever = None


def set_active_data(
    segments: list[TranscriptSegment],
    experts: list[Expert],
    retriever,
) -> None:
    global active_segments
    global active_experts
    global active_retriever

    active_segments = segments
    active_experts = experts
    active_retriever = retriever


def get_active_segments() -> list[TranscriptSegment]:
    return active_segments


def get_active_experts() -> list[Expert]:
    return active_experts


def get_active_retriever():
    return active_retriever