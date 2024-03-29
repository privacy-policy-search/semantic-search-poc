from dataclasses import dataclass
from pathlib import Path
from typing import Union

import numpy as np
import torch
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim

@dataclass
class PrivacyPolicy:
    domain: str
    year: str
    text: list[str]


def get_vectors(
    model: SentenceTransformer,
    privacy_policies: list[PrivacyPolicy],
    embeddings_path: Union[str, Path] = Path("embeddings.npy"),
) -> np.ndarray:

    if Path(embeddings_path).exists():
        # if npy file exists load vectors from disk
        embeddings = np.load(embeddings_path)
    else:
        # otherwise embed texts and save vectors to disk
        sentences = []
        for p in privacy_policies:
            joined_paragraphs = ",".join(p.text)
            sentence = " ".join([p.domain, p.year, joined_paragraphs])
            sentences.append(sentence)
        embeddings = model.encode(sentences=sentences)
        np.save(embeddings_path, embeddings)

    return embeddings


def find_privacy_policy(
    query: str,
    privacy_policies: list[PrivacyPolicy],
    model: SentenceTransformer,
    embeddings,
    n=1,
) -> list[PrivacyPolicy]:
    """embed file, calculate similarity to existing embeddings, return top n hits"""
    embedded_desc: torch.Tensor = model.encode(query, convert_to_tensor=True)  # type: ignore
    sims = cos_sim(embedded_desc, embeddings)
    top_n = sims.argsort(descending=True)[0][:n]
    return [privacy_policies[i] for i in top_n]
