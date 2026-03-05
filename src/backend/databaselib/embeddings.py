import numpy as np
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def normalize(values: list[float]) -> list[float]:
    arr = np.array(values)
    return (arr / np.linalg.norm(arr)).tolist()


def embed_document(text: str) -> list[float]:
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_DOCUMENT", output_dimensionality=1536
        ),
    )
    return normalize(result.embeddings[0].values)


def embed_query(text: str) -> list[float]:
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_QUERY", output_dimensionality=1536
        ),
    )
    return normalize(result.embeddings[0].values)
