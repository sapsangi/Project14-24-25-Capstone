import os
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.schema import Document

# Initialize the OpenAI API Key
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API Key from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    raise ValueError("OpenAI API Key not found in environment variables.")

os.environ["OPENAI_API_KEY"] = openai_api_key


# Step 1: Load Text Files
def load_text_files(directory="sources/"):
    documents = []
    for file_name in os.listdir(directory):
        if file_name.endswith(".txt"):
            file_path = os.path.join(directory, file_name)
            loader = TextLoader(file_path, encoding='utf-8')
            documents.extend(loader.load())  # Append documents from each file
    return documents

# Step 2: Split Text into Chunks
def preprocess_documents(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,  # Customize chunk size
        chunk_overlap=100  # Overlap between chunks
    )
    #print("Documents:", documents)
    return [chunk for doc in documents for chunk in text_splitter.split_text(doc.page_content)]


# Step 3: Generate and Store Embeddings in a Vector Database
def create_vector_db(chunks, db_directory="chroma_db"):
    embeddings = OpenAIEmbeddings()
    if not chunks:
        print("No chunks to process.")
        return None  # Return None if no chunks
    print(embeddings) 
    
    # Generate embeddings for chunks
    embeddings_list = embeddings.embed_documents([chunk.page_content for chunk in chunks])  # Extract page_content
    #print("Embeddings:", embeddings_list)
    
    vector_db = Chroma(persist_directory=db_directory, embedding_function=embeddings)
    
    if chunks:
        vector_db.add_texts([chunk.page_content for chunk in chunks])  # Extract page_content
    else:
        print("No chunks available to add to the vector database.")
    
    return vector_db  # Return the vector_db

if __name__ == "__main__":
    # Define the directory containing your text files
    text_files_directory = "."  # Root directory

    # Step 1: Load documents
    print("Loading text files...")
    docs = load_text_files("sources/")

    # Step 2: Preprocess documents
    print("Preprocessing documents...")
    chunks = preprocess_documents(docs)  # Ensure chunks are defined here

    # Wrap chunks in Document objects
    document_chunks = [Document(page_content=chunk, metadata={"source": "chunk"}) for chunk in chunks]

    # Step 3: Create vector database
    print("Creating vector database...")
    vector_db = create_vector_db(document_chunks, db_directory="chroma_db")  # Use wrapped Document objects
    if vector_db:  # Check if vector_db is not None
        vector_db.add_documents(document_chunks)    
        print(f"Vector database created and saved in 'chroma_db'.")


