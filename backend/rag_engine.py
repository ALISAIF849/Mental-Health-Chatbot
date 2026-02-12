from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os

model = SentenceTransformer("all-MiniLM-L6-v2")

knowledge_path = "data/mental_health_knowledge.txt"

if not os.path.exists(knowledge_path):
    raise FileNotFoundError("mental_health_knowledge.txt not found")

with open(knowledge_path, "r", encoding="utf-8") as f:
    knowledge = [line.strip() for line in f.readlines() if line.strip()]

if len(knowledge) == 0:
    raise ValueError("Knowledge file is empty. Add some content.")

# Generate embeddings
embeddings = model.encode(knowledge)

# Ensure embeddings are 2D
if len(embeddings.shape) == 1:
    embeddings = np.expand_dims(embeddings, axis=0)

dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings))


def retrieve_context(query):
    query_vector = model.encode([query])
    D, I = index.search(np.array(query_vector), k=min(2, len(knowledge)))
    return [knowledge[i] for i in I[0]]
