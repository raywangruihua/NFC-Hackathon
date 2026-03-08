import numpy as np
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
from typing import cast

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def normalize(values: list[float]) -> list[float]:
    arr = np.asarray(values, dtype=float)
    norm = float(np.linalg.norm(arr))
    if norm == 0:
        return [0.0 for _ in values]
    normalized = arr / norm
    return cast(list[float], normalized.tolist())


def _extract_embedding_values(result: object) -> list[float]:
    embeddings = getattr(result, "embeddings", None)
    if not isinstance(embeddings, list) or not embeddings:
        raise RuntimeError("Embedding API returned no embeddings")

    first = embeddings[0]
    values = getattr(first, "values", None)
    if not isinstance(values, list) or not all(isinstance(v, (int, float)) for v in values):
        raise RuntimeError("Embedding API returned invalid embedding values")

    return [float(v) for v in values]


def embed_document(text: str) -> list[float]:
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_DOCUMENT", output_dimensionality=1536
        ),
    )
    return normalize(_extract_embedding_values(result))


def embed_query(text: str) -> list[float]:
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_QUERY", output_dimensionality=1536
        ),
    )
    return normalize(_extract_embedding_values(result))
