import os
import time
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))  # Replace with your actual API key

print("API Key Loaded Successfully!")

# Directory containing your JSONL files
JSONL_DIR = "jsonl-files"  # Ensure all your JSONL files are in this directory
import os
import json

# Path to the JSONL files
jsonl_directory = "jsonl-files"

def validate_and_fix_jsonl(file_path):
    """ Validates and fixes JSONL files by ensuring proper JSON formatting. """
    try:
        fixed_lines = []
        
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                try:
                    json_obj = json.loads(line.strip())  # Validate JSON
                    fixed_lines.append(json.dumps(json_obj, ensure_ascii=False))  # Reformat JSON
                except json.JSONDecodeError as e:
                    print(f"❌ Invalid JSON line in {file_path}: {line.strip()} - Skipping this line.")
        
        if fixed_lines:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write("\n".join(fixed_lines) + "\n")
            print(f"✅ Fixed JSONL file: {file_path}")
        else:
            print(f"⚠️ No valid JSON lines found in {file_path}. Consider reviewing it manually.")

    except Exception as e:
        print(f"Error processing {file_path}: {e}")

# Process all JSONL files in the directory
for jsonl_file in os.listdir(jsonl_directory):
    if jsonl_file.endswith(".jsonl"):
        validate_and_fix_jsonl(os.path.join(jsonl_directory, jsonl_file))

print("🚀 JSONL validation and fixing complete.")


def validate_jsonl(file_path):
    """
    Validates a JSONL file by checking its structure.
    Returns True if valid, False if errors are found.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                json_obj = json.loads(line.strip())  # Ensure valid JSON structure
                
                if "messages" not in json_obj or not isinstance(json_obj["messages"], list):
                    print(f"Invalid structure in {file_path}")
                    return False
                
                for message in json_obj["messages"]:
                    if "role" not in message or "content" not in message:
                        print(f"Missing 'role' or 'content' in {file_path}")
                        return False
                    
        return True  # File is valid

    except Exception as e:
        print(f"Error in {file_path}: {e}")
        return False


def upload_jsonl_files():
    """
    Uploads valid JSONL files to OpenAI for fine-tuning.
    Returns a list of uploaded file IDs.
    """
    file_ids = []
    for file_name in os.listdir(JSONL_DIR):
        if file_name.endswith(".jsonl"):
            file_path = os.path.join(JSONL_DIR, file_name)
            if validate_jsonl(file_path):
                with open(file_path, "rb") as f:
                    response = client.files.create(file=f, purpose="fine-tune")
                    file_id = response.id
                    file_ids.append(file_id)
                    print(f"Uploaded {file_name} → File ID: {file_id}")
            else:
                print(f"Skipping invalid file: {file_name}")

    return file_ids


import os

for file in os.listdir("jsonl-files"):
    if file.endswith(".jsonl"):
        with open(f"jsonl-files/{file}", "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        with open(f"jsonl-files/{file}", "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Re-encoded {file} to UTF-8.")
        

def fine_tune_model(file_ids):
    """
    Creates a fine-tuning job using the uploaded file IDs.
    """
    if not file_ids:
        print("No valid JSONL files uploaded. Exiting.")
        return None

    response = client.fine_tuning.jobs.create(
        training_file=file_ids[0],  # Only one training file allowed per job
        model="gpt-4o-2024-08-06",  # Change if using GPT-4o fine-tuning
        hyperparameters={
            "n_epochs": 5,  # Number of passes over the training data
            "batch_size": "auto",  # Automatically optimizes batch size
            "learning_rate_multiplier": "auto"  # Auto-adjusts learning rate
        }
    )

    job_id = response.id
    print(f"Fine-tuning job created: {job_id}")
    return job_id


def track_fine_tuning_status(job_id):
    """
    Monitors the fine-tuning job until it completes.
    """
    if not job_id:
        print("No job to track.")
        return

    while True:
        job = client.fine_tuning.jobs.retrieve(job_id)
        print(f"Status: {job.status}")

        if job.status in ["succeeded", "failed"]:
            print(f"Final status: {job.status}")
            if job.status == "succeeded":
                print(f"Fine-tuned model ID: {job.fine_tuned_model}")
            break

        time.sleep(60)  # Check every 60 seconds


if __name__ == "__main__":
    print("\n🚀 Starting fine-tuning process...\n")

    # Step 1: Upload valid JSONL files
    file_ids = upload_jsonl_files()

    # Step 2: Start fine-tuning
    job_id = fine_tune_model(file_ids)

    # Step 3: Track the fine-tuning progress
    track_fine_tuning_status(job_id)

    print("\n✅ Fine-tuning process complete.\n")
    
















































