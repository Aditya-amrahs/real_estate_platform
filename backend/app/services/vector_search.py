from sentence_transformers import SentenceTransformer
import numpy as np

# Try FAISS
try:
    import faiss
    use_faiss = True
except:
    use_faiss = False

model = SentenceTransformer('all-MiniLM-L6-v2')

# FAISS setup
dimension = 384

if use_faiss:
    index = faiss.IndexFlatL2(dimension)
    property_ids = []
else:
    # fallback memory
    property_vectors = {}
    property_ids = []


def add_property_embedding(property_id: int, text: str):
    embedding = model.encode([text]).astype('float32')

    if use_faiss:
        index.add(embedding)
        property_ids.append(property_id)
    else:
        property_vectors[property_id] = embedding[0]
        property_ids.append(property_id)


def get_similar_ids(query: str, top_k=5):
    query_embedding = model.encode([query]).astype('float32')

    if use_faiss:
        distances, indices = index.search(query_embedding, top_k)

        results = []
        for i in indices[0]:
            if i < len(property_ids):
                results.append(property_ids[i])

        return results

    else:
        # fallback similarity
        results = []

        for pid in property_ids:
            emb = property_vectors[pid]

            similarity = np.dot(query_embedding[0], emb) / (
                np.linalg.norm(query_embedding[0]) * np.linalg.norm(emb)
            )

            results.append((pid, similarity))

        results.sort(key=lambda x: x[1], reverse=True)

        return [r[0] for r in results[:top_k]]