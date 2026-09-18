from pydantic import BaseModel


class TranscriptSegment(BaseModel):
    id: str
    expert: str
    role: str
    market: str
    speaker: str
    timestamp: str
    text: str


class Expert(BaseModel):
    name: str
    role: str
    market: str
    transcript_id: str