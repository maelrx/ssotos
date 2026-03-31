"""Embedding service — D-94, D-95, D-96.

Batch embedding generation with concurrency control.
"""
from __future__ import annotations

import asyncio
import os
import uuid
from dataclasses import dataclass
from typing import Protocol

import httpx

# --- Embeddings provider protocol ---


class EmbeddingsProvider(Protocol):
    """Protocol for embedding generation providers."""

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a batch of texts.

        Args:
            texts: List of text chunks to embed

        Returns:
            List of embedding vectors (1536-dim for text-embedding-3-small)
        """
        ...


# --- OpenAI embeddings provider ---


@dataclass(frozen=True)
class EmbeddingResult:
    """Result of a single embedding generation."""

    chunk_id: uuid.UUID
    embedding_vector: list[float]
    model: str


class OpenAIEmbeddingsProvider:
    """OpenAI text-embedding-3-small provider.

    Uses httpx async client directly (not full openai SDK) per Stack Decision Record.
    """

    def __init__(self, api_key: str | None = None, model: str = "text-embedding-3-small", dimensions: int = 1536):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.model = model
        self.dimensions = dimensions

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a batch of texts using OpenAI API."""
        if not texts:
            return []
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/embeddings",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "input": texts,
                    "model": self.model,
                    "dimensions": self.dimensions,
                },
            )
            response.raise_for_status()
            data = response.json()
            return [item["embedding"] for item in data["data"]]


# --- Provider cache ---


_provider_cache: EmbeddingsProvider | None = None


def get_embeddings_provider() -> EmbeddingsProvider:
    """Get or create the global embeddings provider.

    Returns cached OpenAIEmbeddingsProvider instance.
    """
    global _provider_cache
    if _provider_cache is None:
        _provider_cache = OpenAIEmbeddingsProvider()
    return _provider_cache


# --- Batch embedding generation ---


async def generate_embeddings_batch(
    provider: EmbeddingsProvider,
    chunks: list[tuple[uuid.UUID, str]],
    batch_size: int = 100,
    max_concurrent: int = 5,
) -> list[EmbeddingResult]:
    """Generate embeddings for chunks in batches with concurrency control.

    Args:
        provider: The embeddings provider to use
        chunks: List of (chunk_id, content_text) pairs
        batch_size: Number of chunks per API call (default 100, per D-96)
        max_concurrent: Maximum concurrent API calls (default 5, per D-95)

    Returns:
        List of EmbeddingResult with chunk_id, vector, and model

    Raises:
        ValueError: If provider raises an error
    """
    if not chunks:
        return []

    semaphore = asyncio.Semaphore(max_concurrent)

    async def embed_batch(batch: list[tuple[uuid.UUID, str]]) -> list[EmbeddingResult]:
        async with semaphore:
            chunk_ids, texts = zip(*batch)
            try:
                vectors = await provider.embed_texts(list(texts))
                return [
                    EmbeddingResult(
                        chunk_id=cid,
                        embedding_vector=vector,
                        model=getattr(provider, "model", "unknown"),
                    )
                    for cid, vector in zip(chunk_ids, vectors)
                ]
            except Exception as e:
                raise ValueError(f"Embedding generation failed: {e}") from e

    # Process in batches
    results: list[EmbeddingResult] = []
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        batch_results = await embed_batch(batch)
        results.extend(batch_results)

    return results
