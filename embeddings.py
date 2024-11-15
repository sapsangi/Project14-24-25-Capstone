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
    return [Document(page_content=chunk) for doc in documents for chunk in text_splitter.split_text(doc.page_content)]


# Step 3: Generate and Print Embeddings
def generate_and_print_embeddings(chunks):
    embeddings = OpenAIEmbeddings()
    if not chunks:
        print("No chunks to process.")
        return None  # Return None if no chunks
    
    # Generate embeddings for chunks
    embeddings_list = embeddings.embed_documents([chunk.page_content for chunk in chunks])  # Extract page_content
    
    # Print the text chunks instead of embeddings
    for chunk in chunks:
        print("Text Chunk:", chunk.page_content)  # Print each chunk's page_content
    return embeddings_list  # Return the embeddings list

# Step 4: Save Chunks to a File
def save_chunks_to_file(chunks, file_name="chunks.txt"):
    with open(file_name, 'w', encoding='utf-8') as file:
        for chunk in chunks:
            file.write(chunk.page_content + "\n")
    print(f"Chunks have been saved to {file_name}")


# Step 4: Load, preprocess documents, and generate embeddings
if __name__ == "__main__":  # Ensure this block runs when the script is executed
    documents = load_text_files()  # Load documents from the specified directory
    chunks = preprocess_documents(documents)  # Preprocess the loaded documents
    generate_and_print_embeddings(chunks)  # Call the function to generate and print embeddings
    save_chunks_to_file(chunks)  # Call the method to save chunks to a file