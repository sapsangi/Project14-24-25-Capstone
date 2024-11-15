import os

# Directory with text files
directory = "sources/"

# Load and preprocess text
documents = []
for filename in os.listdir(directory):
    if filename.endswith(".txt"):
        with open(os.path.join(directory, filename), 'r', encoding='utf-8') as file:
            text = file.read().strip()
            documents.append({"filename": filename, "content": text})


from sentence_transformers import SentenceTransformer

# Load the model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Generate embeddings
embeddings = [{"filename": doc["filename"], 
               "content": doc["content"], 
               "embedding": model.encode(doc["content"])} for doc in documents]

import chromadb

# Initialize Chroma
client = chromadb.Client()
collection = client.create_collection("example_collection")

# Insert embeddings
for doc in embeddings:
    collection.add(
        ids=[doc["filename"]],
        embeddings=[doc["embedding"]],
        metadatas=[{"content": doc["content"]}]
    )

query_embedding = model.encode("What is the FCC?")

# Query ChromaDB
results = collection.query(query_embeddings=[query_embedding], n_results=5)
print(results)
