query = "This is a sample query"
results = vector_db.similarity_search(query, k=3)  # Retrieve the top 3 similar results
for result in results:
    print(f"Content: {result.page_content}, Metadata: {result.metadata}")
