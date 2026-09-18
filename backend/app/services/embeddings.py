import os
from google import genai


# Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

EMBEDDING_MODEL = "gemini-embedding-001"


def create_embedding(text: str) -> list[float]:
    """
    Create an embedding for a piece of transcript text.
    """
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
    )

    return response.embeddings[0].values