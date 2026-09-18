import numpy as np
import faiss

from app.models.transcript import TranscriptSegment
from app.services.embeddings import create_embedding


class TranscriptRetriever:
    def __init__(self, segments: list[TranscriptSegment]):
        self.segments = segments
        self.embeddings: list[list[float]] = []
        self.index = None
        self.searchable_segments: list[TranscriptSegment] = []

    def build_index(self):
        # Use expert statements as the primary evidence source.
        # Interviewer questions are intentionally excluded from retrieval
        # because they are prompts, not expert evidence.
        self.searchable_segments = [
            segment
            for segment in self.segments
            if segment.speaker != "Interviewer"
        ]

        self.embeddings = []

        for segment in self.searchable_segments:
            text_for_embedding = (
                f"Expert: {segment.expert}\n"
                f"Role: {segment.role}\n"
                f"Market: {segment.market}\n"
                f"Speaker: {segment.speaker}\n"
                f"Transcript: {segment.text}"
            )

            embedding = create_embedding(text_for_embedding)
            self.embeddings.append(embedding)

        vectors = np.array(
            self.embeddings,
            dtype="float32",
        )

        faiss.normalize_L2(vectors)

        dimension = vectors.shape[1]

        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(vectors)

    def search(
        self,
        query: str,
        top_k: int = 6,
    ) -> list[tuple[TranscriptSegment, float]]:

        if self.index is None:
            raise RuntimeError(
                "Retrieval index has not been built."
            )

        query_embedding = create_embedding(query)

        query_vector = np.array(
            [query_embedding],
            dtype="float32",
        )

        faiss.normalize_L2(query_vector)

        # Search slightly more results than requested so we can
        # safely return the requested number of valid expert segments.
        search_k = min(
            max(top_k * 2, top_k),
            len(self.searchable_segments),
        )

        scores, indices = self.index.search(
            query_vector,
            search_k,
        )

        results = []

        for score, index in zip(
            scores[0],
            indices[0],
        ):
            if index == -1:
                continue

            segment = self.searchable_segments[index]

            results.append(
                (
                    segment,
                    float(score),
                )
            )

            if len(results) >= top_k:
                break

        return results