query = "This is a sample query"
results = vector_db.query(query, k=3)  # Query the chroma_db and retrieve the top 3 similar results
for result in results:
    print(f"Content: {result.page_content}, Metadata: {result.metadata}")
