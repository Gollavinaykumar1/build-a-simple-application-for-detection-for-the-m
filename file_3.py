from sentence_transformers import SentenceTransformer
import torch

class Embeddings:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def get_embedding(self, text: str) -> torch.Tensor:
        return self.model.encode(text)

    def compare_embeddings(self, embedding1: torch.Tensor, embedding2: torch.Tensor) -> float:
        return torch.cosine_similarity(embedding1, embedding2).item()