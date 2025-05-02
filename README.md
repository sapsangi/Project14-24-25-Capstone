# README: Fine-Tuning ChatGPT with Custom Sources

**Team Members:** Sneha Apsangi, Pushpita Barua, Yemberzal Sartaj, Karthik Seethepalli, and Varsha Venkatesh

---

## LLM Fine-Tuning Process (Brief Overview)

### 1. Prepare the Dataset
- Find URL or PDF sources based on the topic of interest.
- Collect and organize the data for fine-tuning.
- Format this data into JSONL files using the `create-jsonl.py` script.
- The JSONL file should include clear prompts and responses tailored to our specific needs. This is done by prompting gpt-4.o to create chat completion lines.

### 3. Upload the Dataset and Fine-Tune
- Use the OpenAI API to upload the JSONL file to OpenAI's servers. This prepares your dataset for the fine-tuning process.

### 5. Test the Fine-Tuned Model
- After fine-tuning, we shall use scripts like `query.py` to test the model.
- Input prompts and observe how the model generates responses based on the fine-tuned data.

### 6. Deploy or Use
- The fine-tuned model is now ready to be used in real-world applications.
- We can integrate it into projects, run queries, or utilize it for chat-based interactions using tools like `chat.py`.

---

## File Folders and Their Purposes

**Directories:**

> Numbers next to directory names indicate the order in which scripts within the directory should be executed. The `text-files` and `pdf-docs` directories should be moved into the appropriate directory as necessary (ex: when executing scripts in `1-scraping`, both `pdf-docs` and `text-files` should be moved into the `1-scraping` directory).

### `1-scraping`
- This directory covers the scraping of URL and PDF sources.
- URLs are hard-coded into the URL scraping script.
- PDFs are scraped from the `pdf-docs` directory.
- Both the `text-files` and `pdf-docs` directories should be in `1-scraping` when running these scripts.

### `2-jsonlcreation`
- Scripts in this directory prompt OpenAI models to synthesize the raw scraped files and create chat completion lines in a JSONL file based on the content of the file.
- Chat completion lines are a form of prompt that are used to fine-tune OpenAI models for text generation purposes.
- You can learn more about chat completion lines using this link: [https://platform.openai.com/docs/guides/text?api-mode=chat](https://platform.openai.com/docs/guides/text?api-mode=chat).
- Only the `text-files` directory must be in the `2-jsonlcreation` directory when running these scripts.
- Created JSONL files are stored in the `jsonl-files` directory, which should be moved into the `2-jsonlcreation` directory during this step.

### `3-finetuning`
- Using an iterative fine-tuning script, the script in this directory uploads all JSONL files to the OpenAI Files API and creates mini checkpoint models based on the content of the files.
- Using the iterative training, the gradual build-on of sources creates the final fine-tuned model.
- The `jsonl-files` directory should be in the `3-finetuning` directory when running this step.

> **NOTE:** The OpenAI API key should be stored as an environment variable named `OPENAI_API_KEY` for all steps.

---

## Scripts

- `pdf-scraper.py`
- `url-parser.py`
- `create-jsonl.py`
- `iterative-finetuning.py`
- `unused-scripts`

---

**Happy Fine-Tuning!**

